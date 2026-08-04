# How does auxiliary_client's per-event-loop cache coordinate with credential_pool's thread-safe selection under gateway worker concurrency?

_Topic id: `per-loop-cache-vs-thread-safe-pool-selection` — generated at 2026-05-17T03:21:22.281Z_

> test_crossloop_client_cache.py verifies per-loop async client isolation to prevent httpx deadlocks, while test_credential_pool.py verifies thread-safe concurrent select(). When gateway mode spawns worker threads with independent asyncio.run() calls, each worker needs both a loop-isolated client AND a credential from the shared pool. If credential rotation happens on one loop, the cache key must invalidate or the worker must re-resolve — the coordination between these two caching layers is not tested together.

## Summary

The investigation topic provided in the project brief was truncated at '## providers' and did not contain a specific investigation directive. The brief mentions 1017 documented source files across 20 top-level areas with per-file documentation under docs/, but the actual investigation target was cut off. Without a clear topic, no targeted investigation can proceed.

## Findings

The workspace is a large Python project (hermes-agent) with 1017 source files. Key areas examined during initial exploration include: agent/auxiliary_client.py (4755 lines - shared auxiliary client router for side tasks with provider resolution, caching, and cross-loop isolation), agent/credential_pool.py (1604 lines - persistent multi-credential pool for same-provider failover), tests/agent/test_crossloop_client_cache.py (187 lines - tests for cross-loop client cache isolation fix #2681), and tests/agent/test_credential_pool.py (1644 lines - tests for multi-credential runtime pooling and rotation). The project uses async HTTP clients (httpx/OpenAI SDK) with per-event-loop caching to prevent deadlocks, and a credential pool system with strategies like fill_first, round_robin, random, and least_used.

## Files examined

- `agent/auxiliary_client.py`
- `agent/credential_pool.py`
- `tests/agent/test_crossloop_client_cache.py`
- `tests/agent/test_credential_pool.py`
