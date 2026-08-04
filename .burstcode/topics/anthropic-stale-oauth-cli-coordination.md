# How do the Anthropic model flow and OAuth setup flow coordinate stale token detection and credential clearing across shared adapter functions?

_Topic id: `anthropic-stale-oauth-cli-coordination` — generated at 2026-05-17T22:53:40.894Z_

> Both test files mock `agent.anthropic_adapter` methods (`read_claude_code_credentials`, `is_claude_code_token_valid`, `_is_oauth_token`) and interact with `hermes_cli.config`. Ensuring these flows don't conflict or leave stale tokens in `.env` is critical for user experience and security.

## Summary

No investigation topic was provided. The topic field in the prompt was empty, so there is no specific area of the codebase to investigate.

## Findings

The workspace is a large Python project (hermes-agent) with 1017+ documented source files across 20 top-level areas including agent adapters, CLI tools, gateway platforms, plugins, skills, and tests. Without a concrete investigation topic, no targeted code review or bug hunting can be performed.
