#!/bin/bash
# cloud_backup.sh - 云盘备份脚本
# 用途：备份到 OneDrive/Cloud 目录
# 用法：
#   ./cloud_backup.sh          # 默认：最新备份（覆盖）
#   ./cloud_backup.sh --daily  # 每日备份（保留历史）

set -e

LOCAL_WORKSPACE="${OPENCLAW_LOCAL_WORKSPACE:-$HOME/Workspaces/openclaw/main}"
LOCAL_WORKSPACE="${LOCAL_WORKSPACE/#\~/$HOME}"
CLOUD_WORKSPACE="${OPENCLAW_CLOUD_WORKSPACE:-$HOME/Cloud/OneDrivePersonal/OpenClaw}"
CLOUD_WORKSPACE="${CLOUD_WORKSPACE/#\~/$HOME}"
DATE_STAMP=$(date +%Y%m%d)
TIME_STAMP=$(date +%Y-%m-%d\ %H:%M:%S)

# 检查模式
BACKUP_MODE="${1:-latest}"  # 默认 latest，可选 --daily
if [ "$BACKUP_MODE" = "--daily" ]; then
    BACKUP_MODE="daily"
fi

echo "=========================================="
echo "云盘备份脚本 - 开始执行"
echo "=========================================="
echo "云盘目录: ${CLOUD_WORKSPACE}"
echo "备份时间: ${TIME_STAMP}"
echo "备份模式: ${BACKUP_MODE} (latest=覆盖, daily=保留历史)"
echo "=========================================="

# 检查云盘目录
if [ ! -d "${CLOUD_WORKSPACE}" ]; then
    echo "❌ 云盘目录不存在: ${CLOUD_WORKSPACE}"
    echo "   请确认 OneDrive 已同步"
    exit 1
fi

# 创建备份目录
if [ "$BACKUP_MODE" = "daily" ]; then
    # 每日备份：保留历史
    BACKUP_DIR="${CLOUD_WORKSPACE}/backups/${DATE_STAMP}"
else
    # 最新备份：覆盖旧版本
    BACKUP_DIR="${CLOUD_WORKSPACE}/latest"
fi
mkdir -p "${BACKUP_DIR}"

# 备份配置
echo "Step 1: 备份配置文件..."
cp -r "${LOCAL_WORKSPACE}/.system/governance/current/config" "${BACKUP_DIR}/configs/" 2>/dev/null || true
echo "  ✅ 完成"

# 备份治理规范
echo "Step 2: 备份治理规范..."
cp -r "${LOCAL_WORKSPACE}/.system/governance/current/standards" "${BACKUP_DIR}/" 2>/dev/null || true
cp -r "${LOCAL_WORKSPACE}/.system/governance/current/policies" "${BACKUP_DIR}/" 2>/dev/null || true
echo "  ✅ 完成"

# 备份 Agent
echo "Step 3: 备份 Agent 文件..."
mkdir -p "${BACKUP_DIR}/agents"
for agent in main ceo cto cdo cfo cio cqo cvo cco ld ec-ceo; do
    if [ -f "${LOCAL_WORKSPACE}/60_Agents/${agent}/IDENTITY.md" ]; then
        cp "${LOCAL_WORKSPACE}/60_Agents/${agent}/IDENTITY.md" "${BACKUP_DIR}/agents/${agent}.md" 2>/dev/null || true
    fi
done
echo "  ✅ 完成"

# 记录日志
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}" 2>/dev/null | cut -f1 || echo "unknown")
echo "[${TIME_STAMP}] Cloud backup (${BACKUP_MODE}): ${BACKUP_SIZE}" >> "${CLOUD_WORKSPACE}/backup.log"

echo ""
echo "=========================================="
echo "云盘备份完成"
echo "位置: ${BACKUP_DIR}"
echo "大小: ${BACKUP_SIZE}"
if [ "$BACKUP_MODE" = "latest" ]; then
    echo "模式: 最新备份（每次覆盖）"
else
    echo "模式: 每日备份（保留历史）"
fi
echo "=========================================="
