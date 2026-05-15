# TOPIC-BRIEF · N4-P2-T06

> **文件性质**：执行记录文件（非定义文档）
> **唯一真相源**：`docs/NUCLEUS-ARCH-v1.0` · `docs/NUCLEUS-REQ-SPEC-v1.0`
> **版本**：v2.0
> **Topic ID**：N4-P2-T06
> **Topic 名称**：NUCLEUS 新准则实施（Phase 2）
> **PM**：张铁 (CQO)
> **Review 级别**：L2（银月审批即可）
> **状态**：📋 规划完成

---

## 一、Topic 执行概要

| 字段 | 内容 |
|------|------|
| **Topic ID** | N4-P2-T06 |
| **Topic 名称** | NUCLEUS 新准则实施（Phase 2） |
| **PM** | 张铁 (CQO) |
| **Phase** | Phase 2（Week 8-14） |
| **状态** | 📋 规划完成，待执行 |
| **创建日期** | 2026-04-13 |
| **重新规划日期** | 2026-04-18 |

---

## 二、背景

### 2.1 旧 Topic 废弃

原 Topic "通过 BotLearn 优化 OpenClaw Governance" 已不适合 NUCLEUS 新准则。

N4-P2-T01 至 T05（基于旧架构 CycleUnit/CycleScheduler/CycleAggregator）已于 2026-04-18 归档。

### 2.2 新准则四文档

| 文档 | 编号 | 用途 |
|------|------|------|
| **NUCLEUS-REQ-SPEC** | REQ-SPEC-v1.0 | 需求规格（功能性 + 非功能性） |
| **NUCLEUS-ARCH** | ARCH-v1.0 | 系统架构（精简版 pdca.py + heartbeat） |
| **NUCLEUS-DETAILED-DESIGN** | DESIGN-v1.0 | 详细设计（pdca.py 函数级设计 + ADAS 规则） |
| **NUCLEUS-UPGRADE-PLAN** | UPGRADE-v1.0 | Phase 2-3 升级方案 |

### 2.3 Phase 2 目标

基于新准则，实现 Phase 1 到 Phase 2 的升级：
1. pdca.py 差距修复（escalation 集成、无任务健康检查、向后兼容）
2. 并发上限约束（REQ-NF-009）
3. 多粒度调度（task/topic/project/system 不同频率）
4. Obsidian 知识图谱集成
5. 审计出口集成
6. 端到端集成测试

---

## 三、Task 执行计划

| Task ID | Task 名称 | 状态 | 交付物 |
|---------|-----------|------|--------|
| **T06.1** | pdca.py 差距修复 | 📋 待开始 | nucleus SKILL.md 更新、兼容测试 |
| **T06.2** | 并发上限约束 | 📋 待开始 | pdca.py 新增 check_concurrency() |
| **T06.3** | 多粒度调度 | 📋 待开始 | scheduler_state.py + 计数器 |
| **T06.4** | Obsidian 知识图谱 | 📋 待开始 | knowledge/graph.yaml + knowledge.py |
| **T06.5** | 审计出口集成 | 📋 待开始 | nucleus SKILL.md 审计 Step |
| **T06.6** | 集成测试 + 验收 | 📋 待开始 | 端到端测试脚本 + 报告 |

---

## 四、规划文档

详见 `topics/N4-P2-T06/T06-PLAN.md`。

---

*v2.0 | 更新：2026-04-18 | PM：张铁 | 状态：📋 规划完成 | 旧 T01-T05 已归档*
