#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NUCLEUS 4.0 - 真实 Heartbeat 模拟验证

验证完整的自动进化流程：
1. Heartbeat 进入方式
2. MISSION_BOARD 结构
3. Task-Card 选择
4. Skills 加载
5. PDCA 循环（Check 模拟 Harold 评审）
6. Act 等待下一个 Heartbeat

Author: 张铁 (CQO)
Date: 2026-04-06
"""

import os
import sys
import yaml
import json
from datetime import datetime, timezone

# ========================================
# 配置
# ========================================

PROJECT_DIR = "/Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0"
AGENT_WORKSPACE = "/Users/haroldtsui/Workspaces/openclaw/main/60_Agents/cqo"
GOVERNANCE_SKILLS = os.path.expanduser("~/.openclaw/skills/openclaw-governance/skills")

# 添加项目根目录到 Python 路径
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, "core"))
sys.path.insert(0, os.path.join(PROJECT_DIR, "modules"))

# ========================================
# 配置
# ========================================

PROJECT_DIR = "/Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0"
AGENT_WORKSPACE = "/Users/haroldtsui/Workspaces/openclaw/main/60_Agents/cqo"
GOVERNANCE_SKILLS = os.path.expanduser("~/.openclaw/skills/openclaw-governance/skills")

# ========================================
# Step 1: 模拟 Heartbeat 进入
# ========================================

def simulate_heartbeat_entry():
    """模拟 Heartbeat 进入，验证进入方式"""
    print("=" * 60)
    print("Step 1: 模拟 Heartbeat 进入")
    print("=" * 60)
    
    # 读取 AGENTS.md 验证进入方式
    agents_md_path = os.path.join(AGENT_WORKSPACE, "AGENTS.md")
    
    if os.path.exists(agents_md_path):
        print("\n✅ AGENTS.md 存在")
        with open(agents_md_path, 'r') as f:
            content = f.read()
        
        # 检查关键内容
        checks = {
            "Every Session": "## Every Session" in content or "# Every Session" in content,
            "SOUL.md": "SOUL.md" in content,
            "USER.md": "USER.md" in content,
            "memory": "memory" in content,
            "MISSION_BOARD": "MISSION_BOARD" in content or "MISSION-BOARD" in content
        }
        
        print("\n   AGENTS.md 内容检查:")
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
        
        # 检查进入指令
        if "read" in content.lower() and "memory" in content.lower():
            print("\n   ✅ Heartbeat 进入方式正确：read memory 文件")
            return True
        else:
            print("\n   ❌ Heartbeat 进入方式不完整")
            return False
    else:
        print(f"\n❌ AGENTS.md 不存在: {agents_md_path}")
        return False

# ========================================
# Step 2: 读取 MISSION_BOARD
# ========================================

def read_mission_board():
    """读取 MISSION_BOARD，验证结构"""
    print("\n" + "=" * 60)
    print("Step 2: 读取 MISSION_BOARD")
    print("=" * 60)
    
    mission_board_path = os.path.join(AGENT_WORKSPACE, "MISSION_BOARD.md")
    
    if os.path.exists(mission_board_path):
        print("\n✅ MISSION_BOARD.md 存在")
        
        with open(mission_board_path, 'r') as f:
            content = f.read()
        
        # 检查结构
        required_sections = [
            "当前状态",
            "Project",
            "Topic", 
            "Task",
            "阻塞",
            "待处理"
        ]
        
        print("\n   MISSION_BOARD 结构检查:")
        found_sections = []
        for section in required_sections:
            if section in content:
                found_sections.append(section)
                print(f"   ✅ {section}")
            else:
                print(f"   ⚠️  缺少: {section}")
        
        # 检查是否聚焦当前项目
        if "ZT-P015" in content or "NUCLEUS" in content or "4.0" in content:
            print("\n   ✅ 聚焦当前项目 (NUCLEUS 4.0)")
        else:
            print("\n   ⚠️  未明确聚焦当前项目")
        
        return content
    else:
        print(f"\n❌ MISSION_BOARD.md 不存在: {mission_board_path}")
        return None

# ========================================
# Step 3: 找到待推进 Task-Card
# ========================================

def find_task_card(mission_board_content):
    """从 MISSION_BOARD 找到待推进的 Task-Card"""
    print("\n" + "=" * 60)
    print("Step 3: 找到待推进 Task-Card")
    print("=" * 60)
    
    # 解析 MISSION_BOARD 找到待处理 Task
    # 这里简化处理，直接选择 T0.1 作为验证目标
    
    task_id = "T0.1"
    task_name = "接入契约"
    task_card_path = f"tasks/{task_id}_TASK-CARD.md"
    
    # 检查 Task-Card 是否存在
    full_path = os.path.join(PROJECT_DIR, task_card_path)
    
    if os.path.exists(full_path):
        print(f"\n✅ 找到 Task-Card: {task_card_path}")
        
        with open(full_path, 'r') as f:
            task_content = f.read()
        
        # 提取关键信息
        print(f"\n   Task ID: {task_id}")
        print(f"   Task 名称: {task_name}")
        
        # 检查状态
        if "已完成" in task_content or "✅" in task_content:
            print(f"   状态: ✅ 已完成")
            print(f"\n   ⚠️  Task 已完成，选择作为 PDCA 验证目标")
        elif "进行中" in task_content or "🔄" in task_content:
            print(f"   状态: 🔄 进行中")
        else:
            print(f"   状态: 📋 待开始")
        
        return {
            "task_id": task_id,
            "task_name": task_name,
            "task_card_path": full_path,
            "content": task_content
        }
    else:
        print(f"\n❌ Task-Card 不存在: {full_path}")
        return None

# ========================================
# Step 4: 加载 Skills
# ========================================

def load_required_skills(task_info):
    """根据 Task-Card 加载必要的 Skills"""
    print("\n" + "=" * 60)
    print("Step 4: 加载 Skills")
    print("=" * 60)
    
    # 加载 governance-core（必须）
    core_skill_path = os.path.join(GOVERNANCE_SKILLS, "openclaw-governance-core", "SKILL.md")
    
    if os.path.exists(core_skill_path):
        print(f"\n✅ governance-core 已加载")
    else:
        print(f"\n❌ governance-core 不存在")
    
    # 加载 governance-heartbeat（必须）
    heartbeat_skill_path = os.path.join(GOVERNANCE_SKILLS, "openclaw-governance-heartbeat", "SKILL.md")
    
    if os.path.exists(heartbeat_skill_path):
        print(f"✅ governance-heartbeat 已加载")
    else:
        print(f"❌ governance-heartbeat 不存在")
    
    # 加载 governance-nucleus（必须）
    nucleus_skill_path = os.path.join(GOVERNANCE_SKILLS, "openclaw-governance-nucleus", "SKILL.md")
    
    if os.path.exists(nucleus_skill_path):
        print(f"✅ governance-nucleus 已加载")
        
        # 加载脚本
        scripts_path = os.path.join(GOVERNANCE_SKILLS, "openclaw-governance-nucleus", "scripts")
        if os.path.exists(scripts_path):
            sys.path.insert(0, scripts_path)
            print(f"   Scripts 路径: {scripts_path}")
    else:
        print(f"❌ governance-nucleus 不存在")
    
    # 加载 governance-task（如果 Task 管理）
    task_skill_path = os.path.join(GOVERNANCE_SKILLS, "openclaw-governance-task", "SKILL.md")
    
    if os.path.exists(task_skill_path):
        print(f"✅ governance-task 已加载")
    
    return os.path.exists(nucleus_skill_path)

# ========================================
# Step 5: 进入 PDCA 循环
# ========================================

def run_pdca_cycle(task_info, cycle_number=1):
    """运行 PDCA 循环"""
    print("\n" + "=" * 60)
    print(f"Step 5: PDCA 循环 #{cycle_number}")
    print("=" * 60)
    
    # 保存当前工作目录并切换到项目根目录
    original_dir = os.getcwd()
    os.chdir(PROJECT_DIR)
    print(f"   工作目录已切换到: {os.getcwd()}")
    
    # 确保必要的目录存在
    os.makedirs("cycles/task", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 导入 NUCLEUS 模块
    try:
        from core.scheduler import create_cycle_for_scope
        from modules.plan import determine_review
        from modules.do import execute_cycle
        from modules.check import check_cycle
        from modules.act import adjust_automation_level
    except ImportError as e:
        print(f"\n❌ 模块导入失败: {e}")
        os.chdir(original_dir)  # 恢复目录
        return None
    
    # ========================================
    # Plan 阶段
    # ========================================
    print("\n【Plan 阶段】")
    
    # 1. 计算 review_level
    review_context = determine_review(
        task_card_path=task_info["task_card_path"],
        task_id=task_info["task_id"],
        scope="task"
    )
    
    print(f"   review_level: {review_context['review_level']}")
    print(f"   reviewer: {review_context['reviewer']}")
    
    # 2. 创建 CycleUnit
    print(f"   创建 CycleUnit 前的工作目录: {os.getcwd()}")
    print(f"   cycles/task 目录存在性: {os.path.exists('cycles/task')}")
    
    cycle_id = create_cycle_for_scope('task')
    
    if cycle_id:
        print(f"   ✅ CycleUnit: {cycle_id}")
    else:
        print(f"   ❌ CycleUnit 创建失败")
        
        # 检查并发限制
        from core.scheduler import get_active_cycle_count, check_concurrency_limit
        from core.wait_queue import get_wait_queue_size
        
        active_count = get_active_cycle_count('task')
        concurrency_ok = check_concurrency_limit('task')
        wait_queue_size = get_wait_queue_size('task')
        
        print(f"   活跃 CycleUnit 数量: {active_count}")
        print(f"   并发检查: {concurrency_ok}")
        print(f"   等待队列大小: {wait_queue_size}")
        
        os.chdir(original_dir)  # 恢复目录
        return None
    
    # ========================================
    # Do 阶段
    # ========================================
    print("\n【Do 阶段】")
    
    # 执行 Task
    result = execute_cycle(cycle_id)
    
    print(f"   状态: {result['status']}")
    print(f"   执行的 actions: {result['actions_executed']}")
    
    # ========================================
    # Check 阶段 - 模拟 Harold 评审
    # ========================================
    print("\n【Check 阶段 - 模拟 Harold 评审】")
    
    check_result = check_cycle(cycle_id)
    
    print(f"   verdict: {check_result['verdict']}")
    print(f"   evidence: {len(check_result['evidence'])} 条")
    
    # ⚠️ 这里需要模拟 Harold 的评审输入
    # 在真实场景中，Harold 会查看 evidence 并给出评审意见
    
    print(f"\n   📋 等待 Harold 评审...")
    print(f"   模拟评审结果: {check_result['verdict']}")
    
    # ========================================
    # Act 阶段 - 等待下一个 Heartbeat
    # ========================================
    print("\n【Act 阶段 - 等待下一个 Heartbeat】")
    
    adjustments = adjust_automation_level(
        cycle_id=cycle_id,
        verdict=check_result['verdict'],
        consecutive_count=cycle_number - 1,
        current_level="L2",
        evidence=[]
    )
    
    for adj in adjustments:
        print(f"   {adj['from']} → {adj['to']}: {adj['reason']}")
    
    print(f"\n   ⏸️  Act 已完成，等待下一个 Heartbeat 触发...")
    
    # 还原原始工作目录
    os.chdir(original_dir)
    
    return {
        "cycle_number": cycle_number,
        "cycle_id": cycle_id,
        "review_level": review_context['review_level'],
        "verdict": check_result['verdict'],
        "adjustments": adjustments
    }

# ========================================
# 主函数
# ========================================

def main():
    """运行完整的 Heartbeat 模拟验证"""
    print("=" * 60)
    print("NUCLEUS 4.0 - 真实 Heartbeat 模拟验证")
    print("=" * 60)
    
    # Step 1: Heartbeat 进入
    if not simulate_heartbeat_entry():
        print("\n❌ Heartbeat 进入验证失败")
        return
    
    # Step 2: 读取 MISSION_BOARD
    mission_board = read_mission_board()
    if not mission_board:
        print("\n❌ MISSION_BOARD 读取失败")
        return
    
    # Step 3: 找到 Task-Card
    task_info = find_task_card(mission_board)
    if not task_info:
        print("\n❌ Task-Card 查找失败")
        return
    
    # Step 4: 加载 Skills
    if not load_required_skills(task_info):
        print("\n❌ Skills 加载失败")
        return
    
    # Step 5: 运行 PDCA
    result = run_pdca_cycle(task_info, cycle_number=1)
    
    if result:
        print("\n" + "=" * 60)
        print("✅ Heartbeat 模拟验证完成")
        print("=" * 60)
        print(f"\n   已完成 PDCA 循环 #{result['cycle_number']}")
        print(f"   等待下一个 Heartbeat 触发下一个 PDCA...")

if __name__ == "__main__":
    main()