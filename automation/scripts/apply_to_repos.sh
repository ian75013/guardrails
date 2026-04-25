#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER="${SCRIPT_DIR}/install_guardrails.sh"
WITH_CI=0
PROJECT_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-ci)
      WITH_CI=1
      shift
      ;;
    --project-name)
      PROJECT_NAME="${2:-}"
      if [[ -z "${PROJECT_NAME}" ]]; then
        echo "Usage: $0 [--with-ci] [--project-name <name>] <repo_path_1> [repo_path_2 ...]"
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--with-ci] [--project-name <name>] <repo_path_1> [repo_path_2 ...]"
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

if [[ ! -x "${INSTALLER}" ]]; then
  chmod +x "${INSTALLER}"
fi

if [[ "$#" -eq 0 ]]; then
  echo "Usage: $0 [--with-ci] [--project-name <name>] <repo_path_1> [repo_path_2 ...]"
  exit 1
fi

for repo in "$@"; do
  echo "[guardrails] Applying to ${repo}"
  if [[ "${WITH_CI}" == "1" ]]; then
    if [[ -n "${PROJECT_NAME}" ]]; then
      "${INSTALLER}" --with-ci --project-name "${PROJECT_NAME}" "${repo}"
    else
      "${INSTALLER}" --with-ci "${repo}"
    fi
  else
    if [[ -n "${PROJECT_NAME}" ]]; then
      "${INSTALLER}" --project-name "${PROJECT_NAME}" "${repo}"
    else
      "${INSTALLER}" "${repo}"
    fi
  fi
done

echo "[guardrails] Completed for all repositories."
