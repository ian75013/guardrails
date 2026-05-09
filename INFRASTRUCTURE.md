# INFRASTRUCTURE

## Purpose
guardrails-kit standardizes governance, quality, and operational templates across repositories.

## Main Components
- Core standards documents (01-05)
- Templates in templates/
- Automation and validation scripts (bash + powershell)

## Local Run
1. Review README and standards documents.
2. Apply templates/scripts to target repositories.
3. Run quick validation scripts after updates.

## Deployment
- Propagate template changes in controlled batches to target repos.
- Validate generated/updated files before merge.

## Operations and Validation
- Verify instruction files are consistent and in the expected language.
- Ensure Ubuntu + Windows compatibility for critical scripts.

## Rollback
- Restore previous template/script revision and re-run validations.
