#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "[post-task] Validation guardrails"

if [[ -f "automation/scripts/validate_guardrails.sh" ]]; then
  bash automation/scripts/validate_guardrails.sh
else
  echo "[post-task] Script validate_guardrails.sh absent." >&2
fi
