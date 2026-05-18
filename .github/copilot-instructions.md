# Autonomous Coding Instructions

You are an autonomous coding agent.

## Read First

- PRD.md
- PROGRESS.md
- README.md
- AGENTS.md
- tests
- project/package files

## Work Loop

1. Pick the next incomplete task.
2. Implement the smallest safe change.
3. Run validation.
4. Fix failures.
5. Update PROGRESS.md.
6. Continue until complete.

## Do Not

- rewrite unrelated architecture
- remove tests
- fake successful validation
- push without explicit instruction
- expose secrets
- modify production credentials

## Complete Only When

- PRD.md is fully done
- tests/build/lint pass
- GOAL_RESULT.md is written

<!-- codex-long-running-agent-overlay:start -->
## Universal Long-Running Agent Overlay

This section complements the repository-specific guidance already in this file. If anything here conflicts with the repo-specific rules above, the repo-specific rules win.

- `PRD.md` is the task source of truth for long-running sessions.
- `PROGRESS.md` is the persistent checkpoint log.
- `GOAL_RESULT.md` is the final execution report.
- Before coding, read this file, `PRD.md`, `PROGRESS.md` when it exists, `README.md`, project manifests, tests, and the relevant source folders.
- Work in small checkpoints, run the smallest relevant validation after each meaningful change, update `PROGRESS.md`, and continue until complete or genuinely blocked.
- Stop only when the requested work is complete, validation is documented, and `GOAL_RESULT.md` reflects the outcome.
- Do not rewrite unrelated architecture, fake successful validation, expose secrets, or push without explicit operator instruction for the active session.
<!-- codex-long-running-agent-overlay:end -->
