# Generic Guardrails Kit

A reusable guardrails structure for serious software projects.

## Goals
- Keep delivery safe, testable, and reversible.
- Prevent regressions and hidden production risk.
- Standardize quality gates across teams and repositories.

## Structure
- `01-core-principles.md`: non-negotiable engineering principles.
- `02-engineering-standards.md`: coding, review, and dependency standards.
- `03-security-privacy.md`: secure-by-default controls.
- `04-testing-quality-gates.md`: test strategy and merge blockers.
- `05-release-change-management.md`: release and rollback rules.
- `06-observability-operations.md`: runtime checks and incident response.
- `07-documentation-knowledge.md`: mandatory documentation and knowledge transfer.
- `automation/scripts/`: installation and validation scripts.
- `checklists/`: copy-paste operational checklists.
- `templates/`: guardrail templates for project onboarding and CI.

## Automatic Enforcement
Use the installer to activate guardrails automatically in any Git repository:

```bash
bash automation/scripts/install_guardrails.sh /path/to/your/repo
```

What it installs in the target repo:
- `.guardrails/config.env` (project-specific configuration)
- `.guardrails/bin/validate_guardrails.sh` (validator)
- `.git/hooks/pre-commit` entry (automatic local checks)
- `.github/workflows/guardrails.yml` (CI guardrails on PR/push)

To apply on multiple repositories in one command:

```bash
bash automation/scripts/apply_to_repos.sh /repo/one /repo/two /repo/three
```

General command for this workspace:

```bash
bash automation/scripts/apply_to_repos.sh \
	/home/yann/Documents/Github/market_screener \
	/home/yann/Documents/Github/doctum-trading-platform \
	/home/yann/Documents/Github/litellm-gateway-vps \
	/home/yann/Documents/Github/medvision-ai \
	/home/yann/Documents/Github/market_insights \
	/home/yann/Documents/Github/doctumconsilium-html5-css3-portfolio
```

## Recommended Adoption Order
1. Start with `01-core-principles.md`.
2. Adopt `04-testing-quality-gates.md` and `05-release-change-management.md` as merge blockers.
3. Add repository-specific thresholds in `checklists/release-go-nogo.md`.
4. Require all new changes to include documentation updates.

## Minimum Baseline (for any project)
- Every change has tests.
- Every release has rollback.
- Every incident has technical cause + verified fix.
- Every new behavior is documented.
