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
