# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

**NUCLEUS 4.0** (ZT-P015) — Harold Tsui's core governance engine for the OpenClaw multi-agent system. It implements a PDCA (Plan-Do-Check-Act) harness that drives continuous iteration on tasks until delivery. The system is part of the larger OpenClaw governance framework.

## Architecture Principle

**Python only does deterministic I/O. LLM handles all inference, judgment, and decisions.** `pdca.py` records state; the LLM thinks. Never add inference logic to Python.

## Key Entry Points

| Path | Purpose |
|------|---------|
| `docs/NUCLEUS-4-0-ARCHITECTURE.md` | **Sole authoritative architecture document** — merged from 4 separate docs |
| `skills/.../openclaw-governance-nucleus/SKILL.md` | PDCA Harness execution protocol (L4 skill) |
| `skills/.../openclaw-governance-nucleus/scripts/pdca.py` | PDCA state recorder (~2000 lines, the only Python tool) |
| `skills/.../openclaw-governance-nucleus/scripts/scheduler_state.py` | Lightweight multi-granularity scheduler counter |
| `skills/.../openclaw-governance-nucleus/config/pdca_config.yaml` | Externalized configuration (limits, timeouts, concurrency, aggregation) |
| `skills/.../openclaw-governance-nucleus/pdca/` | YAML state storage (one file per task, `_state.yaml` for aggregation) |

The `skills/` path prefix is: `skills/openclaw-governance/skills/openclaw-governance-nucleus/` (relative to the OpenClaw repo root `$LOCAL_WORKSPACE`).

## Commands

### Run PDCA operations
```bash
cd $LOCAL_WORKSPACE/skills/openclaw-governance/skills/openclaw-governance-nucleus

# PDCA cycle steps
python scripts/pdca.py p   --task-card-id T1.1 --summary "..." [--criteria "a|b"] [--topic-id T06] [--project-id ZT-P015]
python scripts/pdca.py d   --task-card-id T1.1 --summary "..." --status completed|blocked|partial [--blocker "..."]
python scripts/pdca.py cqo-review --task-card-id T1.1 --result pass|revise|reject [--report-path PATH] [--issues "CQO-01|CQO-03"]
python scripts/pdca.py c   --task-card-id T1.1 --verdict pass|partial|fail|skip|pending --level L0|L1|L2|L3 [--evidence "a|b"]
python scripts/pdca.py a   --task-card-id T1.1 --summary "..." [--next-task T1.2] [--lessons "a|b"]

# Query
python scripts/pdca.py status  --task-card-id T1.1
python scripts/pdca.py pending
python scripts/pdca.py history --task-card-id T1.1

# Aggregation & concurrency
python scripts/pdca.py aggregate [--triggered-by heartbeat] [--mode strict|weighted]
python scripts/pdca.py check-concurrency [--scope task] [--scope-id T06]

# Operations
python scripts/pdca.py verify-integrity [--task-card-id T1.1]
python scripts/pdca.py health-check
python scripts/pdca.py archive [--older-than-days 30] [--dry-run]

# Scheduler
python scripts/scheduler_state.py read
python scripts/scheduler_state.py bump
python scripts/scheduler_state.py check
python scripts/scheduler_state.py reset {scope_id}
```

### Run tests
```bash
cd $LOCAL_WORKSPACE/skills/openclaw-governance/skills/openclaw-governance-nucleus

# All tests with coverage
pytest

# Single test file
pytest tests/test_pdca.py -v

# Single test function
pytest tests/test_pdca.py::TestPDCA::test_plan -v

# Skip slow tests
pytest -m "not slow"

# Integration tests only
pytest -m integration

# Coverage report
pytest --cov=scripts --cov-report=term-missing
```

### Project-level tools
```bash
cd $LOCAL_WORKSPACE/10_Projects/ZT-P015_NUCLEUS-4-0

python scripts/pdca_dashboard.py   # Real-time PDCA status dashboard
python scripts/pdca_analyzer.py    # Deep analysis of PDCA execution data
python scripts/pdca_optimizer.py   # Bottleneck identification and optimization suggestions
```

## PDCA Flow & State Machine

```
Plan → Do → CQO Review → Check → Act → (auto aggregate)
                     ↓
              pass → Check
              revise → Do (same cycle, revise_count++)
              reject → Do (same cycle, notify 银月)
```

- CQO Review is a gate between Do and Check, not a 5th PDCA phase
- CQO revise limit: 3 per cycle; 4th auto-escalates to reject
- CQO timeout (5 min): default pass with warning
- `a()` auto-triggers `aggregate()` for layer propagation (task → topic → project)
- After `a()`, LLM must update Task-CARD status and MISSION_BOARD (write-through rule A2)

## ADAS Review Levels

| Level | Reviewer | verdict allowed | audit_eligible |
|-------|----------|----------------|----------------|
| L0 | None | pass/fail/skip/partial | pass → true |
| L1 | LLM self | pass/fail/skip/partial (never pending) | pass → true |
| L2 | 银月 sampling | pass/pending | pass → false |
| L3 | Harold | pending first, then pass/fail/skip/partial | false |

## Data Storage

- **Zero-database architecture**: all data as `.md` / `.yaml` / `.jsonl` files
- `pdca/{task_id}.yaml` — per-task PDCA state with SHA-256 checksum
- `pdca/_state.yaml` — aggregated topic/project verdicts (auto-derived, never hand-written)
- `config/pdca_config.yaml` — externalized limits/timeouts/concurrency params
- `config/scheduler_state.yaml` — heartbeat tick counters
- Atomic writes: write `.tmp` then `os.replace()`

## Concurrency Limits

| Scope | Max Concurrent |
|-------|---------------|
| task | 10 |
| topic | 5 |
| project | 3 |

Enforced by `check_concurrency()` before `p()`.

## Scheduler Granularity

| Scope | Frequency | Ticks |
|-------|-----------|-------|
| task | every heartbeat | 1 |
| topic | every 4 heartbeats | 4 |
| project | every 48 heartbeats | 48 |
| system | every 96 heartbeats | 96 |

1 tick ≈ 30 minutes (one heartbeat cycle).

## Project Directory Structure

```
ZT-P015_NUCLEUS-4-0/
├── docs/              ← NUCLEUS-4-0-ARCHITECTURE.md (sole authority)
├── config/            ← business_hours.yaml, escalation_policy.yaml, state_sync_rules.yaml
├── cycles/            ← Phase 1 legacy
├── logs/              ← Observability logs (.jsonl)
├── executions/        ← Execution logs + reports
├── topics/            ← Topic workspaces (N4-P*-T*)
├── tasks/             ← Task cards
├── scripts/           ← Dashboard/analyzer/optimizer scripts
├── development/       ← Dev logs, version history, governance skills panorama
├── decisions/         ← Architecture decision records
├── reviews/           ← Review records
├── test/              ← Integration tests
├── archived/          ← Phase 1 artifacts
└── deliverables/      ← Phase deliverables
```

## Current Phase Status

| Phase | Status |
|-------|--------|
| Phase 0: Boundary definition | Done |
| Phase 1: MVP | Done |
| Phase 1.5: Doc merge + security hardening | Done |
| Phase 2: Layer propagation + multi-granularity scheduling | Done |
| Phase 2.5: Knowledge crystallization | In progress |
| Phase 3: System-level self-evolution | Not started |

## Conventions

- Task IDs: `T{N}.{M}` (Phase 1) or `N4-P{phase}-T{topic}-T{seq}` (Phase 2+)
- Project ID prefix: `ZT-P015` — never invent other prefixes
- All `pdca.py` output is JSON
- Citation format: `NUCLEUS-4.0-ARCH-v1.1 §{section}`
- Verdict mapping to Task-CARD status: pass → `[x]`, partial/fail/skip → `[P]`, pending → `[V]`

## Source Code Structure (v2.0 — Independent Repo)

ZT-P015 is now an independent git repo. Source code lives in `src/`, build output in `build/`.

```
ZT-P015_NUCLEUS-4-0/
├── src/                    # 开发源码（编辑这里）
│   ├── pdca.py             # PDCA 状态记录器
│   ├── scheduler_state.py  # 调度计数器
│   ├── dashboard.py        # 仪表板
│   └── migrate_legacy.py   # 迁移工具
├── test/                   # 测试
├── build/                  # 构建产物 → skill 安装包
│   └── openclaw-governance/    # 最终 install 到 $LOCAL_WORKSPACE/skills/ 的结构
│       ├── SKILL.md
│       ├── skills-extension.yaml
│       └── skills/
│           ├── openclaw-governance-nucleus/  # PDCA harness
│           ├── openclaw-governance-data/      # 数据治理规范
│           └── ...
├── topics/                 # 项目规划文档
├── tasks/                  # Task cards
├── docs/                   # 架构文档
└── scripts/
    ├── build-skill.sh      # src/ → build/ 同步
    └── install-skill.sh    # build/ → $LOCAL_WORKSPACE/skills/ 安装
```

### 开发流程
```bash
# 1. 编辑 src/ 中的源码
vim src/pdca.py

# 2. 构建（同步 src → build）
./scripts/build-skill.sh

# 3. 测试
cd build/openclaw-governance/skills/openclaw-governance-nucleus
pytest

# 4. 安装到运行时
./scripts/install-skill.sh

# 5. 提交推送
git add -A && git commit -m "feat: xxx" && git push
```

### Skill Install 路径
- **本地 dev**: `./scripts/install-skill.sh` (从 build/ 直装)
- **GitHub stable**: `git clone git@github.com:harold-tsui/openclaw-governance.git && cd openclaw-governance && ./scripts/install-skill.sh`
