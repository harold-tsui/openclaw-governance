# Decision Automation Levels (ADAS) — Detailed Reference

> Moved from delegation SKILL.md §三 to reduce main file size.
> Original §三 content preserved here for progressive disclosure.

## 3.1 Level Definitions

| Level | Name | Description | Scenario |
|-------|------|-------------|----------|
| **L5** | Full Automation | Agent autonomous, periodic report only | Routine tasks, mature process |
| **L4** | High Automation | Agent executes, auto-escalates exceptions | Standard tasks, clear rules |
| **L3** | Conditional Automation | Agent executes + auto-reports, Harold post-review | Verified tasks, DL-backed |
| **L2** | Assisted Decision | Agent provides A/B/C/D, Harold confirms | Important tasks, needs best practice |
| **L1** | Human-Assisted | Agent suggests, Harold decides at key nodes | Complex tasks, needs judgment |
| **L0** | Full Manual | Harold decides all, Agent only executes | New scenarios, no DL support |

## 3.2 Agent Decision Matrix

| Agent | Capability | Default Level | Notes |
|-------|-----------|---------------|-------|
| **cto** | Tech evolution | L2-L3 | Tech selection can be automated |
| **cdo** | Data governance | L3-L4 | Data classification automatable |
| **cqo** | Standardization | L3 | Quality review needs confirmation |
| **ceo** | Planning | L1-L2 | Strategic decisions need human |
| **cco** | Content | L3 | Generation auto, review human |
| **cvo** | Visual | L3 | Design generation automatable |
| **cio** | Research | L2 | Research auto, analysis needs human |
| **cfo** | Finance | L2 | Calc auto, decision needs human |
| **ld** | Auto industry | L3 | Tech consulting automatable |
| **ec-ceo** | E-commerce | L3 | Operations automatable |

## 3.3 Dynamic Level Adjustment

**Upgrade conditions**:
- DL hit rate ≥ 80%
- 3 consecutive successes

**Downgrade conditions**:
- 2 consecutive failures
- LL (LESSON-LEARN) rejection

## 3.4 determine_automation_level()

**Scoring**:
- dl_hit_rate >= 0.8 → +40 points
- consecutive_success >= 3 → +30 points
- no_ll_rejection → +20 points
- project_phase != 'establishing' → +10 points
- **Upgrade threshold**: >= 90 → can upgrade
- **Downgrade**: consecutive_failure >= 2 → +50, ll_rejection_exists → +30, dl_expired → +20. Score >= 50 → needs downgrade.

**Error codes**:
- `E_AGENT_NOT_FOUND`: agent_id not in automation-levels.yaml
- `E_INVALID_LEVEL`: level not in L0-L5

## 3.5 adjust_automation_level()

**Constraints**:
- Only single-level changes (L3 → L4, not L3 → L5)
- Must record adjustment history

**Process**:
1. Validate adjustment (single step, valid level)
2. Update automation-levels.yaml (current_level, reset counters, add history)
3. Notify Harold and Agent
