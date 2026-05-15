# Hermes Agent 100X Fast Video Storyboard

Rendered asset:

- `docs/assets/100x-fast/video/hermes-100x-fast-launch.mp4`
- 90 seconds, 1920x1080, 30fps, H.264 + AAC
- Poster: `docs/assets/100x-fast/video/hermes-100x-fast-poster.png`
- Soundtrack source: `public/sound/hermes-100x-fast-soundtrack.wav`

## Intent

Make the performance work feel tangible without overstating it. The video says
"100X Fast" as the performance track, then ties every speed claim to a concrete
hot path: metadata cache, session writes, dead endpoint startup, parallel tools,
and startup discovery.

## Timeline

| Time | Scene | Visual | Audio Cue |
| ---: | --- | --- | --- |
| 0-18s | Opening | GPT-image video cover with title, gain chips, and a slow-to-fast transformation | Slow pulse builds into a brighter synth layer |
| 16-37s | Before vs after | Generated before/after hero and runtime-stack image side by side with a green sweep | Beat becomes more regular to imply motion |
| 35-57s | Measured gains | Five metric cards animate in: 0.4211s / 100 lookups, 37.74x, 9.25x, 5.20x, 2-3x | Ticks emphasize each metric reveal |
| 55-75s | Safety architecture | Cache, batch, fast-fail, metadata disk cache, and parallel tools appear as connected nodes | Wider bass pad, lower tension |
| 73-90s | Close | Repeatable-playbook message and final "Hermes Agent 100X Fast" mark | Release tail fades cleanly |

## Exact Claims Used

- Metadata cache: fresh disk cache lookup measured at median 0.4211s for 100
  cold memory resets over 500 models in the benchmark scenario.
- Session writes: row-by-row persistence to one transaction, latest local
  sample around 37.74x.
- Endpoint startup: dead numeric loopback probe fast-fail, around 9.25x for the
  measured scenario.
- Parallel tools: independent I/O-bound batch around 5.20x.
- Startup discovery: measured local improvements in the 2x-3x class.

## Re-render

```powershell
cd docs\remotion\100x-fast
npm install
npm run audio
npx tsc --noEmit
npm run still
npm run render
```

If numbers change, update both the Remotion source and the README table before
rendering again.
