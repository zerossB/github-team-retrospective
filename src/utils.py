"""
Funções utilitárias. 
"""

import logging
from colorama import Fore, Style


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Configura o sistema de logging.
    
    Args:
        verbose: Se True, define nível DEBUG
    
    Returns:
        Logger configurado
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return logging.getLogger(__name__)


def print_banner():
    """Imprime banner do aplicativo."""
    banner = f"""
{Fore. CYAN}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     {Fore.GREEN}🚀 GitHub Team Retrospective{Fore.CYAN}                      ║
║                                                          ║
║     {Fore.YELLOW}Gere retrospectivas baseadas em métricas do GitHub{Fore.CYAN}  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def format_number(num: int) -> str:
    """
    Formata número com separadores de milhares.
    
    Args:
        num: Número a formatar
    
    Returns: 
        Número formatado
    """
    return f"{num:,}".replace(',', '.')


def format_duration(hours: float) -> str:
    """
    Formata duração em horas para formato legível.
    
    Args:
        hours: Duração em horas
    
    Returns: 
        Duração formatada
    """
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes}min"
    elif hours < 24:
        return f"{hours:.1f}h"
    else:
        days = hours / 24
        return f"{days:.1f}d"


def truncate_string(text: str, max_length: int = 50) -> str:
    """
    Trunca string se exceder tamanho máximo.
    
    Args:
        text:  Texto a truncar
        max_length: Tamanho máximo
    
    Returns:
        Texto truncado
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."