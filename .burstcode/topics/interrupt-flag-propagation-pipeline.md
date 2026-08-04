# How does the is_interrupted flag propagate from GatewayRunner to AIAgent and tool_progress_callback to guarantee immediate UI suppression?

_Topic id: `interrupt-flag-propagation-pipeline` — generated at 2026-05-17T05:42:22.024Z_

> The interrupt tests verify that `is_interrupted` stops progress bubbles. Tracing this flag through `run_agent.py`, `gateway/run.py`, and the callback queue reveals potential async delays or missed checks that could leak stale UI updates or bypass drain loop guards.

## Summary

No investigation topic was provided. The user message contains only the project brief (workspace context documentation describing 1017 source files across 20 top-level areas) but no specific investigation directive, question, bug report, or feature request to act upon.

## Findings

The workspace is a large Python project (hermes-agent) with an AI agent runner, gateway system, CLI tools, plugin architecture, and various integrations. Without a concrete investigation topic, there is nothing to examine.
