# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

**NUCLEUS 4.0** (ZT-P015) — PDCA (Plan-Do-Check-Act) harness for the OpenClaw multi-agent governance system. `pdca.py` records deterministic state; the LLM handles all inference, judgment, and decisions. **Never add inference logic to Python.**

## Development Workflow

This is an independent git repo. Source in `src/`, built skill package in `build/`, installed to `$LOCAL_WORKSPACE/skills/`.

```bash
# 1. Edit src/*.py
# 2. Build (sync src → build)
./scripts/build-skill.sh
# 3. Test (runs from build/ — this is where pytest.ini and tests/ live)
cd build/openclaw-governance/skills/openclaw-governance-nucleus && pytest
# 4. Install to runtime
./scripts/install-skill.sh
# 5. Commit & push
```

## Running Tests

```bash
# Must cd into the build skill directory — pytest.ini, conftest, and tests/ live there
cd build/openclaw-governance/skills/openclaw-governance-nucleus

pytest                                          # All tests + coverage
pytest tests/test_pdca.py -v                    # Single file
pytest tests/test_pdca.py::TestPDCA::test_plan  # Single function
pytest -m "not slow"                            # Skip slow tests
pytest -m integration                           # Integration only
pytest --cov=scripts --cov-report=term-missing  # Coverage report
```

Informal verification scripts also exist at `test/unit/` in the project root.

## PDCA Commands

```bash
cd build/openclaw-governance/skills/openclaw-governance-nucleus

# Cycle steps
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

## Project-level Dashboard Scripts

```bash
python scripts/pdca_dashboard.py   # Real-time PDCA status
python scripts/pdca_analyzer.py    # Deep analysis of execution data
python scripts/pdca_optimizer.py   # Bottleneck identification
```

## Architecture

### Source Layout

```
src/
├── pdca.py             # PDCA state recorder (~2000 lines, sole Python tool)
├── scheduler_state.py  # Multi-granularity scheduler counter
├── dashboard.py        # Dashboard rendering
└── migrate_legacy.py   # Phase 1 migration tool

build/openclaw-governance/skills/openclaw-governance-nucleus/
├── SKILL.md            # PDCA Harness execution protocol (L4 skill)
├── pytest.ini          # Test configuration
├── scripts/            # ← synced from src/ by build-skill.sh
├── tests/              # Primary pytest suite
├── config/pdca_config.yaml   # Externalized limits/timeouts/concurrency
└── knowledge/          # Reference docs

runtime/                # Historical runtime data (gitignore, not tracked)
├── cycles/             # Legacy cycle records (pre-restructure)
└── logs/               # Legacy execution logs

test/                   # Informal verification scripts
├── unit/
├── integration/
├── reports/
└── fixtures/
```

### PDCA State Machine

```
Plan → Do → CQO Review → Check → Act → (auto aggregate)
                     ↓
              pass → Check
              revise → Do (same cycle, revise_count++)
              reject → Do (same cycle, notify 银月)
```

- CQO Review is a gate between Do and Check, not a 5th phase
- CQO revise limit: 3 per cycle; 4th auto-escalates to reject
- CQO timeout (5 min): default pass with warning
- `a()` auto-triggers `aggregate()` for layer propagation (task → topic → project)
- After `a()`, LLM must update Task-CARD status and MISSION_BOARD (write-through rule A2)

### ADAS Review Levels

| Level | Reviewer | verdict allowed | audit_eligible |
|-------|----------|----------------|----------------|
| L0 | None | pass/fail/skip/partial | pass → true |
| L1 | LLM self | pass/fail/skip/partial (never pending) | pass → true |
| L2 | 银月 sampling | pass/pending | pass → false |
| L3 | Harold | pending first, then pass/fail/skip/partial | false |

### Data Model

- Zero-database: all data as `.yaml` / `.md` / `.jsonl` files
- PDCA state lives in the skill's own directory (`build/.../nucleus/pdca/`), resolved by `pdca.py` via `_SKILL_ROOT`
- Per-task state: `{task_id}.yaml` with SHA-256 checksum; aggregation in `_state.yaml` (auto-derived, never hand-edit)
- Atomic writes: write `.tmp` then `os.replace()`
- All `pdca.py` output is JSON

### Concurrency & Scheduling

| Scope | Max Concurrent | Scheduler Frequency |
|-------|---------------|-------------------|
| task | 10 | every heartbeat |
| topic | 5 | every 4 heartbeats |
| project | 3 | every 48 heartbeats |

1 tick ≈ 30 minutes (one heartbeat cycle).

## Key Documents

| Path | Purpose |
|------|---------|
| `docs/NUCLEUS-4-0-ARCHITECTURE.md` | **Sole authoritative architecture document** |
| `docs/VERSION_HISTORY.md` | Version history |
| `docs/GOVERNANCE-SKILLS-PANORAMA.md` | Governance skills overview |

## Conventions

- Task IDs: `T{N}.{M}` (Phase 1) or `N4-P{phase}-T{topic}-T{seq}` (Phase 2+)
- Project ID prefix: `ZT-P015`
- Citation format: `NUCLEUS-4.0-ARCH-v1.1 §{section}`
- Verdict → Task-CARD status: pass → `[x]`, partial/fail/skip → `[P]`, pending → `[V]`

## Skill Install

- **Local dev**: `./scripts/install-skill.sh` (from build/)
- **GitHub stable**: `git clone git@github.com:harold-tsui/openclaw-governance.git && cd openclaw-governance && ./scripts/install-skill.sh`
