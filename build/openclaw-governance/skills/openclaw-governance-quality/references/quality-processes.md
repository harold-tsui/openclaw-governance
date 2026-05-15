# Quality Review, DOD, and Review-gate — Detailed Reference

> Moved from quality SKILL.md §二–§五, §九–§十一 to reduce main file size.

## §二 审核流程

### review() — Deliverable Review

**Input**:
```json
{
  "action": "review",
  "deliverable_path": "10_Projects/ZT-P009/deliverables/RPT-xxx-v1.0.md",
  "checklist_id": "QA-TASK-CARD",
  "sample_ratio": 1.0
}
```

**Output**:
```json
{
  "result": "pass|fail|reject",
  "issues": [{ "id": "CHK-03", "desc": "描述", "level": "major|minor" }],
  "events": [{ "ts": "2026-03-18T09:30:00+08:00", "action": "review_completed" }]
}
```

### Review Result Definitions

| Result | Status | Follow-up |
|--------|--------|-----------|
| **pass** | ✅ PASS | Mark complete, proceed |
| **fail** | 🔄 REVISE | Return for revision with notes |
| **reject** | ❌ REJECT | Reject, task re-execution |

## §三 检查清单规范

### Standard Check Items

| ID | Item | Level |
|----|------|-------|
| CHK-01 | Metadata completeness | major |
| CHK-02 | Version spec compliance | minor |
| CHK-03 | Content structure compliance | major |
| CHK-04 | Reference link validity | minor |
| CHK-05 | Approval signature completeness | major |

## §四 问题管理

### report_issue() — Issue Record

**Input**:
```json
{
  "action": "report_issue",
  "issue_id": "ISS-2026-001",
  "source": "review|feedback|monitor",
  "level": "P0|P1|P2|P3",
  "description": "问题描述",
  "deliverable_path": "...",
  "owner": "agent_id"
}
```

### Issue Lifecycle
```
open → in_progress → resolved → verified → closed
```

## §五 PDCA 改进循环

### Quality PDCA vs Evolution PDCA

| Dimension | governance-quality | governance-evolution |
|-----------|-------------------|---------------------|
| **Scope** | Task/deliverable level | Governance system level |
| **Trigger** | Task complete, review finds issues | Periodic evaluation, system improvement |
| **Target** | Single deliverable, Task-CARD execution | Governance Skills, architecture, specs |
| **Output** | Issue fix, checklist update | Skill version upgrade, architecture refactoring |
| **Cycle** | Short (with task execution) | Long (version evolution) |

### PDCA Stage Definitions

| Stage | Description |
|-------|-------------|
| **Plan** | Identify quality issues, create improvement plan |
| **Do** | Execute improvements |
| **Check** | Verify improvement effectiveness |
| **Act** | Solidify effective improvements, update standards → **enter next PDCA cycle** |

**Key correction (Harold's view)**:
- After Act, it's not just Recheck — it enters a **new PDCA cycle**
- Next cycle's P/D/C are **redefined** based on elevated requirements
- **Don't assume** "same standard tested again"

## §九 示例

### Review Pass
```yaml
action: review
deliverable_path: 10_Projects/ZT-P009/deliverables/QA-CHECKLIST-v1.0.md
checklist_id: QA-TASK-CARD
sample_ratio: 1.0
# Output: result: pass, issues: []
```

### Issue Found
```yaml
action: review
deliverable_path: 10_Projects/ZT-P009/deliverables/RPT-DRAFT.md
checklist_id: QA-TASK-CARD
# Output: result: fail, issues: [CHK-03, CHK-04]
```

## §十 DOD 机制

### create_dod() — Create Acceptance Criteria

**Constraints**:
- Only COO or Task Planner can create
- Auto-locked after creation (Builder cannot modify)
- Standard ID format: DOD-{序号}

### verify_dod() — Verify DOD

**Constraints**:
- Reviewer ≠ Builder (self-certification protection)
- All required=true criteria must be met
- Use `scripts/verify-dod.sh` for verification

### DOD Categories

| Category | Description | Suggested Automation Level |
|----------|-------------|---------------------------|
| **functional** | Functionality | L3+ auto-verifiable |
| **testing** | Tests | L4+ auto-verifiable |
| **documentation** | Documentation | L3+ needs manual check |
| **quality** | Quality | L5 auto-verifiable |
| **security** | Security | L2+ needs manual check |
| **performance** | Performance | L4+ auto-verifiable |

## §十一 Review-gate

### validate_review_gate() — Mandatory Check

**Checks**:
1. Review artifact completeness
2. Self-review detection
3. DOD verification
4. Zero-issue review warning

### Review-gate Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| 0 | Verification passed | Can close task |
| 2 | Missing review artifacts | Add review.md |
| 3 | Self-review detected | Change reviewer |
| 4 | DOD verification missing | Complete DOD verification |
| 5 | Zero-issue review warning | Manual confirmation |

### Automation Level Adaptation

| Level | Review-gate Behavior |
|-------|---------------------|
| **L0** | No review, 银月 direct acceptance |
| **L1** | Exception reporting, mark `[V]` after complete, `[!?]` if concerns |
| **L2** | Sampling check (default), 银月 samples 20-30%, sampled → `[!]` |
| **L3** | Full manual, mark `[!]`, Harold must介入 |
| **L4** | Auto-pass, log retained |
| **L5** | No Review-gate needed |
