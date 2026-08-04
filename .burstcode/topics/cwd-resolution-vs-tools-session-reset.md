# How does `load_cli_config`'s CWD resolution and `TERMINAL_CWD` export interact with `/tools disable/enable`'s session reset and `new_session` initialization?

_Topic id: `cwd-resolution-vs-tools-session-reset` — generated at 2026-05-17T20:50:34.113Z_

> `load_cli_config` sets `TERMINAL_CWD` based on backend type and gateway flags, while `/tools disable/enable` triggers `new_session`. If CWD resolution isn't re-evaluated or correctly propagated during session reset, the new session might inherit a stale, placeholder, or gateway-clobbered working directory.

## Summary

No investigation topic was provided. The user message contains only the project brief documenting 1017 source files across 20 top-level areas of the Hermes Agent codebase, but no specific question or area to investigate.
