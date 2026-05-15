# NUCLEUS 文档索引

> **维护规则**: 文档版本变更时更新此索引。

---

## 一、活跃文档

### 架构文档（ZT-P015_NUCLEUS-4-0）

| 编号 | 文件名 | 版本 | 位置 | 说明 |
|------|--------|------|------|------|
| **NUCLEUS-4.0-ARCH** | NUCLEUS-4-0-ARCHITECTURE.md | v1.1 | `docs/` | **唯一架构权威源**（合并自 REQ-SPEC + ARCH + DESIGN + UPGRADE 四份 v2.0 文档，含 CQO 合规闸门） |

### 执行协议

| 组件 | 版本 | 位置 | 说明 |
|------|------|------|------|
| governance-nucleus (SKILL.md) | v4.1.0 | `skills/.../openclaw-governance-nucleus/SKILL.md` | PDCA Harness 执行协议 + CQO 合规闸门 + 状态机防护 |
| pdca.py | v4.1.0 | `skills/.../openclaw-governance-nucleus/scripts/pdca.py` | PDCA 状态记录器 + CQO Review + Phase 锁定 + 幂等性 |
| scheduler_state.py | v1.0.0 | `skills/.../openclaw-governance-nucleus/scripts/scheduler_state.py` | 轻量多粒度调度计数器 |
| governance-heartbeat | v5.7.0 | `skills/.../openclaw-governance-heartbeat/SKILL.md` | 分布式巡检 |
| governance-delegation | v1.6.0 | `skills/.../openclaw-governance-delegation/SKILL.md` | Human-in-the-Loop A/B/C/D |
| governance-task | v6.0.4 | `skills/.../openclaw-governance-task/SKILL.md` | Task 生命周期 |
| governance-quality | v3.2.0 | `skills/.../openclaw-governance-quality/SKILL.md` | DOD + Review-Gate |

### 如何引用

```
引用架构：NUCLEUS-4.0-ARCH-v1.1 §4.2
引用需求：NUCLEUS-4.0-ARCH-v1.1 §2.1 REQ-PDCA-001
引用设计：NUCLEUS-4.0-ARCH-v1.1 §7.3
引用执行：governance-nucleus SKILL.md v4.1.0 §4.2
```

---

## 二、历史项目

| 项目 | 版本 | 日期 | 说明 |
|------|------|------|------|
| ZT-P000_NUCLEUS | v1.0 | 2026-02 | 灵枢计划原始项目 |
| ZT-P009_NUCLEUS-2-0 | v3.0 | 2026-03 | Harness Engineering 实现 |
| ZT-P015_NUCLEUS-4-0 | v2.0+ | 2026-04 | pdca.py 精简版 |

---

## 三、归档文档

| 文件 | 位置 | 归档原因 |
|------|------|---------|
| NUCLEUS-REQUIREMENTS-SPEC-v2.0 | `docs/archive/v2-superseded/` | 已合并入 NUCLEUS-4.0-ARCH-v1.0 |
| NUCLEUS-ARCH-v2.0 | `docs/archive/v2-superseded/` | 已合并入 NUCLEUS-4.0-ARCH-v1.0 |
| NUCLEUS-DESIGN-v2.0 | `docs/archive/v2-superseded/` | 已合并入 NUCLEUS-4.0-ARCH-v1.0 |
| NUCLEUS-UPGRADE-v2.0 | `docs/archive/v2-superseded/` | 已合并入 NUCLEUS-4.0-ARCH-v1.0 |
| pdca-check-protocol-v1.3 | `docs/archive/` | 基于旧 CycleUnit 架构 |
| ARCH-v1.4.3 等 v1.x 文档 | `docs/archive/nucleus-v1/` | CycleUnit/CycleScheduler 架构 |

---

*版本：v1.3 | 2026-05-06 | 维护人：银月*
