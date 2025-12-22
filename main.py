#!/usr/bin/env python3
"""
Main script to generate GitHub team retrospective.
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
from src.repo_cloner import clone_or_update_repositories

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()


def load_config(config_path: str) -> dict:
    """Load YAML configuration file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        click.echo(f"{Fore.RED}❌ Config file not found: {config_path}")
        click.echo(
            f"{Fore.YELLOW}💡 Copy config.yaml.example to config.yaml and configure it"
        )
        sys.exit(1)
    except yaml.YAMLError as e:
        click.echo(f"{Fore.RED}❌ Error reading config file: {e}")
        sys.exit(1)


@click.command()
@click.option("--config", default="config.yaml", help="Path to config file")
@click.option("--org", help="Organization name (overrides config)")
@click.option(
    "--repos",
    help="Comma-separated repository list (overrides config)",
)
@click.option(
    "--all-repos",
    is_flag=True,
    help="Analyze all organization repositories",
)
@click.option("--start-date", help="Start date (YYYY-MM-DD)")
@click.option("--end-date", help="End date (YYYY-MM-DD)")
@click.option("--output-dir", help="Output directory")
@click.option(
    "--format",
    "output_format",
    multiple=True,
    help="Output format (html, markdown)",
)
@click.option("--verbose", is_flag=True, help="Verbose output")
@click.option(
    "--clone-local",
    is_flag=True,
    help="Clone/update repositories locally before analysis",
)
@click.option(
    "--clone-dir",
    help="Base directory to clone repositories (supports {repo_name})",
)
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
    clone_local,
    clone_dir,
):
    """
    🚀 GitHub Team Retrospective

    Generate team retrospectives based on GitHub metrics.
    """

    print_banner()

    # Configure logging
    logger = setup_logging(verbose or False)

    # Load configuration
    config_data = load_config(config)

    # Override with CLI args
    organization = org or config_data.get("organization")
    if not organization:
        click.echo(f"{Fore.RED}❌ Organization not specified!")
        sys.exit(1)

    # Repositories
    if all_repos:
        repositories = []
    elif repos:
        repositories = [r.strip() for r in repos.split(",")]
    else:
        repositories = config_data.get("repositories", [])

    # Dates
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
        click.echo(f"{Fore.RED}❌ GitHub token not configured!")
        click.echo(
            f"{Fore.YELLOW}💡 Set GITHUB_TOKEN or add it to config.yaml"
        )
        sys.exit(1)

    # Options
    options = config_data.get("options", {}) or {}

    click.echo(f"\n{Fore.CYAN}📊 Configuration:")
    click.echo(f"   Organization: {Fore.GREEN}{organization}")
    click.echo(
        f"   Repositories: {Fore.GREEN}{len(repositories) if repositories else 'All'}"
    )
    click.echo(f"   Period: {Fore.GREEN}{start} to {end}")
    click.echo(f"   Format: {Fore.GREEN}{', '.join(formats)}")
    click.echo()

    try:
        # Initialize GitHub client
        click.echo(f"{Fore.YELLOW}🔑 Connecting to GitHub...")
        client = GitHubClient(token, options)

        # Clone repositories locally if requested
        if clone_local:
            click.echo(f"{Fore.YELLOW}📥 Cloning repositories locally...")

            # Determine local path template
            local_path_template = (
                clone_dir
                or options.get("local_repos_path")
                or str(Path("repos") / "{repo_name}")
            )
            if "{repo_name}" not in local_path_template:
                local_path_template = str(Path(local_path_template) / "{repo_name}")

            # Fetch repository list to clone (all or specified)
            repos_to_clone = client.get_repositories(organization, repositories or None)
            repo_names = [r.name for r in repos_to_clone]

            clone_results = clone_or_update_repositories(
                organization, repo_names, local_path_template, token
            )

            for name, status in clone_results.items():
                click.echo(f"   {Fore.GREEN}✅ {name}: {status}")

            # Ensure metrics collector reads from local clones
            options["local_repos_path"] = local_path_template

        # Collect metrics
        click.echo(f"{Fore.YELLOW}📈 Collecting metrics...")
        collector = MetricsCollector(
            client, organization, repositories, start, end, options
        )
        metrics = collector.collect_all_metrics()

        # Generate reports
        click.echo(f"\n{Fore.YELLOW}📝 Generating reports...")
        generator = ReportGenerator(metrics, organization, start, end)

        # Create output directory
        Path(output_directory).mkdir(parents=True, exist_ok=True)

        # Generate each format
        for fmt in formats:
            output_file = generator.generate(fmt, output_directory)
            click.echo(f"   {Fore.GREEN}✅ {fmt.upper()}:  {output_file}")

        click.echo(f"\n{Fore.GREEN}🎉 Retrospective generated successfully!")
        click.echo(f"{Fore.CYAN}📂 Files saved in: {output_directory}")

    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error:  {str(e)}")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()