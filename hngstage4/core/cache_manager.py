"""
Redis cache manager for user data caching
"""
import logging
from typing import Any, Optional

from django.core.cache import cache

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager for user service"""

    # Cache key prefixes
    USER_PREFIX = "user"
    PROFILE_PREFIX = "user_profile"
    PREFERENCES_PREFIX = "user_preferences"
    TOKENS_PREFIX = "user_tokens"

    # Default TTL (time to live) in seconds
    DEFAULT_TTL = 3600  # 1 hour
    SHORT_TTL = 300  # 5 minutes
    LONG_TTL = 86400  # 24 hours

    @classmethod
    def _make_key(cls, prefix: str, identifier: str) -> str:
        """Create a cache key with prefix"""
        return f"{prefix}:{identifier}"

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            return cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    @classmethod
    def set(cls, key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            cache.set(key, value, ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    @classmethod
    def delete(cls, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        try:
            cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    @classmethod
    def delete_pattern(cls, pattern: str) -> bool:
        """
        Delete all keys matching pattern

        Args:
            pattern: Key pattern to match

        Returns:
            True if successful, False otherwise
        """
        try:
            cache.delete_pattern(pattern)
            return True
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return False

    # User-specific cache methods

    @classmethod
    def get_user(cls, user_id: str) -> Optional[dict]:
        """Get user data from cache"""
        key = cls._make_key(cls.USER_PREFIX, str(user_id))
        return cls.get(key)

    @classmethod
    def set_user(cls, user_id: str, user_data: dict, ttl: int = DEFAULT_TTL) -> bool:
        """Cache user data"""
        key = cls._make_key(cls.USER_PREFIX, str(user_id))
        return cls.set(key, user_data, ttl)

    @classmethod
    def delete_user(cls, user_id: str) -> bool:
        """Delete user data from cache"""
        key = cls._make_key(cls.USER_PREFIX, str(user_id))
        return cls.delete(key)

    @classmethod
    def get_user_preferences(cls, user_id: str) -> Optional[dict]:
        """Get user notification preferences from cache"""
        key = cls._make_key(cls.PREFERENCES_PREFIX, str(user_id))
        return cls.get(key)

    @classmethod
    def set_user_preferences(cls, user_id: str, preferences: dict, ttl: int = LONG_TTL) -> bool:
        """Cache user notification preferences"""
        key = cls._make_key(cls.PREFERENCES_PREFIX, str(user_id))
        return cls.set(key, preferences, ttl)

    @classmethod
    def delete_user_preferences(cls, user_id: str) -> bool:
        """Delete user preferences from cache"""
        key = cls._make_key(cls.PREFERENCES_PREFIX, str(user_id))
        return cls.delete(key)

    @classmethod
    def get_user_profile(cls, user_id: str) -> Optional[dict]:
        """Get user profile from cache"""
        key = cls._make_key(cls.PROFILE_PREFIX, str(user_id))
        return cls.get(key)

    @classmethod
    def set_user_profile(cls, user_id: str, profile: dict, ttl: int = DEFAULT_TTL) -> bool:
        """Cache user profile"""
        key = cls._make_key(cls.PROFILE_PREFIX, str(user_id))
        return cls.set(key, profile, ttl)

    @classmethod
    def delete_user_profile(cls, user_id: str) -> bool:
        """Delete user profile from cache"""
        key = cls._make_key(cls.PROFILE_PREFIX, str(user_id))
        return cls.delete(key)

    @classmethod
    def invalidate_user_cache(cls, user_id: str) -> bool:
        """
        Invalidate all cache entries for a user

        Args:
            user_id: User ID

        Returns:
            True if successful, False otherwise
        """
        try:
            cls.delete_user(user_id)
            cls.delete_user_profile(user_id)
            cls.delete_user_preferences(user_id)
            return True
        except Exception as e:
            logger.error(f"Error invalidating user cache: {e}")
            return False


class RateLimiter:
    """Rate limiter using Redis"""

    RATE_LIMIT_PREFIX = "rate_limit"

    @classmethod
    def _make_key(cls, identifier: str, action: str) -> str:
        """Create rate limit key"""
        return f"{cls.RATE_LIMIT_PREFIX}:{action}:{identifier}"

    @classmethod
    def is_allowed(cls, identifier: str, action: str, limit: int, period: int) -> bool:
        """
        Check if action is allowed based on rate limit

        Args:
            identifier: User ID or IP address
            action: Action being rate limited
            limit: Maximum number of attempts
            period: Time period in seconds

        Returns:
            True if allowed, False if rate limit exceeded
        """
        key = cls._make_key(identifier, action)

        try:
            current = cache.get(key, 0)

            if current >= limit:
                return False

            if current == 0:
                cache.set(key, 1, period)
            else:
                cache.incr(key)

            return True
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Allow request on error to prevent service disruption
            return True

    @classmethod
    def reset(cls, identifier: str, action: str) -> bool:
        """Reset rate limit counter"""
        key = cls._make_key(identifier, action)
        return cache.delete(key)
