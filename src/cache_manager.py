"""
Cache manager for GitHub API responses.
"""

import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages file-based cache for GitHub API responses."""
    
    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time to live for cached data in hours (default: 24)
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Cache initialized at {self.cache_dir} with TTL of {ttl_hours}h")
    
    def _generate_cache_key(self, key_data: dict) -> str:
        """
        Generate a unique cache key from the given data.
        
        Args:
            key_data: Dictionary containing data to generate the key
            
        Returns:
            Hash string to use as cache key
        """
        # Sort keys for consistency
        sorted_data = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, key_data: dict) -> Optional[Any]:
        """
        Retrieve data from cache if available and not expired.
        
        Args:
            key_data: Dictionary containing data to generate the cache key
            
        Returns:
            Cached data if available and fresh, None otherwise
        """
        cache_key = self._generate_cache_key(key_data)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            logger.debug(f"Cache miss for key: {list(key_data.keys())}")
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                logger.debug(f"Cache expired for key: {list(key_data.keys())}")
                cache_path.unlink()  # Remove expired cache
                return None
            
            logger.debug(f"Cache hit for key: {list(key_data.keys())}")
            return cached['data']
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Error reading cache: {e}")
            # Remove corrupted cache file
            cache_path.unlink()
            return None
    
    def set(self, key_data: dict, data: Any) -> None:
        """
        Store data in cache.
        
        Args:
            key_data: Dictionary containing data to generate the cache key
            data: Data to cache (must be JSON serializable)
        """
        cache_key = self._generate_cache_key(key_data)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cached_data = {
                'timestamp': datetime.now().isoformat(),
                'key_data': key_data,
                'data': data
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Cached data for key: {list(key_data.keys())}")
            
        except (TypeError, ValueError) as e:
            logger.warning(f"Error caching data: {e}")
    
    def clear(self, older_than_hours: Optional[int] = None) -> int:
        """
        Clear cache files.
        
        Args:
            older_than_hours: If specified, only remove cache older than this many hours.
                            If None, remove all cache files.
        
        Returns:
            Number of files removed
        """
        count = 0
        cutoff_time = None
        
        if older_than_hours is not None:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if cutoff_time is not None:
                    # Check file age
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached = json.load(f)
                        cached_time = datetime.fromisoformat(cached['timestamp'])
                        if cached_time > cutoff_time:
                            continue
                
                cache_file.unlink()
                count += 1
                
            except Exception as e:
                logger.warning(f"Error removing cache file {cache_file}: {e}")
        
        logger.info(f"Cleared {count} cache file(s)")
        return count
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_files = len(cache_files)
        total_size = sum(f.stat().st_size for f in cache_files)
        
        # Count expired files
        expired = 0
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    cached_time = datetime.fromisoformat(cached['timestamp'])
                    if datetime.now() - cached_time > self.ttl:
                        expired += 1
            except Exception:
                expired += 1
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'expired_files': expired,
            'valid_files': total_files - expired
        }
