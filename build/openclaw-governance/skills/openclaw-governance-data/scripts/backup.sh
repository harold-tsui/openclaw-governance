#!/bin/bash
# backup.sh - 增量/全量备份脚本（v4.0）
# 依据 ZT-2026-003 数据备份与归档规范 v4.0
# 备份策略：增量 30 天 + 全量 4 周 + 季度归档 + 年度归档
# 排除：skills/, memory/evolution/, logs/, cache 等非生产数据
# 保留：memory/*.md 日记文件（人为生产）

set -e

# 配置
BACKUP_ROOT="${OPENCLAW_BACKUP_WORKSPACE:-$HOME/Workspaces/openclaw.bak}"
BACKUP_ROOT="${BACKUP_ROOT/#\~/$HOME}"  # 展开 ~ 为 $HOME
LOCAL_WORKSPACE="${OPENCLAW_LOCAL_WORKSPACE:-$HOME/Workspaces/openclaw/main}"
LOCAL_WORKSPACE="${LOCAL_WORKSPACE/#\~/$HOME}"  # 展开 ~ 为 $HOME

# 判断备份类型
BACKUP_TYPE="${1:-incremental}"  # incremental | full | quarterly

if [ "${BACKUP_TYPE}" == "full" ]; then
    # 全量备份（每周日）
    DATE=$(date +%Y-W%W)
    BACKUP_DIR="${BACKUP_ROOT}/full/${DATE}"
    echo "=========================================="
    echo "全量备份脚本 v4.0 - 开始执行"
    echo "=========================================="
    echo "工作区：${LOCAL_WORKSPACE}"
    echo "备份目录：${BACKUP_DIR}"
    echo "备份周期：${DATE}（周）"
    echo "=========================================="
    
    mkdir -p "${BACKUP_DIR}"
    
    # 使用 rsync 全量备份（仅备份生产数据）
    # 排除 memory/evolution/，保留 memory/*.md 日记文件
    rsync -a --delete \
        --exclude='skills/' \
        --exclude='memory/evolution/' \
        --exclude='logs/' \
        --exclude='.system/logs/' \
        --exclude='.system/governance/heartbeat-logs/' \
        --exclude='.system/governance/logs/' \
        --exclude='qdrant_data/' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='node_modules/' \
        --exclude='.cache/' \
        --exclude='.agent_workspace/' \
        --exclude='60_Agents/*/.openclaw/' \
        --exclude='60_Agents/*/agent/' \
        --exclude='60_Agents/*/inbox/' \
        --exclude='*.tmp' \
        --exclude='*.temp' \
        --exclude='.DS_Store' \
        --exclude='.env' \
        --exclude='.env.*' \
        --exclude='*.key' \
        --exclude='*.pem' \
        --exclude='credentials.json' \
        --exclude='secrets.*' \
        "${LOCAL_WORKSPACE}/" "${BACKUP_DIR}/"
    
    # 清理 4 周前的全量备份
    echo ""
    echo "清理 4 周前的全量备份..."
    find "${BACKUP_ROOT}/full/" -maxdepth 1 -type d -mtime +28 -exec rm -rf {} \; 2>/dev/null || true
    
elif [ "${BACKUP_TYPE}" == "quarterly" ]; then
    # 季度归档
    YEAR=$(date +%Y)
    QUARTER=$((($(date +%m) - 1) / 3 + 1))
    ARCHIVE_NAME="${YEAR}-Q${QUARTER}"
    ARCHIVE_DIR="${BACKUP_ROOT}/quarterly/${ARCHIVE_NAME}"
    
    echo "=========================================="
    echo "季度归档脚本 v4.0 - 开始执行"
    echo "=========================================="
    echo "工作区：${LOCAL_WORKSPACE}"
    echo "归档名称：${ARCHIVE_NAME}"
    echo "=========================================="
    
    mkdir -p "${ARCHIVE_DIR}"
    
    # 完整备份并压缩
    # 排除 memory/evolution/，保留 memory/*.md 日记文件
    rsync -a \
        --exclude='skills/' \
        --exclude='memory/evolution/' \
        --exclude='logs/' \
        --exclude='.system/logs/' \
        --exclude='.system/governance/heartbeat-logs/' \
        --exclude='.system/governance/logs/' \
        --exclude='qdrant_data/' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='node_modules/' \
        --exclude='.cache/' \
        --exclude='.agent_workspace/' \
        --exclude='60_Agents/*/.openclaw/' \
        --exclude='60_Agents/*/agent/' \
        --exclude='60_Agents/*/inbox/' \
        --exclude='*.tmp' \
        --exclude='*.temp' \
        --exclude='.DS_Store' \
        --exclude='.env' \
        --exclude='*.key' \
        "${LOCAL_WORKSPACE}/" "${ARCHIVE_DIR}/"
    
    # 压缩归档
    cd "${BACKUP_ROOT}/quarterly/"
    tar -czf "${ARCHIVE_NAME}.tar.gz" "${ARCHIVE_NAME}/"
    rm -rf "${ARCHIVE_DIR}"
    
    # 清理 3 年前的季度归档
    echo ""
    echo "清理 3 年前的季度归档..."
    find "${BACKUP_ROOT}/quarterly/" -name "*.tar.gz" -mtime +1095 -exec rm -f {} \; 2>/dev/null || true
    
else
    # 增量备份（每天）
    DATE=$(date +%Y-%m-%d)
    BACKUP_DIR="${BACKUP_ROOT}/incremental/${DATE}"
    
    echo "=========================================="
    echo "增量备份脚本 v4.0 - 开始执行"
    echo "=========================================="
    echo "工作区：${LOCAL_WORKSPACE}"
    echo "备份目录：${BACKUP_DIR}"
    echo "备份日期：${DATE}"
    echo "=========================================="
    
    mkdir -p "${BACKUP_DIR}"
    
    # 使用 rsync 增量备份（仅备份变更的生产数据）
    # 排除 memory/evolution/，保留 memory/*.md 日记文件
    rsync -a --delete \
        --exclude='skills/' \
        --exclude='memory/evolution/' \
        --exclude='logs/' \
        --exclude='.system/logs/' \
        --exclude='.system/governance/heartbeat-logs/' \
        --exclude='.system/governance/logs/' \
        --exclude='qdrant_data/' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='node_modules/' \
        --exclude='.cache/' \
        --exclude='.agent_workspace/' \
        --exclude='60_Agents/*/.openclaw/' \
        --exclude='60_Agents/*/agent/' \
        --exclude='60_Agents/*/inbox/' \
        --exclude='*.tmp' \
        --exclude='*.temp' \
        --exclude='.DS_Store' \
        --exclude='.env' \
        --exclude='.env.*' \
        --exclude='*.key' \
        --exclude='*.pem' \
        --exclude='credentials.json' \
        --exclude='secrets.*' \
        "${LOCAL_WORKSPACE}/" "${BACKUP_DIR}/"
    
    # 清理 30 天前的增量备份
    echo ""
    echo "清理 30 天前的增量备份..."
    find "${BACKUP_ROOT}/incremental/" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
fi

# 验证备份
FILE_COUNT=$(find "${BACKUP_DIR:-${ARCHIVE_DIR}}" -type f 2>/dev/null | wc -l)
DIR_COUNT=$(find "${BACKUP_DIR:-${ARCHIVE_DIR}}" -type d 2>/dev/null | wc -l)
BACKUP_SIZE=$(du -sh "${BACKUP_DIR:-${ARCHIVE_DIR}}" 2>/dev/null | cut -f1)

echo ""
echo "✅ 备份完成"
echo "  文件数：${FILE_COUNT}"
echo "  目录数：${DIR_COUNT}"
echo "  备份大小：${BACKUP_SIZE}"

# 记录备份日志
echo ""
echo "[$(date)] ${BACKUP_TYPE} backup completed: ${FILE_COUNT} files, ${BACKUP_SIZE}" >> "${BACKUP_ROOT}/backup.log"

echo ""
echo "=========================================="
echo "备份脚本 v4.0 - 执行完成"
echo "=========================================="