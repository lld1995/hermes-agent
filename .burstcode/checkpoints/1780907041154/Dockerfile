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
# Node 22 LTS source stage. Debian trixie's bundled nodejs is pinned to 20.x
# which reached EOL in April 2026 — we copy node + npm + corepack from the
# upstream node:22 image instead so we can stay on a supported LTS without
# waiting for Debian 14 (forky, ~mid-2027).  Bookworm-based slim image used
# so the produced binary links against glibc 2.36, which runs cleanly on
# our Debian 13 (trixie, glibc 2.41) runtime.  Bumping to a new Node major
# is a one-line ARG change; see #4977. Pulled via DOCKERHUB_MIRROR so the
# node base image is reachable in CN (digest pin preserves integrity).
FROM ${DOCKERHUB_MIRROR}/library/node:22-bookworm-slim@sha256:7af03b14a13c8cdd38e45058fd957bf00a72bbe17feac43b1c15a689c029c732 AS node_source
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

# Install system dependencies in one layer, clear APT cache.
# tini was previously PID 1 to reap orphaned zombie processes (MCP stdio
# subprocesses, git, bun, etc.) that would otherwise accumulate when hermes
# ran as PID 1. See #15012. Phase 2 of the s6-overlay supervision plan
# replaces tini with s6-overlay's /init (PID 1 = s6-svscan), which reaps
# zombies non-blockingly on SIGCHLD and additionally supervises the main
# hermes process, the dashboard, and per-profile gateways.
# node/npm now come from the node_source stage (see COPY below), so they are
# intentionally NOT installed via apt here. build-essential is kept so native
# Python extensions still compile during `uv sync`. xz-utils is required to
# unpack the s6-overlay tarballs.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential ca-certificates curl iputils-ping python3 python-is-python3 ripgrep ffmpeg gcc python3-dev libffi-dev procps git openssh-client docker-cli xz-utils && \
    rm -rf /var/lib/apt/lists/*

# ---------- s6-overlay install ----------
# s6-overlay provides supervision for the main hermes process, the dashboard,
# and per-profile gateways. /init becomes PID 1 below — see ENTRYPOINT.
#
# Multi-arch: BuildKit auto-populates TARGETARCH (amd64 / arm64). s6-overlay
# uses tarball names keyed on the kernel arch string (x86_64 / aarch64), so
# we map between them inline. The noarch + symlinks tarballs are
# architecture-independent and reused as-is.
#
# We use `curl` instead of `ADD` for the per-arch tarball because `ADD`
# evaluates its URL at parse time, before any ARG / TARGETARCH substitution
# — splitting one URL per arch into two ADDs would download both on every
# build and leave dead bytes in the cache. A single curl + arch-keyed URL
# is simpler and cache-friendlier.
#
# Supply-chain integrity: every tarball is checksum-verified against the
# upstream-published SHA256. To bump S6_OVERLAY_VERSION, fetch the four
# `.sha256` files from the corresponding release and update the ARGs. The
# checksum lookup happens during build, so a compromised release artifact
# fails the build loudly instead of silently producing a tampered image.
ARG TARGETARCH
ARG S6_OVERLAY_VERSION=3.2.3.0
ARG S6_OVERLAY_NOARCH_SHA256=b720f9d9340efc8bb07528b9743813c836e4b02f8693d90241f047998b4c53cf
ARG S6_OVERLAY_X86_64_SHA256=a93f02882c6ed46b21e7adb5c0add86154f01236c93cd82c7d682722e8840563
ARG S6_OVERLAY_AARCH64_SHA256=0952056ff913482163cc30e35b2e944b507ba1025d78f5becbb89367bf344581
ARG S6_OVERLAY_SYMLINKS_SHA256=a60dc5235de3ecbcf874b9c1f18d73263ab99b289b9329aa950e8729c4789f0e
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp/
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-symlinks-noarch.tar.xz /tmp/
RUN set -eu; \
    case "${TARGETARCH:-amd64}" in \
        amd64) s6_arch="x86_64"; s6_arch_sha="${S6_OVERLAY_X86_64_SHA256}" ;; \
        arm64) s6_arch="aarch64"; s6_arch_sha="${S6_OVERLAY_AARCH64_SHA256}" ;; \
        *) echo "Unsupported TARGETARCH=${TARGETARCH} for s6-overlay" >&2; exit 1 ;; \
    esac; \
    curl -fsSL --retry 3 -o /tmp/s6-overlay-arch.tar.xz \
        "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${s6_arch}.tar.xz"; \
    { \
        printf '%s  %s\n' "${S6_OVERLAY_NOARCH_SHA256}" /tmp/s6-overlay-noarch.tar.xz; \
        printf '%s  %s\n' "${s6_arch_sha}" /tmp/s6-overlay-arch.tar.xz; \
        printf '%s  %s\n' "${S6_OVERLAY_SYMLINKS_SHA256}" /tmp/s6-overlay-symlinks-noarch.tar.xz; \
    } > /tmp/s6-overlay.sha256; \
    sha256sum -c /tmp/s6-overlay.sha256; \
    tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz; \
    tar -C / -Jxpf /tmp/s6-overlay-arch.tar.xz; \
    tar -C / -Jxpf /tmp/s6-overlay-symlinks-noarch.tar.xz; \
    rm /tmp/s6-overlay-*.tar.xz /tmp/s6-overlay.sha256; \
    # #34192: backward-compat shim for orchestration templates that still\
    # reference the legacy /usr/bin/tini entrypoint (e.g. Hostinger's\
    # 'Hermes WebUI' catalog). The image has moved to s6-overlay /init\
    # as PID 1 (see ENTRYPOINT below + the migration comment at the top\
    # of this file), but external wrappers pinned to /usr/bin/tini will\
    # crash with 'tini: No such file or directory' on startup. The shim\
    # symlinks /usr/bin/tini -> /init so legacy wrappers exec the right\
    # PID-1 reaper without behavior change for users on the current\
    # ENTRYPOINT. Safe to drop once the affected catalogs are updated.\
    ln -sf /init /usr/bin/tini

# Non-root user for runtime; UID can be overridden via HERMES_UID at runtime
RUN useradd -u 10000 -m -d /opt/data hermes

COPY --chmod=0755 --from=uv_source /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

# Node 22 LTS: copy the node binary plus the bundled npm + corepack JS
# installs from the upstream image.  npm and npx are recreated as symlinks
# because they're symlinks in the source image (and need to live on PATH).
# See node_source stage at the top of the file for the version-bump
# rationale (#4977).
COPY --chmod=0755 --from=node_source /usr/local/bin/node /usr/local/bin/
COPY --from=node_source /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
COPY --from=node_source /usr/local/lib/node_modules/corepack /usr/local/lib/node_modules/corepack
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && \
    ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx && \
    ln -sf /usr/local/lib/node_modules/corepack/dist/corepack.js /usr/local/bin/corepack

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
# symlinks instead of copies.  This is the default since npm 10+, which is
# what the image ships now (via the node:22 source stage).  We set it
# explicitly anyway as defense-in-depth: the previous Debian-bundled npm
# 9.x defaulted to install-as-copy, which produced a hidden
# node_modules/.package-lock.json that permanently disagreed with the root
# lock on the @hermes/ink entry, tripped the TUI launcher's
# `_tui_need_npm_install()` check on every startup, and triggered a
# runtime `npm install` that then failed with EACCES.  Keeping the env
# guards against a future regression if the source npm version changes.
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
# `uv sync --frozen --no-install-project --extra all --extra messaging`
# installs the deps reachable through the composite `[all]` extra
# (handpicked set intended for the production image), plus gateway
# messaging adapters that should work in the published image without a
# first-boot lazy install.  We do NOT use `--all-extras`:
# that would pull in `[rl]` (atroposlib + tinker + torch + wandb from
# git), `[yc-bench]` (another git dep), and `[termux-all]` (Android
# redundancy), none of which belong in the published container.
#
# Provider packages (anthropic, bedrock, azure-identity) are included
# so Docker users can use these providers without requiring runtime
# lazy-install access to PyPI (often blocked in containerized envs).
#
# The editable link is created after the source copy below.
COPY pyproject.toml uv.lock ./
RUN touch ./README.md
# `--mount=type=cache,target=${UV_CACHE_DIR}` persists uv's wheel cache across
# rebuilds so a busted upstream layer doesn't re-download every wheel from
# pypi.  uid=10000/gid=10000 so the later hermes-user `uv pip install` step
# can share the same cache without permission issues (root can still write).
# Extras list tracks upstream main: [all] (production handpicked set) plus
# messaging adapters and the anthropic/bedrock/azure-identity provider packages
# so Docker users get them without runtime lazy-install access to PyPI.
RUN --mount=type=cache,target=/build-cache/uv,uid=10000,gid=10000,sharing=locked \
    HTTPS_PROXY="${PIP_PROXY}" HTTP_PROXY="${PIP_PROXY}" \
    uv sync --frozen --no-install-project --extra all --extra messaging --extra anthropic --extra bedrock --extra azure-identity && \
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
# The .venv MUST remain hermes-writable so lazy_deps.py can install
# remaining optional platform packages and future pin bumps at first use.
# Without this, `uv pip install` fails with EACCES and adapters silently
# fail to load.  See tools/lazy_deps.py.
USER root
RUN chmod -R a+rX /opt/hermes && \
    chown -R hermes:hermes /opt/hermes/.venv /opt/hermes/ui-tui /opt/hermes/node_modules
# Start as root so the s6-overlay stage2 hook can usermod/groupmod and chown
# the data volume. Each supervised service then drops to the hermes user via
# `s6-setuidgid hermes` in its run script. If HERMES_UID is unset, services
# run as the default hermes user (UID 10000).

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

# ---------- Bake build-time git revision ----------
# .dockerignore excludes .git, so `git rev-parse HEAD` from inside the
# container always returns nothing — meaning `hermes dump` reports
# "(unknown)" and the startup banner drops its `· upstream <sha>` suffix.
# That makes support triage from container bug reports impossible:
# we can't tell which commit the user is actually running.
#
# Fix: write the commit SHA passed via the HERMES_GIT_SHA build-arg to
# /opt/hermes/.hermes_build_sha at build time, and have
# hermes_cli/build_info.py read it at runtime.  Both `hermes dump` and
# banner.get_git_banner_state() try the baked SHA first, then fall back
# to live `git rev-parse` for source installs (unchanged behaviour).
#
# The arg is optional — local `docker build` without --build-arg simply
# omits the file, and the runtime falls back to live-git lookup.  CI
# (.github/workflows/docker-publish.yml) passes ${{ github.sha }} so
# every published image has it.
ARG HERMES_GIT_SHA=
RUN if [ -n "${HERMES_GIT_SHA}" ]; then \
        printf '%s\n' "${HERMES_GIT_SHA}" > /opt/hermes/.hermes_build_sha && \
        chown hermes:hermes /opt/hermes/.hermes_build_sha; \
    fi

# ---------- s6-overlay service wiring ----------
# Static services declared at build time: main-hermes + dashboard.
# Per-profile gateway services are registered dynamically at runtime by
# the profile create/delete hooks (Phase 4); they live under
# /run/service/ (tmpfs) and are reconciled on container restart by
# /etc/cont-init.d/02-reconcile-profiles (Phase 4 Task 4.0).
COPY docker/s6-rc.d/ /etc/s6-overlay/s6-rc.d/

# stage2-hook handles UID/GID remap, volume chown, config seeding,
# skills sync — all the work the old entrypoint.sh did before
# `exec hermes`. Wired in as cont-init.d/01- so it
# runs before user services start.
#
# 02-reconcile-profiles re-creates per-profile gateway s6 service
# slots from $HERMES_HOME/profiles/<name>/ after a container restart
# (the /run/service/ scandir is tmpfs and wiped on restart). Phase 4.
# Must run as root because /etc/ is root-owned; switch back to hermes after.
USER root
RUN mkdir -p /etc/cont-init.d && \
    printf '#!/command/with-contenv sh\nexec /opt/hermes/docker/stage2-hook.sh\n' \
        > /etc/cont-init.d/01-hermes-setup && \
    chmod +x /etc/cont-init.d/01-hermes-setup
USER hermes
COPY --chmod=0755 docker/cont-init.d/015-supervise-perms /etc/cont-init.d/015-supervise-perms
COPY --chmod=0755 docker/cont-init.d/02-reconcile-profiles /etc/cont-init.d/02-reconcile-profiles

# ---------- Runtime ----------
ENV HERMES_WEB_DIST=/opt/hermes/hermes_cli/web_dist
ENV HERMES_HOME=/opt/data

# `docker exec` privilege-drop shim. When operators run
# `docker exec <c> hermes ...` they default to root, and any file the
# command writes under $HERMES_HOME (auth.json, .env, config.yaml) ends
# up root-owned and unreadable to the supervised gateway (UID 10000).
# The shim lives at /opt/hermes/bin/hermes, sits earliest on PATH, and
# transparently re-exec's the real venv binary via `s6-setuidgid hermes`
# when invoked as root. Non-root callers (supervised processes,
# `--user hermes`, etc.) hit the short-circuit path with no overhead.
# Recursion is impossible because the shim exec's the venv binary by
# absolute path (/opt/hermes/.venv/bin/hermes). See the shim source for
# the opt-out env var (HERMES_DOCKER_EXEC_AS_ROOT=1).
COPY --chmod=0755 docker/hermes-exec-shim.sh /opt/hermes/bin/hermes

# Pre-s6 entrypoint.sh did `source .venv/bin/activate` which exported
# the venv bin onto PATH; Architecture B's main-wrapper.sh does the
# same for the container's main process, but `docker exec` and our
# cont-init.d scripts don't pass through the wrapper. Expose the venv
# bin globally so `docker exec <container> hermes ...` and any
# subprocess that doesn't activate the venv first still find hermes.
#
# /opt/hermes/bin is prepended ahead of the venv so the privilege-drop
# shim wins PATH resolution. The shim's last act is to exec the venv
# binary by absolute path, so this PATH ordering is transparent to
# every other consumer.
ENV PATH="/opt/hermes/bin:/opt/hermes/.venv/bin:/opt/data/.local/bin:${PATH}"
RUN mkdir -p /opt/data
VOLUME [ "/opt/data" ]

# s6-overlay's /init is PID 1. It sets up the supervision tree, runs
# /etc/cont-init.d/* (our stage2 hook), starts s6-rc services
# declared in /etc/s6-overlay/s6-rc.d/, then exec's its remaining
# argv as the container's "main program" with stdin/stdout/stderr
# inherited (this is what makes interactive --tui work). When the
# main program exits, /init begins stage 3 shutdown and the container
# exits with the program's exit code. Replaces tini — see Phase 2 of
# docs/plans/2026-05-07-s6-overlay-dynamic-subagent-gateways.md.
#
# We use the ENTRYPOINT+CMD split rather than CMD alone so the
# wrapper is prepended to user-supplied args automatically:
#
#   docker run <image>                  → /init main-wrapper.sh   (CMD default)
#   docker run <image> chat -q "hi"     → /init main-wrapper.sh chat -q hi
#   docker run <image> sleep infinity   → /init main-wrapper.sh sleep infinity
#   docker run <image> --tui            → /init main-wrapper.sh --tui
#
# main-wrapper.sh handles arg routing (bare-exec vs. hermes
# subcommand vs. no-args), drops to the hermes user via s6-setuidgid,
# and exec's the final program so its exit code becomes the container
# exit code. Without the wrapper-as-ENTRYPOINT, leading-dash args
# like `--version` would be intercepted by /init's POSIX shell.
ENTRYPOINT [ "/init", "/opt/hermes/docker/main-wrapper.sh" ]
CMD [ ]
