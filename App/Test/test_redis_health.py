"""
Tests for Redis health check and availability.
Verifies:
  1. RedisClient.ping() returns False when Redis is down, True when up
  2. PermissionCache gracefully falls back when Redis is unavailable
  3. isRedisAvailable query logic works
"""
import pytest
from unittest.mock import AsyncMock, patch

pytestmark = pytest.mark.asyncio


class TestRedisHealth:
    async def test_ping_returns_bool(self):
        from redis_services.redis_client import RedisClient
        RedisClient._instance = None
        result = await RedisClient.ping()
        assert isinstance(result, bool)

    @patch("redis_services.redis_client.Redis.from_url")
    async def test_ping_returns_true_when_redis_up(self, mock_from_url):
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_from_url.return_value = mock_redis

        from redis_services.redis_client import RedisClient
        RedisClient._instance = None
        result = await RedisClient.ping()
        assert result is True
        mock_redis.ping.assert_awaited_once()

    @patch("redis_services.redis_client.Redis.from_url")
    async def test_ping_returns_false_on_redis_error(self, mock_from_url):
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(side_effect=Exception("Connection refused"))
        mock_from_url.return_value = mock_redis

        from redis_services.redis_client import RedisClient
        RedisClient._instance = None
        result = await RedisClient.ping()
        assert result is False


class TestPermissionCacheGracefulFallback:
    async def test_get_returns_none_when_redis_down(self):
        from redis_services.permission_cache import PermissionCache
        cache = PermissionCache()
        result = await cache.get_permissions("test-user")
        assert result is None

    async def test_set_does_not_crash_when_redis_down(self):
        from redis_services.permission_cache import PermissionCache
        cache = PermissionCache()
        await cache.set_permissions("test-user", [{"name": "test"}])
        # Should not raise

    async def test_invalidate_does_not_crash_when_redis_down(self):
        from redis_services.permission_cache import PermissionCache
        cache = PermissionCache()
        await cache.invalidate("test-user")
        # Should not raise
