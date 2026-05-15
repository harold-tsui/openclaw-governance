#!/bin/bash
# heartbeat_task_scanner.sh - Heartbeat 任务自动扫描脚本 v1.2
# 用途：扫描 10_Projects 目录，自动发现和同步 Task 状态到 MISSION_BOARD
# 执行频率：每次 Heartbeat 巡检

WORKSPACE="/Users/haroldtsui/Workspaces/openclaw/main"
LOG_DIR="${WORKSPACE}/.system/governance/heartbeat-logs"
LOG_FILE="${LOG_DIR}/task_scanner_$(date +%Y%m%d).log"

mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Heartbeat Task Scanner Started ===" > "$LOG_FILE"

echo "" >> "$LOG_FILE"
echo "=== 链路 a: Project -> Topic -> Task -> Deliverable ===" >> "$LOG_FILE"

# 扫描 PROJECT-CHARTER
PROJECT_COUNT=$(find ${WORKSPACE}/10_Projects -name "PROJECT-CHARTER.md" 2>/dev/null | wc -l)
echo "Projects: $PROJECT_COUNT" >> "$LOG_FILE"

# 扫描 TOPIC-BRIEF
TOPIC_COUNT=$(find ${WORKSPACE}/10_Projects -name "TOPIC-BRIEF.md" 2>/dev/null | wc -l)
echo "Topics: $TOPIC_COUNT" >> "$LOG_FILE"

# 扫描 TASK-CARD
TASK_COUNT=$(find ${WORKSPACE}/10_Projects -name "TASK-CARD*.md" 2>/dev/null | wc -l)
echo "Tasks: $TASK_COUNT" >> "$LOG_FILE"

# 列出所有 Tasks
echo "" >> "$LOG_FILE"
echo "=== Task List ===" >> "$LOG_FILE"
find ${WORKSPACE}/10_Projects -name "TASK-CARD*.md" 2>/dev/null | while read f; do
  rel_path=$(echo "$f" | sed "s|$WORKSPACE/10_Projects/||")
  echo "  $rel_path" >> "$LOG_FILE"
done

# 扫描 Deliverables
DELIVERABLE_COUNT=$(find ${WORKSPACE}/10_Projects -path "*/deliverables/*.md" 2>/dev/null | wc -l)
echo "" >> "$LOG_FILE"
echo "Deliverables: $DELIVERABLE_COUNT" >> "$LOG_FILE"

# MISSION_BOARD 对比
MISSION_BOARD="${WORKSPACE}/MISSION_BOARD.md"
MISSION_TASK_COUNT=$(grep -c "TASK-CARD" "$MISSION_BOARD" 2>/dev/null || echo "0")
MISSION_DONE_COUNT=$(grep -c "\[x\]" "$MISSION_BOARD" 2>/dev/null || echo "0")

echo "" >> "$LOG_FILE"
echo "=== MISSION_BOARD 对比 ===" >> "$LOG_FILE"
echo "MISSION_BOARD 记录: $MISSION_TASK_COUNT" >> "$LOG_FILE"
echo "MISSION_BOARD 完成: $MISSION_DONE_COUNT" >> "$LOG_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Scanner Completed ===" >> "$LOG_FILE"

# 输出到 stdout
echo "--- Heartbeat Task Scan ---"
echo "链路 a: Project -> Topic -> Task -> Deliverable"
echo "  Projects: $PROJECT_COUNT"
echo "  Topics: $TOPIC_COUNT"  
echo "  Tasks: $TASK_COUNT"
echo "  Deliverables: $DELIVERABLE_COUNT"
echo ""
echo "MISSION_BOARD:"
echo "  记录任务: $MISSION_TASK_COUNT"
echo "  已完成: $MISSION_DONE_COUNT"
echo ""
if [ "$TASK_COUNT" -gt "$MISSION_TASK_COUNT" ]; then
  MISSING=$((TASK_COUNT - MISSION_TASK_COUNT))
  echo "⚠️ 发现 $MISSING 个未追踪任务!"
fi