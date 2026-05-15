#!/bin/bash
# 测试 verify-dod.sh 脚本
# 用法: ./test-verify-dod.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"
VERIFY_SCRIPT="$SKILL_ROOT/scripts/verify-dod.sh"
TEST_DIR="$SCRIPT_DIR/fixtures"

echo "=== DOD 验证脚本测试 ==="
echo ""

# 测试 1: 验证有效 DOD 文件
test_valid_dod() {
    echo "测试 1: 验证有效 DOD 文件..."
    local dod_file="$TEST_DIR/dod-valid.json"
    
    if [ ! -f "$dod_file" ]; then
        echo "  创建测试文件: $dod_file"
        cat > "$dod_file" << 'EOF'
{
  "task_id": "TEST-001",
  "version": "1.0",
  "created_by": "coo",
  "created_at": "2026-03-23T12:00:00+08:00",
  "locked": true,
  "criteria": [
    {
      "id": "DOD-1",
      "category": "functional",
      "description": "功能测试通过",
      "required": true,
      "met": true,
      "verified_by": "cqo",
      "verified_at": "2026-03-23T14:00:00+08:00"
    },
    {
      "id": "DOD-2",
      "category": "documentation",
      "description": "文档完整",
      "required": true,
      "met": true,
      "verified_by": "cqo",
      "verified_at": "2026-03-23T14:00:00+08:00"
    }
  ]
}
EOF
    fi
    
    local result
    result=$("$VERIFY_SCRIPT" "$dod_file" 2>&1) || true
    
    if echo "$result" | grep -q "OK\|PASS"; then
        echo "  ✅ 通过: 有效 DOD 验证成功"
    else
        echo "  ⚠️  结果: $result"
    fi
}

# 测试 2: 验证无效 DOD 文件（缺少必填字段）
test_invalid_dod() {
    echo ""
    echo "测试 2: 验证无效 DOD 文件..."
    local dod_file="$TEST_DIR/dod-invalid.json"
    
    if [ ! -f "$dod_file" ]; then
        echo "  创建测试文件: $dod_file"
        cat > "$dod_file" << 'EOF'
{
  "task_id": "TEST-002",
  "criteria": [
    {
      "id": "DOD-1",
      "description": "缺少必填字段",
      "required": true,
      "met": false
    }
  ]
}
EOF
    fi
    
    local result
    result=$("$VERIFY_SCRIPT" "$dod_file" 2>&1) || true
    
    if echo "$result" | grep -q "FAIL\|ERROR"; then
        echo "  ✅ 通过: 正确检测到无效 DOD"
    else
        echo "  ⚠️  结果: $result"
    fi
}

# 测试 3: 验证未满足所有 required 的 DOD
test_unmet_required() {
    echo ""
    echo "测试 3: 验证未满足 required 标准..."
    local dod_file="$TEST_DIR/dod-unmet.json"
    
    if [ ! -f "$dod_file" ]; then
        echo "  创建测试文件: $dod_file"
        cat > "$dod_file" << 'EOF'
{
  "task_id": "TEST-003",
  "version": "1.0",
  "created_by": "coo",
  "created_at": "2026-03-23T12:00:00+08:00",
  "locked": true,
  "criteria": [
    {
      "id": "DOD-1",
      "category": "functional",
      "description": "已满足",
      "required": true,
      "met": true
    },
    {
      "id": "DOD-2",
      "category": "documentation",
      "description": "未满足",
      "required": true,
      "met": false
    }
  ]
}
EOF
    fi
    
    local result
    result=$("$VERIFY_SCRIPT" "$dod_file" 2>&1) || true
    
    if echo "$result" | grep -q "FAIL\|unmet"; then
        echo "  ✅ 通过: 正确检测到未满足的 required 标准"
    else
        echo "  ⚠️  结果: $result"
    fi
}

# 测试 4: Schema 验证
test_schema_validation() {
    echo ""
    echo "测试 4: Schema 文件验证..."
    local schema_file="$SKILL_ROOT/schemas/dod.schema.json"
    
    if [ -f "$schema_file" ]; then
        echo "  ✅ 通过: Schema 文件存在"
        
        # 检查 JSON 格式
        if python3 -c "import json; json.load(open('$schema_file'))" 2>/dev/null; then
            echo "  ✅ 通过: Schema 是有效 JSON"
        else
            echo "  ❌ 失败: Schema 不是有效 JSON"
        fi
    else
        echo "  ❌ 失败: Schema 文件不存在"
    fi
}

# 运行所有测试
main() {
    mkdir -p "$TEST_DIR"
    
    test_schema_validation
    test_valid_dod
    test_invalid_dod
    test_unmet_required
    
    echo ""
    echo "=== 测试完成 ==="
}

main "$@"