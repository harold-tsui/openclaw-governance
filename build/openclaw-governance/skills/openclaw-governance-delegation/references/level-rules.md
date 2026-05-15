# Review Level Rules and Decision Flow — Detailed Reference

> Moved from delegation SKILL.md §二, §四, §五, §六 to reduce main file size.

## Review Levels

| Level | Description | Approver | Sampling |
|-------|-------------|----------|----------|
| L3 | Harold full review | Harold | 100% |
| L2 | 银月 sampling + Harold key nodes | Harold | 20-30% |
| L1 | 银月 acceptance | 银月 | — |
| L0 | Direct acceptance | 银月 | — |

## Level Determination Rules

### Project Level
| Scenario | Level | Rule |
|----------|-------|------|
| New Project | L3 | Always L3 |
| Any Project modification | L3 | Always L3 |

### Topic Level
| Scenario | Level | Rule |
|----------|-------|------|
| First Topic type | L3 | New type |
| In-scope Topic | L2 | Default for transition/cruising |
| Out-of-bound Topic | L3 | Needs Harold approval |
| Cross-project Topic | L3 | Needs Harold approval |

### Task Level
| Scenario | Level | Rule |
|----------|-------|------|
| First Task type | L3 | New type |
| P0 emergency | L2 | Post-mortem review |
| P1 normal | L1/L2 | By phase |
| P2/P3 normal | L0/L1 | By phase |

### Phase Defaults
| Project Phase | Default Level | Notes |
|---------------|---------------|-------|
| Establishing | L3 | Project startup, architecture |
| Transition | L2 | Core development, process validation |
| Cruising | L1 | Stable operation, routine iteration |
| Maintaining | L0 | Continuous maintenance, periodic tasks |

## Decision Flow

```
Receive level determination request
    ↓
Determine target_type (project/topic/task)
    ↓
    ├─ project → L3 → return
    ├─ topic
    │   ├─ first type → L3
    │   ├─ out-of-bound/cross-project → L3
    │   └─ in-scope → by phase (§4.4)
    └─ task
        ├─ first type → L3
        ├─ P0 → L2 (post-mortem)
        └─ other → by phase (§4.4)
    ↓
Return level + rationale
```

## Authorization Matrix

| Operation | Harold | 银月 | Topic Main PIC | Task PIC | Other Agent |
|-----------|--------|------|----------------|----------|-------------|
| Create Project | ✅ | ❌ | ❌ | ❌ | ❌ |
| Close Project | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create Topic | ✅ | ✅ | ❌ | ❌ | ❌ |
| Close Topic | ✅ | ✅ | ❌ | ❌ | ❌ |
| Create Task | ✅ | ✅ | ✅ | ❌ | ❌ |
| Close Task | ✅ | ✅ | ✅ | ❌ | ❌ |

## Routing Permission Check

```
Intent recognized → Before routing decision
    ↓
Check operation permission:
    ├─ Create Project → Harold only
    ├─ Create Topic → Harold or 银月 or Topic Main PIC
    ├─ Create Task → Harold or 银月 or Topic Main PIC
    └─ Other → Normal routing
    ↓
Insufficient permission → Return error + suggestion
```
