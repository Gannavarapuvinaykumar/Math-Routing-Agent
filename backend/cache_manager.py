# Advanced Caching Layer for Math Routing Agent

import hashlib
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class MathCacheManager:
    """Advanced caching system for frequently asked mathematical questions"""
    
    def __init__(self, max_cache_size: int = 1000, ttl_hours: int = 24):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_cache_size = max_cache_size
        self.ttl_seconds = ttl_hours * 3600
        self.access_count: Dict[str, int] = {}
        self.last_access: Dict[str, float] = {}
    
    def _generate_cache_key(self, query: str) -> str:
        """Generate consistent cache key for queries"""
        # Normalize query (lowercase, remove extra spaces, common math synonyms)
        normalized = query.lower().strip()
        normalized = ' '.join(normalized.split())  # Remove extra spaces
        
        # Handle common mathematical synonyms
        synonyms = {
            'find': 'solve',
            'calculate': 'solve',
            'compute': 'solve',
            'determine': 'solve',
            'derivative': 'differentiate',
            'integral': 'integrate'
        }
        
        for old, new in synonyms.items():
            normalized = normalized.replace(old, new)
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result if available and valid"""
        cache_key = self._generate_cache_key(query)
        
        if cache_key not in self.cache:
            return None
        
        cached_data = self.cache[cache_key]
        cached_time = cached_data.get('timestamp', 0)
        
        # Check if cache entry is still valid (TTL)
        if time.time() - cached_time > self.ttl_seconds:
            self._remove_cache_entry(cache_key)
            return None
        
        # Update access statistics
        self.access_count[cache_key] = self.access_count.get(cache_key, 0) + 1
        self.last_access[cache_key] = time.time()
        
        return cached_data.get('result')
    
    def get_route_info(self, query: str) -> Optional[str]:
        """Get the original route information for a cached query"""
        cache_key = self._generate_cache_key(query)
        
        if cache_key not in self.cache:
            return None
        
        cached_data = self.cache[cache_key]
        cached_time = cached_data.get('timestamp', 0)
        
        # Check if cache entry is still valid (TTL)
        if time.time() - cached_time > self.ttl_seconds:
            return None
        
        return cached_data.get('route', 'Cache')
    
    def set(self, query: str, result: Dict[str, Any], route: str) -> None:
        """Cache a new result with metadata"""
        cache_key = self._generate_cache_key(query)
        
        # If cache is full, remove least recently used entries
        if len(self.cache) >= self.max_cache_size:
            self._evict_lru_entries()
        
        cached_data = {
            'result': result,
            'route': route,
            'timestamp': time.time(),
            'query': query,
            'created_at': datetime.now().isoformat()
        }
        
        self.cache[cache_key] = cached_data
        self.access_count[cache_key] = 1
        self.last_access[cache_key] = time.time()
    
    def _remove_cache_entry(self, cache_key: str) -> None:
        """Remove a cache entry and its metadata"""
        self.cache.pop(cache_key, None)
        self.access_count.pop(cache_key, None)
        self.last_access.pop(cache_key, None)
    
    def _evict_lru_entries(self) -> None:
        """Remove least recently used entries when cache is full"""
        # Sort by last access time and remove oldest 10%
        sorted_keys = sorted(
            self.last_access.keys(), 
            key=lambda k: self.last_access[k]
        )
        
        entries_to_remove = max(1, len(sorted_keys) // 10)
        for cache_key in sorted_keys[:entries_to_remove]:
            self._remove_cache_entry(cache_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_entries = len(self.cache)
        total_hits = sum(self.access_count.values())
        
        # Calculate hit ratio (estimated)
        hit_ratio = 0.0
        if hasattr(self, '_total_requests'):
            hit_ratio = total_hits / self._total_requests if self._total_requests > 0 else 0.0
        
        # Most popular queries
        popular_queries = sorted(
            [(self.cache[k]['query'], self.access_count[k]) for k in self.access_count.keys()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_entries': total_entries,
            'total_hits': total_hits,
            'hit_ratio': hit_ratio,
            'cache_size_limit': self.max_cache_size,
            'ttl_hours': self.ttl_seconds / 3600,
            'popular_queries': popular_queries,
            'cache_efficiency': min(100, (total_hits / max(1, total_entries)) * 10)
        }
    
    def clear_expired(self) -> int:
        """Clear all expired cache entries and return count removed"""
        current_time = time.time()
        expired_keys = []
        
        for cache_key, cached_data in self.cache.items():
            if current_time - cached_data.get('timestamp', 0) > self.ttl_seconds:
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            self._remove_cache_entry(cache_key)
        
        return len(expired_keys)
    
    def force_clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()
        self.access_count.clear()
        self.last_access.clear()

# Global cache instance
math_cache = MathCacheManager()
