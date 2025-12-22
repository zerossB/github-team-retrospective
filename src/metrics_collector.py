"""
GitHub metrics collector.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm
from src.cache_manager import CacheManager

try:
    from git import Repo, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    logger.warning("GitPython not installed. Local repository support disabled.")

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects GitHub repository metrics."""
    
    def __init__(self, client, organization:  str, repositories: List[str], 
                 start_date: str, end_date: str, options: dict = None):
        """
        Initialize the metrics collector.
        
        Args:
            client: GitHubClient instance
            organization: Organization name
            repositories: List of repository names
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            options: Configuration options
        """
        self.client = client
        self.organization = organization
        self.repository_names = repositories
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.options = options or {}
        
        # Initialize cache if enabled
        cache_enabled = self.options.get('cache', {}).get('enabled', True)
        cache_dir = self.options.get('cache', {}).get('dir', '.cache')
        cache_ttl = self.options.get('cache', {}).get('ttl_hours', 24)
        self.cache = CacheManager(cache_dir, cache_ttl) if cache_enabled else None
        
        if self.cache:
            logger.info(f"Cache enabled: {cache_dir} (TTL: {cache_ttl}h)")
        
        # Load repositories
        self.repositories = self.client.get_repositories(organization, repositories)
        
        if not self.repositories:
            raise Exception("No repositories found!")
        
        logger.info(f"Loaded {len(self.repositories)} repositories")
    
    def _is_in_date_range(self, date) -> bool:
        """Check if a date is within the specified range."""
        if not date:
            return False
        if not date.tzinfo:
            # If no timezone, assume UTC
            date = date. replace(tzinfo=self.start_date.tzinfo)
        date_naive = date.replace(tzinfo=None)
        return self.start_date <= date_naive <= self.end_date
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all metrics."""
        metrics = {
            'organization': self.organization,
            'period': {
                'start': self.start_date.strftime('%Y-%m-%d'),
                'end': self.end_date.strftime('%Y-%m-%d')
            },
            'repositories':  [],
            'summary': {}
        }
        
        print(f"\n📚 Analyzing {len(self.repositories)} repositories...\n")
        
        # Collect metrics for each repository in parallel (per repo workload is independent)
        concurrency = max(1, self.options.get('concurrency', 2))
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {executor.submit(self._collect_repository_metrics, repo): repo for repo in self.repositories}
            for future in tqdm(as_completed(futures), total=len(self.repositories), desc="Repositories"):
                repo_metrics = future.result()
                metrics['repositories'].append(repo_metrics)
        
        # Calculate overall summary
        metrics['summary'] = self._calculate_summary(metrics['repositories'])
        
        return metrics
    
    def _collect_repository_metrics(self, repo) -> Dict[str, Any]: 
        """Collect metrics for a specific repository."""
        logger.info(f"Collecting metrics for {repo. name}")
        
        # Try to get from cache
        if self.cache:
            cache_key = {
                'type': 'repository_metrics',
                'organization': self.organization,
                'repository': repo.name,
                'start_date': self.start_date.strftime('%Y-%m-%d'),
                'end_date': self.end_date.strftime('%Y-%m-%d')
            }
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"📦 Using cached data for {repo.name}")
                return cached_data
        
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
        
        # Cache the data
        if self.cache:
            cache_key = {
                'type': 'repository_metrics',
                'organization': self.organization,
                'repository': repo.name,
                'start_date': self.start_date.strftime('%Y-%m-%d'),
                'end_date': self.end_date.strftime('%Y-%m-%d')
            }
            self.cache.set(cache_key, repo_data)
        
        return repo_data
    
    def _collect_commits(self, repo) -> Dict[str, Any]:
        """Collect commit statistics."""
        # Check if local repository path is configured
        local_path = self.options.get('local_repos_path')
        if local_path and GIT_AVAILABLE:
            return self._collect_commits_from_local(repo)
        else:
            return self._collect_commits_from_api(repo)
    
    def _collect_commits_from_local(self, repo) -> Dict[str, Any]:
        """Collect commit statistics from local Git repository."""
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
            # Build local repository path
            local_path = self.options.get('local_repos_path').replace('{repo_name}', repo.name)
            repo_path = Path(local_path)
            
            if not repo_path.exists():
                logger.warning(f"Local repository not found: {repo_path}. Falling back to API.")
                return self._collect_commits_from_api(repo)
            
            logger.info(f"Reading commits from local repository: {repo_path}")
            git_repo = Repo(repo_path)
            
            # Get commits in date range
            since_timestamp = int(self.start_date.timestamp())
            until_timestamp = int(self.end_date.timestamp())
            
            commits = list(git_repo.iter_commits(
                all=True,
                since=since_timestamp,
                until=until_timestamp
            ))
            
            for commit in tqdm(commits, desc=f"  Commits ({repo.name})", unit="commits"):
                commit_date = datetime.fromtimestamp(commit.committed_date, tz=timezone.utc)
                
                if not self._is_in_date_range(commit_date):
                    continue
                
                commits_data['total'] += 1
                
                # By author
                author = commit.author.name or commit.author.email
                commits_data['by_author'][author] += 1
                
                # By month
                month = commit_date.strftime('%Y-%m')
                commits_data['by_month'][month] += 1
                
                # By weekday
                weekday = commit_date.strftime('%A')
                commits_data['by_weekday'][weekday] += 1
                
                # Code statistics
                try:
                    stats = commit.stats.total
                    commits_data['additions'][author] += stats['insertions']
                    commits_data['deletions'][author] += stats['deletions']
                    commits_data['files_changed'][author] += stats['files']
                except Exception as e:
                    logger.debug(f"Could not get stats for commit {commit.hexsha}: {e}")
                    pass
                
        except GitCommandError as e:
            logger.error(f"Git error reading {repo.name}: {e}. Falling back to API.")
            return self._collect_commits_from_api(repo)
        except Exception as e:
            logger.warning(f"Error collecting commits from local repo {repo.name}: {e}")
        
        # Convert defaultdict to regular dict
        return {
            'total': commits_data['total'],
            'by_author': dict(commits_data['by_author']),
            'by_month': dict(commits_data['by_month']),
            'by_weekday': dict(commits_data['by_weekday']),
            'additions': dict(commits_data['additions']),
            'deletions': dict(commits_data['deletions']),
            'files_changed': dict(commits_data['files_changed'])
        }
    
    def _collect_commits_from_api(self, repo) -> Dict[str, Any]:
        """Collect commit statistics from GitHub API."""
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
                
                # By author
                author = commit.commit.author.name or commit.commit.author.email
                commits_data['by_author'][author] += 1
                
                # By month
                month = commit.commit.author.date.strftime('%Y-%m')
                commits_data['by_month'][month] += 1
                
                # By weekday
                weekday = commit.commit.author.date.strftime('%A')
                commits_data['by_weekday'][weekday] += 1
                
                # Code statistics
                try:
                    stats = commit.stats
                    commits_data['additions'][author] += stats.additions
                    commits_data['deletions'][author] += stats.deletions
                    commits_data['files_changed'][author] += len(commit.files)
                except:
                    pass
                
        except Exception as e:
            logger.warning(f"Error collecting commits for {repo.name}: {e}")
        
        # Convert defaultdict to regular dict
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
        """Collect pull request statistics."""
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
            # Fetch PRs
            prs = repo.get_pulls(state='all', sort='created', direction='desc')
            
            for pr in self.client.safe_paginated_request(prs, f"  PRs ({repo. name})"):
                if not self._is_in_date_range(pr.created_at):
                    continue
                
                pr_data['total'] += 1
                
                # Status
                if pr.merged:
                    pr_data['merged'] += 1
                    # Merge time
                    if pr.merged_at and pr.created_at:
                        merge_time = (pr.merged_at - pr. created_at).total_seconds() / 3600  # hours
                        pr_data['merge_times'].append(merge_time)
                elif pr.state == 'closed':
                    pr_data['closed'] += 1
                else:
                    pr_data['open'] += 1
                
                # By author
                author = pr.user. login if pr.user else 'unknown'
                pr_data['by_author'][author] += 1
                
                # Size (additions + deletions)
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
                
                # Comments
                try:
                    comments = pr.get_comments()
                    for comment in comments:
                        commenter = comment.user. login if comment.user else 'unknown'
                        pr_data['comments'][commenter] += 1
                except:
                    pass
                
        except Exception as e:
            logger.warning(f"Error collecting PRs for {repo.name}:  {e}")
        
        # Calculate averages
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
            'avg_size_lines': round(avg_size, 0),
            'sizes': pr_data['sizes']
        }
    
    def _collect_issues(self, repo) -> Dict[str, Any]:
        """Collect issue statistics."""
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
                # Skip pull requests (GitHub API returns PRs as issues)
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
                    # Resolution time
                    if issue.closed_at:
                        close_time = (issue.closed_at - issue.created_at).total_seconds() / 3600  # hours
                        issue_data['close_times'].append(close_time)
                
                # By author
                author = issue.user.login if issue.user else 'unknown'
                issue_data['by_author'][author] += 1
                
        except Exception as e:
            logger.warning(f"Error collecting issues for {repo. name}: {e}")
        
        # Compute average resolution time
        avg_close_time = sum(issue_data['close_times']) / len(issue_data['close_times']) if issue_data['close_times'] else 0
        
        return {
            'total': issue_data['total'],
            'open': issue_data['open'],
            'closed': issue_data['closed'],
            'by_author': dict(issue_data['by_author']),
            'avg_close_time_hours': round(avg_close_time, 2)
        }
    
    def _collect_releases(self, repo) -> Dict[str, Any]:
        """Collect release statistics."""
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
            logger. warning(f"Error collecting releases for {repo.name}: {e}")
        
        return release_data
    
    def _calculate_summary(self, repositories:  List[Dict]) -> Dict[str, Any]:
        """Calculate overall summary for all repositories."""
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
            'commits_by_weekday': defaultdict(int),
            'total_additions': 0,
            'total_deletions': 0,
            'total_reviews': 0,
            'pr_approval_rate': 0,
            'avg_reviews_per_pr': 0,
            'pr_size_distribution': {'small': 0, 'medium': 0, 'large': 0, 'xlarge': 0}
        }
        
        all_contributors = defaultdict(int)
        all_reviewers = defaultdict(int)
        total_pr_sizes = []
        
        for repo in repositories:
            # Totals
            summary['total_commits'] += repo['commits']['total']
            summary['total_prs'] += repo['pull_requests']['total']
            summary['total_issues'] += repo['issues']['total']
            summary['total_releases'] += repo['releases']['total']
            
            # Languages
            if repo['language']:
                summary['languages'][repo['language']] += 1
            
            # Commits by month
            for month, count in repo['commits']['by_month'].items():
                summary['commits_by_month'][month] += count
            
            # Commits by weekday
            for weekday, count in repo['commits'].get('by_weekday', {}).items():
                summary['commits_by_weekday'][weekday] += count
            
            # Contributors
            for author, count in repo['commits']['by_author'].items():
                all_contributors[author] += count
            
            # Reviewers
            for reviewer, count in repo['pull_requests']['by_reviewer'].items():
                all_reviewers[reviewer] += count
                summary['total_reviews'] += count
            
            # PR sizes for distribution
            if 'sizes' in repo['pull_requests']:
                total_pr_sizes.extend(repo['pull_requests']['sizes'])
            
            # Lines of code
            for author, lines in repo['commits']['additions'].items():
                summary['total_additions'] += lines
            for author, lines in repo['commits']['deletions'].items():
                summary['total_deletions'] += lines
        
        # Top 10 contributors
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
        
        # Calculate average reviews per PR
        if summary['total_prs'] > 0:
            summary['avg_reviews_per_pr'] = round(summary['total_reviews'] / summary['total_prs'], 2)
        
        # Calculate PR approval rate
        total_merged = sum(repo['pull_requests']['merged'] for repo in repositories)
        if summary['total_prs'] > 0:
            summary['pr_approval_rate'] = round((total_merged / summary['total_prs']) * 100, 1)
        
        # Calculate PR size distribution
        for size in total_pr_sizes:
            if size < 100:
                summary['pr_size_distribution']['small'] += 1
            elif size < 500:
                summary['pr_size_distribution']['medium'] += 1
            elif size < 1000:
                summary['pr_size_distribution']['large'] += 1
            else:
                summary['pr_size_distribution']['xlarge'] += 1
        
        # Sort weekdays in order
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        sorted_weekdays = {day: summary['commits_by_weekday'].get(day, 0) for day in weekday_order}
        summary['commits_by_weekday'] = sorted_weekdays
        
        # Convert defaultdict to dict
        summary['languages'] = dict(summary['languages'])
        summary['commits_by_month'] = dict(sorted(summary['commits_by_month'].items()))
        
        return summary