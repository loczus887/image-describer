from typing import Optional, Dict
from datetime import datetime, timedelta

class CacheManager:
    """Simple in-memory cache for frequently requested image hashes"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, tuple] = {}  # {hash: (description, expiry_time)}
        self.ttl_seconds = ttl_seconds
    
    def get(self, image_hash: str) -> Optional[str]:
        """Get cached description if available and not expired"""
        if image_hash in self.cache:
            description, expiry = self.cache[image_hash]
            if datetime.now() < expiry:
                return description
            else:
                # Expired, remove it
                del self.cache[image_hash]
        return None
    
    def set(self, image_hash: str, description: str):
        """Cache a description with TTL"""
        expiry = datetime.now() + timedelta(seconds=self.ttl_seconds)
        self.cache[image_hash] = (description, expiry)
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
    
    def remove(self, image_hash: str):
        """Remove a specific cache entry"""
        if image_hash in self.cache:
            del self.cache[image_hash]

