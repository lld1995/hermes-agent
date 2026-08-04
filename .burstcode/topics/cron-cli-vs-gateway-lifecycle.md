# How does cron.py's CLI-only job management coordinate with the gateway process lifecycle for reliable execution?

_Topic id: `cron-cli-vs-gateway-lifecycle` — generated at 2026-05-15T10:27:24.200Z_

> cron.py is marked cli_only in commands.py but explicitly checks find_gateway_pids() to warn if automatic firing is unavailable. Investigating how job state persists, how the gateway scheduler consumes these jobs, and what happens during gateway restarts ensures cron reliability.

## Summary

Investigation into how cron.py's CLI-only job management coordinates with the gateway process lifecycle. The CLI (hermes_cli/cron.py) handles job CRUD operations while the gateway scheduler (cron/scheduler.py) consumes these jobs for automatic execution. Job state persists in JSON files under ~/.hermes/cron/, and the CLI checks gateway availability via find_gateway_pids() to warn users when automatic firing is unavailable.

## Findings

The cron system has two main components: (1) CLI management via hermes_cli/cron.py which is marked cli_only in commands.py, handling job creation, editing, scheduling, and status reporting; and (2) Gateway execution via cron/scheduler.py which polls and executes due jobs. The CLI checks gateway availability using find_gateway_pids() to warn users if automatic firing is unavailable. Job state persists in JSON files under ~/.hermes/cron/jobs/ with atomic writes for crash safety. The gateway scheduler runs as a background task that periodically checks for due jobs and executes them, with support for both LLM-driven and pure-script (no_agent) modes. During gateway restarts, job state is preserved on disk, and the scheduler resumes checking for due jobs after restart. The system uses file-based locking to prevent concurrent execution issues.

## Files examined

- `hermes_cli/cron.py`
- `hermes_cli/commands.py`
- `cron/jobs.py`
- `cron/scheduler.py`
- `cron/__init__.py`

## Uncertainties / generated tests

- **Gateway restart behavior and job state recovery** — Need to verify how the gateway scheduler handles restarts - whether it properly resumes job execution and if there are any race conditions during restart _(python/asyncio)_
