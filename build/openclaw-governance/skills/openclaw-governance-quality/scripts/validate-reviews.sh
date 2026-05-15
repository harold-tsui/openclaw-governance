#!/bin/bash
# validate-reviews.sh - Review-gate 验证脚本
# 用于强制检查审查完整性，增强 NUCLEUS L0-L3 Review 体系
#
# 用法: ./validate-reviews.sh <task-dir> [--verbose]
#
# 返回码:
#   0 - 验证通过
#   1 - 任务目录不存在
#   2 - 缺少审查产物
#   3 - 检测到自我审查
#   4 - DOD 验证缺失
#   5 - 零问题审查警告
#   6 - 配置文件错误

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认值
TASK_DIR=""
VERBOSE=false
WARNINGS=0
ERRORS=0

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "用法: $0 <task-dir> [-v|--verbose]"
            echo ""
            echo "参数:"
            echo "  task-dir       任务目录路径（包含 TASK-CARD.md）"
            echo "  -v, --verbose  详细输出"
            echo ""
            echo "返回码:"
            echo "  0 - 验证通过"
            echo "  1 - 任务目录不存在"
            echo "  2 - 缺少审查产物"
            echo "  3 - 检测到自我审查"
            echo "  4 - DOD 验证缺失"
            echo "  5 - 零问题审查警告"
            echo "  6 - 配置文件错误"
            exit 0
            ;;
        *)
            TASK_DIR="$1"
            shift
            ;;
    esac
done

# 检查目录
if [ -z "$TASK_DIR" ]; then
    echo -e "${RED}错误: 未指定任务目录${NC}"
    exit 1
fi

if [ ! -d "$TASK_DIR" ]; then
    echo -e "${RED}错误: 任务目录不存在: $TASK_DIR${NC}"
    exit 1
fi

TASK_CARD="$TASK_DIR/TASK-CARD.md"
if [ ! -f "$TASK_CARD" ]; then
    echo -e "${RED}错误: 未找到 TASK-CARD.md: $TASK_CARD${NC}"
    exit 6
fi

echo -e "${BLUE}=== Review-Gate 验证 ===${NC}"
echo "任务目录: $TASK_DIR"
echo ""

# ============================================
# 检查 1: 审查产物完整性
# ============================================
check_review_artifacts() {
    echo "[1/4] 检查审查产物完整性..."
    
    # 查找审查产物
    local review_files=$(find "$TASK_DIR" -name "*review*.md" -o -name "*REVIEW*.md" 2>/dev/null | head -20)
    local review_count=0
    
    if [ -n "$review_files" ]; then
        review_count=$(echo "$review_files" | wc -l | tr -d ' ')
    fi
    
    if [ "$review_count" -eq 0 ]; then
        echo -e "${RED}错误: 未找到审查产物${NC}"
        echo "  期望位置: $TASK_DIR/review.md 或 $TASK_DIR/deliverables/*review*.md"
        ERRORS=$((ERRORS + 1))
        return 2
    fi
    
    echo -e "${GREEN}✓ 找到 $review_count 个审查产物${NC}"
    if [ "$VERBOSE" = true ]; then
        echo "$review_files" | while read -r file; do
            [ -n "$file" ] && echo "  - $file"
        done
    fi
    return 0
}

# ============================================
# 检查 2: 自我审查检测
# ============================================
check_self_review() {
    echo ""
    echo "[2/4] 检查自我审查..."
    
    # 从 TASK-CARD 提取 Task PIC
    local builder=$(grep -E "^\| \*\*Task PIC\*\*" "$TASK_CARD" | sed 's/.*| //;s/ |.*//' | tr -d ' ')
    
    if [ -z "$builder" ]; then
        echo -e "${YELLOW}警告: 无法从 TASK-CARD 提取 Task PIC${NC}"
        return 0
    fi
    
    if [ "$VERBOSE" = true ]; then
        echo "  Task PIC: $builder"
    fi
    
    # 检查审查产物中的 Reviewer
    local self_review_found=false
    local review_files=$(find "$TASK_DIR" -name "*review*.md" -o -name "*REVIEW*.md" 2>/dev/null)
    
    while IFS= read -r review_file; do
        if [ -f "$review_file" ]; then
            # 尝试提取 Reviewer
            local reviewer=$(grep -iE "Reviewer|审查者|验证人" "$review_file" | head -1 | sed 's/.*: *//;s/ *$//' | tr -d '|')
            
            if [ -n "$reviewer" ] && [ "$reviewer" = "$builder" ]; then
                echo -e "${RED}错误: 检测到自我审查${NC}"
                echo "  Builder: $builder"
                echo "  Reviewer: $reviewer"
                echo "  文件: $review_file"
                self_review_found=true
                ERRORS=$((ERRORS + 1))
            fi
        fi
    done <<< "$review_files"
    
    if [ "$self_review_found" = false ]; then
        echo -e "${GREEN}✓ 无自我审查检测${NC}"
        return 0
    fi
    
    return 3
}

# ============================================
# 检查 3: DOD 验证
# ============================================
check_dod_verification() {
    echo ""
    echo "[3/4] 检查 DOD 验证..."
    
    # 检查 TASK-CARD 中是否有 DOD 部分
    if ! grep -q "##.*DOD\|Definition of Done" "$TASK_CARD"; then
        echo -e "${YELLOW}警告: TASK-CARD 中未找到 DOD 部分${NC}"
        echo "  建议: 添加结构化验收标准"
        WARNINGS=$((WARNINGS + 1))
        return 0
    fi
    
    # 检查 DOD 状态列
    local dod_section=$(sed -n '/##.*DOD\|Definition of Done/,/^##[^#]/p' "$TASK_CARD")
    
    # 检查是否有 ✅ 或 "完成" 标记
    if echo "$dod_section" | grep -q "✅\|已完成\|完成"; then
        # 检查是否有验证人
        if echo "$dod_section" | grep -q "验证人\|Verifier\|Reviewer"; then
            echo -e "${GREEN}✓ DOD 已验证${NC}"
            return 0
        else
            echo -e "${YELLOW}警告: DOD 已标记但缺少验证人${NC}"
            WARNINGS=$((WARNINGS + 1))
            return 0
        fi
    fi
    
    # 检查是否有 ⬜ 或 "待验证" 标记
    if echo "$dod_section" | grep -q "⬜\|待验证\|未完成"; then
        echo -e "${RED}错误: DOD 未完成验证${NC}"
        ERRORS=$((ERRORS + 1))
        return 4
    fi
    
    echo -e "${GREEN}✓ DOD 验证检查完成${NC}"
    return 0
}

# ============================================
# 检查 4: 零问题审查警告
# ============================================
check_zero_issue_review() {
    echo ""
    echo "[4/4] 检查零问题审查..."
    
    local review_files=$(find "$TASK_DIR" -name "*review*.md" -o -name "*REVIEW*.md" 2>/dev/null)
    local suspicious_count=0
    
    while IFS= read -r review_file; do
        if [ -f "$review_file" ]; then
            # 检查是否是"橡皮图章"审查
            # 条件：通过 + 无问题列表 + 无改进建议
            local content=$(cat "$review_file")
            local has_pass=$(echo "$content" | grep -ci "pass\|通过\|✅" || echo "0")
            local has_issues=$(echo "$content" | grep -ci "问题\|issue\|建议\|suggestion\|改进" || echo "0")
            local has_detail=$(echo "$content" | wc -l)
            
            if [ "$has_pass" -gt 0 ] && [ "$has_issues" -eq 0 ] && [ "$has_detail" -lt 20 ]; then
                echo -e "${YELLOW}警告: 可疑的零问题审查${NC}"
                echo "  文件: $review_file"
                echo "  特征: 通过但无问题/建议，内容过短（$has_detail 行）"
                suspicious_count=$((suspicious_count + 1))
                WARNINGS=$((WARNINGS + 1))
            fi
        fi
    done <<< "$review_files"
    
    if [ "$suspicious_count" -eq 0 ]; then
        echo -e "${GREEN}✓ 无可疑审查${NC}"
    else
        echo -e "${YELLOW}发现 $suspicious_count 个可疑审查，请人工确认${NC}"
    fi
    
    return 0
}

# ============================================
# 输出详细报告
# ============================================
print_summary() {
    echo ""
    echo -e "${BLUE}=== 验证结果 ===${NC}"
    echo ""
    
    if [ "$WARNINGS" -gt 0 ]; then
        echo -e "${YELLOW}警告: $WARNINGS 个${NC}"
    fi
    
    if [ "$ERRORS" -gt 0 ]; then
        echo -e "${RED}错误: $ERRORS 个${NC}"
        echo ""
        echo -e "${RED}Review-Gate 验证失败${NC}"
        echo ""
        echo "建议操作:"
        echo "  1. 补充缺失的审查产物"
        echo "  2. 确保审查者不是任务执行者"
        echo "  3. 完成所有 DOD 验证"
        exit 2
    else
        echo -e "${GREEN}✓ Review-Gate 验证通过${NC}"
        if [ "$WARNINGS" -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}注意: 存在 $WARNINGS 个警告，建议检查${NC}"
        fi
        exit 0
    fi
}

# ============================================
# 主逻辑
# ============================================
main() {
    check_review_artifacts || true
    check_self_review || true
    check_dod_verification || true
    check_zero_issue_review || true
    print_summary
}

main