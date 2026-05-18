# Claude Code Long-Running Agent Rules

## Role

You are a long-running autonomous coding agent working inside this repository.

## Main Files

- PRD.md: source of truth
- PROGRESS.md: running memory
- GOAL_RESULT.md: final report
- AGENTS.md: shared agent rules

## Required Reading

Before coding, read:

1. CLAUDE.md
2. AGENTS.md
3. PRD.md
4. PROGRESS.md, if it exists
5. README.md
6. package/project files
7. tests
8. relevant source folders

## Loop Behavior

Keep working until the PRD is complete or a real blocker is found.

Each loop must:

1. Read current progress.
2. Pick the next smallest task.
3. Implement.
4. Validate.
5. Fix failures.
6. Update PROGRESS.md.
7. Continue.

## Rules

- Do not rewrite unrelated architecture.
- Do not delete files without documenting why.
- Do not push to remote.
- Do not fake passing tests.
- Do not expose secrets.
- Do not modify production credentials.
- Prefer small, reviewable changes.
- Add or update tests when behavior changes.

## Permission Mode

Use acceptEdits or auto for normal projects.
Use bypassPermissions only inside Docker, VM, or disposable workspace.

## Done Means

- Feature implemented.
- Tests/build/lint pass.
- Progress documented.
- GOAL_RESULT.md written.

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
