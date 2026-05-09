# CLAUDE.md

This file defines Claude Code execution rules for `guardrails-kit`.

## Mandatory Sources of Truth
- `README.md`
- `INFRASTRUCTURE.md`
- `SKILLS.md`
- `ROADMAP.md`
- `.github/copilot-instructions.md`
- `.github/agents/guardrails-agent.agent.md`

## Project Context
guardrails-kit — canonical standards, templates, and agents for all repos.
Changes here propagate to all 13 downstream repos.

## Execution Principles
1. Read sources of truth before any non-trivial task.
2. Align every change with the active phase in `ROADMAP.md`.
3. Fix root causes before any workaround.
4. Keep changes minimal, targeted, and verifiable.
5. Update documentation when behavior changes.
6. When modifying a template, propagate the change to all downstream repos.

## Code Documentation Standard (Mandatory)
- Every public function, class, and module MUST have a docstring in the language's canonical format:
  - Python: Google-style docstrings (Args, Returns, Raises, Example).
  - TypeScript/JavaScript: JSDoc with @param, @returns, @throws, @example.
  - C#: XML summary with <summary>, <param>, <returns>.
  - Shell: header block with Purpose, Usage, Arguments, Exit codes.
- When modifying a function, update its docstring to reflect the new behavior.
- Run `pydoc`, `typedoc`, or equivalent after doc changes to verify output.

## Secret Management Protocol (Mandatory)
- Never hardcode secrets, tokens, or credentials in any file, script, log, or commit.
- ECR / Docker Registry tokens rotate every 12 hours. Before any image operation:
  1. `aws ecr get-login-password --region <region>` to refresh.
  2. Recreate the k8s pull secret via `kubectl delete/create secret`.
  3. Restart pods stuck in `ImagePullBackOff`.
- Full runbook: `.github/agents/ecr-secrets-agent.agent.md`

## Terminal Sessions (Mandatory for Critical Operations)
- Always use a named tmux session for long-running, deployment, or destructive operations:
  ```bash
  tmux new-session -A -s <task-name>   # start or reattach
  # Naming: deploy-<service>, build-<tag>, k3s-ops, ecr-refresh
  # Detach: Ctrl+B D  |  Reattach: tmux attach -t <task-name>
  ```
- On Windows: use Windows Terminal tabs or Start-Process with file logging.
- On macOS: same tmux convention (iTerm2 or Terminal).

## Environment Policy
- Use a single standard environment per repo when possible.
- Parallel environments allowed only if technically unavoidable — document reason, limits, naming, activation.

## Platform Compatibility (Ubuntu + Windows + macOS)
- Critical automation scripts must provide:
  - Ubuntu: Bash (`.sh`)
  - Windows: PowerShell (`.ps1`)
  - macOS: zsh/bash (same as Ubuntu when POSIX-standard)
- Any exception must be documented with an operational alternative.

## Multi-AI Compatibility
- All instructions must be valid for: GitHub Copilot, Claude Code, Gemini CLI.
- Template files:
  - `templates/copilot-instructions.template.md` → `.github/copilot-instructions.md`
  - `templates/CLAUDE.template.md` → `CLAUDE.md`
  - `templates/GEMINI.template.md` → `GEMINI.md`
- When updating guardrails, regenerate all three target files in all downstream repos.

## Hooks (if present)
- Preflight: `.claude/hooks/preflight.ps1` and `.claude/hooks/preflight.sh`
- Post-task check: `.claude/hooks/post-task.ps1` and `.claude/hooks/post-task.sh`
- Usage details: `.claude/hooks/README.md`
