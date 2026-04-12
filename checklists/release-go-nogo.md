# Release GO/NOGO Checklist

## GO Conditions
- [ ] Build is reproducible and versioned.
- [ ] Unit/integration/E2E tests pass.
- [ ] Health checks pass in target environment.
- [ ] Key contract/schema checks pass.
- [ ] Monitoring and alerts are active.
- [ ] Rollback command/procedure validated.

## NOGO Conditions
- [ ] Any blocking test fails.
- [ ] Critical endpoint/schema mismatch.
- [ ] No rollback plan.
- [ ] Missing production telemetry for critical path.
- [ ] Undocumented production behavior change.
