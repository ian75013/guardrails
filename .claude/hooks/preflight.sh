#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "[preflight] Repo: $REPO_ROOT"

required_files=(
  "SKILLS.md"
  "ROADMAP.md"
  "CLAUDE.md"
  ".github/copilot-instructions.md"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "Fichier requis manquant: $file" >&2
    exit 1
  fi
done

if command -v pwsh >/dev/null 2>&1; then
  echo "[preflight] PowerShell détecté"
else
  echo "[preflight] PowerShell non détecté." >&2
fi

echo "[preflight] OK"
