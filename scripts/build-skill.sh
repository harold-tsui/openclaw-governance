#!/bin/bash
# build-skill.sh — 将 src/ 中的源码同步到 build/openclaw-governance/ 的 skill 包结构
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$PROJECT_DIR/build/openclaw-governance"
SRC_DIR="$PROJECT_DIR/src"

echo "🔧 Building openclaw-governance skill package..."

# Sync src/*.py → build/openclaw-governance/skills/openclaw-governance-nucleus/scripts/
NUCLEUS_SCRIPTS="$BUILD_DIR/skills/openclaw-governance-nucleus/scripts"
mkdir -p "$NUCLEUS_SCRIPTS"

for py in "$SRC_DIR"/*.py; do
    filename=$(basename "$py")
    cp "$py" "$NUCLEUS_SCRIPTS/$filename"
    echo "  ✅ src/$filename → skills/openclaw-governance-nucleus/scripts/$filename"
done

# Copy config files if they exist in src/config/
if [ -d "$SRC_DIR/config" ]; then
    NUCLEUS_CONFIG="$BUILD_DIR/skills/openclaw-governance-nucleus/config"
    mkdir -p "$NUCLEUS_CONFIG"
    cp "$SRC_DIR/config/"* "$NUCLEUS_CONFIG/" 2>/dev/null || true
    echo "  ✅ src/config/ → skills/openclaw-governance-nucleus/config/"
fi

# Update _meta.json version timestamp
META_FILE="$NUCLEUS_SCRIPTS/../_meta.json"
if [ -f "$META_FILE" ]; then
    # Extract current version
    version=$(python3 -c "import json; print(json.load(open('$META_FILE'))['latest']['version'])" 2>/dev/null || echo "unknown")
    echo "  📦 Skill version: $version"
fi

echo "✅ Build complete → $BUILD_DIR"
