#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_pdca_simulation.py - PDCA 全流程模拟测试

模拟 7 个场景，覆盖完整 harness 执行序列：
  S1: L1 自验收完整循环（P→D→C(pass)→A）
  S2: L3 human-in-the-loop 循环（P→D→C(pending)→Harold回复→C(pass)→A）
  S3: 失败后重试收敛（fail cycle → 新 cycle pass）
  S4: p() 放弃 pending 重新规划
  S5: 超时检测（days_waiting + is_overdue）
  S6: ADAS 规则守卫（L0/L1 拒 pending，L3 首次拒非 pending）
  S7: 连续 do 内容相同检测 + status/pending CLI
"""

import os
import sys
import json
import shutil
import time
from datetime import datetime, timezone, timedelta

# 以 skill 根目录为 CWD（pdca.py 的 _setup() 期望）
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(SKILL_ROOT)
sys.path.insert(0, SKILL_ROOT)

import scripts.pdca as pdca

# ── 测试基础设施 ─────────────────────────────────────
PASS = "✓"
FAIL = "✗"
results = []

def ok(label, cond, detail=""):
    sym = PASS if cond else FAIL
    results.append((sym, label))
    print(f"  {sym}  {label}" + (f" — {detail}" if detail else ""))
    if not cond:
        print(f"      ↳ DETAIL: {detail}")

def section(name):
    print(f"\n{'─'*60}")
    print(f"  {name}")
    print(f"{'─'*60}")

def cleanup(*task_ids):
    for tid in task_ids:
        path = pdca._record_path(tid)
        if os.path.exists(path):
            os.remove(path)

os.makedirs("pdca", exist_ok=True)

# ════════════════════════════════════════════════════
# S1: L1 自验收完整循环
# ════════════════════════════════════════════════════
section("S1: L1 自验收完整循环（P→D→C(pass)→A）")
TID = "sim-s1"
cleanup(TID)

r = pdca.p(TID, "第一轮：实现功能 X", ["标准A", "标准B"])
ok("p() 返回 ok", r['ok'])
ok("p() cycle_index=1", r['cycle_index'] == 1)
ok("p() phase=plan", r['phase'] == 'plan')

r = pdca.d(TID, "完成功能 X，修改了 foo.py", "completed")
ok("d() 返回 ok", r['ok'])
ok("d() phase=do", r['phase'] == 'do')

r = pdca.c(TID, "pass", "L1", ["标准A: 通过", "标准B: 通过"])
ok("c(pass,L1) 返回 ok", r['ok'])
ok("c(pass,L1) phase=act", r['phase'] == 'act')
ok("c(pass,L1) needs_act=True", r['needs_act'])

r = pdca.a(TID, "功能 X 完成，下一任务 S1-T2", next_task="S1-T2", lessons=["标准B 需提前确认"])
ok("a() 返回 ok", r['ok'])
ok("a() phase=completed", r['phase'] == 'completed')
ok("a() next_task=S1-T2", r['next_task'] == 'S1-T2')

s = pdca.get_status(TID)
ok("status: cycles_total=1", s['cycles_total'] == 1)
ok("status: current_phase=completed", s['current_phase'] == 'completed')
ok("status: current_verdict=pass", s['current_verdict'] == 'pass')
cleanup(TID)

# ════════════════════════════════════════════════════
# S2: L3 human-in-the-loop 完整循环
# ════════════════════════════════════════════════════
section("S2: L3 Human-in-the-Loop（P→D→C(pending)→Harold回复→C(pass)→A）")
TID = "sim-s2"
cleanup(TID)

pdca.p(TID, "需 Harold 审批的任务", ["审批标准X"])
pdca.d(TID, "交付物已完成", "completed")

# L3 首次调用必须 pending
r = pdca.c(TID, "pending", "L3", ["自查通过，提交 Harold 审批"])
ok("L3 首次 c(pending) 通过", r['ok'])
ok("L3 首次 phase=check（等待）", r['phase'] == 'check')
ok("L3 首次 needs_act=False", not r['needs_act'])

# 验证 pending list
pending = pdca.get_pending()
ok("pending 列表非空", len(pending) > 0)
p_item = next((x for x in pending if x['task_card_id'] == TID), None)
ok("pending 包含 sim-s2", p_item is not None)
ok("pending review_level=L3", p_item and p_item.get('review_level') == 'L3')
ok("pending is_overdue=False（刚创建）", p_item and not p_item.get('is_overdue'))

# 模拟 Harold 回复 "A" → pass
r = pdca.c(TID, "pass", "L3", ["Harold: A 批准，验收标准全部满足"])
ok("Harold 回复后 c(pass,L3) 通过", r['ok'])
ok("Harold 回复后 phase=act", r['phase'] == 'act')

# 执行 Act
r = pdca.a(TID, "Harold 批准，任务完成", next_task="S2-T2")
ok("a() 在 Harold 批准后通过", r['ok'])
ok("a() phase=completed", r['phase'] == 'completed')

# 验证 pending 已清空
pending_after = [x for x in pdca.get_pending() if x['task_card_id'] == TID]
ok("Act 后 pending 列表不再包含 sim-s2", len(pending_after) == 0)
cleanup(TID)

# ════════════════════════════════════════════════════
# S3: 失败后重试收敛（2 cycle）
# ════════════════════════════════════════════════════
section("S3: fail → 新 cycle → pass（持续收敛）")
TID = "sim-s3"
cleanup(TID)

# Cycle 1: fail
pdca.p(TID, "第一轮：未充分测试", ["测试覆盖率>80%"])
pdca.d(TID, "实现了功能但测试覆盖率仅60%", "partial")
pdca.c(TID, "fail", "L1", ["测试覆盖率60%<80%，不通过"])
pdca.a(TID, "根因：测试用例不足；下轮增加边界测试", next_task=TID)

s = pdca.get_status(TID)
ok("Cycle 1 completed，verdict=fail", s['current_phase'] == 'completed' and s['current_verdict'] == 'fail')
ok("Cycle 1 总数=1", s['cycles_total'] == 1)

# Cycle 2: 基于根因改进
r = pdca.p(TID, "第二轮：增加边界测试用例（上次失败：覆盖率不足）", ["测试覆盖率>80%"])
ok("p() 在 completed 后创建 cycle 2", r['cycle_index'] == 2)

pdca.d(TID, "新增 15 个边界测试用例，覆盖率达到85%", "completed")
pdca.c(TID, "pass", "L1", ["覆盖率85%>80% ✓"])
pdca.a(TID, "收敛成功，测试覆盖率满足标准", next_task="S3-T2")

s = pdca.get_status(TID)
ok("Cycle 2 completed，verdict=pass", s['current_phase'] == 'completed' and s['current_verdict'] == 'pass')
ok("总 cycles=2，体现迭代历史", s['cycles_total'] == 2)
ok("current_cycle_index=2", s['current_cycle_index'] == 2)
cleanup(TID)

# ════════════════════════════════════════════════════
# S4: p() 放弃 pending 重新规划
# ════════════════════════════════════════════════════
section("S4: p() 放弃 L3 pending，重新规划")
TID = "sim-s4"
cleanup(TID)

pdca.p(TID, "第一轮计划")
pdca.d(TID, "完成了一些工作", "partial")
pdca.c(TID, "pending", "L3")  # L3 pending

s = pdca.get_status(TID)
ok("初始 phase=check，verdict=pending", s['current_phase'] == 'check' and s['current_verdict'] == 'pending')
ok("初始 cycle_index=1", s['current_cycle_index'] == 1)

# 放弃 pending，重新规划 → 应创建新 cycle
r = pdca.p(TID, "放弃等待，重新规划（调整方案）")
ok("p() 在 pending 时创建新 cycle", r['cycle_index'] == 2)
ok("新 cycle phase=plan", r['phase'] == 'plan')

s = pdca.get_status(TID)
ok("status 显示 cycle=2，phase=plan", s['current_cycle_index'] == 2 and s['current_phase'] == 'plan')
cleanup(TID)

# ════════════════════════════════════════════════════
# S5: 超时检测（days_waiting + is_overdue）
# ════════════════════════════════════════════════════
section("S5: 超时检测（模拟 8 天前提交的 pending）")
TID = "sim-s5"
cleanup(TID)

pdca.p(TID, "8天前提交的任务")
pdca.d(TID, "完成", "completed")
pdca.c(TID, "pending", "L3")

# 手动篡改 timestamp 为 8 天前
import yaml
record_path = pdca._record_path(TID)
with open(record_path, 'r') as f:
    rec = yaml.safe_load(f)
old_ts = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
rec['cycles'][-1]['c']['timestamp'] = old_ts
with open(record_path, 'w') as f:
    yaml.dump(rec, f, allow_unicode=True)

pending = pdca.get_pending()
item = next((x for x in pending if x['task_card_id'] == TID), None)
ok("pending 包含超时任务", item is not None)
ok("days_waiting >= 8", item and item.get('days_waiting', 0) >= 8, str(item.get('days_waiting') if item else '?'))
ok("is_overdue=True（>7天）", item and item.get('is_overdue') == True)
cleanup(TID)

# ════════════════════════════════════════════════════
# S6: ADAS 规则守卫
# ════════════════════════════════════════════════════
section("S6: ADAS 规则守卫")
TID = "sim-s6"
cleanup(TID)
pdca.p(TID, "规则测试")
pdca.d(TID, "done", "completed")

# L0 + pending → 拒绝
r = pdca.c(TID, "pending", "L0")
ok("L0 + pending → 拒绝", not r['ok'], r.get('error', ''))

# 重置 phase
cleanup(TID)
pdca.p(TID, "规则测试2")
pdca.d(TID, "done", "completed")

# L1 + pending → 拒绝
r = pdca.c(TID, "pending", "L1")
ok("L1 + pending → 拒绝", not r['ok'], r.get('error', ''))

# L3 + pass（首次）→ 拒绝
r = pdca.c(TID, "pass", "L3")
ok("L3 首次 + pass → 拒绝", not r['ok'], r.get('error', ''))

# L3 + pending（首次）→ 通过
r = pdca.c(TID, "pending", "L3")
ok("L3 首次 + pending → 通过", r['ok'])

# L3 + fail（Harold 回复）→ 通过
r = pdca.c(TID, "fail", "L3", ["Harold: C 拒绝，原因：XXX"])
ok("L3 Harold 回复 fail → 通过", r['ok'] and r['phase'] == 'act')

# invalid verdict → 拒绝
r = pdca.c(TID, "approved", "L1")
ok("invalid verdict 'approved' → 拒绝", not r['ok'])

cleanup(TID)

# ════════════════════════════════════════════════════
# S7: status CLI + pending CLI 格式验证
# ════════════════════════════════════════════════════
section("S7: status / pending 输出格式验证")
TID_A = "sim-s7a"
TID_B = "sim-s7b"
cleanup(TID_A, TID_B)

# s7a: completed task
pdca.p(TID_A, "任务 A", ["标准1"])
pdca.d(TID_A, "完成 A", "completed")
pdca.c(TID_A, "pass", "L1")
pdca.a(TID_A, "A 完成", next_task="s7b")

# s7b: pending task
pdca.p(TID_B, "任务 B，需 Harold 审批")
pdca.d(TID_B, "完成 B", "completed")
pdca.c(TID_B, "pending", "L3")

s_a = pdca.get_status(TID_A)
ok("status 包含 task_card_id", 'task_card_id' in s_a)
ok("status 包含 cycles_total", 'cycles_total' in s_a)
ok("status 包含 current_phase", 'current_phase' in s_a)
ok("status 包含 current_verdict", 'current_verdict' in s_a)
ok("status 包含 last_p_summary", 'last_p_summary' in s_a)
ok("status 包含 last_d_status", 'last_d_status' in s_a)

pending_list = pdca.get_pending()
b_item = next((x for x in pending_list if x['task_card_id'] == TID_B), None)
ok("pending 包含 task_card_id 字段", b_item and 'task_card_id' in b_item)
ok("pending 包含 days_waiting 字段", b_item and 'days_waiting' in b_item)
ok("pending 包含 is_overdue 字段", b_item and 'is_overdue' in b_item)
ok("pending 包含 review_level 字段", b_item and 'review_level' in b_item)
ok("pending 包含 p_summary 字段", b_item and 'p_summary' in b_item)
ok("s7a 完成后不在 pending 中", not any(x['task_card_id'] == TID_A for x in pending_list))

cleanup(TID_A, TID_B)

# ════════════════════════════════════════════════════
# 汇总
# ════════════════════════════════════════════════════
total = len(results)
passed = sum(1 for s, _ in results if s == PASS)
failed = total - passed

print(f"\n{'═'*60}")
print(f"  测试汇总：{passed}/{total} 通过" + (f"，{failed} 失败" if failed else " 🎉"))
print(f"{'═'*60}")

if failed:
    print("\n失败项：")
    for sym, label in results:
        if sym == FAIL:
            print(f"  {sym}  {label}")
    sys.exit(1)
