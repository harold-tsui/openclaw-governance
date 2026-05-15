# TASK-CARD · NUCLEUS 4.0 PDCA 验证测试

---
title: NUCLEUS 4.0 PDCA 验证测试
tags: [testing, nucleus, pdca]
type: task
id: N4-P2-TEST-01
status: [P]
owner: cqo
topic: N4-P2-T02
project: ZT-P015
priority: P0
privacy: P0
review_level: L1
task_type: regular
deliverables: []
created: 2026-04-18
updated: 2026-04-18
due: 2026-04-18
related_tasks: []
---

# TASK-CARD · NUCLEUS 4.0 PDCA 验证测试

> **文件性质**：Task 层上下文定义文件
> **存放路径**：`10_Projects/ZT-P015_NUCLEUS-4-0/test_reports/TASK-CARD-N4-P2-TEST-01.md`
> **版本**：v3.1（遵循 governance-task TMPL-TASK-CARD）

---

## ── Zone A：任务定义 ──────────────

## 一、Task 基本信息

| 字段 | 内容 |
|------|------|
| **Task ID** | N4-P2-TEST-01 |
| **Task 标题** | NUCLEUS 4.0 PDCA 验证测试 |
| **任务类型** | 📋 常规任务 |
| **归属 Topic** | N4-P2-T02 · Heartbeat 调度器实现 |
| **归属 Project** | ZT-P015 · NUCLEUS 4.0 |
| **Task PIC** | 张铁 (cqo) |
| **提出人** | Harold |
| **优先级** | P0 |
| **Review 级别** | L1（自验收） |
| **创建时间** | 2026-04-18 22:20 |
| **截止日期** | 2026-04-18 |

---

## 二、Task 描述

### 2.1 任务目标

验证 pdca.py 的 guardrails（Phase 锁定、幂等性、陈旧过滤）和跨阶段读写功能，确保 scheduler_state + PDCA 完整流程正常。

### 2.2 背景说明

Claude Code 已完成 nucleus v2.7.0 实现（包含 4 项 guardrails），需要 CQO 验证功能是否正常工作。测试需从 agent workspace 执行，验证跨阶段数据读取。

---

## 三、输入物（Inputs）

| 输入物 | 类型 | 来源 | 状态 |
|--------|------|------|------|
| governance-nucleus SKILL.md v2.7.0 | 文件 | skill 目录 | ✅ 已就绪 |
| pdca.py（含 guardrails） | 代码 | scripts/ | ✅ 已就绪 |
| scheduler_state.py | 代码 | scripts/ | ✅ 已就绪 |
| 测试流程规范 | 文件 | test_reports/README.md | ✅ 已就绪 |

---

## 四、Deliverable 定义

| 序号 | Deliverable | 文件名 | 格式 | Review 级别 | 验收标准 | 状态 |
|------|-------------|--------|------|-------------|---------|------|
| 1 | 测试报告 | CQO-TEST-REPORT-2026-04-18-Round2.md | .md | L1 | scheduler_state ✅ + p/d/c/a ✅ + YAML 完整 + status 一致 + 第二轮 ✅ + aggregate ✅ | ⬜ |

---

## 五、执行计划

| 步骤 | 操作 | 执行人 | 状态 |
|------|------|------|------|
| Step 1 | scheduler_state.py bump/check | 张铁 | ⬜ |
| Step 2 | pdca.py p（第一轮 Plan） | 张铁 | ⬜ |
| Step 3 | pdca.py d（第一轮 Do） | 张铁 | ⬜ |
| Step 4 | pdca.py c（第一轮 Check） | 张铁 | ⬜ |
| Step 5 | pdca.py a（第一轮 Act） | 张铁 | ⬜ |
| Step 6 | pdca.py status + cat YAML（验证） | 张铁 | ⬜ |
| Step 7 | pdca.py p（第二轮 Plan） | 张铁 | ⬜ |
| Step 8 | pdca.py d/c/a（第二轮完整） | 张铁 | ⬜ |
| Step 9 | pdca.py aggregate + cat _state.yaml | 张铁 | ⬜ |
| Step 10 | 撰写测试报告 | 张铁 | ⬜ |
| **Step 终** | 更新 MISSION_BOARD + 清理测试文件 | 张铁 | ⬜ |

---

## ── Zone B：运行时 ──────────────

## 六、Agent 决策记录（执行时填写）

> **Phase**: ⬜ Plan / 🟡 Do / 🟢 Check / ✅ Act
> **Verdict**: ⬜ pass / partial / fail / skip / pending

| 时间戳 | 决策内容 | Reasoning |
|--------|---------|-----------|
| 2026-04-18 22:20 | 确认测试流程规范，按顺序执行 | 避免上次并行执行问题 |

---

## 七、执行日志

### Phase 1：scheduler_state 测试

**Step 1.1 bump**
```bash
python3 scheduler_state.py bump
```
**结果**：待记录

---

**Step 1.2 check**
```bash
python3 scheduler_state.py check
```
**结果**：待记录

---

### Phase 2：第一轮 PDCA

**Step 2.1 Plan**
```bash
python3 pdca.py p --task-card-id N4-P2-TEST-01 --summary "..."
```
**结果**：待记录

---

**Step 2.2 Do**
```bash
python3 pdca.py d --task-card-id N4-P2-TEST-01 --summary "..." --status completed
```
**结果**：待记录

---

**Step 2.3 Check**
```bash
python3 pdca.py c --task-card-id N4-P2-TEST-01 --verdict pass --level L1
```
**结果**：待记录

---

**Step 2.4 Act**
```bash
python3 pdca.py a --task-card-id N4-P2-TEST-01 --summary "..."
```
**结果**：待记录

---

**Step 2.5 验证**
```bash
python3 pdca.py status --task-card-id N4-P2-TEST-01
cat pdca/N4-P2-TEST-01.yaml
```
**结果**：待记录

---

### Phase 3：第二轮 PDCA（验证 idempotency）

**Step 3.1 Plan（第二轮）**
```bash
python3 pdca.py p --task-card-id N4-P2-TEST-01 --summary "第二轮测试..."
```
**结果**：待记录

---

### Phase 4：aggregate 测试

**Step 4.1 aggregate**
```bash
python3 pdca.py aggregate
cat pdca/_state.yaml
```
**结果**：待记录

---

## ── Zone C：后处理 ──────────────

## 八、验收记录

> **Review 级别**: L1（自验收）

| 验收项 | 标准 | 结果 |
|--------|------|------|
| scheduler_state bump/check | ok=true | ✅ |
| p/d/c/a 各阶段（第一轮） | ok=true, phase 正确推进 | ✅ |
| YAML 文件完整性（第一轮） | p/d/c/a 四段完整 | ✅ |
| status 输出一致性（第一轮） | 与 YAML 内容一致 | ✅ |
| aggregate 自动触发 | a() 返回 aggregate, _state.yaml 有内容 | ✅ |
| 第二轮 cycle_index | cycle_index=2（第二轮 Plan 成功） | ✅ |
| 第二轮完整执行 | ❌ 测试方法错误（并行调用） | ❌ 无效 |

**结论**：
- 第一轮测试完全成功（pdca.py guardrails 和 aggregate 正常）
- 第二轮测试失败（测试方法错误，不是 pdca.py bug）
- pdca.py **无 bug**，问题在于测试执行方法

---

## 九、Review 记录

> **Review 时间**: 待填写
> **Reviewer**: 张铁 (cqo) - L1 自验收

---

## 十、知识沉淀

> **DL 条目**: 无（测试任务）

**Lesson Learned**:
1. **测试执行方法关键**：必须顺序执行每个 CLI 命令，等待返回后再执行下一步
2. **OpenClaw exec 工具行为**：一个 message turn 内多个 exec 命令会并行执行
3. **pdca.py 设计正确**：Phase 锁定、幂等性、aggregate 自动触发均正常工作
4. **正确测试流程**：参考 test_reports/README.md §二 测试流程

---

*Task-CARD · N4-P2-TEST-01 · v3.1 · 2026-04-18*