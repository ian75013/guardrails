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

**Linux/macOS:**
```bash
cd $GUARDRAILS_KIT  # or: cd /path/to/guardrails-kit
bash scripts/install_into_repo.sh $TARGET_REPO
```

**Windows PowerShell:**
```powershell
cd $env:GUARDRAILS_KIT  # or: cd C:\path\to\guardrails-kit
pwsh -File scripts/install_into_repo.ps1 $env:TARGET_REPO
```

**Optional flags (all platforms):**
```bash
bash scripts/install_into_repo.sh $TARGET_REPO --without-copilot-instructions
bash scripts/install_into_repo.sh $TARGET_REPO --force
bash scripts/install_into_repo.sh $TARGET_REPO --project-name "My Project"
```

By default, all new repositories receive:
- ✅ `.github/copilot-instructions.md` (GitHub Copilot)
- ✅ `CLAUDE.md` (Claude Code)
- ✅ `GEMINI.md` (Gemini CLI + Gemini Assistant)
- ✅ `.antigravity/workspace.yaml` (Antigravity IDE)

## Install into multiple repositories at once (CLI)

Use batch installers to deploy guardrails-kit on several repositories in one command.

**Linux/macOS (Bash):**
```bash
cd $GUARDRAILS_KIT
bash scripts/install_many_repos.sh --base-dir /path/to/repos repo-a repo-b repo-c --force
```

Or with a file list:
```bash
# repos.txt supports comments (#) and blank lines
bash scripts/install_many_repos.sh --repos-file repos.txt --force
```

**Windows PowerShell:**
```powershell
cd $env:GUARDRAILS_KIT
pwsh -File scripts/install_many_repos.ps1 -BaseDir C:\path\to\repos -TargetRepos repo-a,repo-b,repo-c -Force
```

Or with a file list:
```powershell
pwsh -File scripts/install_many_repos.ps1 -ReposFile .\repos.txt -Force
```

Dry run examples:
```bash
bash scripts/install_many_repos.sh --base-dir /path/to/repos repo-a repo-b --dry-run
```

```powershell
pwsh -File scripts/install_many_repos.ps1 -BaseDir C:\path\to\repos -TargetRepos repo-a,repo-b -DryRun
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

## Multi-AI Assistant Support (Default)

**By default, every new repository gets all 5 AI platform configurations.** No extra steps needed:

Guardrails Kit automatically installs and configures **5 major AI development tools**:

### 1. **Claude Code** (Anthropic)
- Configuration: `CLAUDE.md` in each repo
- Activation: Automatically loaded by Claude Code
- Context: Reads `ROADMAP.md`, `README.md`, `INFRASTRUCTURE.md`, `.github/copilot-instructions.md`

### 2. **GitHub Copilot** (Microsoft)
- Configuration: `.github/copilot-instructions.md`
- Activation: Auto-loaded by GitHub Copilot in VS Code
- Context: Points to guardrails-kit policy rules

### 3. **Gemini CLI** (Google)
- Configuration: `GEMINI.md`
- Activation: `gemini context add . --name <project-name>`
- Usage: `gemini run "Ask AI a question about this repo"`

### 4. **Gemini Assistant** (Google)
- Configuration: `GEMINI.md`
- Activation: Install VS Code extension `google.gemini-assistant`
- Context: Auto-reads `README.md`, `ROADMAP.md`, `GEMINI.md`, `CLAUDE.md`
- Slash Commands: `/check`, `/explain`, `/improve`, `/generate`, `/review`

### 5. **Antigravity IDE** (Google)
- Configuration: `.antigravity/workspace.yaml`
- Activation: `antigravity /path/to/repo`
- Context: Auto-loads all project folders, docs, and AI context files
- AI Commands: `Cmd+K` (macOS) or `Ctrl+K` (Linux/Windows)

### Re-apply Multi-AI Support to Existing Repos

If you need to update existing repositories with latest guardrails:

**Linux/macOS:**
```bash
cd $GUARDRAILS_KIT
bash scripts/install_into_repo.sh $TARGET_REPO --force
```

**Windows PowerShell:**
```powershell
cd $env:GUARDRAILS_KIT
pwsh -File scripts/install_into_repo.ps1 $env:TARGET_REPO -Force
```

This creates/updates in each repo:
- `GEMINI.md` — Gemini CLI & Gemini Assistant configuration
- `.antigravity/workspace.yaml` — Antigravity IDE workspace config

### Verify Multi-AI Installation

**Linux/macOS:**
```bash
cd $TARGET_REPO
ls -la CLAUDE.md .github/copilot-instructions.md GEMINI.md .antigravity/workspace.yaml
```

**Windows PowerShell:**
```powershell
cd $env:TARGET_REPO
Test-Path CLAUDE.md, .github/copilot-instructions.md, GEMINI.md, .antigravity/workspace.yaml
```

### Use Gemini CLI for Context & Tasks

```bash
# Add repo context to Gemini
cd $TARGET_REPO
gemini context add . --name my-project
gemini context add README.md --priority high
gemini context add ROADMAP.md --priority high

# Ask Gemini AI about the project
gemini run "Explain the project architecture"
gemini run "Generate documentation for this service"
```

### Use Antigravity IDE

**Linux/macOS:**
```bash
antigravity $TARGET_REPO
# Then press Cmd+K (macOS) or Ctrl+K to open AI copilot
```

**Windows PowerShell:**
```powershell
antigravity $env:TARGET_REPO
# Then press Ctrl+K to open AI copilot
```

**Inside Antigravity:**
- Ask: "Explain the README"
- Ask: "Generate tests for this module"
- Ask: "Review my code change"
- Ask: "Document this function"
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

## Presentation Standards and Templates

Guardrails Kit provides standard templates and formats to ensure consistency and traceability:

### Action Plans
For any substantial work, use **`templates/ACTION_PLAN.template.md`** with:
- Clear objectives
- Numbered steps with checkboxes
- Explicit validation criteria
- Before/after results table
- Updated progress state

See **`FORMAT_GUIDE.md`** for full details and best practices.

### Other Templates
- `ROADMAP.template.md` — roadmap produit/projet
- `SKILLS.template.md` — documentation de domaine
- `adr-template.md` — Architecture Decision Records
- `risk-register-template.md` — registre de risques

### Multi-AI Assistant Files (Generated by Default)

Guardrails Kit automatically generates **4 AI assistant config files** per repo:

| File | AI Assistant | Purpose |
|---|---|---|
| `.github/copilot-instructions.md` | GitHub Copilot | Auto-loaded by Copilot in VS Code |
| `CLAUDE.md` | Claude Code (Anthropic) | Auto-loaded by Claude Code editor |
| `GEMINI.md` | Gemini CLI / Gemini Assistant (VS Code) | CLI context + /slash commands |
| `.antigravity/workspace.yaml` | Antigravity IDE (Google) | Workspace config + Ctrl+K AI |

All files enforce **unified guardrails**:
- Code documentation standard (docstrings/JSDoc/XML)
- Secret management protocol (ECR 12h rotation, k8s secrets)
- Terminal sessions for critical ops (tmux)
- Platform compatibility (Ubuntu + Windows + macOS)

To regenerate all files for a repo:

```bash
bash $GUARDRAILS_KIT/scripts/install_into_repo.sh $TARGET_REPO --force
```

### ECR Secrets Agent
For AWS ECR token rotation, ImagePullBackOff diagnosis, and k8s pull secret lifecycle:
- Full runbook: `.github/agents/ecr-secrets-agent.agent.md`
- Copy to operational repos: `k3s-fromOVHVps`, `doctum-trading-platform`

## Notes

- The validator currently checks **staged files**. In CI (where nothing is staged), it exits successfully with "No staged files".
- If you want strict CI checks on changed files from the merge base, add a CI-specific validator mode in a future iteration.

## How This Project Works (Operations)
- Runtime and infra details are documented in [INFRASTRUCTURE.md](INFRASTRUCTURE.md).
- Start from the local run section, then use the deployment section for production updates.
- Keep changes reversible and validate health checks after rollout.
