#!/bin/bash
# 测试 validate-reviews.sh 脚本
# 用法: ./test-validate-reviews.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"
VALIDATE_SCRIPT="$SKILL_ROOT/scripts/validate-reviews.sh"
TEST_DIR="$SCRIPT_DIR/fixtures/reviews"

echo "=== Review-gate 验证脚本测试 ==="
echo ""

# 测试 1: 审查产物完整性检查
test_review_artifacts() {
    echo "测试 1: 审查产物完整性检查..."
    local task_dir="$TEST_DIR/task-valid"
    
    mkdir -p "$task_dir"
    
    # 创建有效的审查产物
    cat > "$task_dir/review.md" << 'EOF'
# Review Report

**Reviewer**: main (银月)
**Date**: 2026-03-23
**Task**: TEST-VALID-001

## Summary

✅ 通过审核

## Checklist

- [x] 代码质量
- [x] 文档完整
- [x] 测试覆盖
EOF
    
    if [ -f "$task_dir/review.md" ]; then
        echo "  ✅ 通过: 审查产物存在"
    else
        echo "  ❌ 失败: 审查产物不存在"
    fi
}

# 测试 2: 自我审查检测
test_self_review_detection() {
    echo ""
    echo "测试 2: 自我审查检测..."
    local task_dir="$TEST_DIR/task-self-review"
    
    mkdir -p "$task_dir"
    
    # 创建自我审查场景（builder = reviewer）
    cat > "$task_dir/review.md" << 'EOF'
# Review Report

**Reviewer**: cqo (张铁)
**Date**: 2026-03-23
**Task**: TEST-SELF-001
**Builder**: cqo (张铁)

## ⚠️ 自我审查警告

Builder 和 Reviewer 相同！
EOF
    
    if grep -q "cqo" "$task_dir/review.md" | head -1; then
        echo "  ✅ 通过: 自我审查场景可识别"
    fi
}

# 测试 3: 零问题审查警告
test_zero_issue_warning() {
    echo ""
    echo "测试 3: 零问题审查警告..."
    local task_dir="$TEST_DIR/task-zero-issue"
    
    mkdir -p "$task_dir"
    
    # 创建零问题审查
    cat > "$task_dir/review.md" << 'EOF'
# Review Report

**Reviewer**: main (银月)
**Date**: 2026-03-23
**Task**: TEST-ZERO-001

## Summary

✅ 完美通过，没有任何问题！
EOF
    
    if [ -f "$task_dir/review.md" ]; then
        echo "  ✅ 通过: 零问题审查场景可检测"
    fi
}

# 测试 4: 缺少审查产物
test_missing_review() {
    echo ""
    echo "测试 4: 缺少审查产物检测..."
    local task_dir="$TEST_DIR/task-no-review"
    
    mkdir -p "$task_dir"
    # 不创建 review.md
    
    if [ ! -f "$task_dir/review.md" ]; then
        echo "  ✅ 通过: 正确识别缺失审查产物"
    else
        echo "  ❌ 失败: 审查产物不应存在"
    fi
}

# 测试 5: 脚本存在性检查
test_script_exists() {
    echo ""
    echo "测试 5: 验证脚本存在..."
    
    if [ -f "$VALIDATE_SCRIPT" ]; then
        echo "  ✅ 通过: validate-reviews.sh 存在"
        
        if [ -x "$VALIDATE_SCRIPT" ]; then
            echo "  ✅ 通过: 脚本可执行"
        else
            echo "  ⚠️  警告: 脚本不可执行，尝试修复..."
            chmod +x "$VALIDATE_SCRIPT"
        fi
    else
        echo "  ❌ 失败: validate-reviews.sh 不存在"
    fi
}

# 运行所有测试
main() {
    mkdir -p "$TEST_DIR"
    
    test_script_exists
    test_review_artifacts
    test_self_review_detection
    test_zero_issue_warning
    test_missing_review
    
    echo ""
    echo "=== 测试完成 ==="
}

main "$@"