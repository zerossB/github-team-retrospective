"""
Cliente para interação com a API do GitHub.
"""

import time
from typing import List, Optional
from github import Github, GithubException, RateLimitExceededException
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


class GitHubClient: 
    """Cliente wrapper para PyGithub com tratamento de erros e rate limiting."""
    
    def __init__(self, token: str, options: dict = None):
        """
        Inicializa o cliente GitHub.
        
        Args:
            token: Token de acesso do GitHub
            options: Opções de configuração
        """
        self.github = Github(token, timeout=options.get('timeout', 30) if options else 30)
        self.options = options or {}
        self._test_connection()
    
    def _test_connection(self):
        """Testa a conexão e autenticação com GitHub."""
        try:
            user = self.github.get_user()
            logger.info(f"Conectado como: {user.login}")
            
            # Verificar rate limit
            rate_limit = self.github.get_rate_limit()
            logger.info(f"Rate limit: {rate_limit.resources.core.remaining}/{rate_limit.resources.core.limit}")
            
        except GithubException as e: 
            raise Exception(f"Erro ao conectar ao GitHub: {e. data.get('message', str(e))}")
    
    def get_organization(self, org_name: str):
        """Obtém uma organização pelo nome."""
        try:
            return self.github.get_organization(org_name)
        except GithubException as e:
            raise Exception(f"Organização '{org_name}' não encontrada: {e.data. get('message', str(e))}")
    
    def get_repositories(self, org_name:  str, repo_names: List[str] = None) -> List: 
        """
        Obtém repositórios da organização.
        
        Args:
            org_name: Nome da organização
            repo_names: Lista de nomes de repositórios (None = todos)
        
        Returns: 
            Lista de repositórios
        """
        org = self.get_organization(org_name)
        
        if repo_names:
            # Buscar repositórios específicos
            repositories = []
            for repo_name in tqdm(repo_names, desc="Carregando repositórios"):
                try:
                    repo = org.get_repo(repo_name)
                    repositories. append(repo)
                except GithubException as e:
                    logger.warning(f"Repositório '{repo_name}' não encontrado: {e.data. get('message')}")
            return repositories
        else:
            # Buscar todos os repositórios
            all_repos = list(org.get_repos())
            
            # Filtrar baseado nas opções
            repositories = []
            for repo in all_repos:
                if repo.archived and not self.options.get('include_archived', False):
                    continue
                if repo.fork and not self.options.get('include_forks', False):
                    continue
                repositories.append(repo)
            
            return repositories
    
    def handle_rate_limit(self):
        """Aguarda se o rate limit foi excedido."""
        rate_limit = self.github.get_rate_limit()
        if rate_limit.resources.core.remaining < 100: 
            reset_time = rate_limit.resources.core.reset
            wait_time = (reset_time - time.time()) + 10  # +10s de margem
            if wait_time > 0:
                logger.warning(f"Rate limit baixo.  Aguardando {wait_time:.0f}s...")
                time.sleep(wait_time)
    
    def safe_paginated_request(self, paginated_list, desc: str = "Processando"):
        """
        Itera sobre uma lista paginada com tratamento de rate limit.
        
        Args:
            paginated_list: Lista paginada do PyGithub
            desc:  Descrição para barra de progresso
        
        Yields:
            Itens da lista paginada
        """
        items = []
        try:
            # Tentar obter o total para barra de progresso
            try:
                total = paginated_list.totalCount
            except: 
                total = None
            
            with tqdm(desc=desc, total=total, unit="items") as pbar:
                for item in paginated_list: 
                    self. handle_rate_limit()
                    items.append(item)
                    pbar.update(1)
                    
        except RateLimitExceededException: 
            self.handle_rate_limit()
            # Tentar novamente
            for item in paginated_list: 
                items.append(item)
        
        return items