"""
conftest.py — shared fixtures for Python API E2E tests.

Copy this into apps/<service>/server/conftest.py and adapt:
  - _REPO_ROOT: adjust .parents[N] to point to the repository root
  - Any extra sys.path entries needed for local packages
"""
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path fix: mirror the Dockerfile PYTHONPATH so local packages are importable.
#
# Example: if research/ lives at repo-root and the Dockerfile does:
#   COPY research ./research
#   ENV  PYTHONPATH=/app
# then we need repo-root in sys.path so `from research.x import y` resolves.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[3]   # adjust depth as needed
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
