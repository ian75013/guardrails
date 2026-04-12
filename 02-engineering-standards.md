# 02 - Engineering Standards

## Code Standards
- Keep modules cohesive and interfaces explicit.
- Prefer pure functions for critical business logic where possible.
- Validate all external input at boundaries.
- Avoid hidden global state for decision logic.

## Review Standards
- Every PR must include: scope, risk, test evidence, rollback note.
- Review must focus first on correctness, regressions, and failure modes.
- High-risk changes require at least one additional reviewer.

## Dependency Standards
- Pin dependencies in production builds.
- Track license and known vulnerabilities.
- Do not add a dependency if standard library or existing dependency can solve it safely.
