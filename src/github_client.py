"""
Client for interacting with the GitHub API.
"""

import time
from typing import List, Optional
from github import Github, GithubException, RateLimitExceededException
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


class GitHubClient:
    """Wrapper client for PyGithub with error handling and rate limiting."""
    
    def __init__(self, token: str, options: dict = None):
        """
        Initialize the GitHub client.
        
        Args:
            token: GitHub access token
            options: Configuration options
        """
        self.github = Github(token, timeout=options.get('timeout', 30) if options else 30)
        self.options = options or {}
        self._test_connection()
    
    def _test_connection(self):
        """Test connection and authentication with GitHub."""
        try:
            user = self.github.get_user()
            logger.info(f"Connected as: {user.login}")
            
            # Check rate limit
            rate_limit = self.github.get_rate_limit()
            logger.info(f"Rate limit: {rate_limit.resources.core.remaining}/{rate_limit.resources.core.limit}")
            
        except GithubException as e:
            raise Exception(f"Error connecting to GitHub: {e.data.get('message', str(e))}")
    
    def get_organization(self, org_name: str):
        """Get an organization by name."""
        try:
            return self.github.get_organization(org_name)
        except GithubException as e:
            raise Exception(f"Organization '{org_name}' not found: {e.data.get('message', str(e))}")
    
    def get_repositories(self, org_name: str, repo_names: List[str] = None) -> List:
        """
        Get organization repositories.
        
        Args:
            org_name: Organization name
            repo_names: List of repository names (None = all)
        
        Returns:
            List of repositories
        """
        org = self.get_organization(org_name)
        
        if repo_names:
            # Fetch specific repositories
            repositories = []
            for repo_name in tqdm(repo_names, desc="Loading repositories"):
                try:
                    repo = org.get_repo(repo_name)
                    repositories.append(repo)
                except GithubException as e:
                    logger.warning(f"Repository '{repo_name}' not found: {e.data.get('message')}")
            return repositories
        else:
            # Fetch all repositories
            all_repos = list(org.get_repos())
            
            # Filter based on options
            repositories = []
            for repo in all_repos:
                if repo.archived and not self.options.get('include_archived', False):
                    continue
                if repo.fork and not self.options.get('include_forks', False):
                    continue
                repositories.append(repo)
            
            return repositories
    
    def handle_rate_limit(self):
        """Wait if the rate limit was exceeded."""
        rate_limit = self.github.get_rate_limit()
        if rate_limit.resources.core.remaining < 100:
            reset_time = rate_limit.resources.core.reset
            wait_time = (reset_time - time.time()) + 10  # +10s buffer
            if wait_time > 0:
                logger.warning(f"Low rate limit. Waiting {wait_time:.0f}s...")
                time.sleep(wait_time)
    
    def safe_paginated_request(self, paginated_list, desc: str = "Processing"):
        """
        Iterate over a paginated list with rate limit handling.
        
        Args:
            paginated_list: PyGithub paginated list
            desc: Description for progress bar
        
        Yields:
            Items from the paginated list
        """
        items = []
        try:
            # Try to get total for progress bar
            try:
                total = paginated_list.totalCount
            except:
                total = None
            
            with tqdm(desc=desc, total=total, unit="items") as pbar:
                for item in paginated_list:
                    self.handle_rate_limit()
                    items.append(item)
                    pbar.update(1)
                    
        except RateLimitExceededException:
            self.handle_rate_limit()
            # Try again
            for item in paginated_list:
                items.append(item)
        
        return items