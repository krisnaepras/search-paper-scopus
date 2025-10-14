"""
Redis caching service for Scopus API results
"""

import redis
import json
import hashlib
from typing import Optional, Any
from app.core.config import settings


class RedisCache:
    """Redis caching service"""
    
    def __init__(self):
        try:
            # Parse Redis URL to add SSL options if needed
            redis_url = settings.redis_url
            
            # If using rediss:// (Redis with SSL), add SSL options
            if redis_url.startswith('rediss://'):
                import ssl
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    ssl_cert_reqs=ssl.CERT_NONE,  # Disable SSL certificate verification
                    ssl_check_hostname=False
                )
            else:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True
                )
            
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}. Caching disabled.")
            self.enabled = False
            self.redis_client = None
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        # Create a sorted string of parameters
        params_str = json.dumps(kwargs, sort_keys=True)
        # Hash it to create a fixed-length key
        hash_obj = hashlib.md5(params_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self.enabled:
            return False
        
        try:
            ttl = ttl or settings.redis_cache_ttl
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis clear pattern error: {e}")
            return 0
    
    def cache_search_results(self, query: str, limit: int, filters: dict, results: Any) -> bool:
        """Cache search results"""
        key = self._generate_key("search", query=query, limit=limit, **filters)
        return self.set(key, results)
    
    def get_cached_search(self, query: str, limit: int, filters: dict) -> Optional[Any]:
        """Get cached search results"""
        key = self._generate_key("search", query=query, limit=limit, **filters)
        return self.get(key)


# Create singleton instance
redis_cache = RedisCache()
