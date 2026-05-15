#!/bin/bash
# install-skill.sh — 将 build/ 中的 skill 包安装到 $LOCAL_WORKSPACE/skills/
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$PROJECT_DIR/build/openclaw-governance"
TARGET="${LOCAL_WORKSPACE:-$HOME/Workspaces/openclaw/main}/skills"

MODE="${1:---stable}"

if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build directory not found. Run ./scripts/build-skill.sh first."
    exit 1
fi

echo "📦 Installing openclaw-governance → $TARGET/"

# Remove old installation and copy new
rm -rf "$TARGET/openclaw-governance"
cp -r "$BUILD_DIR" "$TARGET/openclaw-governance"

# Verify
if [ -f "$TARGET/openclaw-governance/SKILL.md" ]; then
    echo "✅ openclaw-governance installed → $TARGET/openclaw-governance/"
    echo "   Mode: $MODE"
    
    # Health check if pdca.py exists
    PDCA="$TARGET/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py"
    if [ -f "$PDCA" ]; then
        python3 "$PDCA" health-check 2>&1 | head -5 || true
    fi
else
    echo "❌ Installation failed — SKILL.md not found"
    exit 1
fi
