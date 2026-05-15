#!/bin/bash
# verify-dod.sh - DOD 验证脚本
# 用于 Review-Gate 强制检查
# 增强 NUCLEUS 闭环流程的验收环节
#
# 用法: ./verify-dod.sh <dod-file> [--builder <agent-id>]
#
# 返回码:
#   0 - 验证通过
#   1 - DOD 文件不存在
#   2 - DOD JSON 格式错误
#   3 - 必须标准未全部满足
#   4 - 自我认证（Builder 验证了自己的 DOD）
#   5 - DOD 未锁定
#   6 - 缺少必要字段

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认值
DOD_FILE=""
BUILDER_ID=""
VERBOSE=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --builder)
            BUILDER_ID="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "用法: $0 <dod-file> [--builder <agent-id>] [-v|--verbose]"
            echo ""
            echo "参数:"
            echo "  dod-file          DOD JSON 文件路径"
            echo "  --builder ID      Builder Agent ID，用于检查自我认证"
            echo "  -v, --verbose     详细输出"
            echo ""
            echo "返回码:"
            echo "  0 - 验证通过"
            echo "  1 - DOD 文件不存在"
            echo "  2 - DOD JSON 格式错误"
            echo "  3 - 必须标准未全部满足"
            echo "  4 - 自我认证检测"
            echo "  5 - DOD 未锁定"
            echo "  6 - 缺少必要字段"
            exit 0
            ;;
        *)
            DOD_FILE="$1"
            shift
            ;;
    esac
done

# 检查文件是否存在
if [ -z "$DOD_FILE" ]; then
    echo -e "${RED}错误: 未指定 DOD 文件${NC}"
    exit 1
fi

if [ ! -f "$DOD_FILE" ]; then
    echo -e "${RED}错误: DOD 文件不存在: $DOD_FILE${NC}"
    exit 1
fi

echo -e "${BLUE}=== DOD 验证 ===${NC}"
echo "文件: $DOD_FILE"
echo ""

# 验证 JSON 格式
if ! jq empty "$DOD_FILE" 2>/dev/null; then
    echo -e "${RED}错误: DOD JSON 格式错误${NC}"
    exit 2
fi

# 检查必要字段
check_required_fields() {
    local missing=()
    
    if [ -z "$(jq -r '.version // empty' "$DOD_FILE")" ]; then
        missing+=("version")
    fi
    
    if [ -z "$(jq -r '.criteria // empty' "$DOD_FILE")" ]; then
        missing+=("criteria")
    fi
    
    if [ -z "$(jq -r '.metadata.created_by // empty' "$DOD_FILE")" ]; then
        missing+=("metadata.created_by")
    fi
    
    if [ -z "$(jq -r '.metadata.created_at // empty' "$DOD_FILE")" ]; then
        missing+=("metadata.created_at")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}错误: 缺少必要字段:${NC}"
        printf '  - %s\n' "${missing[@]}"
        exit 6
    fi
}

# 检查锁定状态
check_locked() {
    local locked=$(jq -r '.metadata.locked // false' "$DOD_FILE")
    
    if [ "$locked" != "true" ]; then
        echo -e "${YELLOW}警告: DOD 未锁定，Builder 可以修改${NC}"
        if [ "$VERBOSE" = true ]; then
            echo "  建议: 在任务开始前锁定 DOD"
        fi
        return 5
    fi
    
    echo -e "${GREEN}✓ DOD 已锁定${NC}"
    return 0
}

# 检查标准完整性
check_criteria() {
    local total=$(jq '.criteria | length' "$DOD_FILE")
    local required=$(jq '[.criteria[] | select(.required == true)] | length' "$DOD_FILE")
    local met=$(jq '[.criteria[] | select(.status.met == true)] | length' "$DOD_FILE")
    local required_met=$(jq '[.criteria[] | select(.required == true and .status.met == true)] | length' "$DOD_FILE")
    
    echo ""
    echo "标准统计:"
    echo "  总标准数: $total"
    echo "  必须标准数: $required"
    echo "  已满足标准数: $met"
    echo "  必须标准已满足数: $required_met"
    
    # 检查必须标准是否全部满足
    if [ "$required_met" -lt "$required" ]; then
        echo ""
        echo -e "${RED}错误: 必须标准未全部满足 ($required_met/$required)${NC}"
        
        # 列出未满足的必须标准
        echo ""
        echo "未满足的必须标准:"
        jq -r '.criteria[] | select(.required == true and .status.met != true) | "  - [\(.id)] \(.description)"' "$DOD_FILE"
        
        return 3
    fi
    
    echo ""
    echo -e "${GREEN}✓ 所有必须标准已满足 ($required_met/$required)${NC}"
    return 0
}

# 检查自我认证
check_self_certification() {
    if [ -z "$BUILDER_ID" ]; then
        echo ""
        echo -e "${YELLOW}提示: 未指定 Builder ID，跳过自我认证检查${NC}"
        return 0
    fi
    
    local self_verified=$(jq -r --arg builder "$BUILDER_ID" '
        [.criteria[] | select(.status.verifier == $builder)] | length
    ' "$DOD_FILE")
    
    if [ "$self_verified" -gt 0 ]; then
        echo ""
        echo -e "${RED}错误: 检测到自我认证 ($self_verified 项)${NC}"
        echo "  Builder: $BUILDER_ID"
        echo "  自我验证的标准:"
        jq -r --arg builder "$BUILDER_ID" '
            .criteria[] | select(.status.verifier == $builder) | "    - [\(.id)] \(.description)"
        ' "$DOD_FILE"
        return 4
    fi
    
    echo ""
    echo -e "${GREEN}✓ 无自我认证检测${NC}"
    return 0
}

# 输出详细报告
print_verbose_report() {
    echo ""
    echo -e "${BLUE}=== 详细报告 ===${NC}"
    
    echo ""
    echo "元数据:"
    echo "  创建者: $(jq -r '.metadata.created_by' "$DOD_FILE")"
    echo "  创建时间: $(jq -r '.metadata.created_at' "$DOD_FILE")"
    echo "  锁定状态: $(jq -r '.metadata.locked' "$DOD_FILE")"
    echo "  关联任务: $(jq -r '.metadata.task_id // "未指定"' "$DOD_FILE")"
    echo "  自动化级别: $(jq -r '.metadata.automation_level // "未指定"' "$DOD_FILE")"
    
    echo ""
    echo "标准详情:"
    jq -r '.criteria[] | "  [\(.id)] \(.description)
    类别: \(.category) | 必须: \(.required) | 满足: \(.status.met)
    验证者: \(.status.verifier // "未验证") | 时间: \(.status.verified_at // "未验证")"' "$DOD_FILE"
}

# 主逻辑
main() {
    local errors=0
    
    # 1. 检查必要字段
    echo "[1/4] 检查必要字段..."
    check_required_fields
    echo -e "${GREEN}✓ 必要字段完整${NC}"
    
    # 2. 检查锁定状态
    echo ""
    echo "[2/4] 检查锁定状态..."
    check_locked || errors=$((errors + 1))
    
    # 3. 检查标准完整性
    echo ""
    echo "[3/4] 检查标准完整性..."
    check_criteria || errors=$((errors + 1))
    
    # 4. 检查自我认证
    echo ""
    echo "[4/4] 检查自我认证..."
    check_self_certification || errors=$((errors + 1))
    
    # 详细报告
    if [ "$VERBOSE" = true ]; then
        print_verbose_report
    fi
    
    # 汇总
    echo ""
    echo -e "${BLUE}=== 验证结果 ===${NC}"
    
    if [ $errors -gt 0 ]; then
        echo -e "${RED}验证失败: 发现 $errors 个问题${NC}"
        exit 3
    else
        echo -e "${GREEN}验证通过${NC}"
        exit 0
    fi
}

main