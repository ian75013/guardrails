#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER="${SCRIPT_DIR}/install_guardrails.sh"

if [[ ! -x "${INSTALLER}" ]]; then
  chmod +x "${INSTALLER}"
fi

if [[ "$#" -eq 0 ]]; then
  echo "Usage: $0 <repo_path_1> [repo_path_2 ...]"
  exit 1
fi

for repo in "$@"; do
  echo "[guardrails] Applying to ${repo}"
  "${INSTALLER}" "${repo}"
done

echo "[guardrails] Completed for all repositories."
