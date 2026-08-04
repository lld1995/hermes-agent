# How do DISCORD_ALLOW_BOTS and DISCORD_ALLOWED_ROLES policies coordinate between the adapter's on_message gate and GatewayRunner._is_user_authorized?

_Topic id: `bot-auth-gate-coordination` — generated at 2026-05-19T06:41:00.000Z_

> The adapter's initial filter and the gateway's authorization layer both evaluate bot policies. Misalignment could cause double-rejection of valid bot messages or security bypasses if one gate is skipped.

## Summary

No investigation topic was provided. The user message contained only the project brief (workspace documentation) without specifying what to investigate. Please provide a concrete investigation topic such as a specific module, feature, potential bug area, or architectural question to explore.
