"""Redis client for caching"""
import redis
import json
from typing import Optional, Any
from ..config import settings


class RedisClient:
    """Client for interacting with Redis cache"""
    
    def __init__(self):
        self.client = redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
    
    async def check_connection(self) -> bool:
        """Check if Redis connection is healthy"""
        try:
            self.client.ping()
            return True
        except Exception as e:
            print(f"Redis connection check failed: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Error getting from cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache with TTL in seconds"""
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting from cache: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> bool:
        """Invalidate all keys matching pattern"""
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
            return True
        except Exception as e:
            print(f"Error invalidating cache pattern: {e}")
            return False


# Singleton instance
redis_client = RedisClient()
