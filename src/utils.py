"""
Utility functions.
"""

import logging
from colorama import Fore, Style


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Configure the logging system.
    
    Args:
        verbose: If True, set level to DEBUG
    
    Returns:
        Configured logger
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return logging.getLogger(__name__)


def print_banner():
    """Print the application banner."""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     {Fore.GREEN}🚀 GitHub Team Retrospective{Fore.CYAN}                      ║
║                                                          ║
║     {Fore.YELLOW}Generate retrospectives based on GitHub metrics{Fore.CYAN}   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def format_number(num: int) -> str:
    """
    Format number with thousand separators.
    
    Args:
        num: Number to format
    
    Returns: 
        Formatted number
    """
    return f"{num:,}".replace(',', '.')


def format_duration(hours: float) -> str:
    """
    Format duration in hours to a readable format.
    
    Args:
        hours: Duration in hours
    
    Returns: 
        Formatted duration
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
    Truncate string if it exceeds maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."