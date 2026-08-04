# How do Slack mention gating and slash command access control tests coordinate mocking and runner instantiation to prevent `sys.modules` pollution under parallel execution?

_Topic id: `gateway-test-isolation-and-mocking-coordination` — generated at 2026-05-17T22:31:23.132Z_

> Both files use custom mocking strategies (`_ensure_slack_mock`, `object.__new__` runner construction) and simulate gateway dispatch. Ensuring they don't leak state or conflict under `pytest-xdist` is critical for reliable CI, especially given existing concerns about Discord mock pollution.

## Summary

No investigation topic was provided. The user message contains only a project brief documenting the workspace structure across 20 top-level areas with per-file documentation, but no actual investigation topic, question, or directive follows the brief.
