# How do provider-specific error classifications (Bedrock context overflow/throttling vs Codex incomplete/leaked tool calls) feed into the agent's retry and context compression logic?

_Topic id: `provider-error-retry-coordination` — generated at 2026-05-14T22:58:50.002Z_

> Each adapter implements distinct error detection and recovery strategies. The agent loop must interpret these signals correctly to trigger retries, backoffs, or context compression without infinite loops.

## Summary

No specific investigation topic was provided in the prompt. The project brief was truncated and only contained a general workspace overview describing 1004 source files across 20 top-level areas of the Hermes Agent project (a self-improving AI agent by Nous Research). Without a concrete investigation topic, there is nothing actionable to investigate.

## Findings

The Hermes Agent workspace is a large, well-documented Python project (v0.13.0) with 1004 source files. Key areas include: agent/ (core agent loop, adapters, error classification), tools/ (terminal, browser, file tools), gateway/ (messaging integrations), acp_adapter/ (agent communication protocol), skills/ and sm-skills/ (skill system), hermes_cli/ (CLI interface), and tests/. The project supports multiple LLM providers (OpenAI, Anthropic, Bedrock, OpenRouter, etc.) and messaging platforms (Telegram, Discord, Slack, WhatsApp, Signal). No investigation topic was specified.

## Files examined

- `README.md`
- `pyproject.toml`
- `run_agent.py`
- `agent/error_classifier.py`
- `agent/bedrock_adapter.py`
- `agent/codex_responses_adapter.py`
