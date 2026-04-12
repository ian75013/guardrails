#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TARGET_REPO="${1:-$PWD}"

if [[ ! -d "${TARGET_REPO}" ]]; then
  echo "[guardrails] Target repository path does not exist: ${TARGET_REPO}"
  exit 1
fi

if [[ ! -d "${TARGET_REPO}/.git" ]]; then
  echo "[guardrails] Target is not a git repository: ${TARGET_REPO}"
  exit 1
fi

mkdir -p "${TARGET_REPO}/.guardrails/bin"
mkdir -p "${TARGET_REPO}/.github/workflows"

if [[ ! -f "${TARGET_REPO}/.guardrails/config.env" ]]; then
  cp "${KIT_ROOT}/templates/guardrails.config.template.env" "${TARGET_REPO}/.guardrails/config.env"
  echo "[guardrails] Created .guardrails/config.env"
else
  echo "[guardrails] Keeping existing .guardrails/config.env"
fi

cp "${KIT_ROOT}/automation/scripts/validate_guardrails.sh" "${TARGET_REPO}/.guardrails/bin/validate_guardrails.sh"
chmod +x "${TARGET_REPO}/.guardrails/bin/validate_guardrails.sh"
echo "[guardrails] Installed .guardrails/bin/validate_guardrails.sh"

if [[ ! -f "${TARGET_REPO}/.github/workflows/guardrails.yml" ]]; then
  cp "${KIT_ROOT}/templates/ci/github-actions-guardrails.yml" "${TARGET_REPO}/.github/workflows/guardrails.yml"
  echo "[guardrails] Created .github/workflows/guardrails.yml"
else
  echo "[guardrails] Keeping existing .github/workflows/guardrails.yml"
fi

PRE_COMMIT_HOOK="${TARGET_REPO}/.git/hooks/pre-commit"
HOOK_MARKER="# guardrails-pre-commit-hook"

if [[ -f "${PRE_COMMIT_HOOK}" ]] && grep -q "${HOOK_MARKER}" "${PRE_COMMIT_HOOK}"; then
  echo "[guardrails] Pre-commit hook already configured."
else
  {
    echo "${HOOK_MARKER}"
    echo "if [[ -x .guardrails/bin/validate_guardrails.sh ]]; then"
    echo "  ./.guardrails/bin/validate_guardrails.sh"
    echo "fi"
  } >> "${PRE_COMMIT_HOOK}"
  chmod +x "${PRE_COMMIT_HOOK}"
  echo "[guardrails] Installed pre-commit hook."
fi

echo "[guardrails] Automatic guardrails are now active for ${TARGET_REPO}"
