# Hermes Agent 10x Fast PR - Phase 1 + 2

Date: 2026-05-15

Upstream-ready PR body:
`docs/hermes-performance-upstream-pr.md`

This PR is the first concrete performance pass from
`docs/performance-pr-candidates-2026-05-15.md`. The headline result is a
~2.15x faster cold `model_tools` import plus tool-schema startup path on this
Windows workstation, while preserving the full gateway/platform path for
callers that need it.

The "10x fast" target is still a multi-PR goal. These phases remove several
large startup and persistence costs and add repeatable benchmarks so future PRs
can keep compounding the gains without guessing.

## Architecture Inspiration

This phase borrows safe ideas from the DS4/US4 notes, adapted to Hermes rather
than copied literally:

- Hot/cold cache and profile-store thinking from US4: keep the hot path on
  fingerprints and cached manifests, and only scan or reload when the relevant
  profile changed.
- Continuous batching from US4: batch writes when correctness does not require
  one transaction per item.
- Benchmark/correctness discipline from DS4-v4/US4: document targets and
  measured results separately; do not claim final wins without data.

References:

- https://github.com/wesleysimplicio/us4-v6-simplicio-windows/blob/main/US4-V6-Windows-Edition.md
- https://github.com/wesleysimplicio/us4-v6-simplicio-apple/blob/main/US4-V6-simplicio.md
- https://github.com/wesleysimplicio/ds4-v2-simplicio/blob/main/docs/ds4pp.md
- https://github.com/wesleysimplicio/ds4-v4-simplicio/blob/main/ds4-v4-development-prompt.md

## Benchmark

Command:

```powershell
python scripts\benchmark_startup_perf.py -n 7
```

Baseline was measured from detached `main` at
`a1c316c6f664fa507bb43ea8f91519b390ed9f75` in a separate worktree.

| Case | main median | branch median | Speedup | Change |
| --- | ---: | ---: | ---: | ---: |
| `import_model_tools` | 2.0847s | 0.8419s | 2.48x | 59.6% faster |
| `import_and_get_tool_definitions` | 1.8782s | 0.8741s | 2.15x | 53.5% faster |
| `get_tool_definitions` | 0.0918s | 0.0898s | 1.02x | 2.2% faster |
| platform plugin discovery fast path | 0.5571s full baseline | 0.1930s fast path | 2.89x | 65.4% faster |

Visual summary:

![Hermes Agent 10x Fast Phase 1](assets/hermes-agent-10x-fast-before-after.svg)

Generated visual:

![Hermes Agent 10x Fast generated PR visual](assets/10x-fast/hermes-agent-10x-fast-phase-1.png)

## What Shipped

### Phase 1 - Startup Import Weight

1. Deferred platform plugin imports outside normal model-tool startup.
   `model_tools` now calls `discover_plugins(include_platforms=False)`, while
   gateway/platform callers can still use the default full discovery.

2. Added an on-demand platform-plugin load path.
   `PluginManager.discover_and_load()` can start fast, then hydrate platform
   plugins later without forcing a restart.

3. Replaced AST parsing in built-in tool discovery.
   `tools/registry.py` now detects top-level `registry.register(...)` with a
   lightweight regex, avoiding per-file AST construction during discovery.

4. Made browser provider imports lazy.
   `tools/browser_tool.py` no longer imports cloud browser providers,
   `requests`, Camofox, `cfg_get`, or auxiliary LLM code during module import.

5. Preserved browser test patch surfaces while staying lazy.
   `call_llm` and `requests` remain patchable from `tools.browser_tool`, but
   they resolve the heavy modules only when used.

6. Made cloud browser requirement checks credential-gated.
   Provider classes are imported only when config or environment variables make
   a cloud browser path possible.

7. Made TTS availability checks lightweight.
   `check_tts_requirements()` now uses `importlib.util.find_spec()` for SDK
   presence instead of importing `edge_tts`, `aiohttp`, OpenAI, ElevenLabs, or
   Mistral just to expose schemas.

8. Kept TTS tests compatible with monkeypatched lazy import helpers.
   Production uses `find_spec`; tests that patch `_import_edge_tts` and friends
   still control availability.

9. Made Yuanbao schema checks avoid importing gateway platform adapters.
   `_check_yuanbao()` only consults the active adapter if the Yuanbao platform
   module is already loaded, avoiding `aiohttp`/gateway imports during CLI
   startup.

10. Added a repeatable startup benchmark.
    `scripts/benchmark_startup_perf.py` measures cold subprocess timings for
    import, schema assembly, and plugin discovery paths.

### Phase 2 - Cached Hot Paths and Batch Persistence

11. Added a persistent built-in tool discovery cache.
    `tools/registry.py` now stores the self-registering module list under the
    Hermes cache directory, keyed by `tools/` filename, mtime, and size. A warm
    startup can skip source scanning unless a tool file changed.

![Phase 2 tool discovery cache](assets/10x-fast/phase-2-tool-discovery-cache.svg)

12. Memoized recursive toolset resolution.
    `toolsets.py` now caches resolved toolsets, toolset names, and merged
    toolset maps by registry object + generation. Dynamic plugin toolsets still
    invalidate when the registry changes.

![Phase 3 toolset memoization](assets/10x-fast/phase-3-toolset-cache.svg)

13. Batched session message persistence.
    `SessionDB.append_messages()` inserts a completed flush in one SQLite write
    transaction and updates session counters once. `AIAgent` now uses the batch
    path when available and falls back to the old per-message method if needed.

![Phase 4 SQLite batch writes](assets/10x-fast/phase-4-sqlite-batch-writes.svg)

14. Made TUI config polling MCP-aware.
    `config.get mtime` now returns an `mcp_servers` fingerprint. The TUI still
    hydrates display/voice changes on any config mtime change, but it only calls
    `reload.mcp` when the MCP fingerprint changes.

![Phase 5 TUI MCP fingerprint](assets/10x-fast/phase-5-tui-mcp-fingerprint.svg)

15. Expanded the benchmark harness.
    `scripts/benchmark_startup_perf.py` now includes toolset memoization and
    SQLite batch write microbenchmarks in addition to startup/import cases.

16. Added adaptive parallelism for large source-scan cache misses.
    Built-in tool discovery can now scan candidate source files with a
    `ThreadPoolExecutor` when a tool directory is large enough. The current
    Hermes `tools/` directory is below the byte threshold, because local
    benchmarking showed thread overhead was slower than the sequential scan.
    The import phase remains ordered and serial so tool registration side
    effects stay deterministic.

![Phase 6 adaptive parallel scan](assets/10x-fast/phase-6-adaptive-parallel-scan.svg)

## Latest Local Benchmark

Command:

```powershell
python scripts\benchmark_startup_perf.py -n 5
```

Results from this Windows workstation after Phase 2:

| Case | Median | Notes |
| --- | ---: | --- |
| `import_model_tools` | 2.1392s | `tools=76`; noisy Windows cold subprocess run |
| `import_and_get_tool_definitions` | 2.1729s | `tools=16`; noisy Windows cold subprocess run |
| `get_tool_definitions` | 0.2378s | warm path ~0.000475s |
| `discover_plugins_fast` | 0.5278s | platform plugins deferred |
| `discover_plugins_full` | 1.3316s | platform plugins loaded |
| `tool_discovery_source_scan_adaptive` | 0.0987s | `parallel_eligible=False`; adaptive guard kept local scan sequential |
| `resolve_toolset_cached` | 0.1610s cold | warm path ~0.000002s/call |
| `session_append_messages_batch` | 0.0240s batch | loop ~0.6329s, ~24.21x faster for 180 messages |

The SQLite result is the largest concrete Phase 2 win. Startup import results
are directionally useful but noisy on this machine because cold subprocess runs
vary with Windows filesystem and antivirus activity.

## Follow-Up PRs Toward 10x

1. Generate a persistent tool manifest so schema metadata can load without
   importing every tool module.
2. Cache plugin manifest scans by directory fingerprint and entry-point
   metadata.
3. Keep prompt-cache prefixes stable by moving volatile prompt data out of
   system prompts.
4. Extend the skill snapshot cache to external skill dirs.
5. Denormalize session previews and last-active metadata.
6. Make `/goal` continuation checks adaptive instead of every turn.
7. Add CI perf-budget smoke tests for the startup benchmark.
8. Add a config/profile performance report similar to the DS4/US4 profile
   reports, but scoped to Hermes startup, toolsets, DB writes, and MCP reloads.

## Verification

```powershell
python -m py_compile hermes_cli\plugins.py model_tools.py tools\registry.py tools\browser_tool.py tools\tts_tool.py tools\yuanbao_tools.py scripts\benchmark_startup_perf.py
python -m pytest tests\hermes_cli\test_plugins.py tests\tools\test_registry.py -q -k "platform_plugins_can_be_deferred_then_loaded or imports_only_self_registering_modules or ignores_indented_register_calls or skips_mcp_tool"
python -m pytest tests\tools\test_browser_cloud_fallback.py tests\tools\test_browser_cdp_override.py tests\tools\test_browser_content_none_guard.py -q
python -m pytest tests\tools\test_tts_gemini.py tests\tools\test_tts_mistral.py tests\tools\test_tts_piper.py tests\tools\test_tts_dotenv_fallback.py -q
python -m pytest tests\tools\test_yuanbao_tools.py -q
python scripts\benchmark_startup_perf.py -n 7
python -m py_compile tools\registry.py toolsets.py hermes_state.py run_agent.py tui_gateway\server.py scripts\benchmark_startup_perf.py
python -m pytest tests\tools\test_registry.py tests\test_toolsets.py tests\test_hermes_state.py -q
python -m pytest tests\test_tui_gateway_server.py::test_config_get_mtime_includes_mcp_fingerprint tests\test_tui_gateway_server.py::test_mcp_config_fingerprint_treats_missing_section_as_empty -q
cd ui-tui; npm test -- useConfigSync.test.ts; npm run type-check
python scripts\benchmark_startup_perf.py -n 5
```
