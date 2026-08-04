# How does skills_tool.py's bump_view/bump_use telemetry coordinate with the curator's stale/archive transition logic to prevent active skills from being pruned?

_Topic id: `skill-usage-bump-curator-stale-sync` — generated at 2026-05-15T23:39:21.190Z_

> The skill_view wrapper bumps both view and use counts via tools.skill_usage. The curator's stale detection keys off last_used_at timestamps. If telemetry writes are delayed, lost, or not persisted atomically, actively used skills could be incorrectly archived or have their references rewritten.

## Summary

Investigated how tools/skills_tool.py's bump_view/bump_use telemetry coordinates with agent/curator.py's stale/archive transition logic. The pipeline is: (1) _skill_view_with_bump in skills_tool.py calls both bump_view() and bump_use() on successful skill_view; (2) these update last_viewed_at/last_used_at in the .usage.json sidecar via _mutate(); (3) agent_created_report() derives last_activity_at as the max of last_used_at, last_viewed_at, last_patched_at; (4) apply_automatic_transitions() in curator.py uses last_activity_at (falling back to created_at) as the anchor to compare against stale_cutoff and archive_cutoff thresholds. The coordination is clean and intentional — every skill_view bumps both view and use counters so that curator's stale timer (which keys off last_used_at via latest_activity_at) is always refreshed when a skill is loaded.

## Findings

## Telemetry-to-Curator Coordination

### Telemetry Emission (tools/skills_tool.py :1534-1556)
The registered `skill_view` tool is wrapped by `_skill_view_with_bump`. On a successful view (parsed JSON with `success: true`), it calls both `bump_view(resolved_name)` and `bump_use(resolved_name)`. The design rationale (line 1550-1552) is that a skill_view is the agent actively loading a skill to act on it, so it counts as use, not just a browse.

### Counter Mutation (tools/skill_usage.py :405-419)
- `bump_view(skill_name)`: increments `view_count`, sets `last_viewed_at` to UTC now
- `bump_use(skill_name)`: increments `use_count`, sets `last_used_at` to UTC now
- Both delegate to `_mutate()` which: (a) skips bundled/hub skills, (b) acquires a file lock, (c) load-modify-save the .usage.json sidecar atomically

### Activity Derivation (tools/skill_usage.py :120-137, :592-609)
- `latest_activity_at(record)` returns the newest of `last_used_at`, `last_viewed_at`, `last_patched_at` (creation time excluded)
- `agent_created_report()` enriches each row with `last_activity_at` = `latest_activity_at(row)` and `activity_count`

### Curator Transitions (agent/curator.py :256-296)
`apply_automatic_transitions()` iterates `agent_created_report()` rows and for each unpinned skill:
1. Parses `last_activity_at`; falls back to `created_at` if never active
2. Compares anchor against `stale_cutoff` (now - stale_after_days, default 30) and `archive_cutoff` (now - archive_after_days, default 90)
3. Transitions: active→stale if anchor <= stale_cutoff; active/stale→archived if anchor <= archive_cutoff; stale→active if anchor > stale_cutoff

### Key Design Decisions
- Both bump_view and bump_use fire on skill_view, ensuring last_used_at is always refreshed alongside last_viewed_at
- The curator's `latest_activity_at` considers all three activity types (use, view, patch), so any interaction resets the stale timer
- Pinned skills bypass all auto-transitions
- Bundled/hub skills are excluded from telemetry entirely via `_mutate()`'s provenance check
- First-run curator seeds last_run_at and defers by one full interval (default 7 days)

## Files examined

- `tools/skills_tool.py`
- `tools/skill_usage.py`
- `agent/curator.py`
- `tests/tools/test_skill_usage.py`

## Uncertainties / generated tests

- **Whether bump_view + bump_use double-counting on skill_view is intentional or a subtle over-counting** — Every successful skill_view calls both bump_view() and bump_use(), incrementing both view_count and use_count. The comment at skills_tool.py:1550-1552 justifies this as intentional ('counts as use, not just a browse/view'). However, if a skill is viewed many times but never actually invoked in a task, use_count will be high. The curator's latest_activity_at uses the max of all timestamps, so this doesn't affect stale/archive timing — but it could mislead human readers of the usage report. _(python/hermes-agent)_
