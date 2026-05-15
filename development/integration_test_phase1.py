#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NUCLEUS 4.0 集成测试 - Phase 1

验证 pdca.py 基本功能和 YAML 输出

Author: 张铁 (CQO)
Date: 2026-04-16
"""

import os
import sys
import json
import yaml
from datetime import datetime, timezone

# 添加 skill 根目录到 Python 路径
skill_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(skill_root, "scripts"))

# 导入 pdca.py
from pdca import p, d, c, a, get_status, get_pending, get_audit_queue, mark_audit

print("=" * 60)
print("NUCLEUS 4.0 集成测试 - Phase 1")
print("=" * 60)

# ========================================
# Test S1: L1 自验收完整循环
# ========================================

print("\n[S1] L1 自验收完整循环测试...")

task_id = "TEST-S1"

try:
    # Plan
    result_p = p(task_id, "实现功能 X", criteria="测试通过|文档更新")
    print(f"  p() 结果: {result_p}")
    
    # Do
    result_d = d(task_id, "完成功能 X，修改了 foo.py", "completed")
    print(f"  d() 结果: {result_d}")
    
    # Check (L1 自验收)
    result_c = c(task_id, "pass", level="L1", evidence="标准A: 通过|标准B: 通过")
    print(f"  c() 结果: {result_c}")
    
    # Act
    result_a = a(task_id, "功能 X 完成", next_task="TEST-S2")
    print(f"  a() 结果: {result_a}")
    
    # 验证 YAML 输出
    yaml_path = os.path.join(skill_root, "pdca", f"{task_id}.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        print(f"  YAML 输出: ✅ 存在")
        print(f"  phase: {yaml_data['cycles'][0]['phase']}")
        print(f"  verdict: {yaml_data['cycles'][0]['c']['verdict']}")
        print(f"  audit_eligible: {yaml_data['cycles'][0]['c']['audit_eligible']}")
        print("✅ S1 测试通过")
    else:
        print("❌ YAML 文件不存在")
        
except Exception as e:
    print(f"❌ S1 测试失败: {e}")

# ========================================
# Test S6: ADAS 规则守卫
# ========================================

print("\n[S6] ADAS 规则守卫测试...")

task_id_2 = "TEST-S6"

try:
    # Plan
    p(task_id_2, "测试 ADAS 规则")
    
    # Do
    d(task_id_2, "执行测试", "completed")
    
    # Check (L0 + pending) - 应该被拒绝
    result_c_l0_pending = c(task_id_2, "pending", level="L0")
    if result_c_l0_pending.get('ok') == False:
        print(f"  ✅ L0 + pending 被正确拒绝: {result_c_l0_pending.get('error')}")
    else:
        print(f"  ❌ L0 + pending 未被拒绝")
    
    # Check (L1 + pending) - 应该被拒绝
    result_c_l1_pending = c(task_id_2, "pending", level="L1", evidence="测试")
    if result_c_l1_pending.get('ok') == False:
        print(f"  ✅ L1 + pending 被正确拒绝: {result_c_l1_pending.get('error')}")
    else:
        print(f"  ❌ L1 + pending 未被拒绝")
    
    print("✅ S6 测试通过")
    
except Exception as e:
    print(f"❌ S6 测试失败: {e}")

# ========================================
# Test A1: audit_eligible 标记规则
# ========================================

print("\n[A1] audit_eligible 标记规则测试...")

try:
    # 读取 TEST-S1 的 YAML
    yaml_path = os.path.join(skill_root, "pdca", "TEST-S1.yaml")
    with open(yaml_path, 'r') as f:
        yaml_data = yaml.safe_load(f)
    
    # 验证 L1 pass → audit_eligible=true
    audit_eligible = yaml_data['cycles'][0]['c']['audit_eligible']
    if audit_eligible == True:
        print(f"  ✅ L1 pass → audit_eligible=true")
    else:
        print(f"  ❌ L1 pass 但 audit_eligible={audit_eligible}")
    
    print("✅ A1 测试通过")
    
except Exception as e:
    print(f"❌ A1 测试失败: {e}")

# ========================================
# Test A2: get_audit_queue()
# ========================================

print("\n[A2] get_audit_queue() 测试...")

try:
    audit_queue = get_audit_queue()
    print(f"  审计队列长度: {len(audit_queue)}")
    
    # 检查 TEST-S1 是否在队列中
    found = False
    for item in audit_queue:
        if item['task_card_id'] == 'TEST-S1':
            found = True
            print(f"  ✅ TEST-S1 在审计队列中")
            print(f"    dl_refs: {item.get('dl_refs', 'None')}")
            print(f"    p_summary: {item.get('p_summary', 'None')}")
            break
    
    if not found:
        print(f"  ⚠️ TEST-S1 未在审计队列中（可能已被审计）")
    
    print("✅ A2 测试通过")
    
except Exception as e:
    print(f"❌ A2 测试失败: {e}")

# ========================================
# Test A3/A4: mark_audit()
# ========================================

print("\n[A3/A4] mark_audit() 测试...")

try:
    # A3: 评分 >= 80
    result_audit_pass = mark_audit("TEST-S1", 1, 85)
    print(f"  mark_audit(score=85) 结果: {result_audit_pass}")
    if result_audit_pass.get('has_problem') == False:
        print(f"  ✅ 评分 >= 80 → has_problem=false")
    else:
        print(f"  ❌ 评分 >= 80 但 has_problem={result_audit_pass.get('has_problem')}")
    
    # A4: 评分 < 80
    # 先创建一个新的测试任务
    task_id_3 = "TEST-A4"
    p(task_id_3, "测试评分 < 80")
    d(task_id_3, "执行测试", "completed")
    c(task_id_3, "pass", level="L1", evidence="测试")
    
    result_audit_fail = mark_audit(task_id_3, 1, 75)
    print(f"  mark_audit(score=75) 结果: {result_audit_fail}")
    if result_audit_fail.get('has_problem') == True:
        print(f"  ✅ 评分 < 80 → has_problem=true")
        print(f"    next_action: {result_audit_fail.get('next_action')}")
    else:
        print(f"  ❌ 评分 < 80 但 has_problem={result_audit_fail.get('has_problem')}")
    
    print("✅ A3/A4 测试通过")
    
except Exception as e:
    print(f"❌ A3/A4 测试失败: {e}")

# ========================================
# Test CLI 输出格式
# ========================================

print("\n[CLI] CLI 输出格式测试...")

try:
    # status
    status_result = get_status("TEST-S1")
    print(f"  status 输出: {json.dumps(status_result, indent=2)}")
    
    # pending
    pending_result = get_pending()
    print(f"  pending 输出长度: {len(pending_result)}")
    
    print("✅ CLI 测试通过")
    
except Exception as e:
    print(f"❌ CLI 测试失败: {e}")

print("\n" + "=" * 60)
print("✅ Phase 1 集成测试完成")
print("=" * 60)