# Copilot Instructions

Ces règles sont obligatoires pour les tâches sur `guardrails`.

## Guardrails de chat
- Lire `SKILLS.md` et `ROADMAP.md` avant toute tâche substantielle.
- Aligner le plan sur la phase active de `ROADMAP.md`.
- Donner des mises à jour courtes et actionnables pendant l'exécution.
- Privilégier des changements minimaux et vérifiables.

## Guardrails techniques
- Corriger la cause racine plutôt que contourner le symptôme.
- Préserver le style du repo et éviter les refactors hors périmètre.
- Maintenir la compatibilité Ubuntu + Windows des scripts d'automatisation.
- Éviter tout secret en dur dans fichiers, scripts ou logs.
- Quand un comportement change, mettre à jour la documentation concernée.

## Qualité
- Vérifier les changements (script de validation ciblé, dry-run, ou check équivalent).
- Si un blocage persiste, documenter la cause et proposer l'alternative la plus simple.
