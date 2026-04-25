#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
WITH_CI=0
PROJECT_NAME=""
TARGET_REPO=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-ci)
      WITH_CI=1
      shift
      ;;
    --project-name)
      PROJECT_NAME="${2:-}"
      if [[ -z "${PROJECT_NAME}" ]]; then
        echo "[guardrails] --project-name requires a value"
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--with-ci] [--project-name <name>] <target_repo_path>"
      exit 0
      ;;
    *)
      TARGET_REPO="$1"
      shift
      ;;
  esac
done

TARGET_REPO="${TARGET_REPO:-$PWD}"

if [[ ! -d "${TARGET_REPO}" ]]; then
  echo "[guardrails] Target repository path does not exist: ${TARGET_REPO}"
  exit 1
fi

if [[ ! -d "${TARGET_REPO}/.git" ]]; then
  echo "[guardrails] Target is not a git repository: ${TARGET_REPO}"
  exit 1
fi

mkdir -p "${TARGET_REPO}/.guardrails/bin"
mkdir -p "${TARGET_REPO}/.github"
mkdir -p "${TARGET_REPO}/.github/agents"

REPO_NAME="$(basename "${TARGET_REPO}")"
if [[ -z "${PROJECT_NAME}" ]]; then
  PROJECT_NAME="${REPO_NAME}"
fi

render_template() {
  local src="$1"
  local dest="$2"
  sed \
    -e "s|{{PROJECT_NAME}}|${PROJECT_NAME}|g" \
    -e "s|{{REPO_NAME}}|${REPO_NAME}|g" \
    "${src}" > "${dest}"
}

if [[ ! -f "${TARGET_REPO}/.guardrails/config.env" ]]; then
  cp "${KIT_ROOT}/templates/guardrails.config.template.env" "${TARGET_REPO}/.guardrails/config.env"
  echo "[guardrails] Created .guardrails/config.env"
else
  echo "[guardrails] Keeping existing .guardrails/config.env"
fi

cp "${KIT_ROOT}/automation/scripts/validate_guardrails.sh" "${TARGET_REPO}/.guardrails/bin/validate_guardrails.sh"
chmod +x "${TARGET_REPO}/.guardrails/bin/validate_guardrails.sh"
echo "[guardrails] Installed .guardrails/bin/validate_guardrails.sh"

if [[ ! -f "${TARGET_REPO}/SKILLS.md" ]]; then
  render_template "${KIT_ROOT}/templates/SKILLS.template.md" "${TARGET_REPO}/SKILLS.md"
  echo "[guardrails] Created SKILLS.md"
else
  echo "[guardrails] Keeping existing SKILLS.md"
fi

if [[ ! -f "${TARGET_REPO}/ROADMAP.md" ]]; then
  render_template "${KIT_ROOT}/templates/ROADMAP.template.md" "${TARGET_REPO}/ROADMAP.md"
  echo "[guardrails] Created ROADMAP.md"
else
  echo "[guardrails] Keeping existing ROADMAP.md"
fi

if [[ ! -f "${TARGET_REPO}/.github/copilot-instructions.md" ]]; then
  render_template "${KIT_ROOT}/templates/copilot-instructions.template.md" "${TARGET_REPO}/.github/copilot-instructions.md"
  echo "[guardrails] Created .github/copilot-instructions.md"
else
  echo "[guardrails] Keeping existing .github/copilot-instructions.md"
fi

AGENT_FILE="${TARGET_REPO}/.github/agents/${REPO_NAME}-agent.agent.md"
if [[ ! -f "${AGENT_FILE}" ]]; then
  render_template "${KIT_ROOT}/templates/agents/project-agent.template.agent.md" "${AGENT_FILE}"
  echo "[guardrails] Created .github/agents/${REPO_NAME}-agent.agent.md"
else
  echo "[guardrails] Keeping existing .github/agents/${REPO_NAME}-agent.agent.md"
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

if [[ "${WITH_CI}" == "1" ]]; then
  mkdir -p "${TARGET_REPO}/.github/workflows"
  if [[ ! -f "${TARGET_REPO}/.github/workflows/guardrails.yml" ]]; then
    cp "${KIT_ROOT}/templates/ci/github-actions-guardrails.yml" "${TARGET_REPO}/.github/workflows/guardrails.yml"
    echo "[guardrails] Created .github/workflows/guardrails.yml"
  else
    echo "[guardrails] Keeping existing .github/workflows/guardrails.yml"
  fi
else
  echo "[guardrails] CI workflow skipped (default). Use --with-ci to enable."
fi

echo "[guardrails] Automatic guardrails are now active for ${TARGET_REPO}"
