#!/bin/bash
# install-skill.sh — 将 build/ 中的 skill 包安装到 $LOCAL_WORKSPACE/skills/
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$PROJECT_DIR/build/openclaw-governance"
# 检测并设置目标目录
if [ -n "${LOCAL_WORKSPACE:-}" ]; then
    TARGET="$LOCAL_WORKSPACE/skills"
elif [ -d "$HOME/.openclaw/workspace" ]; then
    TARGET="$HOME/.openclaw/workspace/skills"
else
    TARGET="$HOME/Workspaces/openclaw/main/skills"
fi

MODE="${1:---stable}"

if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build directory not found. Run ./scripts/build-skill.sh first."
    exit 1
fi

echo "📦 Installing openclaw-governance → $TARGET/"

# 确保目标目录存在
mkdir -p "$TARGET"

# Remove old installation and copy new
rm -rf "$TARGET/openclaw-governance"
cp -r "$BUILD_DIR" "$TARGET/openclaw-governance"

# 确保运行时目录存在
mkdir -p "$TARGET/openclaw-governance/pdca"
mkdir -p "$TARGET/openclaw-governance/logs"

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
