"""
Tests for the permission caching system.
Verifies:
  1. JWT service produces valid tokens with timestamps
  2. PermissionCache stores/retrieves from Redis with TTL
  3. First context call: cache miss → DB query → cache set
  4. Second context call: cache hit → no DB query
  5. No token → empty context, no DB/cache activity
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone



from auth.domain.services.jwt_service import JwtService
from redis_services.permission_cache import PermissionCache


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_permissions():
    return [
        {"code": "users.read", "name": "Read Users", "module": "users", "description": None},
        {"code": "users.write", "name": "Write Users", "module": "users", "description": None},
        {"code": "reports.view", "name": "View Reports", "module": "reports", "description": "Access report module"},
    ]


@pytest.fixture
def user_payload():
    return {
        "sub": "550e8400-e29b-41d4-a716-446655440000",
        "roles": ["Admin", "Manager"],
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc),
    }


# ---------------------------------------------------------------------------
# JWT Service Tests
# ---------------------------------------------------------------------------

class TestJwtService:
    def test_create_token_pair_returns_tokens_and_dates(self):
        svc = JwtService(secret_key="test-secret-key-for-testing-purposes-only")
        result = svc.create_token_pair("user-1", ["Admin"])

        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_created_at" in result
        assert "access_token_expires_at" in result
        assert "refresh_token_expires_at" in result

        # Verify the JWT is valid
        payload = svc.decode_token(result["access_token"])
        assert payload["sub"] == "user-1"
        assert payload["roles"] == ["Admin"]
        assert payload["type"] == "access"

        # Verify dates are ISO format
        created = datetime.fromisoformat(result["token_created_at"])
        access_exp = datetime.fromisoformat(result["access_token_expires_at"])
        refresh_exp = datetime.fromisoformat(result["refresh_token_expires_at"])
        assert created < access_exp
        assert access_exp < refresh_exp

    def test_refresh_token_type(self):
        svc = JwtService(secret_key="test-secret-key-for-testing-purposes-only")
        result = svc.create_token_pair("user-1", [])
        payload = svc.decode_token(result["refresh_token"])
        assert payload["type"] == "refresh"
        assert payload["sub"] == "user-1"

    def test_decode_invalid_token_returns_none(self):
        svc = JwtService(secret_key="test-secret-key-for-testing-purposes-only")
        assert svc.decode_token("invalid-token") is None
        assert svc.decode_token("") is None


# ---------------------------------------------------------------------------
# PermissionCache Unit Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestPermissionCache:
    async def test_get_returns_none_when_key_missing(self):
        redis = AsyncMock(spec_set=["get", "setex", "delete"])
        redis.get = AsyncMock(return_value=None)
        cache = PermissionCache(redis=redis)
        result = await cache.get_permissions("u1")
        assert result is None
        redis.get.assert_awaited_once_with("user:u1:permissions")

    async def test_get_returns_parsed_json(self, sample_permissions):
        redis = AsyncMock(spec_set=["get", "setex", "delete"])
        redis.get = AsyncMock(return_value=json.dumps(sample_permissions))
        cache = PermissionCache(redis=redis)
        result = await cache.get_permissions("u1")
        assert result == sample_permissions

    async def test_set_stores_with_ttl(self, sample_permissions):
        redis = AsyncMock(spec_set=["get", "setex", "delete"])
        redis.setex = AsyncMock()
        cache = PermissionCache(redis=redis, ttl_minutes=15)
        await cache.set_permissions("u1", sample_permissions)
        redis.setex.assert_awaited_once_with(
            "user:u1:permissions",
            900,  # 15 * 60
            json.dumps(sample_permissions, default=str),
        )

    async def test_invalidate_deletes_key(self):
        redis = AsyncMock(spec_set=["get", "setex", "delete"])
        redis.delete = AsyncMock()
        cache = PermissionCache(redis=redis)
        await cache.invalidate("u1")
        redis.delete.assert_awaited_once_with("user:u1:permissions")


# ---------------------------------------------------------------------------
# Caching Behaviour Integration Tests  (first call → DB, second → Redis)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestPermissionCachingFlow:
    """Verifica que la primera llamada consulte DB y cachee, y la segunda no."""

    @patch("auth.domain.services.jwt_service.JwtService.decode_token")
    @patch("redis_services.permission_cache.PermissionCache")
    @patch("person.adapters.driven.postgres_person_repository.PostgresPersonRepository")
    @patch("db.config.AsyncSessionLocal")
    async def test_first_request_fetches_from_db_and_caches(
        self,
        mock_session_local,
        mock_repo_class,
        mock_cache_class,
        mock_decode,
        user_payload,
        sample_permissions,
    ):
        """Cache miss → query DB → store in Redis."""
        mock_decode.return_value = user_payload

        mock_cache = AsyncMock(spec=["get_permissions", "set_permissions"])
        mock_cache.get_permissions = AsyncMock(return_value=None)
        mock_cache.set_permissions = AsyncMock()
        mock_cache_class.return_value = mock_cache

        mock_repo = AsyncMock()
        mock_repo.find_permissions_by_person_id = AsyncMock(return_value=sample_permissions)
        mock_repo_class.return_value = mock_repo

        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        from graphql.context import get_context

        request = MagicMock()
        request.headers = {"Authorization": "Bearer ey-test-token"}
        response = MagicMock()

        ctx = await get_context(request, response)

        mock_repo.find_permissions_by_person_id.assert_awaited_once_with(user_payload["sub"])
        mock_cache.set_permissions.assert_awaited_once_with(user_payload["sub"], sample_permissions)
        assert ctx["user_id"] == user_payload["sub"]
        assert ctx["roles"] == user_payload["roles"]
        assert ctx["permissions"] == sample_permissions

    @patch("auth.domain.services.jwt_service.JwtService.decode_token")
    @patch("redis_services.permission_cache.PermissionCache")
    @patch("person.adapters.driven.postgres_person_repository.PostgresPersonRepository")
    @patch("db.config.AsyncSessionLocal")
    async def test_second_request_uses_cache_does_not_query_db(
        self,
        mock_session_local,
        mock_repo_class,
        mock_cache_class,
        mock_decode,
        user_payload,
        sample_permissions,
    ):
        """Cache hit → NO DB query, permissions from Redis."""
        mock_decode.return_value = user_payload

        mock_cache = AsyncMock(spec=["get_permissions", "set_permissions"])
        mock_cache.get_permissions = AsyncMock(return_value=sample_permissions)
        mock_cache.set_permissions = AsyncMock()
        mock_cache_class.return_value = mock_cache

        mock_repo = AsyncMock()
        mock_repo.find_permissions_by_person_id = AsyncMock()
        mock_repo_class.return_value = mock_repo

        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        from graphql.context import get_context

        request = MagicMock()
        request.headers = {"Authorization": "Bearer ey-test-token"}
        response = MagicMock()

        ctx = await get_context(request, response)

        mock_repo.find_permissions_by_person_id.assert_not_awaited()
        mock_cache.set_permissions.assert_not_awaited()
        assert ctx["permissions"] == sample_permissions

    @patch("auth.domain.services.jwt_service.JwtService.decode_token")
    @patch("redis_services.permission_cache.PermissionCache")
    @patch("person.adapters.driven.postgres_person_repository.PostgresPersonRepository")
    @patch("db.config.AsyncSessionLocal")
    async def test_no_token_returns_empty_context(
        self, mock_session_local, mock_repo_class, mock_cache_class, mock_decode,
    ):
        """Sin Authorization header → contexto vacío, sin DB ni cache."""
        from graphql.context import get_context

        request = MagicMock()
        request.headers = {}  # no auth header
        response = MagicMock()

        ctx = await get_context(request, response)

        assert ctx["user_id"] is None
        assert ctx["roles"] == []
        assert ctx["permissions"] == []

        mock_decode.assert_not_called()
        mock_cache_class.assert_not_called()
        mock_repo_class.assert_not_called()

    @patch("auth.domain.services.jwt_service.JwtService.decode_token")
    @patch("redis_services.permission_cache.PermissionCache")
    @patch("person.adapters.driven.postgres_person_repository.PostgresPersonRepository")
    @patch("db.config.AsyncSessionLocal")
    async def test_invalid_token_returns_empty_context(
        self, mock_session_local, mock_repo_class, mock_cache_class, mock_decode,
    ):
        """Token inválido → contexto vacío."""
        mock_decode.return_value = None  # invalid token

        from graphql.context import get_context

        request = MagicMock()
        request.headers = {"Authorization": "Bearer bad-token"}
        response = MagicMock()

        ctx = await get_context(request, response)

        assert ctx["user_id"] is None
        assert ctx["roles"] == []
        assert ctx["permissions"] == []
        mock_cache_class.assert_not_called()
        mock_repo_class.assert_not_called()
