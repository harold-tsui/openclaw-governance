#!/bin/bash
# test_skill_loading.sh - Skill 加载测试脚本
#
# Version: 7.0.0
# Author: Governance Core Team
# Created: 2026-04-22
#
# Usage:
#     bash test_skill_loading.sh
#     bash test_skill_loading.sh --verbose
#     bash test_skill_loading.sh --help

set -e

# 配置
SKILLS_DIR="${HOME}/Workspaces/openclaw/main/skills/openclaw-governance/skills"
CORE_DIR="${SKILLS_DIR}/openclaw-governance-core"
DISPATCH_DIR="${SKILLS_DIR}/openclaw-governance-dispatch"
TASK_DIR="${SKILLS_DIR}/openclaw-governance-task"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试计数
PASS_COUNT=0
FAIL_COUNT=0

# 函数：测试通过
pass() {
    echo "${GREEN}✅ PASS: $1${NC}"
    PASS_COUNT=$((PASS_COUNT + 1))
}

# 函数：测试失败
fail() {
    echo "${RED}❌ FAIL: $1${NC}"
    echo "   Reason: $2"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

# 函数：测试警告
warn() {
    echo "${YELLOW}⚠️  WARN: $1${NC}"
}

# 测试 1：目录结构
test_directory_structure() {
    echo "${BLUE}=== Test 1: Directory Structure ===${NC}"
    
    # governance-core
    if [ -d "${CORE_DIR}/scripts" ]; then
        pass "governance-core/scripts/ exists"
    else
        fail "governance-core/scripts/ missing" "Directory not found"
    fi
    
    if [ -d "${CORE_DIR}/references" ]; then
        pass "governance-core/references/ exists"
    else
        fail "governance-core/references/ missing" "Directory not found"
    fi
    
    if [ -d "${CORE_DIR}/assets" ]; then
        pass "governance-core/assets/ exists"
    else
        fail "governance-core/assets/ missing" "Directory not found"
    fi
    
    # governance-dispatch
    if [ -d "${DISPATCH_DIR}/scripts" ]; then
        pass "governance-dispatch/scripts/ exists"
    else
        fail "governance-dispatch/scripts/ missing" "Directory not found"
    fi
    
    if [ -d "${DISPATCH_DIR}/references" ]; then
        pass "governance-dispatch/references/ exists"
    else
        fail "governance-dispatch/references/ missing" "Directory not found"
    fi
    
    # governance-task
    if [ -d "${TASK_DIR}/scripts" ]; then
        pass "governance-task/scripts/ exists"
    else
        fail "governance-task/scripts/ missing" "Directory not found"
    fi
    
    if [ -d "${TASK_DIR}/references" ]; then
        pass "governance-task/references/ exists"
    else
        fail "governance-task/references/ missing" "Directory not found"
    fi
}

# 测试 2：脚本文件
test_script_files() {
    echo "${BLUE}=== Test 2: Script Files ===${NC}"
    
    # barrier_lock.py
    if [ -f "${CORE_DIR}/scripts/barrier_lock.py" ]; then
        pass "barrier_lock.py exists"
        
        # 检查 Python 语法
        if python3 -m py_compile "${CORE_DIR}/scripts/barrier_lock.py" 2>/dev/null; then
            pass "barrier_lock.py syntax OK"
        else
            fail "barrier_lock.py syntax error" "Python syntax check failed"
        fi
    else
        fail "barrier_lock.py missing" "File not found"
    fi
    
    # probe_checker.py
    if [ -f "${CORE_DIR}/scripts/probe_checker.py" ]; then
        pass "probe_checker.py exists"
        
        if python3 -m py_compile "${CORE_DIR}/scripts/probe_checker.py" 2>/dev/null; then
            pass "probe_checker.py syntax OK"
        else
            fail "probe_checker.py syntax error" "Python syntax check failed"
        fi
    else
        fail "probe_checker.py missing" "File not found"
    fi
    
    # state_manager.py
    if [ -f "${CORE_DIR}/scripts/state_manager.py" ]; then
        pass "state_manager.py exists"
        
        if python3 -m py_compile "${CORE_DIR}/scripts/state_manager.py" 2>/dev/null; then
            pass "state_manager.py syntax OK"
        else
            fail "state_manager.py syntax error" "Python syntax check failed"
        fi
    else
        fail "state_manager.py missing" "File not found"
    fi
    
    # decision_tree.py
    if [ -f "${DISPATCH_DIR}/scripts/decision_tree.py" ]; then
        pass "decision_tree.py exists"
        
        if python3 -m py_compile "${DISPATCH_DIR}/scripts/decision_tree.py" 2>/dev/null; then
            pass "decision_tree.py syntax OK"
        else
            fail "decision_tree.py syntax error" "Python syntax check failed"
        fi
    else
        fail "decision_tree.py missing" "File not found"
    fi
}

# 测试 3：参考文档
test_reference_files() {
    echo "${BLUE}=== Test 3: Reference Files ===${NC}"
    
    for file in barrier-design.md failure-matrix.md phase-sequence.md pdca-workflow.md; do
        if [ -f "${CORE_DIR}/references/${file}" ]; then
            pass "references/${file} exists"
            
            # 检查 Markdown 格式（至少有标题）
            if grep -q "^#" "${CORE_DIR}/references/${file}" 2>/dev/null; then
                pass "references/${file} has headings"
            else
                warn "references/${file} missing headings"
            fi
        else
            fail "references/${file} missing" "File not found"
        fi
    done
}

# 测试 4：SKILL.md 行数
test_skill_md_lines() {
    echo "${BLUE}=== Test 4: SKILL.md Lines ===${NC}"
    
    MAX_LINES=800
    
    # governance-core
    CORE_LINES=$(wc -l < "${CORE_DIR}/SKILL.md" | tr -d ' ')
    if [ "$CORE_LINES" -lt "$MAX_LINES" ]; then
        pass "governance-core SKILL.md < ${MAX_LINES} lines (${CORE_LINES})"
    else
        warn "governance-core SKILL.md too long (${CORE_LINES} lines)"
    fi
    
    # governance-dispatch
    DISPATCH_LINES=$(wc -l < "${DISPATCH_DIR}/SKILL.md" | tr -d ' ')
    if [ "$DISPATCH_LINES" -lt "$MAX_LINES" ]; then
        pass "governance-dispatch SKILL.md < ${MAX_LINES} lines (${DISPATCH_LINES})"
    else
        warn "governance-dispatch SKILL.md too long (${DISPATCH_LINES} lines)"
    fi
    
    # governance-task
    TASK_LINES=$(wc -l < "${TASK_DIR}/SKILL.md" | tr -d ' ')
    if [ "$TASK_LINES" -lt "$MAX_LINES" ]; then
        pass "governance-task SKILL.md < ${MAX_LINES} lines (${TASK_LINES})"
    else
        warn "governance-task SKILL.md too long (${TASK_LINES} lines)"
    fi
}

# 测试 5：SKILL.md frontmatter
test_frontmatter() {
    echo "${BLUE}=== Test 5: SKILL.md Frontmatter ===${NC}"
    
    # 检查 name 字段
    for dir in "${CORE_DIR}" "${DISPATCH_DIR}" "${TASK_DIR}"; do
        skill_name=$(grep -m1 "^name:" "${dir}/SKILL.md" | cut -d: -f2- | tr -d ' ')
        if [ -n "$skill_name" ]; then
            pass "${dir}/SKILL.md has name: ${skill_name}"
        else
            fail "${dir}/SKILL.md missing name" "Frontmatter incomplete"
        fi
    done
    
    # 检查 version 字段
    for dir in "${CORE_DIR}" "${DISPATCH_DIR}" "${TASK_DIR}"; do
        if grep -q "version:" "${dir}/SKILL.md"; then
            pass "${dir}/SKILL.md has version"
        else
            warn "${dir}/SKILL.md missing version"
        fi
    done
}

# 测试 6：脚本可执行性
test_script_executable() {
    echo "${BLUE}=== Test 6: Script Executable ===${NC}"
    
    # 测试 probe_checker.py --help
    if python3 "${CORE_DIR}/scripts/probe_checker.py" --help >/dev/null 2>&1; then
        pass "probe_checker.py --help works"
    else
        fail "probe_checker.py --help failed" "Script execution error"
    fi
    
    # 测试 state_manager.py --help
    if python3 "${CORE_DIR}/scripts/state_manager.py" --help >/dev/null 2>&1; then
        pass "state_manager.py --help works"
    else
        fail "state_manager.py --help failed" "Script execution error"
    fi
    
    # 测试 decision_tree.py --help
    if python3 "${DISPATCH_DIR}/scripts/decision_tree.py" --help >/dev/null 2>&1; then
        pass "decision_tree.py --help works"
    else
        fail "decision_tree.py --help failed" "Script execution error"
    fi
}

# 主函数
main() {
    echo "${BLUE}========================================${NC}"
    echo "${BLUE}  Governance Skills Refactor Test${NC}"
    echo "${BLUE}========================================${NC}"
    echo ""
    
    test_directory_structure
    test_script_files
    test_reference_files
    test_skill_md_lines
    test_frontmatter
    test_script_executable
    
    echo ""
    echo "${BLUE}========================================${NC}"
    echo "${GREEN}Summary: ${PASS_COUNT} passed, ${FAIL_COUNT} failed${NC}"
    echo "${BLUE}========================================${NC}"
    
    if [ "$FAIL_COUNT" -gt 0 ]; then
        echo "${RED}Some tests failed. Please fix before proceeding.${NC}"
        exit 1
    else
        echo "${GREEN}All tests passed! ✅${NC}"
        exit 0
    fi
}

# 解析参数
VERBOSE=false
while [ "$#" -gt 0 ]; do
    case "$1" in
        --verbose)
            VERBOSE=true
            ;;
        --help)
            echo "Usage: bash test_skill_loading.sh [--verbose] [--help]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# 执行测试
main