#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_pdca_audit_and_routing.py - 审计出口 + 路由路径测试

覆盖场景：
  A1: L0/L1 pass → audit_eligible=True，L2/L3/fail → audit_eligible=False
  A2: get_audit_queue() 只返回未审计的 audit_eligible 条目
  A3: mark_audit() 评分 >= 80（通过）
  A4: mark_audit() 评分 < 80（有问题）→ has_problem=True，dl_refs 可追溯
  A5: mark_audit() 同一条目不可重复审计（audit_result 已存在）
  A6: mark_audit() 错误参数：cycle_index 不存在
  A7: dl_refs 在 Plan 阶段正确记录，audit_queue 返回可追溯
  G1: 模拟 Step 1 任务选择过滤逻辑（只选 [P] 状态任务）
  G2: 直接入口路径（同会话 accept → 立即 PDCA）与 heartbeat 路径等价
  CLI: audit-queue / mark-audit CLI 命令输出格式
"""

import os
import sys
import json
import subprocess

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(SKILL_ROOT)
sys.path.insert(0, SKILL_ROOT)

import scripts.pdca as pdca

PASS = "✓"
FAIL = "✗"
results = []

def ok(label, cond, detail=""):
    sym = PASS if cond else FAIL
    results.append((sym, label))
    print(f"  {sym}  {label}" + (f" — {detail}" if detail else ""))

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
# A1: audit_eligible 标记规则
# ════════════════════════════════════════════════════
section("A1: audit_eligible 标记规则")

for level, verdict, expect_eligible, label in [
    ("L0", "pass",    True,  "L0+pass → eligible=True"),
    ("L1", "pass",    True,  "L1+pass → eligible=True"),
    ("L1", "fail",    False, "L1+fail → eligible=False"),
    ("L2", "pass",    False, "L2+pass → eligible=False（非自验收）"),
    ("L3", "pending", False, "L3+pending → eligible=False"),
]:
    TID = f"a1-{level}-{verdict}"
    cleanup(TID)
    pdca.p(TID, f"plan for {label}")
    pdca.d(TID, "done", "completed")
    if level == "L3" and verdict == "pending":
        r = pdca.c(TID, "pending", "L3")
    elif level == "L2":
        r = pdca.c(TID, "pass", "L2")
    else:
        r = pdca.c(TID, verdict, level)

    import yaml
    with open(pdca._record_path(TID)) as f:
        rec = yaml.safe_load(f)
    actual = rec['cycles'][-1]['c'].get('audit_eligible', False)
    ok(label, actual == expect_eligible, f"got audit_eligible={actual}")
    cleanup(TID)

# ════════════════════════════════════════════════════
# A2: get_audit_queue 只返回未审计的
# ════════════════════════════════════════════════════
section("A2: get_audit_queue() 只返回未审计的 audit_eligible 条目")

TID_A = "a2-eligible"
TID_B = "a2-not-eligible"
TID_C = "a2-already-audited"
cleanup(TID_A, TID_B, TID_C)

# TID_A: eligible，未审计
pdca.p(TID_A, "plan A", dl_refs=["DL-2026-001"])
pdca.d(TID_A, "done A", "completed")
pdca.c(TID_A, "pass", "L1")
pdca.a(TID_A, "act A")

# TID_B: not eligible（L3 pass）
pdca.p(TID_B, "plan B")
pdca.d(TID_B, "done B", "completed")
pdca.c(TID_B, "pending", "L3")
pdca.c(TID_B, "pass", "L3")   # Harold 回复
pdca.a(TID_B, "act B")

# TID_C: eligible 但已审计
pdca.p(TID_C, "plan C")
pdca.d(TID_C, "done C", "completed")
pdca.c(TID_C, "pass", "L0")
pdca.a(TID_C, "act C")
pdca.mark_audit(TID_C, 1, score=90)

queue = pdca.get_audit_queue()
ids_in_queue = [x['task_card_id'] for x in queue]
ok("TID_A 在队列中（eligible 未审计）", TID_A in ids_in_queue)
ok("TID_B 不在队列中（non-eligible）", TID_B not in ids_in_queue)
ok("TID_C 不在队列中（已审计）", TID_C not in ids_in_queue)
cleanup(TID_A, TID_B, TID_C)

# ════════════════════════════════════════════════════
# A3: mark_audit 评分 >= 80（通过）
# ════════════════════════════════════════════════════
section("A3: mark_audit() 评分 >= 80（通过）")
TID = "a3-pass-audit"
cleanup(TID)
pdca.p(TID, "plan", dl_refs=["DL-2026-010"])
pdca.d(TID, "done", "completed")
pdca.c(TID, "pass", "L1")
pdca.a(TID, "act")

r = pdca.mark_audit(TID, 1, score=85)
ok("mark_audit ok=True", r['ok'])
ok("score=85 返回正确", r['score'] == 85)
ok("has_problem=False", not r['has_problem'])
ok("dl_refs 可追溯", r['dl_refs'] == ["DL-2026-010"])
ok("next_action 提示审计通过", "审计通过" in r['next_action'])

# 已审计后不再出现在 audit_queue
queue = [x for x in pdca.get_audit_queue() if x['task_card_id'] == TID]
ok("审计后不再出现在 audit_queue", len(queue) == 0)
cleanup(TID)

# ════════════════════════════════════════════════════
# A4: mark_audit 评分 < 80（有问题）
# ════════════════════════════════════════════════════
section("A4: mark_audit() 评分 < 80（发现问题）")
TID = "a4-fail-audit"
cleanup(TID)
pdca.p(TID, "plan", dl_refs=["DL-2026-007", "DL-2026-003"])
pdca.d(TID, "done", "completed")
pdca.c(TID, "pass", "L0")
pdca.a(TID, "act")

r = pdca.mark_audit(TID, 1, score=72, issues=["规范A未满足", "验收标准B遗漏"])
ok("mark_audit ok=True", r['ok'])
ok("has_problem=True", r['has_problem'])
ok("dl_refs 返回两条", len(r['dl_refs']) == 2)
ok("next_action 提示质疑 DL + popup", "quality" in r['next_action'].lower() or "质疑" in r['next_action'])

import yaml
with open(pdca._record_path(TID)) as f:
    rec = yaml.safe_load(f)
audit_result = rec['cycles'][-1]['c']['audit_result']
ok("issues 写入 yaml", audit_result['issues'] == ["规范A未满足", "验收标准B遗漏"])
ok("score 写入 yaml", audit_result['score'] == 72)
ok("has_problem 写入 yaml", audit_result['has_problem'] is True)
cleanup(TID)

# ════════════════════════════════════════════════════
# A5: mark_audit 错误情况
# ════════════════════════════════════════════════════
section("A5/A6: mark_audit() 错误参数")
TID = "a5-errors"
cleanup(TID)
pdca.p(TID, "plan")
pdca.d(TID, "done", "completed")
pdca.c(TID, "pass", "L1")
pdca.a(TID, "act")

# cycle_index 不存在
r = pdca.mark_audit(TID, 99, score=80)
ok("不存在的 cycle_index → ok=False", not r['ok'])

# 非 audit_eligible（重新创建 L3 任务）
TID2 = "a5-l3"
cleanup(TID2)
pdca.p(TID2, "plan")
pdca.d(TID2, "done", "completed")
pdca.c(TID2, "pending", "L3")
pdca.c(TID2, "pass", "L3")
pdca.a(TID2, "act")
r2 = pdca.mark_audit(TID2, 1, score=85)
ok("L3 pass 非 eligible → ok=False", not r2['ok'])
cleanup(TID, TID2)

# ════════════════════════════════════════════════════
# A7: dl_refs 在 audit_queue 中可追溯
# ════════════════════════════════════════════════════
section("A7: dl_refs 审计追溯")
TID = "a7-dl-trace"
cleanup(TID)
pdca.p(TID, "本轮基于 DL-001 实现自动化", dl_refs=["DL-2026-001", "DL-2026-002"])
pdca.d(TID, "done", "completed")
pdca.c(TID, "pass", "L1")
# 不执行 Act，让它留在 audit_queue

queue = pdca.get_audit_queue()
item = next((x for x in queue if x['task_card_id'] == TID), None)
ok("audit_queue 包含 dl_refs", item and item.get('dl_refs') == ["DL-2026-001", "DL-2026-002"])
ok("audit_queue 包含 p_summary", item and "DL-001" in (item.get('p_summary') or ''))
ok("audit_queue 包含 d_summary", item and 'done' in (item.get('d_summary') or ''))
cleanup(TID)

# ════════════════════════════════════════════════════
# G1: 任务选择只应选 [P] 任务（文档规则验证）
# ════════════════════════════════════════════════════
section("G1: Step 1 任务过滤规则验证（pdca.py 侧）")
# pdca.py 本身不维护 task-card 状态（那是 task SKILL 的事）
# 这里验证：pdca.py status 对"还没有 PDCA 记录"的任务正确返回 cycles_total=0
# 表示 heartbeat 可以用此区分"还没开始 PDCA"的任务
TID = "g1-new-task"
cleanup(TID)
s = pdca.get_status(TID)
ok("新 task 无 PDCA 记录，cycles_total=0", s['cycles_total'] == 0)
ok("current_phase=None", s['current_phase'] is None)
# 一旦进入 PDCA（p 被调用），标志任务开始
pdca.p(TID, "开始第一轮")
s2 = pdca.get_status(TID)
ok("p() 后 cycles_total=1", s2['cycles_total'] == 1)
ok("phase=plan（表明 PDCA 已启动）", s2['current_phase'] == 'plan')
cleanup(TID)

# ════════════════════════════════════════════════════
# G2: 直接入口路径与 heartbeat 路径产生等价 PDCA 历史
# ════════════════════════════════════════════════════
section("G2: 直接入口（路径A）vs heartbeat（路径B）产生等价 PDCA 历史")

def run_full_pdca(tid, label):
    """模拟一次完整 PDCA 循环（无论通过哪条路径触发）"""
    pdca.p(tid, f"{label} plan", acceptance_criteria=["标准X"])
    pdca.d(tid, f"{label} done", "completed")
    pdca.c(tid, "pass", "L1", ["标准X 满足"])
    pdca.a(tid, f"{label} act", next_task=f"{tid}-T2")

TID_A = "g2-direct"     # 路径 A：直接进入
TID_B = "g2-heartbeat"  # 路径 B：heartbeat 进入
cleanup(TID_A, TID_B)

run_full_pdca(TID_A, "direct")
run_full_pdca(TID_B, "heartbeat")

s_a = pdca.get_status(TID_A)
s_b = pdca.get_status(TID_B)
ok("两路径均达到 phase=completed", s_a['current_phase'] == 'completed' == s_b['current_phase'])
ok("两路径均 verdict=pass", s_a['current_verdict'] == 'pass' == s_b['current_verdict'])
ok("两路径 cycles_total 相同（均为1）", s_a['cycles_total'] == s_b['cycles_total'] == 1)
cleanup(TID_A, TID_B)

# ════════════════════════════════════════════════════
# CLI: audit-queue 和 mark-audit 输出格式
# ════════════════════════════════════════════════════
section("CLI: audit-queue / mark-audit 命令输出格式")

TID = "cli-audit"
cleanup(TID)
pdca.p(TID, "cli test plan", dl_refs=["DL-2026-099"])
pdca.d(TID, "cli test done", "completed")
pdca.c(TID, "pass", "L1")
pdca.a(TID, "cli test act")

# audit-queue CLI
result = subprocess.run(
    ["python3", "scripts/pdca.py", "audit-queue"],
    capture_output=True, text=True, cwd=SKILL_ROOT
)
ok("audit-queue CLI 退出码=0", result.returncode == 0, result.stderr[:100] if result.returncode != 0 else "")
try:
    queue_out = json.loads(result.stdout)
    item = next((x for x in queue_out if x['task_card_id'] == TID), None)
    ok("audit-queue CLI 返回 JSON 数组", isinstance(queue_out, list))
    ok("audit-queue CLI 包含 dl_refs 字段", item and 'dl_refs' in item)
    ok("audit-queue CLI dl_refs 正确", item and item['dl_refs'] == ["DL-2026-099"])
except json.JSONDecodeError as e:
    ok("audit-queue CLI 输出可解析 JSON", False, str(e))

# mark-audit CLI
result2 = subprocess.run(
    ["python3", "scripts/pdca.py", "mark-audit",
     "--task-card-id", TID, "--cycle-index", "1",
     "--score", "65", "--issues", "规范X未满足|标准Y遗漏"],
    capture_output=True, text=True, cwd=SKILL_ROOT
)
ok("mark-audit CLI 退出码=0", result2.returncode == 0, result2.stderr[:100] if result2.returncode != 0 else "")
try:
    r_out = json.loads(result2.stdout)
    ok("mark-audit CLI ok=True", r_out.get('ok'))
    ok("mark-audit CLI has_problem=True（score=65<80）", r_out.get('has_problem'))
    ok("mark-audit CLI 包含 next_action", 'next_action' in r_out)
except json.JSONDecodeError as e:
    ok("mark-audit CLI 输出可解析 JSON", False, str(e))
cleanup(TID)

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
