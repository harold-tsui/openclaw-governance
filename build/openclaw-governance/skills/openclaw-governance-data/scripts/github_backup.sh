#!/bin/bash
# github_backup.sh - GitHub 备份脚本（v3.0）
# 依据 ZT-2026-003 数据备份与归档规范 v3.0
# 备份策略：git add . 提交所有非排除文件
# 执行频率：每天 04:00

set -e

LOCAL_WORKSPACE="${OPENCLAW_LOCAL_WORKSPACE:-$HOME/Workspaces/openclaw/main}"
LOCAL_WORKSPACE="${LOCAL_WORKSPACE/#\~/$HOME}"
DATE=$(date +%Y-%m-%d)
TIME=$(date +'%Y-%m-%d %H:%M:%S')

echo "=========================================="
echo "GitHub 备份脚本 v3.0 - 开始执行"
echo "=========================================="
echo "工作区: ${LOCAL_WORKSPACE}"
echo "备份时间: ${TIME}"
echo "=========================================="

cd "${LOCAL_WORKSPACE}"

# Step 1: 添加所有非排除文件（使用 git add .）
echo ""
echo "Step 1: git add ."
git add .
echo "  ✅ 添加完成"

# Step 2: 检查是否有变更
echo ""
echo "Step 2: 检查是否有变更..."
if git diff --cached --quiet; then
    echo "  ⏭️ 无变更，跳过提交"
    echo ""
    echo "=========================================="
    echo "GitHub 备份完成（无变更）"
    echo "=========================================="
    exit 0
fi

# Step 3: 提交变更
echo ""
echo "Step 3: git commit"
git commit -m "Auto-backup: ${TIME}"
echo "  ✅ 提交完成"

# Step 4: 推送到 GitHub
echo ""
echo "Step 4: git push"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

for i in 1 2 3; do
    echo "  尝试 ${i}/3..."
    if git push origin "${CURRENT_BRANCH}" 2>&1; then
        echo "  ✅ 推送成功"
        break
    else
        echo "  ⚠️ 推送失败，重试中..."
        [ $i -lt 3 ] && sleep 5
    fi
done

# Step 5: 记录日志
echo ""
echo "Step 5: 记录日志..."
LOG_DIR="${LOCAL_WORKSPACE}/.system/logs"
mkdir -p "${LOG_DIR}"
echo "[${TIME}] GitHub backup: completed" >> "${LOG_DIR}/github_backup.log"
echo "  ✅ 完成"

echo ""
echo "=========================================="
echo "GitHub 备份完成"
echo "=========================================="
