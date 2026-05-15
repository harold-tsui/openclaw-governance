# ZT-P015_NUCLEUS-4-0

NUCLEUS 4.0 — 徐在红的核心思维引擎架构项目。

## 项目 lineage

| 项目 | 版本 | 日期 | 说明 |
|------|------|------|------|
| ZT-P000_NUCLEUS | v1.0 | 2026-02 | 灵枢计划原始项目，建立使命/飞轮/六大模块 |
| ZT-P009_NUCLEUS-2-0 | v3.0 | 2026-03 | Harness Engineering 实现，11 Skill 上线 |
| **ZT-P015_NUCLEUS-4-0** | **v2.0+** | **2026-04** | **pdca.py 精简版架构，当前实施 Phase 2** |

---

## 唯一架构文档

> **`docs/NUCLEUS-4-0-ARCHITECTURE.md`** 是 NUCLEUS 4.0 的唯一架构权威源。
> 需求、架构、详细设计、升级计划四文档已合并为一份。

| 文档 | 路径 | 版本 |
|------|------|------|
| **架构与实施文档** | `docs/NUCLEUS-4-0-ARCHITECTURE.md` | v1.0 (2026-04-18) |

## 核心执行协议

| 组件 | 路径 | 版本 |
|------|------|------|
| **PDCA Harness (SKILL.md)** | `skills/openclaw-governance/skills/openclaw-governance-nucleus/SKILL.md` | v2.7.1 |
| **pdca.py** | `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py` | v2.7.1 (Phase 锁定 + 幂等性 + 陈旧过滤 + 执行日志) |
| **scheduler_state.py** | `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/scheduler_state.py` | v1.0.0 (Phase 2 新增) |

---

## Directory Structure

```
./
├── docs/
│   ├── NUCLEUS-4-0-ARCHITECTURE.md   ← 唯一架构权威源
│   └── archive/                      ← 历史文档归档
├── config/                           ← 配置文件（scheduler_state.yaml 等）
├── pdca/                             ← pdca.py 数据存储
├── cycles/                           ← Phase 1 遗留
├── logs/                             ← 观测日志
├── executions/                       ← 执行日志
├── topics/                           ← Topic 管理
├── tasks/                            ← Task 管理
├── scripts/                          ← 可执行脚本
├── knowledge/                        ← 知识存储（Phase 2）
├── development/                      ← 开发过程记录
├── decisions/                        ← 架构决策
├── reviews/                          ← 评审记录
├── test/                             ← 测试文件
├── archived/                         ← Phase 1 归档
└── README.md                         ← 本文件
```

## 核心架构

```
┌─ dispatch ─┐      ┌─ heartbeat ─┐      ┌─ evolution ─┐
│ (任务分发)  │      │ (定时巡检)   │      │ (元治理)     │
└─────┬──────┘      └─────┬───────┘      └─────┬───────┘
      │                   │                   │
      ▼                   ▼                   ▼
    ┌─────────────────────────────────────────┐
    │    governance-nucleus (L4 Skill)         │
    │    SKILL.md 定义 PDCA Harness 规则       │
    │    pdca.py 做确定性状态记录               │
    └──────────────────┬──────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    pdca/*.yaml    pdca/*.yaml    pdca/*.yaml
    (Task级)       (Topic级)      (Project级)
        │              │              │
        ▼              ▼              ▼
    轻量级聚合：扫描同级 yaml 的 verdict → 父级 verdict 自动派生
```

**核心原则**: pdca.py 是唯一 Python 工具（确定性 I/O），LLM 负责所有推断/执行/判断/决策。

---

*README v2.1 | 2026-04-18*
