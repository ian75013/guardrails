# Python API E2E Test Boilerplate

Template for backend E2E tests that cover an external-HTTP service
(e.g. Tradovate, Binance, Alpaca) **without hitting the real API**.

Stack: `pytest` + `pytest-asyncio` + `respx` (httpx transport mock)
Async style: `unittest.IsolatedAsyncioTestCase` (stdlib, no extra config needed)

## Why this pattern

Every bug that was debugged by rebuilding and redeploying to remote was a
failure to have the right local test first.  See:

- `guardrails/01-core-principles.md` § "No remote redeploy loop to debug"
- `guardrails/05-release-change-management.md` § Anti-Pattern: Deploy Loop

**Rule**: write a failing test → fix the code → run tests → deploy once.

## Files

| File | Purpose |
|------|---------|
| `conftest.py` | sys.path fix + shared async fixtures (Redis mock, settings, hub) |
| `test_auth_flow.py` | Auth happy path + rate-limit + retry — adapt names to your service |
| `test_provider_status.py` | Provider status transitions (stream loop level) |

## Install test dependencies

```bash
cd apps/<service>/server
pip install pytest pytest-asyncio
# (respx is optional — AsyncMock on hub.client.post is simpler for unit tests)
```

## Run

```bash
cd apps/<service>/server
python -m pytest tests/ -v
```

## Key patterns

### Mock Redis (no real connection)

```python
from unittest.mock import AsyncMock, MagicMock, patch

redis = MagicMock()
redis.get  = AsyncMock(return_value=None)   # cache miss
redis.set  = AsyncMock()
redis.aclose = AsyncMock()

with patch("app.<module>.aioredis.from_url", return_value=redis):
    hub = MyHub()
    hub._redis_client = redis
```

### Mock httpx POST (no real HTTP)

```python
from unittest.mock import AsyncMock, MagicMock

def _ok_resp(body: dict) -> MagicMock:
    m = MagicMock()
    m.json.return_value = body
    m.raise_for_status.return_value = None
    return m

hub.client.post = AsyncMock(return_value=_ok_resp({"accessToken": "fake"}))
```

### Capture POST body

```python
captured: dict = {}

async def _capture(url, json=None, timeout=None):
    captured.update(json or {})
    return _ok_resp({"accessToken": "fake"})

hub.client.post = _capture
await hub._ensure_access_token()
assert captured == {"expected": "body"}
```

### Drive a stream loop for one iteration

```python
async def _run_loop(self, side_effects: list) -> None:
    effects = list(side_effects) + [asyncio.CancelledError()]
    self.hub._ensure_access_token = AsyncMock(side_effect=effects)
    with patch("asyncio.sleep", new=AsyncMock()):
        task = asyncio.create_task(self.hub._stream_loop())
        done, pending = await asyncio.wait({task}, timeout=2.0)
        if pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
```

### Assert provider status

```python
snap = hub.snapshots["SYMBOL"]
assert snap["status"] == "rate_limited"
assert snap["retry_at"] is not None
```
