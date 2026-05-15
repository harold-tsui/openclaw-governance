#!/bin/bash
# safe_delete.sh - 安全删除脚本（删除前自动备份）
# 依据 ZT-2026-003 数据备份与归档规范 v1.1

set -e

FILE_TO_DELETE="$1"

if [ -z "${FILE_TO_DELETE}" ]; then
  echo "❌ 使用方法: ./safe_delete.sh <文件或目录路径>"
  echo "示例: ./safe_delete.sh 60_Agents/cdo/temp.md"
  exit 1
fi

# 配置
BACKUP_WORKSPACE="${OPENCLAW_BACKUP_WORKSPACE:-$HOME/Workspaces/openclaw.bak}"
BACKUP_WORKSPACE="${BACKUP_WORKSPACE/#\~/$HOME}"
BACKUP_TIME=$(date +%y%m/%d/%H%M%S)
BACKUP_DIR="${BACKUP_WORKSPACE}/deleted/${BACKUP_TIME}"

echo "=========================================="
echo "安全删除脚本 - 开始执行"
echo "=========================================="
echo "文件路径: ${FILE_TO_DELETE}"
echo "备份时间: ${BACKUP_TIME}"
echo "备份目录: ${BACKUP_DIR}"
echo "=========================================="

# 1. 检查文件是否存在
if [ ! -e "${FILE_TO_DELETE}" ]; then
  echo "❌ 文件不存在: ${FILE_TO_DELETE}"
  exit 1
fi

# 2. 创建备份目录（保留完整路径结构）
BACKUP_FULL_PATH="${BACKUP_DIR}/${FILE_TO_DELETE}"
mkdir -p "$(dirname "${BACKUP_FULL_PATH}")"

echo "📦 备份路径: ${BACKUP_FULL_PATH}"

# 3. 备份文件
if [ -d "${FILE_TO_DELETE}" ]; then
  cp -r "${FILE_TO_DELETE}" "${BACKUP_FULL_PATH}"
else
  cp -r "${FILE_TO_DELETE}" "${BACKUP_FULL_PATH}"
fi

# 4. 验证备份成功
if [ -e "${BACKUP_FULL_PATH}" ]; then
  echo ""
  echo "✅ 备份成功: ${BACKUP_FULL_PATH}"
  echo "📁 备份目录: ${BACKUP_DIR}"
  
  # 5. 删除原文件
  rm -rf "${FILE_TO_DELETE}"
  echo "✅ 删除成功: ${FILE_TO_DELETE}"
  echo ""
  echo "=========================================="
  echo "安全删除脚本 - 执行完成"
  echo "=========================================="
else
  echo ""
  echo "❌ 备份失败，取消删除操作"
  exit 1
fi
