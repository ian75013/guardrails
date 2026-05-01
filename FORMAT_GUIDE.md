# Format de présentation des plans d'action

## Vue d'ensemble

Ce guide décrit le format standard pour présenter les plans d'action dans guardrails-kit. Ce format assure **clarté, traçabilité et vérifiabilité** pour tous les travaux substantiels.

## Quand utiliser ce format

Utilisez `templates/ACTION_PLAN.template.md` pour:
- ✅ Toute tâche multi-étapes non triviale
- ✅ Travaux qui nécessitent planification et coordination
- ✅ Changements qui impactent plusieurs services ou composants
- ✅ Modifications d'infrastructure ou de configuration
- ✅ Toute déliverable nécessitant validation

## Composants du format

### 1. Objectifs
Clarifiez **quoi** et **pourquoi**:
- **Principal:** L'objectif central (une phrase courte)
- **Secondaires:** Impacts ou résultats additionnels

**Exemple:**
```
## Objectifs
- **Principal:** Migrer logs vers table dédiée execution_log
- **Secondaires:**
  - Séparer concerns (trades vs. système)
  - Améliorer performance des requêtes analytics
```

### 2. Étapes
Décrivez **comment** avec des étapes claires et ordonnées:
- Utilisez des checkboxes `[ ]` pour chaque phase
- Numérotez si l'ordre est critique
- Ajoutez des détails sous chaque étape

**Exemple:**
```
## Étapes
- [ ] **Phase 1:** Créer table execution_log en DB
  - Indexes sur (level, source, ts)
  - Migrer 14 logs existants de execution
- [ ] **Phase 2:** Rediriger API vers nouvelle table
  - Modifier POST /api/v1/logs
  - Ajouter GET /api/v1/logs avec filtrage
- [ ] **Phase 3:** Déployer et valider
  - Build + push image v4
  - Test endpoints
```

### 3. Validation
Définissez **critères d'acceptation observables**:
- Checklist de critères mesurables
- Doivent être vérifiables (pas de "semble OK")
- Incluez les cas d'erreur

**Exemple:**
```
## Validation
- ✅ execution_log contient 14 logs migré
- ✅ POST /api/v1/logs insère dans execution_log
- ✅ GET /api/v1/logs?level=INFO retourne résultats filtrés
- ✅ Dashboard analytics ne montrent que trades purs
```

### 4. Résultats attendus
Montrez impact avant/après avec tableau:
- Métrique/élément dans colonne 1
- Valeur "avant" → "après"
- Impact ou gain quantifié

**Exemple:**
```
## Résultats attendus
| Élément | Avant | Après | Impact |
|---------|-------|-------|--------|
| Trades execution | 6,350 rows | 5,322 rows | -1,014 junk rows |
| System logs | mixed in execution | dedicated table | +queries clarity |
| Analytics accuracy | 244 corrupted instruments | 8 real instruments | 100% accuracy |
```

### 5. État de progression
Mettez à jour **régulièrement** pendant l'exécution:
- ✅ Phase complétée
- ⏳ Phase en cours
- ⏹️ Phase à venir

Incluez aussi:
- **Blocages:** Aucun, ou liste des obstacles rencontrés
- **Commits:** Références git des changements

**Exemple:**
```
## État de progression
- ✅ **Phase 1** — COMPLÉTÉE (CREATE TABLE + migration)
- ✅ **Phase 2** — COMPLÉTÉE (API redirect)
- ✅ **Phase 3** — COMPLÉTÉE (Déployé en k3s)

**Blocages identifiés:** Aucun

**Commits:** 0ef6b68, 2fb4e1e
```

## Bonnes pratiques

### Longueur et densité
- **Garder concis:** 1-2 pages maximum
- **Éviter le verbeux:** Utiliser listes à puces plutôt que prose
- **Scanner rapidement:** Structure visuelle claire

### Mise à jour
- Mettre à jour **après chaque phase complétée**
- Ajouter blocages **au moment où ils surviennent**
- Actualiser critères de validation si contexte change

### Tableau de résultats
- Inclure seulement si impact quantifiable
- Éviter les métriques triviales ("= pas de changement")
- Montrer gain ou risque mitigé

## Exemple complet

Voir: `templates/ACTION_PLAN.template.md`

Ce fichier contient un template vierge prêt à remplir.

## Avantages

1. **Clarté:** Tous comprennent plan et progrès
2. **Traçabilité:** État et blocages documentés
3. **Vérifiabilité:** Critères d'acceptation explicites
4. **Réutilisabilité:** Format cohérent d'un projet à l'autre
5. **Autonomie:** Moins de questions, plus de contexte

---

**Intégration:** Ce format est utilisé dans `.github/copilot-instructions.md` comme standard obligatoire pour tous les plans d'action substantiels dans guardrails-kit.
