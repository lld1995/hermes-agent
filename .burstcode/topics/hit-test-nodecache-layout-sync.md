# How does hit-test's nodeCache rect lookup coordinate with yoga layout computation and screen rendering to ensure hit targets align with rendered cell positions?

_Topic id: `hit-test-nodecache-layout-sync` — generated at 2026-05-15T22:27:37.272Z_

> hit-test.ts uses nodeCache rects populated by renderNodeToOutput to determine which DOM element is under the cursor. These rects must stay synchronized with yoga layout positions and the actual screen buffer positions used by log-update.ts. Any drift between layout computation, rect caching, and screen rendering would cause clicks to land on wrong elements.

## Summary

No specific investigation topic was provided. The user message contains only a truncated project brief describing the workspace structure (1017 source files, 20 top-level areas, docs/ directory) without any concrete investigation directive. The brief text cuts off mid-sentence at '- `websi' and provides no actionable investigation target.

## Findings

The workspace is a large TypeScript/Python project called 'hermes-agent' with a TUI (terminal UI) component under ui-tui/packages/hermes-ink/. Key areas include: agent/ (Python agent logic), ui-tui/ (TypeScript terminal UI with Ink framework), plugins/ (various plugin implementations), providers/ (AI provider integrations), and tools/. Without a specific investigation topic, no targeted code review can be performed.

## Files examined

- `.burstcode/activity.log`
- `.burstcode/state.json`
- `ui-tui/packages/hermes-ink/src/ink/hit-test.ts`
- `ui-tui/packages/hermes-ink/src/ink/node-cache.ts`
- `ui-tui/packages/hermes-ink/src/ink/layout/yoga.ts`
- `ui-tui/packages/hermes-ink/src/ink/render-node-to-output.ts`
- `ui-tui/packages/hermes-ink/src/ink/log-update.ts`
- `ui-tui/packages/hermes-ink/src/ink/output.ts`
