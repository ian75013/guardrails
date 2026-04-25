# CLAUDE.md

Ce fichier définit les règles d'exécution Claude Code pour `guardrails`.

## Sources de vérité obligatoires
- `SKILLS.md`
- `ROADMAP.md`
- `.github/copilot-instructions.md`
- `.github/agents/guardrails-agent.agent.md`

## Principes d'exécution
1. Lire les sources de vérité avant toute tâche non triviale.
2. Aligner chaque changement sur la phase active de `ROADMAP.md`.
3. Corriger la cause racine avant tout contournement.
4. Conserver des changements minimaux, ciblés, et vérifiables.
5. Mettre à jour la documentation quand le comportement change.

## Politique d'environnement (obligatoire)
- Utiliser un environnement standard unique par repo autant que possible.
- Utiliser GPU si disponible et compatible; sinon CPU dans le même environnement standard.
- Les environnements parallèles sont autorisés uniquement si techniquement inévitables.
- Si un environnement parallèle est créé, documenter clairement:
  - la raison technique,
  - les limites,
  - le nommage explicite,
  - la procédure d'activation.

## Compatibilité plateforme
- Les scripts d'automatisation critiques doivent fournir une exécution Ubuntu (Bash) et Windows (PowerShell).
- Toute exception doit être documentée avec une alternative opérationnelle.

## Hooks
- Préparation: `.claude/hooks/preflight.ps1` et `.claude/hooks/preflight.sh`
- Vérification rapide: `.claude/hooks/post-task.ps1` et `.claude/hooks/post-task.sh`
- Détails d'usage: `.claude/hooks/README.md`
