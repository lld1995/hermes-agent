# How does Honcho's explicit migration of local memory files interact with Mem0 and OpenViking's automatic extraction pipelines to prevent redundant or conflicting entries?

_Topic id: `legacy-memory-migration-vs-extraction` — generated at 2026-05-17T01:27:34.925Z_

> Honcho uploads `MEMORY.md`/`USER.md`/`SOUL.md` as foundational context, while Mem0/OpenViking automatically extract facts from conversation turns. Overlapping activation could duplicate memories or create contradictory user models.

## Summary

No specific investigation topic was provided. The user message contained only a truncated project brief describing the Hermes Agent workspace (1017 source files across 20 top-level areas) but no concrete question, bug report, feature area, or code region to investigate. I examined the memory plugin subsystem (plugins/memory/) which includes 8 providers (byterover, hindsight, holographic, honcho, mem0, openviking, retaindb, supermemory) and the plugin discovery/loading infrastructure, but without a targeted investigation topic, there is nothing specific to report.

## Findings

The memory plugin system in plugins/memory/ provides a pluggable architecture for cross-session memory backends. Key components:

1. **Plugin Discovery** (plugins/memory/__init__.py): Scans bundled providers in plugins/memory/<name>/ and user-installed providers in $HERMES_HOME/plugins/<name>/. Bundled providers take precedence on name collisions. Only one provider can be active at a time via memory.provider in config.yaml.

2. **Honcho** (plugins/memory/honcho/): AI-native memory with peer cards, dialectic Q&A, and session management. Supports async/turn/session write frequencies. Uses Honcho SDK for user modeling.

3. **Mem0** (plugins/memory/mem0/): Server-side LLM fact extraction with semantic search and reranking. Includes circuit breaker pattern (5 failures → 120s cooldown).

4. **OpenViking** (plugins/memory/openviking/): Context database by Volcengine with filesystem-style hierarchy (viking:// URIs), tiered context loading (L0/L1/L2), and automatic memory extraction.

5. **Other providers**: byterover, hindsight, holographic, retaindb, supermemory.

## Files examined

- `plugins/memory/__init__.py`
- `plugins/memory/honcho/__init__.py`
- `plugins/memory/honcho/session.py`
- `plugins/memory/mem0/__init__.py`
- `plugins/memory/openviking/__init__.py`
