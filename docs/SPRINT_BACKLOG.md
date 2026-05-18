# Tota Agent — Sprint Backlog

Mirror of the GitHub issues in `wesleysimplicio/tota-agent` (see #58 for
the live roadmap). This file lives in the repo so anyone reading the
codebase can find the plan without leaving their editor.

## Master index

| Sprint | Tracker | Theme |
| --- | --- | --- |
| Sprint 1 | #22 | Foundation hardening |
| Sprint 2 | #23 | Performance wave alignment |
| Sprint 3 | #24 | Distribution + identity polish |
| Sprint 4 | #25 | Features, skills, nice-to-have |
| Roadmap  | #58 | Master index |

## Sprint 1 — Foundation hardening

- ✅ #21 — Sync to Hermes 0.14.0 + promote llm-project-mapper to core.
- ✅ #26 — Auto-invoke llm-project-mapper on first turn in any code project (`agent/auto_mapper.py`).
- ✅ #27 — Bootstrap `.tota/` defaults into runtime `$TOTA_HOME` on first run (`agent/tota_home_bootstrap.py`).
- ✅ #28 — Pytest coverage for the llm-project-mapper skill (23 cases).
- ✅ #29 — Consolidate `HERMES_HOME` literal lookups behind `hermes_constants.get_hermes_home()`.
- ⏳ #30 — Cherry-pick upstream cross-session 1h Claude prompt cache (Hermes #23828). Needs upstream commit identification.
- ⏳ #31 — Cherry-pick upstream per-turn file-mutation verifier footer (Hermes #24498).
- ✅ #32 — Decide `.github/workflows/lint.yml` fork-guard policy → `docs/adr/0002-lint-yml-fork-guard.md`.

## Sprint 2 — Performance wave alignment

- ⏳ #33 — Cherry-pick 180x faster `browser_console` (Hermes #23226).
- ⏳ #34 — Adopt upstream cold-start wave (~19s win).
- ⏳ #35 — Phase 2 `msgspec.Struct` migration for `transports/types.py::ToolCall`. High-risk; needs dedicated PR.
- ⏳ #36 — Phase 1.5 `run_agent.py` `orjson` migration. Needs per-site `strict=False` audit.
- ⏳ #37 — Phase 1.5 `hermes_state.py` `orjson` migration + SQLite round-trip audit. Highest-risk; behind `TOTA_FAST_STATE=1` feature flag.
- ⏳ #38 — Refresh `tota_agent_benchmark_report.pdf` post-merge.

## Sprint 3 — Distribution + identity polish

- ✅ #39 — PyPI publishing plan → `docs/adr/0001-pypi-publishing.md` (chose Option B: metapackage).
- ⏳ #40 — Adopt upstream lazy-deps framework (Hermes #24220).
- ⏳ #41 — Adopt supply-chain advisory checker.
- ⏳ #42 — Adopt tiered install fallback (Hermes #24515).
- ✅ #43 — Brand consistency pass (default + 4 neutral skins, CLI welcome banner, SOUL.md template).
- ✅ #44 — `SOUL.md` override docs page (`docs/tota-identity-customization.md`).
- ⏳ #45 — Native Windows beta integration test pass (40+ Windows fixes). Needs a Windows runner.
- ✅ #46 — `tota` / `tota-agent` / `tota-acp` `console_scripts` aliases added.

## Sprint 4 — Features, skills, nice-to-have

- 🚦 #55 — Security trio (land first) → `docs/adr/0003-security-trio-cherry-pick-plan.md` documents the cherry-pick plan.
- ⏳ #47 — Local OpenAI-compatible proxy (Hermes #25969).
- ⏳ #48 — `/handoff` live session transfer (Hermes #23395).
- ⏳ #49 — `/subgoal` user controls (Hermes #25449).
- ⏳ #50 — LSP semantic diagnostics on every write (Hermes #24168, #25978).
- ⏳ #51 — `vision_analyze` raw pixels to vision models (Hermes #22955).
- ⏳ #52 — `clarify` button UI on Telegram + Discord (Hermes #24199, #25485).
- ⏳ #53 — OSC8 clickable URLs (Hermes #25071, #24013).
- ⏳ #54 — Brave Search + DuckDuckGo web-search backends (Hermes #21337).
- ⏳ #56 — Pull 4 new optional skills (hyperliquid, yahoo-finance, api-testing, watchers).
- ⏳ #57 — (Stretch) `huggingface/skills` trusted default tap (Hermes #26219).

## Status legend

- ✅ — Closed (PR merged or doc shipped).
- ⏳ — Open; tractable but not yet started in this session.
- 🚦 — Gating priority for the sprint (must land before other sprint items).

## Process notes

- One PR per child issue wherever possible.
- Cherry-picks are scoped tight: identify the upstream commit, apply, resolve conflicts preferring Tota's perf customizations + upstream's behavior, test.
- Sprints are sequential. Each sprint's DoD must hold before the next sprint starts.
- The `.tota/` repo directory is the source of truth for runtime defaults; `$TOTA_HOME` is the operator-mutable runtime home.
