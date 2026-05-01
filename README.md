# Guardrails Kit

Guardrails Kit is a reusable policy + validation bundle for repositories that need enforceable engineering and documentation standards.

## What it installs

- `.guardrails/config.env`: repository-level policy toggles
- `.guardrails/rules/*.md`: policy/rule documents for humans and AI agents
- `.guardrails/bin/validate_guardrails.sh`: commit/CI validator
- `.github/workflows/guardrails.yml`: GitHub Actions workflow to enforce guardrails

## How it works

### 1) Policy source of truth

Rules live in `.guardrails/rules/` and are referenced by repository instructions (for example `.github/copilot-instructions.md`).

### 2) Configurable enforcement

`validate_guardrails.sh` loads `.guardrails/config.env` and enforces:

- required documentation files (`REQUIRED_DOCS`)
- docs update requirement when code files are changed (`REQUIRE_DOC_UPDATE_ON_CODE_CHANGE=1`)
- optional lint/test/build commands (`LINT_CMD`, `TEST_CMD`, `BUILD_CMD`)

### 3) GitHub Actions gate

Workflow `.github/workflows/guardrails.yml` runs on push/PR and executes the validator script.

## Install into a target repository

```bash
cd /home/yann/Documents/Github/guardrails-kit
bash scripts/install_into_repo.sh /absolute/path/to/target-repo
```

Windows PowerShell:

```powershell
cd C:\path\to\guardrails-kit
pwsh -File scripts/install_into_repo.ps1 C:\absolute\path\to\target-repo
```

Optional flags:

```bash
bash scripts/install_into_repo.sh /path/to/repo --without-copilot-instructions
bash scripts/install_into_repo.sh /path/to/repo --force
bash scripts/install_into_repo.sh /path/to/repo --project-name "My Project"
```

PowerShell optional flags:

```powershell
pwsh -File scripts/install_into_repo.ps1 C:\path\to\repo -WithoutCopilotInstructions
pwsh -File scripts/install_into_repo.ps1 C:\path\to\repo -Force
pwsh -File scripts/install_into_repo.ps1 C:\path\to\repo -ProjectName "My Project"
```

## Make it apply to every new Copilot chat (per project)

To enforce guardrails on every new chat in one repository:

1. Install the kit once in that repository (default install now includes Copilot instructions).
2. Commit and push these files in the project:
	- `.github/copilot-instructions.md`
	- `.guardrails/config.env`
	- `.guardrails/rules/*`
3. Open future chats from that same repository/workspace.

Why this works:

- Copilot loads repository instructions from `.github/copilot-instructions.md` at the start of new chats for that project.
- Those instructions point to `.guardrails/rules/*`, so the same policy context is re-applied each time.
- CI enforcement remains active via `.github/workflows/guardrails.yml`.

Recommended hardening:

1. Protect `main`/`master` with required status check: `Guardrails`.
2. Keep `.github/copilot-instructions.md` minimal and stable; put evolving policy details in `.guardrails/rules/*`.
3. Set `TEST_CMD`, `LINT_CMD`, and `BUILD_CMD` in `.guardrails/config.env` for real quality gates.

## Quick local validation in target repo

```bash
cd /path/to/target-repo
# stage files first (validator checks staged files)
git add -A
./.guardrails/bin/validate_guardrails.sh
```

## Configuration

Edit target repo `.guardrails/config.env`:

- `REQUIRED_DOCS="README.md docs/ARCHITECTURE.md"`
- `REQUIRE_DOC_UPDATE_ON_CODE_CHANGE=1`
- `LINT_CMD="npm run lint"`
- `TEST_CMD="pytest -q"`
- `BUILD_CMD="npm run build"`

## Notes

- The validator currently checks **staged files**. In CI (where nothing is staged), it exits successfully with "No staged files".
- If you want strict CI checks on changed files from the merge base, add a CI-specific validator mode in a future iteration.
