#!/usr/bin/env bash
# bootstrap.sh — Set up ai-skills-sync on a new VM.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/YOU/agent-config/main/bootstrap.sh | bash
#   — or —
#   bash bootstrap.sh [~/.agents/skills]
#
# What it does:
#   1. Clones (or updates) this repo to ~/agent-config
#   2. Runs the initial sync
#   3. Installs a post-merge git hook so future `git pull` auto-syncs

set -euo pipefail

REPO_URL="https://github.com/carlosdobler/agent-config.git"
CLONE_DIR="${HOME}/agent-config"
SKILLS_DEST="${1:-${HOME}/.agents/skills}"

# ── 1. Clone or update the config repo ──────────────────────────────────────
if [ -d "${CLONE_DIR}/.git" ]; then
    echo "→ Updating existing repo at ${CLONE_DIR}"
    git -C "${CLONE_DIR}" pull --ff-only
else
    echo "→ Cloning ${REPO_URL} into ${CLONE_DIR}"
    git clone "${REPO_URL}" "${CLONE_DIR}"
fi

cd "${CLONE_DIR}"

# ── 2. Initial sync ──────────────────────────────────────────────────────────
echo "→ Running initial skill sync to ${SKILLS_DEST}"
python3 sync_skills.py --dest "${SKILLS_DEST}"

# ── 3. Install post-merge hook (auto-sync on git pull) ───────────────────────
HOOK_SRC="${CLONE_DIR}/hooks/post-merge"
HOOK_DST="${CLONE_DIR}/.git/hooks/post-merge"

if [ -f "${HOOK_SRC}" ]; then
    cp "${HOOK_SRC}" "${HOOK_DST}"
    chmod +x "${HOOK_DST}"
    echo "→ post-merge hook installed"
fi

echo ""
echo "✓ Bootstrap complete."
echo "  Skills are at: ${SKILLS_DEST}"
echo "  To update: cd ${CLONE_DIR} && git pull"