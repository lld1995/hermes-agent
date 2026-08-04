# BurstCode Background Explorer

This directory is maintained automatically by BurstCode while the
IDE is idle. You can safely delete it; it will be regenerated.

## Latest run

- Last cycle: 2026-05-19T12:22:17.486Z
- Cycles completed: 7
- Files analysed: 1852
- Bugs flagged: 0
- Tests generated: 2
- Tests run: 0 (passed 0, failed 0, skipped 0)
- Auto-run tests: disabled
- Model: `Qwen3.6-27B-FP8` @ `http://192.168.191.2:30010/v1`

## Layout

- `docs/<source-path>.md` — per-file summary, design notes, hotspots
- `bugs.md` — rolling log of suspected issues
- `tests/<source-path>.d/` — auto-generated unit tests for uncertainties
- `tests/<source-path>.d/<file>.result.md` — per-test execution result (when auto-run is on)
- `verifications.md` — chronological log of every test run
- `activity.log` — full timestamped activity log (also visible in the "BurstCode Background" output channel)
- `state.json` — internal scheduler state (file hashes, counters)

## Configuration

- Toggle: `burstcode.background.enabled`
- Idle threshold (ms): `burstcode.background.idleThresholdMs`
- Model: `Qwen3.6-27B-FP8` (set via `burstcode.llm.background`)
- Auto-run generated tests: `burstcode.background.runGeneratedTests` (currently off)

## Recent activity

- `2026-05-19T12:22:17.486Z` _event_ — Topic cancelled: picker-filter-live-model-sync
- `2026-05-19T12:22:17.427Z` _running_ — Investigating topic: How does list_picker_providers' live OpenRouter model filtering coordinate with platform adapters' …
- `2026-05-19T12:22:17.426Z` _event_ — Topic cancelled: tui-hyperlink-process-isolation
- `2026-05-19T12:19:17.129Z` _running_ — Investigating 2 topics in parallel — latest: How does list_picker_providers' live OpenRouter model filtering coordinate with…
- `2026-05-19T12:19:17.129Z` _event_ — Topic cancelled: file-tools-safety-state-coordination
- `2026-05-19T12:16:17.125Z` _running_ — Investigating 3 topics in parallel — latest: How does list_picker_providers' live OpenRouter model filtering coordinate with…
- `2026-05-19T12:16:17.124Z` _event_ — Topic cancelled: file-sync-remote-backend-coordination
- `2026-05-19T12:15:17.470Z` _running_ — Investigating 4 topics in parallel — latest: How does list_picker_providers' live OpenRouter model filtering coordinate with…
- `2026-05-19T12:15:17.467Z` _event_ — Topic cancelled: ws-auth-retry-test-alignment
- `2026-05-19T12:15:17.140Z` _running_ — Investigating 5 topics in parallel — latest: How does list_picker_providers' live OpenRouter model filtering coordinate with…
- `2026-05-19T12:15:17.139Z` _event_ — Topic cancelled: shell-noise-filtering-alignment
- `2026-05-19T12:14:17.425Z` _running_ — Investigating 6 topics in parallel — latest: How does list_picker_providers' live OpenRouter model filtering coordinate with…
- `2026-05-19T12:14:17.425Z` _event_ — Topic cancelled: nous-auth-tls-fallback-coordination
- `2026-05-19T12:08:17.591Z` _running_ — Investigating 7 topics in parallel — latest: How does list_picker_providers' live OpenRouter model filtering coordinate with…
- `2026-05-19T12:08:17.591Z` _event_ — Topic cancelled: media-chunking-config-alignment
- `2026-05-19T12:07:17.488Z` _running_ — Investigating 8 topics in parallel — latest: How does list_picker_providers' live OpenRouter model filtering coordinate with…
- `2026-05-19T12:07:17.488Z` _event_ — Topic cancelled: slash-confirm-vs-approval-state-isolation
- `2026-05-19T12:06:17.587Z` _running_ — Investigating 9 topics in parallel — latest: How does list_picker_providers' live OpenRouter model filtering coordinate with…
- `2026-05-19T12:06:17.587Z` _event_ — Topic cancelled: skill-env-passthrough-coordination
- `2026-05-19T12:02:17.447Z` _running_ — Investigating 10 topics in parallel — latest: How does list_picker_providers' live OpenRouter model filtering coordinate with…
- `2026-05-19T12:02:17.447Z` _running_ — Investigating 9 topics in parallel — latest: How does openExternalUrl.ts's child process spawning coordinate with Ink's rend…
- `2026-05-19T12:02:17.447Z` _event_ — Topic cancelled: mcp-provider-lifecycle
- `2026-05-19T12:02:17.365Z` _running_ — Investigating 10 topics in parallel — latest: How does openExternalUrl.ts's child process spawning coordinate with Ink's rend…
- `2026-05-19T12:02:17.364Z` _running_ — Investigating 9 topics in parallel — latest: How do file_tools.py's safety gates and pagination logic coordinate with file_o…
- `2026-05-19T12:02:17.364Z` _event_ — Topic cancelled: mcp-401-dedup-reconnect
