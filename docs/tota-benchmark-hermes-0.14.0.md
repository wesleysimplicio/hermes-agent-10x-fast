# Tota Agent vs Hermes 0.14.0

- Generated: 2026-05-18 16:17:57 -0300
- Stock ref: `v2026.5.16` (`version = 0.14.0`)
- Local Python: `/Users/wesleysimplicio/Projetos/contribuicoes/hermes/tota-agent/.venv/bin/python`
- Stock Python: `temporary stock venv/bin/python`
- Browser benchmark: **measured**
- Measured rows: **5 wins / 1 losses / 1 ties / 0 blocked** for Tota Agent on this host

## Side-by-side rows

| Row | Hermes 0.14.0 | Tota Agent | Winner | Delta | Notes |
| --- | ---: | ---: | --- | --- | --- |
| Cold start (import_model_tools proxy) | 459.58 ms | 254.03 ms | Tota Agent | 1.81x | Fresh subprocess import of model_tools as a cold-start proxy. |
| JSON dumps short payload | 1.368 us | 0.281 us | Tota Agent | 4.87x |  |
| Tool-call parse | 0.530 us | 0.938 us | Hermes 0.14.0 | 0.57x | Tota path uses the Rust parser. |
| Token estimate batch | 93.996 us | 24.561 us | Tota Agent | 3.83x | Tota uses estimate_messages_tokens; stock uses estimate_messages_tokens_rough. |
| Async 1,000-task scheduler | 46.61 ms | 32.01 ms | Tota Agent | 1.46x | Tota run requested uvloop; stock stayed on default asyncio. |
| browser_console p99 | 1.34 ms | 0.56 ms | Tota Agent | 2.38x | Measures browser_console(expression) p99 over a shared headless Chrome CDP session. |
| Integration breadth | 31 | 31 | Tie | 1.00x | Counts Python gateway platform modules excluding __init__.py. |

## Status

Measured against a shared local headless Chrome instance via CDP.

## Commands

```bash
.venv/bin/python scripts/benchmark_tota_vs_hermes_0140.py --output-json /Users/wesleysimplicio/Projetos/contribuicoes/hermes/tota-agent/docs/tota-benchmark-hermes-0.14.0.json --output-md /Users/wesleysimplicio/Projetos/contribuicoes/hermes/tota-agent/docs/tota-benchmark-hermes-0.14.0.md
```
