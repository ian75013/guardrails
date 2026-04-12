# 05 - Release and Change Management

## Change Scope Rules
- Avoid multi-axis risky releases (architecture + infra + business logic at once).
- Prefer incremental rollout when possible.

## Release Requirements
- Release plan with owner and rollback path.
- Versioned artifact and reproducible build.
- Pre-release smoke checks documented.

## Rollback Requirements
- Define rollback trigger conditions before release.
- Keep rollback command/procedure tested and documented.
- Record rollback outcome and follow-up actions.

## Deployment Safety
- No destructive cleanup commands in standard deploy path.
- Confirm target environment and config before execution.
- Stop release immediately on failed smoke checks.
