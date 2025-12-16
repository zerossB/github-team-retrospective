#!/usr/bin/env python3
"""
Script principal para gerar retrospectiva de time do GitHub.
"""

import os
import sys
import click
import yaml
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from colorama import init, Fore, Style

from src.github_client import GitHubClient
from src.metrics_collector import MetricsCollector
from src.report_generator import ReportGenerator
from src.utils import setup_logging, print_banner

# Inicializar colorama
init(autoreset=True)

# Carregar variáveis de ambiente
load_dotenv()


def load_config(config_path: str) -> dict:
    """Carrega o arquivo de configuração YAML."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        click.echo(
            f"{Fore.RED}❌ Arquivo de configuração não encontrado: {config_path}"
        )
        click.echo(
            f"{Fore.YELLOW}💡 Copie config.yaml.example para config.yaml e configure-o"
        )
        sys.exit(1)
    except yaml.YAMLError as e:
        click.echo(f"{Fore.RED}❌ Erro ao ler arquivo de configuração: {e}")
        sys.exit(1)


@click.command()
@click.option(
    "--config", default="config.yaml", help="Caminho para arquivo de configuração"
)
@click.option("--org", help="Nome da organização (sobrescreve config)")
@click.option(
    "--repos", help="Lista de repositórios separados por vírgula (sobrescreve config)"
)
@click.option(
    "--all-repos", is_flag=True, help="Analisar todos os repositórios da organização"
)
@click.option("--start-date", help="Data inicial (YYYY-MM-DD)")
@click.option("--end-date", help="Data final (YYYY-MM-DD)")
@click.option("--output-dir", help="Diretório de saída")
@click.option(
    "--format", "output_format", multiple=True, help="Formato de saída (html, markdown)"
)
@click.option("--verbose", is_flag=True, help="Saída detalhada")
def main(
    config,
    org,
    repos,
    all_repos,
    start_date,
    end_date,
    output_dir,
    output_format,
    verbose,
):
    """
    🚀 GitHub Team Retrospective

    Gera retrospectivas de time baseadas em métricas do GitHub.
    """

    print_banner()

    # Configurar logging
    logger = setup_logging(verbose or False)

    # Carregar configuração
    config_data = load_config(config)

    # Sobrescrever com argumentos da linha de comando
    organization = org or config_data.get("organization")
    if not organization:
        click.echo(f"{Fore.RED}❌ Organização não especificada!")
        sys.exit(1)

    # Repositórios
    if all_repos:
        repositories = []
    elif repos:
        repositories = [r.strip() for r in repos.split(",")]
    else:
        repositories = config_data.get("repositories", [])

    # Datas
    start = start_date or config_data.get("start_date", "2025-01-01")
    end = end_date or config_data.get("end_date")
    if not end:
        end = datetime.now().strftime("%Y-%m-%d")

    # Output
    output_directory = output_dir or config_data.get("output_dir", "reports")
    formats = (
        list(output_format)
        if output_format
        else config_data.get("output_formats", ["html"])
    )

    # Token
    token = os.getenv("GITHUB_TOKEN") or config_data.get("github_token")
    if not token:
        click.echo(f"{Fore.RED}❌ Token do GitHub não configurado!")
        click.echo(f"{Fore.YELLOW}💡 Configure GITHUB_TOKEN ou adicione no config.yaml")
        sys.exit(1)

    # Opções
    options = config_data.get("options", {})

    click.echo(f"\n{Fore.CYAN}📊 Configuração:")
    click.echo(f"   Organização: {Fore.GREEN}{organization}")
    click.echo(
        f"   Repositórios: {Fore.GREEN}{len(repositories) if repositories else 'Todos'}"
    )
    click.echo(f"   Período: {Fore.GREEN}{start} até {end}")
    click.echo(f"   Formato: {Fore.GREEN}{', '.join(formats)}")
    click.echo()

    try:
        # Inicializar cliente GitHub
        click.echo(f"{Fore.YELLOW}🔑 Conectando ao GitHub...")
        client = GitHubClient(token, options)

        # Coletar métricas
        click.echo(f"{Fore.YELLOW}📈 Coletando métricas...")
        collector = MetricsCollector(
            client, organization, repositories, start, end, options
        )
        metrics = collector.collect_all_metrics()

        # Gerar relatórios
        click.echo(f"\n{Fore.YELLOW}📝 Gerando relatórios...")
        generator = ReportGenerator(metrics, organization, start, end)

        # Criar diretório de saída
        Path(output_directory).mkdir(parents=True, exist_ok=True)

        # Gerar cada formato
        for fmt in formats:
            output_file = generator.generate(fmt, output_directory)
            click.echo(f"   {Fore.GREEN}✅ {fmt.upper()}:  {output_file}")

        click.echo(f"\n{Fore.GREEN}🎉 Retrospectiva gerada com sucesso!")
        click.echo(f"{Fore.CYAN}📂 Arquivos salvos em: {output_directory}")

    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Erro:  {str(e)}")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
