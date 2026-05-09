# ---------- CN mirror configuration (override with --build-arg to disable) ----------
# Registry mirrors (ghcr.io not reachable in CN; docker.m.daocloud.io preserves
# upstream digests so sha256 pinning still validates integrity).
ARG GHCR_MIRROR=ghcr.m.daocloud.io
ARG DOCKERHUB_MIRROR=docker.m.daocloud.io
# Package mirrors
ARG APT_MIRROR=mirrors.aliyun.com
ARG NPM_REGISTRY=https://registry.npmmirror.com
ARG PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
# pip / uv go upstream pypi.org via PIP_PROXY (CN aliyun mirror's torch /
# onnxruntime / ctranslate2 wheels were observed at <1MB/s in this network;
# upstream pypi behind the local HTTP proxy is faster and more reliable).
# Override PIP_PROXY with --build-arg if no proxy is available.
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_TRUSTED_HOST=pypi.org
ARG PIP_PROXY=""

FROM ${GHCR_MIRROR}/astral-sh/uv:0.11.6-python3.13-trixie@sha256:b3c543b6c4f23a5f2df22866bd7857e5d304b67a564f4feab6ac22044dde719b AS uv_source
FROM ${DOCKERHUB_MIRROR}/library/debian:13.4

# Re-declare ARGs that need to be visible in this stage (ARGs before FROM are
# only available to the FROM line itself).
ARG APT_MIRROR
ARG NPM_REGISTRY
ARG PLAYWRIGHT_DOWNLOAD_HOST
ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST
ARG PIP_PROXY

# Disable Python stdout buffering to ensure logs are printed immediately
ENV PYTHONUNBUFFERED=1

# Store Playwright browsers outside the volume mount so the build-time
# install survives the /opt/data volume overlay at runtime.
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/hermes/.playwright

# Shared uv cache directory for both the root-stage `uv sync` and the
# hermes-stage `uv pip install -e` so they hit the same BuildKit cache
# mount and never re-download wheels across rebuilds (#cache_mount).
ENV UV_CACHE_DIR=/build-cache/uv

# Swap Debian sources to the CN mirror (trixie uses deb822-style sources).
# If APT_MIRROR is set to the upstream deb.debian.org this is a no-op.
RUN set -eux; \
    if [ "${APT_MIRROR}" != "deb.debian.org" ] && [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i "s|deb.debian.org|${APT_MIRROR}|g; s|security.debian.org|${APT_MIRROR}|g" \
            /etc/apt/sources.list.d/debian.sources; \
    fi

# Install system dependencies in one layer, clear APT cache
# tini reaps orphaned zombie processes (MCP stdio subprocesses, git, bun, etc.)
# that would otherwise accumulate when hermes runs as PID 1. See #15012.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential curl nodejs npm python3 ripgrep ffmpeg gcc python3-dev libffi-dev procps git gosu openssh-client docker-cli tini && \
    rm -rf /var/lib/apt/lists/*

# Non-root user for runtime; UID can be overridden via HERMES_UID at runtime
RUN useradd -u 10000 -m -d /opt/data hermes

COPY --from=uv_source /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/
RUN chmod 0755 /usr/local/bin/uv /usr/local/bin/uvx

WORKDIR /opt/hermes

# Configure npm + pip globally so any `npm install` / `pip install` picks up
# the CN mirrors automatically (also inherited by `npx` and uv's pip).
RUN npm config set registry "${NPM_REGISTRY}" && \
    npm config set fetch-timeout 600000 && \
    npm config set fetch-retries 5 && \
    mkdir -p /etc/pip && \
    printf '[global]\nindex-url = %s\ntrusted-host = %s\ntimeout = 120\n' \
        "${PIP_INDEX_URL}" "${PIP_TRUSTED_HOST}" > /etc/pip.conf

# ---------- Layer-cached dependency install ----------
# Copy only package manifests first so npm install + Playwright are cached
# unless the lockfiles themselves change.
#
# ui-tui/packages/hermes-ink/ is copied IN FULL (not just its manifests)
# because it is referenced as a `file:` workspace dependency from
# ui-tui/package.json.  Copying the tree up front lets npm resolve the
# workspace to real content instead of stopping at a bare package.json.
COPY package.json package-lock.json ./
COPY web/package.json web/package-lock.json web/
COPY ui-tui/package.json ui-tui/package-lock.json ui-tui/
COPY ui-tui/packages/hermes-ink/ ui-tui/packages/hermes-ink/

# `npm_config_install_links=false` forces npm to install `file:` deps as
# symlinks (the npm 10+ default) even on Debian's older bundled npm 9.x,
# which defaults to `install-links=true` and installs file deps as *copies*.
# The host-side package-lock.json is generated with a newer npm that uses
# symlinks, so an install-as-copy produces a hidden node_modules/.package-lock.json
# that permanently disagrees with the root lock on the @hermes/ink entry.
# That disagreement trips the TUI launcher's `_tui_need_npm_install()`
# check on every startup and triggers a runtime `npm install` that then
# fails with EACCES (node_modules/ is root-owned from build time).
ENV npm_config_install_links=false

# Optional proxy for playwright only (npmmirror does not mirror the newer
# `builds/cft/` path used by chrome-headless-shell, so we fall back to upstream
# playwright.azureedge.net via the configured proxy when PLAYWRIGHT_PROXY is set).
ARG PLAYWRIGHT_PROXY=""

# npm install uses npmmirror (fast in CN). Skip playwright's postinstall browser
# download here; we do it in a separate RUN below so we can scope the proxy.
# `--mount=type=cache,target=/root/.npm` persists the npm tarball cache across
# rebuilds so a busted upstream layer doesn't re-download the npm registry.
RUN --mount=type=cache,target=/root/.npm,sharing=locked \
    export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 && \
    npm install --prefer-offline --no-audit && \
    (cd web && npm install --prefer-offline --no-audit) && \
    (cd ui-tui && npm install --prefer-offline --no-audit)

# Playwright chromium-headless-shell falls back to upstream via PLAYWRIGHT_PROXY
# (npmmirror's mirror does not cover the newer builds/cft/ paths). Note: legacy
# docker builder exports ARGs as env vars, so we explicitly unset the ARG-leaked
# PLAYWRIGHT_DOWNLOAD_HOST before invoking playwright.
RUN unset PLAYWRIGHT_DOWNLOAD_HOST && \
    HTTPS_PROXY="${PLAYWRIGHT_PROXY}" HTTP_PROXY="${PLAYWRIGHT_PROXY}" \
    npx playwright install --with-deps chromium --only-shell && \
    npm cache clean --force

# ---------- Layer-cached Python dependency install ----------
# Copy only pyproject.toml + uv.lock so the Python dep resolve + wheel
# download + native-extension compile layer is cached unless those inputs
# change.  Before this split the Python install sat after `COPY . .`, so
# every source-only commit re-did ~4-5 min of dep work on cold builds.
#
# README.md is referenced by pyproject.toml's `readme =` field, but it's
# excluded from the build context by .dockerignore's `*.md`.  uv's build
# frontend stats the readme path during dep resolution, so we `touch` an
# empty placeholder — the real README is restored by `COPY . .` below.
#
# `uv sync --frozen --no-install-project --extra all` installs only the
# deps reachable through the composite `[all]` extra (handpicked set
# intended for the production image).  We do NOT use `--all-extras`:
# that would pull in `[rl]` (atroposlib + tinker + torch + wandb from
# git), `[yc-bench]` (another git dep), and `[termux-all]` (Android
# redundancy), none of which belong in the published container.
#
# The editable link is created after the source copy below.
COPY pyproject.toml uv.lock ./
RUN touch ./README.md
# `--mount=type=cache,target=${UV_CACHE_DIR}` persists uv's wheel cache across
# rebuilds so a busted upstream layer doesn't re-download every wheel from
# pypi.  uid=10000/gid=10000 so the later hermes-user `uv pip install` step
# can share the same cache without permission issues (root can still write).
RUN --mount=type=cache,target=/build-cache/uv,uid=10000,gid=10000,sharing=locked \
    HTTPS_PROXY="${PIP_PROXY}" HTTP_PROXY="${PIP_PROXY}" \
    uv sync --frozen --no-install-project --extra all && \
    chown -R 10000:10000 /build-cache/uv

# ---------- Source code ----------
# .dockerignore excludes node_modules, so the installs above survive.
COPY --chown=hermes:hermes . .

# Build browser dashboard and terminal UI assets.
RUN cd web && npm run build && \
    cd ../ui-tui && npm run build

# ---------- Permissions ----------
# Make install dir world-readable so any HERMES_UID can read it at runtime.
# The venv needs to be traversable too.
# node_modules trees additionally need to be writable by the hermes user
# so the runtime `npm install` triggered by _tui_need_npm_install() in
# hermes_cli/main.py succeeds (see #18800). /opt/hermes/web is build-time
# only (HERMES_WEB_DIST points at hermes_cli/web_dist) and is intentionally
# not chowned here.
USER root
RUN chmod -R a+rX /opt/hermes && \
    chown -R hermes:hermes /opt/hermes/ui-tui /opt/hermes/node_modules /opt/hermes/.venv
# Start as root so the entrypoint can usermod/groupmod + gosu.
# If HERMES_UID is unset, the entrypoint drops to the default hermes user (10000).

# ---------- Link hermes-agent itself (editable) ----------
RUN chown hermes:hermes /opt/hermes
USER hermes
ENV UV_INDEX_URL=${PIP_INDEX_URL}
# Deps are already installed in the cached layer above (`uv sync ... --extra all`),
# so this is just a fast (~1s) egg-link creation with no resolution or downloads.
# Cache mount is still attached so any incidental sdist build artefacts hit the
# shared cache rather than rebuilding from scratch.
RUN --mount=type=cache,target=/build-cache/uv,uid=10000,gid=10000,sharing=locked \
    uv pip install --no-config --no-deps -e "."

# ---------- Runtime ----------
ENV HERMES_WEB_DIST=/opt/hermes/hermes_cli/web_dist
ENV HERMES_HOME=/opt/data
ENV PATH="/opt/data/.local/bin:${PATH}"
VOLUME [ "/opt/data" ]
ENTRYPOINT [ "/usr/bin/tini", "-g", "--", "/opt/hermes/docker/entrypoint.sh" ]
