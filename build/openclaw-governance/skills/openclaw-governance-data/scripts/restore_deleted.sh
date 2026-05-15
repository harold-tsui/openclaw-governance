# restore_deleted.sh - 从删除备份恢复文件
# 依据 ZT-2026-003 数据备份与归档规范 v1.1

set -e

RELATIVE_PATH="$1"

if [ -z "${RELATIVE_PATH}" ]; then
  echo "❌ 使用方法: ./restore_deleted.sh <相对路径>"
  echo "示例: ./restore_deleted.sh /tmp/test_backup_file.txt"
  exit 1
fi

# 配置
BACKUP_WORKSPACE="${OPENCLAW_BACKUP_WORKSPACE:-$HOME/Workspaces/openclaw.bak}"
BACKUP_WORKSPACE="${BACKUP_WORKSPACE/#\~/$HOME}"
BACKUP_ROOT="${BACKUP_WORKSPACE}/deleted"

echo "=========================================="
echo "删除备份恢复脚本 - 开始执行"
echo "=========================================="
echo "目标路径: ${RELATIVE_PATH}"
echo "备份根目录: ${BACKUP_ROOT}"
echo "=========================================="

# 提取文件名（移除路径）
FILENAME=$(basename "${RELATIVE_PATH}")

# 查找最近的备份（按文件名搜索）
LATEST_BACKUP=$(find "${BACKUP_ROOT}" -type f -name "${FILENAME}" 2>/dev/null | sort -r | head -1)

if [ -z "${LATEST_BACKUP}" ]; then
  echo "❌ 未找到备份: ${RELATIVE_PATH}"
  echo "ν Search path: ${BACKUP_ROOT}"
  exit 1
fi

echo ""
echo "📦 找到备份: ${LATEST_BACKUP}"
echo "📍 恢复到: ${RELATIVE_PATH}"
echo "=========================================="

# 创建目标目录
mkdir -p "$(dirname "${RELATIVE_PATH}")"

# 恢复文件
cp -r "${LATEST_BACKUP}" "${RELATIVE_PATH}"

if [ -e "${RELATIVE_PATH}" ]; then
  echo ""
  echo "✅ 恢复成功: ${RELATIVE_PATH}"
  echo ""
  echo "=========================================="
  echo "删除备份恢复脚本 - 执行完成"
  echo "=========================================="
else
  echo ""
  echo "❌ 恢复失败"
  exit 1
fi
