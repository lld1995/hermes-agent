# How does logs.py's component filtering rely on hermes_logging.COMPONENT_PREFIXES, and does it handle dynamically registered loggers or third-party library logs gracefully?

_Topic id: `logs-component-prefix-sync` — generated at 2026-05-15T10:48:01.455Z_

> Component filtering maps high-level names to logger prefixes. If new modules use unmapped logger names or third-party libs inject logs, the filter may silently drop relevant lines or fail validation.
