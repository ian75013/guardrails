# Hooks Claude Code (guardrails)

## Scripts disponibles
- `preflight.ps1` / `preflight.sh`: vérifie les fichiers de gouvernance essentiels.
- `post-task.ps1` / `post-task.sh`: lance la validation guardrails.

## Exécution manuelle (Windows)

```powershell
pwsh -File .claude/hooks/preflight.ps1
pwsh -File .claude/hooks/post-task.ps1
```

## Exécution manuelle (Ubuntu)

```bash
bash .claude/hooks/preflight.sh
bash .claude/hooks/post-task.sh
```
