"""
test_auth_flow.py — boilerplate for external-service auth tests.

Adapt to your service:
  - Replace AUTH_URL with your real auth endpoint
  - Replace _SUCCESS_RESP / _RATE_LIMIT_RESP bodies with real shapes
  - Replace MarketHub / _ensure_tradovate_access_token with your class/method
  - Replace aioredis.from_url patch target with your module's Redis import

WHAT IS TESTED
--------------
1. Nominal auth returns the access token
2. Token is cached in Redis after a successful auth
3. Redis cache hit skips HTTP entirely
4. In-memory cache skips both Redis and HTTP
5. Rate-limit response (service-specific shape) raises the right error
6. Rate-limit error carries the correct wait time and ticket/token
7. Retry with pending ticket posts ONLY the ticket (no credentials)
8. Credentials are absent from retry body
9. Successful retry clears the pending ticket

Run:
    cd apps/<service>/server
    python -m pytest tests/test_auth_flow.py -v
"""
import asyncio
import json
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

# ---------------------------------------------------------------------------
# Adapt these imports / constants to your service
# ---------------------------------------------------------------------------
# from app.market_hub import MarketHub, _TradovateRateLimitError, settings as hub_settings

AUTH_URL = "https://demo.tradovateapi.com/v1/auth/accesstokenrequest"

_SUCCESS_TOKEN = "fake_access_token_abc"
_SUCCESS_RESP = {
    "accessToken": _SUCCESS_TOKEN,
    "expirationTime": "2099-01-01T00:00:00Z",
}
_RATE_LIMIT_RESP = {
    "p-ticket": "p_ticket_xyz",
    "p-time": 120,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ok_resp(body: dict) -> MagicMock:
    """Fake successful httpx response."""
    m = MagicMock()
    m.json.return_value = body
    m.raise_for_status.return_value = None
    return m


def _http_error(status: int) -> httpx.HTTPStatusError:
    return httpx.HTTPStatusError(
        f"HTTP {status}",
        request=httpx.Request("POST", AUTH_URL),
        response=httpx.Response(status),
    )


# ---------------------------------------------------------------------------
# Fixture base
# ---------------------------------------------------------------------------

class _HubFixture(unittest.IsolatedAsyncioTestCase):
    REDIS_PATCH_TARGET = "app.market_hub.aioredis.from_url"

    async def asyncSetUp(self):
        self._redis = MagicMock()
        self._redis.get = AsyncMock(return_value=None)
        self._redis.set = AsyncMock()
        self._redis.aclose = AsyncMock()

        self._redis_patcher = patch(self.REDIS_PATCH_TARGET, return_value=self._redis)
        self._redis_patcher.start()

        # Import after patching so the constructor uses the mock
        import app.market_hub as _m  # noqa: PLC0415
        from app.market_hub import MarketHub, settings as hub_s  # noqa: PLC0415

        self._settings = hub_s
        hub_s.tradovate_username = "testuser"
        hub_s.tradovate_password = "testpass"
        hub_s.tradovate_cid = "999"
        hub_s.tradovate_sec = "testsec"
        hub_s.tradovate_mode = "demo"

        self.hub = MarketHub()
        self.hub._redis_client = self._redis
        self.hub.instrument_map = {"MNQ": "tradovate"}

    async def asyncTearDown(self):
        self._redis_patcher.stop()
        self._settings.tradovate_username = ""
        self._settings.tradovate_password = ""
        self._settings.tradovate_cid = ""
        self._settings.tradovate_sec = ""
        await self.hub.client.aclose()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestNominalAuth(_HubFixture):

    async def test_returns_access_token(self):
        self.hub.client.post = AsyncMock(return_value=_ok_resp(_SUCCESS_RESP))
        token = await self.hub._ensure_tradovate_access_token()
        self.assertEqual(token, _SUCCESS_TOKEN)

    async def test_clears_pending_ticket_on_success(self):
        self.hub._pending_p_ticket = "stale"
        self.hub.client.post = AsyncMock(return_value=_ok_resp(_SUCCESS_RESP))
        await self.hub._ensure_tradovate_access_token()
        self.assertEqual(self.hub._pending_p_ticket, "")

    async def test_writes_token_to_redis(self):
        self.hub.client.post = AsyncMock(return_value=_ok_resp(_SUCCESS_RESP))
        await self.hub._ensure_tradovate_access_token()
        self._redis.set.assert_awaited_once()

    async def test_redis_cache_hit_skips_http(self):
        future_exp = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        self._redis.get = AsyncMock(
            return_value=json.dumps({"token": "cached_tok", "expires_at": future_exp})
        )
        self.hub.client.post = AsyncMock()
        token = await self.hub._ensure_tradovate_access_token()
        self.assertEqual(token, "cached_tok")
        self.hub.client.post.assert_not_awaited()

    async def test_in_memory_cache_skips_redis_and_http(self):
        self.hub._tradovate_access_token = "mem_tok"
        self.hub._tradovate_access_expiration = datetime.now(timezone.utc) + timedelta(hours=1)
        self.hub.client.post = AsyncMock()
        token = await self.hub._ensure_tradovate_access_token()
        self.assertEqual(token, "mem_tok")
        self._redis.get.assert_not_awaited()
        self.hub.client.post.assert_not_awaited()


class TestRateLimit(_HubFixture):

    async def test_rate_limit_raises_error(self):
        from app.market_hub import _TradovateRateLimitError
        self.hub.client.post = AsyncMock(return_value=_ok_resp(_RATE_LIMIT_RESP))
        with self.assertRaises(_TradovateRateLimitError):
            await self.hub._ensure_tradovate_access_token()

    async def test_error_carries_ticket_and_wait_seconds(self):
        from app.market_hub import _TradovateRateLimitError
        self.hub.client.post = AsyncMock(return_value=_ok_resp(_RATE_LIMIT_RESP))
        with self.assertRaises(_TradovateRateLimitError) as ctx:
            await self.hub._ensure_tradovate_access_token()
        self.assertEqual(ctx.exception.p_ticket, "p_ticket_xyz")
        self.assertEqual(ctx.exception.wait_seconds, 120)


class TestTicketRetry(_HubFixture):
    """
    Core regression: retry must post ONLY the ticket.
    Tradovate rejects the request if credentials are included alongside it.
    """

    async def test_retry_posts_ticket_only(self):
        self.hub._pending_p_ticket = "ticket_abc"
        captured: dict = {}

        async def _cap(url, json=None, timeout=None):  # noqa: ARG001
            captured.update(json or {})
            return _ok_resp(_SUCCESS_RESP)

        self.hub.client.post = _cap
        await self.hub._ensure_tradovate_access_token()
        self.assertEqual(captured, {"p-ticket": "ticket_abc"})

    async def test_no_credentials_in_retry_body(self):
        self.hub._pending_p_ticket = "ticket_abc"
        captured: dict = {}

        async def _cap(url, json=None, timeout=None):  # noqa: ARG001
            captured.update(json or {})
            return _ok_resp(_SUCCESS_RESP)

        self.hub.client.post = _cap
        await self.hub._ensure_tradovate_access_token()
        for key in ("name", "password", "cid", "sec"):
            self.assertNotIn(key, captured)

    async def test_success_clears_pending_ticket(self):
        self.hub._pending_p_ticket = "ticket_abc"
        self.hub.client.post = AsyncMock(return_value=_ok_resp(_SUCCESS_RESP))
        await self.hub._ensure_tradovate_access_token()
        self.assertEqual(self.hub._pending_p_ticket, "")


if __name__ == "__main__":
    unittest.main()
