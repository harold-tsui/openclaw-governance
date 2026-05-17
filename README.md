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

| 文档 | 路径 | 版本 |
|------|------|------|
| **架构与实施文档** | `docs/NUCLEUS-4-0-ARCHITECTURE.md` | v1.0 (2026-04-18) |

## 核心执行协议

| 组件 | 路径 | 版本 |
|------|------|------|
| **PDCA Harness (SKILL.md)** | `build/openclaw-governance/skills/openclaw-governance-nucleus/SKILL.md` | v2.7.1 |
| **pdca.py** | `build/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py` | v2.7.1 |
| **scheduler_state.py** | `build/openclaw-governance/skills/openclaw-governance-nucleus/scripts/scheduler_state.py` | v1.0.0 |

---

## Directory Structure

```
./
├── src/                    # 开发源码（编辑这里）
│   ├── pdca.py
│   ├── scheduler_state.py
│   ├── dashboard.py
│   └── migrate_legacy.py
├── build/                  # 生产 skill 包（git 追踪，不含运行时状态）
│   └── openclaw-governance/
├── test/                   # 验证脚本
│   ├── unit/
│   ├── integration/
│   ├── reports/
│   └── fixtures/
├── scripts/                # 构建/安装/工具脚本
│   ├── build-skill.sh
│   ├── install-skill.sh
│   ├── pdca_dashboard.py
│   ├── pdca_analyzer.py
│   └── pdca_optimizer.py
├── config/                 # 项目配置
├── docs/                   # 架构文档（唯一权威源）
├── decisions/              # 架构决策记录 (ADR)
├── reviews/                # 代码审查记录
├── topics/                 # Topic 工作区 (N4-P*-T*)
├── tasks/                  # Task 卡片
├── runtime/                # 运行时状态（gitignore，不追踪）
│   ├── cycles/
│   ├── logs/
│   ├── pdca/
│   └── scheduler_state.yaml
├── archived/               # Phase 1 归档
└── README.md               # 本文件
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
    runtime/pdca/  runtime/pdca/  runtime/pdca/
    (Task级)       (Topic级)      (Project级)
        │              │              │
        ▼              ▼              ▼
    轻量级聚合：扫描同级 yaml 的 verdict → 父级 verdict 自动派生
```

**核心原则**: pdca.py 是唯一 Python 工具（确定性 I/O），LLM 负责所有推断/执行/判断/决策。

---

*README v2.2 | 2026-05-17*
