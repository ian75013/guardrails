#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <target_repo_path> [--without-copilot-instructions] [--project-name <name>] [--force]" >&2
  exit 1
fi

TARGET_REPO="$1"
shift || true

WITH_COPILOT_INSTRUCTIONS=1
FORCE=0
PROJECT_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --without-copilot-instructions)
      WITH_COPILOT_INSTRUCTIONS=0
      ;;
    --force)
      FORCE=1
      ;;
    --project-name)
      PROJECT_NAME="${2:-}"
      if [[ -z "${PROJECT_NAME}" ]]; then
        echo "--project-name requires a value" >&2
        exit 1
      fi
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
  shift
 done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_NAME="$(basename "${TARGET_REPO}")"

if [[ -z "${PROJECT_NAME}" ]]; then
  PROJECT_NAME="${REPO_NAME}"
fi

if [[ ! -d "${TARGET_REPO}" ]]; then
  echo "Target path does not exist: ${TARGET_REPO}" >&2
  exit 1
fi

if [[ ! -d "${TARGET_REPO}/.git" ]]; then
  echo "Target is not a git repository: ${TARGET_REPO}" >&2
  exit 1
fi

mkdir -p "${TARGET_REPO}/.guardrails/bin" "${TARGET_REPO}/.guardrails/rules" "${TARGET_REPO}/.github/workflows"

copy_file() {
  local src="$1"
  local dst="$2"

  if [[ -f "${dst}" && "${FORCE}" -ne 1 ]]; then
    echo "Skip existing file (use --force to overwrite): ${dst}"
    return 0
  fi

  cp "${src}" "${dst}"
  echo "Installed: ${dst}"
}

render_template() {
  local src="$1"
  local dst="$2"

  if [[ -f "${dst}" && "${FORCE}" -ne 1 ]]; then
    echo "Skip existing file (use --force to overwrite): ${dst}"
    return 0
  fi

  sed \
    -e "s|{{PROJECT_NAME}}|${PROJECT_NAME}|g" \
    -e "s|{{REPO_NAME}}|${REPO_NAME}|g" \
    "${src}" > "${dst}"
  echo "Installed: ${dst}"
}

copy_file "${KIT_ROOT}/.guardrails/config.env" "${TARGET_REPO}/.guardrails/config.env"
copy_file "${KIT_ROOT}/.guardrails/bin/validate_guardrails.sh" "${TARGET_REPO}/.guardrails/bin/validate_guardrails.sh"
chmod +x "${TARGET_REPO}/.guardrails/bin/validate_guardrails.sh"

for rule in "${KIT_ROOT}"/.guardrails/rules/*.md; do
  copy_file "${rule}" "${TARGET_REPO}/.guardrails/rules/$(basename "${rule}")"
done

copy_file "${KIT_ROOT}/.github/workflows/guardrails.yml" "${TARGET_REPO}/.github/workflows/guardrails.yml"

if [[ "${WITH_COPILOT_INSTRUCTIONS}" -eq 1 ]]; then
  render_template "${KIT_ROOT}/templates/copilot-instructions.template.md" "${TARGET_REPO}/.github/copilot-instructions.md"
fi

# Install Claude Code support (default)
render_template "${KIT_ROOT}/templates/CLAUDE.template.md" "${TARGET_REPO}/CLAUDE.md"

# Install Gemini CLI + Gemini Assistant support (default)
render_template "${KIT_ROOT}/templates/GEMINI.template.md" "${TARGET_REPO}/GEMINI.md"

# Install Antigravity IDE support (default)
mkdir -p "${TARGET_REPO}/.antigravity"
render_template "${KIT_ROOT}/templates/workspace.template.yaml" "${TARGET_REPO}/.antigravity/workspace.yaml"

echo "Guardrails Kit installation completed for: ${TARGET_REPO}"
echo "✓ Multi-AI support enabled by default:"
echo "  • .github/copilot-instructions.md (GitHub Copilot)"
echo "  • CLAUDE.md (Claude Code)"
echo "  • GEMINI.md (Gemini CLI + Gemini Assistant)"
echo "  • .antigravity/workspace.yaml (Antigravity IDE)"
