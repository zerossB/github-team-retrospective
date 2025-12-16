"""
Coletor de métricas do GitHub.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Coleta métricas de repositórios do GitHub."""
    
    def __init__(self, client, organization:  str, repositories: List[str], 
                 start_date: str, end_date: str, options: dict = None):
        """
        Inicializa o coletor de métricas. 
        
        Args:
            client: GitHubClient instance
            organization: Nome da organização
            repositories: Lista de nomes de repositórios
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            options: Opções de configuração
        """
        self.client = client
        self.organization = organization
        self.repository_names = repositories
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.options = options or {}
        
        # Carregar repositórios
        self.repositories = self.client.get_repositories(organization, repositories)
        
        if not self.repositories:
            raise Exception("Nenhum repositório encontrado!")
        
        logger.info(f"Carregados {len(self.repositories)} repositórios")
    
    def _is_in_date_range(self, date) -> bool:
        """Verifica se uma data está no range especificado."""
        if not date:
            return False
        if not date.tzinfo:
            # Se não tem timezone, assumir UTC
            date = date. replace(tzinfo=self.start_date.tzinfo)
        date_naive = date.replace(tzinfo=None)
        return self.start_date <= date_naive <= self.end_date
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Coleta todas as métricas."""
        metrics = {
            'organization': self.organization,
            'period': {
                'start': self.start_date.strftime('%Y-%m-%d'),
                'end': self.end_date.strftime('%Y-%m-%d')
            },
            'repositories':  [],
            'summary': {}
        }
        
        print(f"\n📚 Analisando {len(self.repositories)} repositórios...\n")
        
        # Coletar métricas de cada repositório
        for repo in tqdm(self.repositories, desc="Repositórios"):
            repo_metrics = self._collect_repository_metrics(repo)
            metrics['repositories'].append(repo_metrics)
        
        # Calcular sumário geral
        metrics['summary'] = self._calculate_summary(metrics['repositories'])
        
        return metrics
    
    def _collect_repository_metrics(self, repo) -> Dict[str, Any]: 
        """Coleta métricas de um repositório específico."""
        logger.info(f"Coletando métricas de {repo. name}")
        
        repo_data = {
            'name': repo.name,
            'full_name': repo.full_name,
            'url': repo.html_url,
            'description': repo.description,
            'language': repo.language,
            'stars': repo. stargazers_count,
            'forks': repo.forks_count,
            'commits': self._collect_commits(repo),
            'pull_requests': self._collect_pull_requests(repo),
            'issues': self._collect_issues(repo),
            'releases': self._collect_releases(repo),
            'contributors': {}
        }
        
        return repo_data
    
    def _collect_commits(self, repo) -> Dict[str, Any]:
        """Coleta estatísticas de commits."""
        commits_data = {
            'total':  0,
            'by_author': defaultdict(int),
            'by_month': defaultdict(int),
            'by_weekday': defaultdict(int),
            'additions': defaultdict(int),
            'deletions': defaultdict(int),
            'files_changed': defaultdict(int)
        }
        
        try:
            commits = repo.get_commits(since=self.start_date, until=self.end_date)
            
            for commit in self.client.safe_paginated_request(commits, f"  Commits ({repo.name})"):
                if not self._is_in_date_range(commit.commit.author.date):
                    continue
                
                commits_data['total'] += 1
                
                # Por autor
                author = commit.commit.author.name or commit.commit.author.email
                commits_data['by_author'][author] += 1
                
                # Por mês
                month = commit.commit.author.date.strftime('%Y-%m')
                commits_data['by_month'][month] += 1
                
                # Por dia da semana
                weekday = commit.commit.author.date. strftime('%A')
                commits_data['by_weekday'][weekday] += 1
                
                # Estatísticas de código
                try:
                    stats = commit.stats
                    commits_data['additions'][author] += stats.additions
                    commits_data['deletions'][author] += stats.deletions
                    commits_data['files_changed'][author] += len(commit.files)
                except:
                    pass
                
        except Exception as e:
            logger.warning(f"Erro ao coletar commits de {repo.name}: {e}")
        
        # Converter defaultdict para dict normal
        return {
            'total': commits_data['total'],
            'by_author': dict(commits_data['by_author']),
            'by_month': dict(commits_data['by_month']),
            'by_weekday': dict(commits_data['by_weekday']),
            'additions': dict(commits_data['additions']),
            'deletions': dict(commits_data['deletions']),
            'files_changed': dict(commits_data['files_changed'])
        }
    
    def _collect_pull_requests(self, repo) -> Dict[str, Any]:
        """Coleta estatísticas de pull requests."""
        pr_data = {
            'total': 0,
            'merged': 0,
            'closed': 0,
            'open': 0,
            'by_author': defaultdict(int),
            'by_reviewer': defaultdict(int),
            'merge_times': [],
            'sizes': [],
            'comments': defaultdict(int)
        }
        
        try:
            # Buscar PRs
            prs = repo.get_pulls(state='all', sort='created', direction='desc')
            
            for pr in self.client.safe_paginated_request(prs, f"  PRs ({repo. name})"):
                if not self._is_in_date_range(pr.created_at):
                    continue
                
                pr_data['total'] += 1
                
                # Status
                if pr.merged:
                    pr_data['merged'] += 1
                    # Tempo de merge
                    if pr.merged_at and pr.created_at:
                        merge_time = (pr.merged_at - pr. created_at).total_seconds() / 3600  # horas
                        pr_data['merge_times'].append(merge_time)
                elif pr.state == 'closed':
                    pr_data['closed'] += 1
                else:
                    pr_data['open'] += 1
                
                # Por autor
                author = pr.user. login if pr.user else 'unknown'
                pr_data['by_author'][author] += 1
                
                # Tamanho (additions + deletions)
                size = pr.additions + pr.deletions
                pr_data['sizes'].append(size)
                
                # Reviews
                try:
                    reviews = pr.get_reviews()
                    for review in reviews:
                        reviewer = review.user.login if review.user else 'unknown'
                        pr_data['by_reviewer'][reviewer] += 1
                except:
                    pass
                
                # Comentários
                try:
                    comments = pr.get_comments()
                    for comment in comments:
                        commenter = comment.user. login if comment.user else 'unknown'
                        pr_data['comments'][commenter] += 1
                except:
                    pass
                
        except Exception as e:
            logger.warning(f"Erro ao coletar PRs de {repo.name}:  {e}")
        
        # Calcular médias
        avg_merge_time = sum(pr_data['merge_times']) / len(pr_data['merge_times']) if pr_data['merge_times'] else 0
        avg_size = sum(pr_data['sizes']) / len(pr_data['sizes']) if pr_data['sizes'] else 0
        
        return {
            'total': pr_data['total'],
            'merged': pr_data['merged'],
            'closed': pr_data['closed'],
            'open': pr_data['open'],
            'by_author': dict(pr_data['by_author']),
            'by_reviewer': dict(pr_data['by_reviewer']),
            'comments': dict(pr_data['comments']),
            'avg_merge_time_hours': round(avg_merge_time, 2),
            'avg_size_lines': round(avg_size, 0)
        }
    
    def _collect_issues(self, repo) -> Dict[str, Any]:
        """Coleta estatísticas de issues."""
        issue_data = {
            'total':  0,
            'open':  0,
            'closed':  0,
            'by_author': defaultdict(int),
            'close_times': []
        }
        
        try:
            issues = repo.get_issues(state='all', since=self.start_date)
            
            for issue in self.client.safe_paginated_request(issues, f"  Issues ({repo.name})"):
                # Pular pull requests (GitHub API retorna PRs como issues)
                if issue.pull_request:
                    continue
                
                if not self._is_in_date_range(issue.created_at):
                    continue
                
                issue_data['total'] += 1
                
                # Status
                if issue.state == 'open':
                    issue_data['open'] += 1
                else:
                    issue_data['closed'] += 1
                    # Tempo de resolução
                    if issue.closed_at:
                        close_time = (issue.closed_at - issue.created_at).total_seconds() / 3600  # horas
                        issue_data['close_times'].append(close_time)
                
                # Por autor
                author = issue.user.login if issue.user else 'unknown'
                issue_data['by_author'][author] += 1
                
        except Exception as e:
            logger.warning(f"Erro ao coletar issues de {repo. name}: {e}")
        
        # Calcular média de tempo de resolução
        avg_close_time = sum(issue_data['close_times']) / len(issue_data['close_times']) if issue_data['close_times'] else 0
        
        return {
            'total': issue_data['total'],
            'open': issue_data['open'],
            'closed': issue_data['closed'],
            'by_author': dict(issue_data['by_author']),
            'avg_close_time_hours': round(avg_close_time, 2)
        }
    
    def _collect_releases(self, repo) -> Dict[str, Any]:
        """Coleta estatísticas de releases."""
        release_data = {
            'total':  0,
            'releases': []
        }
        
        try:
            releases = repo.get_releases()
            
            for release in releases:
                if not self._is_in_date_range(release.created_at):
                    continue
                
                release_data['total'] += 1
                release_data['releases'].append({
                    'name': release.title or release.tag_name,
                    'tag': release.tag_name,
                    'date': release.created_at.strftime('%Y-%m-%d'),
                    'author': release.author.login if release.author else 'unknown'
                })
                
        except Exception as e:
            logger. warning(f"Erro ao coletar releases de {repo.name}: {e}")
        
        return release_data
    
    def _calculate_summary(self, repositories:  List[Dict]) -> Dict[str, Any]:
        """Calcula sumário geral de todos os repositórios."""
        summary = {
            'total_repositories': len(repositories),
            'total_commits': 0,
            'total_prs': 0,
            'total_issues': 0,
            'total_releases': 0,
            'top_contributors': {},
            'top_reviewers': {},
            'languages': defaultdict(int),
            'commits_by_month': defaultdict(int),
            'total_additions': 0,
            'total_deletions': 0
        }
        
        all_contributors = defaultdict(int)
        all_reviewers = defaultdict(int)
        
        for repo in repositories:
            # Totais
            summary['total_commits'] += repo['commits']['total']
            summary['total_prs'] += repo['pull_requests']['total']
            summary['total_issues'] += repo['issues']['total']
            summary['total_releases'] += repo['releases']['total']
            
            # Linguagens
            if repo['language']:
                summary['languages'][repo['language']] += 1
            
            # Commits por mês
            for month, count in repo['commits']['by_month'].items():
                summary['commits_by_month'][month] += count
            
            # Contribuidores
            for author, count in repo['commits']['by_author'].items():
                all_contributors[author] += count
            
            # Reviewers
            for reviewer, count in repo['pull_requests']['by_reviewer'].items():
                all_reviewers[reviewer] += count
            
            # Linhas de código
            for author, lines in repo['commits']['additions'].items():
                summary['total_additions'] += lines
            for author, lines in repo['commits']['deletions'].items():
                summary['total_deletions'] += lines
        
        # Top 10 contribuidores
        summary['top_contributors'] = dict(sorted(
            all_contributors.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10])
        
        # Top 10 reviewers
        summary['top_reviewers'] = dict(sorted(
            all_reviewers.items(), 
            key=lambda x:  x[1], 
            reverse=True
        )[:10])
        
        # Converter defaultdict para dict
        summary['languages'] = dict(summary['languages'])
        summary['commits_by_month'] = dict(sorted(summary['commits_by_month'].items()))
        
        return summary