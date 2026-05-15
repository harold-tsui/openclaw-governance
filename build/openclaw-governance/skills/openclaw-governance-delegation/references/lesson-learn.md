# LESSON-LEARN Integration — Detailed Reference

> Moved from delegation SKILL.md §九 to reduce main file size.

## 9.1 Trigger Scenarios

| Scenario | Description |
|----------|-------------|
| Decision result doesn't match expectation | DL execution produced poor results |
| Agent uses DL incorrectly | Misunderstanding or misquoting DL |
| Environment change invalidates DL | External conditions changed |
| Better solution discovered | Found optimal approach in practice |

## 9.2 Four-Question Analysis

```
Problem discovered
    ↓
Q1: Is this a DL problem itself?
    YES → DL assumptions/conditions changed → QUESTIONED
    NO → Q2

Q2: Is this an Agent understanding error?
    YES → Record "Agent execution error"
    NO → Q3

Q3: Is this a new scenario?
    YES → Escalate to Harold to create new DL
    NO → Q4

Q4: Is this a reasonable exception?
    YES → Record exception in DL
    NO → Find root cause
```

## 9.3 Extended Output

```json
{
  "status": "OK",
  "level": "L2",
  "delegation": {
    "level": "L2",
    "needs_harold_approval": false
  },
  "lesson_learn": {
    "has_history": true,
    "similar_tasks": ["ZT-P009-T02-T01"],
    "warnings": ["注意路径规范"],
    "dl_status": "ACTIVE"
  },
  "rationale": [...]
}
```

## 9.4 Data Sources

| Data | Location |
|------|----------|
| LESSON-LEARN Index | `.system/governance/current/lessons/LESSON-LEARN-索引.md` |
| LESSON-LEARN Entries | `.system/governance/current/lessons/entries/` |
| DL Decision Library | `.system/governance/current/decisions/` |
