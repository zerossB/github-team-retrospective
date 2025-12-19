#!/usr/bin/env python3
"""
Cache management utility for GitHub Team Retrospective.
"""

import click
import yaml
from pathlib import Path
from colorama import init, Fore

from src.cache_manager import CacheManager

# Initialize colorama
init(autoreset=True)


def load_config(config_path: str) -> dict:
    """Load YAML configuration file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        click.echo(f"{Fore.RED}❌ Config file not found: {config_path}")
        return {}
    except yaml.YAMLError as e:
        click.echo(f"{Fore.RED}❌ Error reading config file: {e}")
        return {}


@click.group()
def cli():
    """🗄️  Cache management for GitHub Team Retrospective"""
    pass


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config file")
def stats(config):
    """Show cache statistics"""
    config_data = load_config(config)
    cache_dir = config_data.get('options', {}).get('cache', {}).get('dir', '.cache')
    
    cache = CacheManager(cache_dir)
    stats = cache.get_cache_stats()
    
    click.echo(f"\n{Fore.CYAN}📊 Cache Statistics:")
    click.echo(f"   Directory: {Fore.GREEN}{cache_dir}")
    click.echo(f"   Total files: {Fore.GREEN}{stats['total_files']}")
    click.echo(f"   Valid files: {Fore.GREEN}{stats['valid_files']}")
    click.echo(f"   Expired files: {Fore.YELLOW}{stats['expired_files']}")
    click.echo(f"   Total size: {Fore.GREEN}{stats['total_size_mb']} MB")
    click.echo()


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config file")
@click.option("--older-than", type=int, help="Remove cache older than X hours")
@click.option("--all", "clear_all", is_flag=True, help="Clear all cache")
def clear(config, older_than, clear_all):
    """Clear cache files"""
    config_data = load_config(config)
    cache_dir = config_data.get('options', {}).get('cache', {}).get('dir', '.cache')
    
    cache = CacheManager(cache_dir)
    
    if not clear_all and older_than is None:
        # Default: clear expired cache
        ttl_hours = config_data.get('options', {}).get('cache', {}).get('ttl_hours', 24)
        older_than = ttl_hours
    
    if clear_all:
        click.echo(f"{Fore.YELLOW}⚠️  Clearing ALL cache files...")
        count = cache.clear()
    else:
        click.echo(f"{Fore.YELLOW}🧹 Clearing cache older than {older_than} hours...")
        count = cache.clear(older_than_hours=older_than)
    
    click.echo(f"{Fore.GREEN}✅ Removed {count} cache file(s)")


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config file")
def info(config):
    """Show cache configuration"""
    config_data = load_config(config)
    cache_config = config_data.get('options', {}).get('cache', {})
    
    enabled = cache_config.get('enabled', True)
    cache_dir = cache_config.get('dir', '.cache')
    ttl_hours = cache_config.get('ttl_hours', 24)
    
    click.echo(f"\n{Fore.CYAN}⚙️  Cache Configuration:")
    click.echo(f"   Enabled: {Fore.GREEN if enabled else Fore.RED}{enabled}")
    click.echo(f"   Directory: {Fore.GREEN}{cache_dir}")
    click.echo(f"   TTL: {Fore.GREEN}{ttl_hours} hours")
    
    # Check if directory exists
    cache_path = Path(cache_dir)
    if cache_path.exists():
        click.echo(f"   Status: {Fore.GREEN}Directory exists")
    else:
        click.echo(f"   Status: {Fore.YELLOW}Directory not created yet")
    click.echo()


if __name__ == "__main__":
    cli()
