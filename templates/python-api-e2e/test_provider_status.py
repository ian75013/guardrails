"""
test_provider_status.py — stream loop / provider status transition tests.

Tests that the loop orchestration (store ticket, set status, clear on 401)
is correct without making network calls.

Adapt to your service as needed.

Run:
    cd apps/<service>/server
    python -m pytest tests/test_provider_status.py -v
"""
import asyncio
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

AUTH_URL = "https://demo.tradovateapi.com/v1/auth/accesstokenrequest"


def _http_error(status: int) -> httpx.HTTPStatusError:
    return httpx.HTTPStatusError(
        f"HTTP {status}",
        request=httpx.Request("POST", AUTH_URL),
        response=httpx.Response(status),
    )


class _HubFixture(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self._redis = MagicMock()
        self._redis.get = AsyncMock(return_value=None)
        self._redis.set = AsyncMock()
        self._redis.aclose = AsyncMock()

        self._redis_patcher = patch(
            "app.market_hub.aioredis.from_url", return_value=self._redis
        )
        self._redis_patcher.start()

        import app.market_hub  # noqa: PLC0415, F401
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
        self.hub.snapshots["MNQ"] = {
            "symbol": "MNQ", "display_symbol": "MNQ", "provider": "tradovate",
            "status": "awaiting_quotes", "retry_at": None,
            "bars": [], "indicators": {}, "features": [], "headlines": [], "decision": {},
        }

    async def asyncTearDown(self):
        self._redis_patcher.stop()
        self._settings.tradovate_username = ""
        self._settings.tradovate_password = ""
        self._settings.tradovate_cid = ""
        self._settings.tradovate_sec = ""
        await self.hub.client.aclose()

    async def _run_loop(self, side_effects: list) -> None:
        """
        Drive _tradovate_stream_loop through the given sequence of
        _ensure_tradovate_access_token outcomes, then stop via CancelledError.
        asyncio.sleep is patched to be instant.
        """
        effects = list(side_effects) + [asyncio.CancelledError()]
        self.hub._ensure_tradovate_access_token = AsyncMock(side_effect=effects)
        with patch("asyncio.sleep", new=AsyncMock()):
            task = asyncio.create_task(self.hub._tradovate_stream_loop())
            done, pending = await asyncio.wait({task}, timeout=2.0)
            if pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


class TestRateLimitStatus(_HubFixture):

    async def test_rate_limit_stores_ticket(self):
        from app.market_hub import _TradovateRateLimitError
        reset_at = datetime.now(timezone.utc) + timedelta(seconds=120)
        await self._run_loop([
            _TradovateRateLimitError(120, reset_at=reset_at, p_ticket="loop_ticket"),
        ])
        self.assertEqual(self.hub._pending_p_ticket, "loop_ticket")

    async def test_rate_limit_sets_status(self):
        from app.market_hub import _TradovateRateLimitError
        reset_at = datetime.now(timezone.utc) + timedelta(seconds=120)
        await self._run_loop([
            _TradovateRateLimitError(120, reset_at=reset_at, p_ticket="ticket"),
        ])
        self.assertEqual(self.hub.snapshots["MNQ"]["status"], "rate_limited")

    async def test_retry_at_includes_30s_buffer(self):
        """retry_at = reset_at + 30s — prevents firing auth too early."""
        from app.market_hub import _TradovateRateLimitError
        reset_at = datetime.now(timezone.utc) + timedelta(seconds=120)
        await self._run_loop([
            _TradovateRateLimitError(120, reset_at=reset_at, p_ticket="ticket"),
        ])
        retry_at_str = self.hub.snapshots["MNQ"].get("retry_at")
        self.assertIsNotNone(retry_at_str)
        retry_at_dt = datetime.fromisoformat(retry_at_str)
        diff = abs((retry_at_dt - (reset_at + timedelta(seconds=30))).total_seconds())
        self.assertLess(diff, 2.0)


class TestStatus401(_HubFixture):

    async def test_401_with_ticket_clears_pending_ticket(self):
        self.hub._pending_p_ticket = "stale_ticket"
        await self._run_loop([_http_error(401)])
        self.assertEqual(self.hub._pending_p_ticket, "")

    async def test_401_sets_reconnecting(self):
        self.hub._pending_p_ticket = "stale_ticket"
        await self._run_loop([_http_error(401)])
        self.assertEqual(self.hub.snapshots["MNQ"]["status"], "reconnecting")


if __name__ == "__main__":
    unittest.main()
