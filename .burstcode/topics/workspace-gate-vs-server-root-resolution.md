# How do workspace.py's git worktree gates and servers.py's per-language root resolvers coordinate in monorepos or nested projects?

_Topic id: `workspace-gate-vs-server-root-resolution` — generated at 2026-05-17T14:20:52.252Z_

> `workspace.py` enforces a hard git boundary, while `servers.py` resolves language-specific roots that may differ. Misalignment could cause servers to spawn with wrong CWDs, miss config files, or incorrectly gate out valid subprojects.

## Summary

The investigation topic was truncated in the user's message. Only the project brief context was provided, ending mid-word at 'websi...'. No specific investigation question or area to examine was included. I read all three files referenced in the truncated context (agent/lsp/workspace.py, agent/lsp/servers.py, agent/lsp/manager.py) to be prepared, but without a clear topic I cannot proceed with a meaningful investigation.

## Findings

The three LSP-related files form a cohesive module for language server protocol integration:

1. **agent/lsp/workspace.py** (224 lines) — Handles workspace/project-root resolution. Key functions: `find_git_worktree()` walks up from a path looking for `.git`, `nearest_root()` walks up looking for marker files (e.g., `pyproject.toml`, `Cargo.toml`), `resolve_workspace_for_file()` determines if a file is inside a git worktree (the workspace gate), and `clear_cache()` resets the workspace cache.

2. **agent/lsp/servers.py** (1041 lines) — Server registry with per-language LSP server definitions. Contains `ServerDef` dataclass (server_id, extensions, resolve_root, build_spawn), `SpawnSpec` (command, workspace_root, cwd, env, initialization_options), `ServerContext` (user overrides), spawn builders for 26+ language servers (pyright, typescript, gopls, rust-analyzer, clangd, etc.), root resolvers per language, and the `SERVERS` registry list.

3. **agent/lsp/manager.py** (608 lines) — Service-level orchestration. `LSPService` manages a single asyncio event loop in a background thread, one client per (server_id, workspace_root) key, a broken-set for failed servers, and a delta-baseline map for showing only new diagnostics after edits. Key methods: `enabled_for()`, `snapshot_baseline()`, `get_diagnostics_sync()`, `_get_or_spawn()`, `shutdown()`.

## Files examined

- `agent/lsp/workspace.py`
- `agent/lsp/servers.py`
- `agent/lsp/manager.py`
