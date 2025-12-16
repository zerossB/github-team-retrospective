"""
Gerador de relatórios em diferentes formatos. 
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from jinja2 import Template
from tabulate import tabulate

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Gera relatórios de retrospectiva em diferentes formatos."""
    
    def __init__(self, metrics: Dict[str, Any], organization: str, 
                 start_date: str, end_date: str):
        """
        Inicializa o gerador de relatórios.
        
        Args:
            metrics:  Métricas coletadas
            organization: Nome da organização
            start_date: Data inicial
            end_date: Data final
        """
        self.metrics = metrics
        self.organization = organization
        self.start_date = start_date
        self.end_date = end_date
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def generate(self, format: str, output_dir: str) -> str:
        """
        Gera relatório no formato especificado.
        
        Args:
            format:  Formato do relatório (html, markdown, json)
            output_dir: Diretório de saída
        
        Returns:
            Caminho do arquivo gerado
        """
        if format == 'html':
            return self._generate_html(output_dir)
        elif format == 'markdown':
            return self._generate_markdown(output_dir)
        elif format == 'json':
            return self._generate_json(output_dir)
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def _generate_html(self, output_dir: str) -> str:
        """Gera relatório HTML interativo."""
        output_file = Path(output_dir) / f"retrospective_{self.organization}_{self.timestamp}.html"
        
        # Gerar gráficos
        charts = self._generate_charts()
        
        # Carregar template
        template_path = Path(__file__).parent. parent / 'templates' / 'report_template.html'
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = Template(template_content)
        
        # Preparar dados para o template
        summary = self. metrics['summary']
        
        html_content = template.render(
            organization=self.organization,
            start_date=self.start_date,
            end_date=self.end_date,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            summary=summary,
            repositories=self.metrics['repositories'],
            charts=charts,
            total_repos=summary['total_repositories'],
            total_commits=summary['total_commits'],
            total_prs=summary['total_prs'],
            total_issues=summary['total_issues'],
            total_releases=summary['total_releases'],
            top_contributors=summary['top_contributors'],
            top_reviewers=summary['top_reviewers']
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)
    
    def _generate_markdown(self, output_dir: str) -> str:
        """Gera relatório em Markdown."""
        output_file = Path(output_dir) / f"retrospective_{self.organization}_{self.timestamp}.md"
        
        summary = self.metrics['summary']
        
        md_content = f"""# 📊 Retrospectiva de Time - {self.organization}

**Período:** {self.start_date} até {self.end_date}  
**Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 Resumo Geral

| Métrica | Valor |
|---------|-------|
| 📚 Repositórios | {summary['total_repositories']} |
| 💻 Commits | {summary['total_commits']} |
| 🔀 Pull Requests | {summary['total_prs']} |
| 🐛 Issues | {summary['total_issues']} |
| 🏷️ Releases | {summary['total_releases']} |
| ➕ Linhas Adicionadas | {summary['total_additions']: ,} |
| ➖ Linhas Removidas | {summary['total_deletions']:,} |

---

## 🏆 Top Contribuidores

"""
        
        # Top contribuidores
        for i, (author, commits) in enumerate(summary['top_contributors'].items(), 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
            md_content += f"{i}. {medal} **{author}**:  {commits} commits\n"
        
        md_content += "\n---\n\n## 👀 Top Reviewers\n\n"
        
        # Top reviewers
        for i, (reviewer, reviews) in enumerate(summary['top_reviewers'].items(), 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
            md_content += f"{i}.  {medal} **{reviewer}**:  {reviews} reviews\n"
        
        md_content += "\n---\n\n## 💻 Linguagens Utilizadas\n\n"
        
        # Linguagens
        for lang, count in sorted(summary['languages'].items(), key=lambda x: x[1], reverse=True):
            md_content += f"- **{lang}**: {count} repositório(s)\n"
        
        md_content += "\n---\n\n## 📅 Atividade por Mês\n\n"
        
        # Commits por mês
        for month, commits in summary['commits_by_month'].items():
            md_content += f"- **{month}**: {commits} commits\n"
        
        md_content += "\n---\n\n## 📚 Detalhamento por Repositório\n\n"
        
        # Detalhes de cada repositório
        for repo in self.metrics['repositories']:
            md_content += f"""### [{repo['name']}]({repo['url']})

{repo['description'] or '_Sem descrição_'}

**Estatísticas:**
- 💻 Commits: {repo['commits']['total']}
- 🔀 Pull Requests: {repo['pull_requests']['total']} ({repo['pull_requests']['merged']} merged)
- 🐛 Issues: {repo['issues']['total']} ({repo['issues']['closed']} fechadas)
- 🏷️ Releases: {repo['releases']['total']}
- ⏱️ Tempo médio de merge: {repo['pull_requests']['avg_merge_time_hours']:.1f}h
- 📏 Tamanho médio de PR: {repo['pull_requests']['avg_size_lines']:.0f} linhas

"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(output_file)
    
    def _generate_json(self, output_dir: str) -> str:
        """Gera dados em formato JSON."""
        output_file = Path(output_dir) / f"retrospective_{self. organization}_{self.timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        
        return str(output_file)
    
    def _generate_charts(self) -> Dict[str, str]:
        """Gera gráficos interativos usando Plotly."""
        charts = {}
        summary = self.metrics['summary']
        
        # 1. Gráfico de commits por mês
        if summary['commits_by_month']: 
            months = list(summary['commits_by_month'].keys())
            commits = list(summary['commits_by_month'].values())
            
            fig = go.Figure(data=[
                go.Bar(x=months, y=commits, marker_color='rgb(55, 83, 109)')
            ])
            fig.update_layout(
                title='Commits por Mês',
                xaxis_title='Mês',
                yaxis_title='Commits',
                height=400
            )
            charts['commits_timeline'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        # 2. Top contribuidores (pizza)
        if summary['top_contributors']:
            authors = list(summary['top_contributors'].keys())[:5]
            commits = list(summary['top_contributors'].values())[:5]
            
            fig = go.Figure(data=[
                go.Pie(labels=authors, values=commits, hole=1)
            ])
            fig.update_layout(
                title='Top 5 Contribuidores',
                height=400
            )
            charts['top_contributors_pie'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        # 3. Linguagens (pizza)
        if summary['languages']:
            langs = list(summary['languages'].keys())
            counts = list(summary['languages'].values())
            
            fig = go.Figure(data=[
                go.Pie(labels=langs, values=counts)
            ])
            fig.update_layout(
                title='Linguagens Utilizadas',
                height=400
            )
            charts['languages_pie'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        # 4. PRs por repositório
        repo_names = [repo['name'] for repo in self.metrics['repositories']]
        pr_counts = [repo['pull_requests']['total'] for repo in self.metrics['repositories']]
        
        fig = go.Figure(data=[
            go.Bar(x=repo_names, y=pr_counts, marker_color='rgb(26, 118, 255)')
        ])
        fig.update_layout(
            title='Pull Requests por Repositório',
            xaxis_title='Repositório',
            yaxis_title='PRs',
            height=400
        )
        charts['prs_by_repo'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return charts