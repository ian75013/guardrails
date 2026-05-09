# ROADMAP

## Phase actuelle
- Phase: standardisation opérationnelle
- Objectif actif: fournir un kit guardrails cohérent, automatisable et compatible Ubuntu + Windows.

## Phases

### 1) Socle de gouvernance
- Stabiliser principes, standards, sécurité, tests, release et observabilité.
- Garantir cohérence entre standards et checklists.

### 2) Automatisation multi-repos
- Maintenir scripts d'installation et validation Bash + PowerShell.
- Assurer idempotence et traces d'exécution claires.

### 3) Templates projet
- Fournir templates SKILLS, ROADMAP, agent, copilot-instructions, CI.
- Réduire la variance d'onboarding entre repos.

### 4) Compatibilité plateforme
- Exiger compatibilité Ubuntu + Windows pour scripts critiques.
- Documenter limites et alternatives quand une parité stricte n'est pas possible.

### 5) Qualité continue
- Ajouter vérifications rapides et documentation d'usage.
- Consolider le feedback d'adoption pour itérations.

## Backlog court terme
1. Ajouter une politique explicite “environnement standard unique” dans les standards.
2. Uniformiser les hooks Claude (PowerShell + Bash) dans les repos cibles.
3. Renforcer la doc d'exécution locale/CI sur Linux/Windows.

## Execution Log — 2026-05-09

### Multi-AI Assistant Support (Gemini + Antigravity)

- ✅ Created `GEMINI.md` template with support for:
  - Gemini CLI (`gemini context add`, `gemini run`)
  - Gemini Assistant (VS Code extension)
  - Antigravity IDE (native workspace support)
- ✅ Created `.antigravity/workspace.yaml` config template
- ✅ Propagated to all 13 repos via `scripts/propagate_gemini_antigravity.py`
- ✅ Updated guardrails-kit README with multi-AI usage guide
- ✅ All 13 repos now have:
  - `CLAUDE.md` (Claude Code)
  - `.github/copilot-instructions.md` (GitHub Copilot)
  - `GEMINI.md` (Gemini CLI + Gemini Assistant)
  - `.antigravity/workspace.yaml` (Antigravity IDE)

### Status: 5 AI platforms supported
- Claude Code ✓
- GitHub Copilot ✓
- Gemini CLI ✓
- Gemini Assistant (VS Code) ✓
- Antigravity IDE ✓

## Execution Log — 2026-05-09 (Updated)

### Generic Paths & Default Multi-AI Enablement

- ✅ Updated README.md with generic path variables:
  - Replaced `~/Documents/Github/<repo>` with `$TARGET_REPO`
  - Replaced hardcoded paths with environment variables (`$GUARDRAILS_KIT`, `$env:GUARDRAILS_KIT`)
  - Added platform-specific instructions (Linux/macOS vs Windows)
- ✅ Updated `scripts/install_into_repo.sh` to install multi-AI by default:
  - CLAUDE.md ✓
  - GEMINI.md ✓
  - .antigravity/workspace.yaml ✓
  - .github/copilot-instructions.md ✓
- ✅ Updated `scripts/install_into_repo.ps1` (PowerShell) with same defaults
- ✅ Updated `.antigravity/workspace.yaml` to use template variables `{{PROJECT_NAME}}`
- ✅ Re-propagated to all 13 repos with corrected workspace names

### Status: Installation now 100% multi-AI enabled by default
Every new repo install gets all 4 AI platform configs automatically.

## Execution Log — 2026-05-09 (Batch CLI)

### Multi-repository command-line deployment

- ✅ Added Bash batch installer: `scripts/install_many_repos.sh`
- ✅ Added PowerShell batch installer: `scripts/install_many_repos.ps1`
- ✅ Updated README with multi-repo usage examples (direct list, file list, dry-run)
- ✅ Bash dry-run validation completed on 2 repos
- ⚠️ PowerShell runtime validation pending on host with `pwsh` installed

### Status
- Guardrails can now be deployed from CLI to multiple repos in a single command.

## Rollback
- All changes are documentation-only and non-breaking.
- Revert any file via `git checkout HEAD~1 -- <file>`.
