# How do synchronous terminal calls in agentic_opd_env.py interact with the async event loop compared to terminalbench2_env.py's executor pattern?

_Topic id: `event-loop-blocking-terminal-exec` — generated at 2026-05-15T08:39:20.638Z_

> agentic_opd_env.py calls ctx.terminal() directly inside the async compute_reward method, while terminalbench2_env.py explicitly wraps _run_tests in loop.run_in_executor to prevent blocking. This inconsistency could cause event loop stalls during OPD training if terminal commands hang, unlike the TB2 eval which guards against it.

## Summary

No investigation topic was provided. The topic field is empty, so there is nothing substantive to examine.
