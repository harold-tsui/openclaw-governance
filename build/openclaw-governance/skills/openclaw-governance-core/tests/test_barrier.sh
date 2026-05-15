#!/bin/bash
# test_barrier.sh - Phase 屏障规则测试脚本
#
# Version: 7.0.0
# Author: Governance Core Team
# Created: 2026-04-22
#
# Usage:
#     bash test_barrier.sh
#     bash test_barrier.sh --help

set -e

SCRIPTS_DIR="${HOME}/Workspaces/openclaw/main/skills/openclaw-governance/skills/openclaw-governance-core/scripts"
STATE_FILE="${HOME}/Workspaces/openclaw/main/.system/governance/current/gov-state.json"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS_COUNT=0
FAIL_COUNT=0

pass() {
    echo "${GREEN}✅ PASS: $1${NC}"
    PASS_COUNT=$((PASS_COUNT + 1))
}

fail() {
    echo "${RED}❌ FAIL: $1${NC}"
    echo "   Reason: $2"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

# 测试 1：PhaseBarrierLock 类
test_barrier_lock_class() {
    echo "${BLUE}=== Test 1: PhaseBarrierLock Class ===${NC}"
    
    # 测试类定义存在
    if grep -q "class PhaseBarrierLock" "${SCRIPTS_DIR}/barrier_lock.py"; then
        pass "PhaseBarrierLock class defined"
    else
        fail "PhaseBarrierLock class missing" "Class not found"
    fi
    
    # 测试 __enter__ 和 __exit__ 存在
    if grep -q "__enter__" "${SCRIPTS_DIR}/barrier_lock.py"; then
        pass "__enter__ method exists"
    else
        fail "__enter__ missing" "Method not found"
    fi
    
    if grep -q "__exit__" "${SCRIPTS_DIR}/barrier_lock.py"; then
        pass "__exit__ method exists"
    else
        fail "__exit__ missing" "Method not found"
    fi
    
    # 测试 lock_snapshot 方法
    if grep -q "def lock_snapshot" "${SCRIPTS_DIR}/barrier_lock.py"; then
        pass "lock_snapshot method exists"
    else
        fail "lock_snapshot missing" "Method not found"
    fi
    
    # 测试 unlock_snapshot 方法
    if grep -q "def unlock_snapshot" "${SCRIPTS_DIR}/barrier_lock.py"; then
        pass "unlock_snapshot method exists"
    else
        fail "unlock_snapshot missing" "Method not found"
    fi
}

# 测试 2：状态快照锁定
test_state_lock() {
    echo "${BLUE}=== Test 2: State Lock ===${NC}"
    
    # 运行 Python 测试
    python3 -c "
import sys
sys.path.insert(0, '${SCRIPTS_DIR}')
from barrier_lock import PhaseBarrierLock

# 测试上下文管理器
with PhaseBarrierLock() as barrier:
    barrier.lock_snapshot({'core': 'success', 'config': 'degraded'})
    
    # 测试状态获取
    state = barrier.get_state('core')
    assert state == 'success', f'Expected success, got {state}'
    
    # 测试 FIX-2: 返回 'failed' 而非 'unknown'
    state = barrier.get_state('nonexistent')
    assert state == 'failed', f'Expected failed, got {state}'
    
    assert barrier.locked == True, 'Barrier should be locked'

# 测试自动 unlock
assert barrier.locked == False, 'Barrier should be unlocked after context exit'

print('✅ State lock tests passed')
" 2>&1
    
    if [ $? -eq 0 ]; then
        pass "State lock tests passed"
    else
        fail "State lock tests failed" "Python test error"
    fi
}

# 测试 3：阻塞条件检查
test_blocking_conditions() {
    echo "${BLUE}=== Test 3: Blocking Conditions ===${NC}"
    
    # 创建测试状态文件
    mkdir -p "${HOME}/Workspaces/openclaw/main/.system/governance/current"
    
    python3 -c "
import sys
sys.path.insert(0, '${SCRIPTS_DIR}')
from state_manager import StateManager
from pathlib import Path
import json

# 创建测试状态
state_file = Path('${STATE_FILE}')
state_file.parent.mkdir(parents=True, exist_ok=True)

# 测试 1: hierarchy failed → 阻塞
with open(state_file, 'w') as f:
    json.dump({
        'hierarchy': 'failed',
        'delegation': 'success',
        'core': 'success'
    }, f)

manager = StateManager(state_file)
blocked = manager.check_blocking_conditions()
assert blocked == True, 'Should be blocked when hierarchy failed'

# 测试 2: delegation failed → 阻塞
with open(state_file, 'w') as f:
    json.dump({
        'hierarchy': 'success',
        'delegation': 'failed',
        'core': 'success'
    }, f)

manager = StateManager(state_file)
blocked = manager.check_blocking_conditions()
assert blocked == True, 'Should be blocked when delegation failed'

# 测试 3: 无阻塞
with open(state_file, 'w') as f:
    json.dump({
        'hierarchy': 'success',
        'delegation': 'success',
        'core': 'success'
    }, f)

manager = StateManager(state_file)
blocked = manager.check_blocking_conditions()
assert blocked == False, 'Should not be blocked when all success'

print('✅ Blocking condition tests passed')
" 2>&1
    
    if [ $? -eq 0 ]; then
        pass "Blocking condition tests passed"
    else
        fail "Blocking condition tests failed" "Python test error"
    fi
}

# 测试 4：降级阈值检测
test_degradation_threshold() {
    echo "${BLUE}=== Test 4: Degradation Threshold ===${NC}"
    
    python3 -c "
import sys
sys.path.insert(0, '${SCRIPTS_DIR}')
from state_manager import StateManager
from pathlib import Path
import json

state_file = Path('${STATE_FILE}')

# 测试 1: 40% 降级阈值
with open(state_file, 'w') as f:
    json.dump({
        'core': 'success',
        'config': 'degraded',
        'dispatch': 'success',
        'hierarchy': 'failed',
        'data': 'degraded',
        'quality': 'degraded',
        'delegation': 'success',
        'task': 'success'
    }, f)

manager = StateManager(state_file)
exceeded = manager.check_degradation_threshold()
assert exceeded == True, f'Should exceed threshold (4/8 = 50%)'

# 测试 2: 未超过阈值
with open(state_file, 'w') as f:
    json.dump({
        'core': 'success',
        'config': 'degraded',
        'dispatch': 'success',
        'hierarchy': 'success',
        'data': 'success',
        'quality': 'success',
        'delegation': 'success',
        'task': 'success'
    }, f)

manager = StateManager(state_file)
exceeded = manager.check_degradation_threshold()
assert exceeded == False, 'Should not exceed threshold (1/8 = 12.5%)'

print('✅ Degradation threshold tests passed')
" 2>&1
    
    if [ $? -eq 0 ]; then
        pass "Degradation threshold tests passed"
    else
        fail "Degradation threshold tests failed" "Python test error"
    fi
}

# 主函数
main() {
    echo "${BLUE}========================================${NC}"
    echo "${BLUE}  Phase Barrier Tests${NC}"
    echo "${BLUE}========================================${NC}"
    echo ""
    
    test_barrier_lock_class
    test_state_lock
    test_blocking_conditions
    test_degradation_threshold
    
    echo ""
    echo "${BLUE}========================================${NC}"
    echo "${GREEN}Summary: ${PASS_COUNT} passed, ${FAIL_COUNT} failed${NC}"
    echo "${BLUE}========================================${NC}"
    
    if [ "$FAIL_COUNT" -gt 0 ]; then
        echo "${RED}Some tests failed.${NC}"
        exit 1
    else
        echo "${GREEN}All tests passed! ✅${NC}"
        exit 0
    fi
}

# 参数解析
while [ "$#" -gt 0 ]; do
    case "$1" in
        --help)
            echo "Usage: bash test_barrier.sh [--help]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

main