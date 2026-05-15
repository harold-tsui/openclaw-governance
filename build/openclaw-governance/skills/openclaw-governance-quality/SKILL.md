---
name: enforcing-quality
description: |
  Enforcing quality standards, DOD verification, and review-gate checks for all deliverables.
  
  Activates when: Quality-related keywords detected, task completion, or review requested
  
  Capabilities:
  - Review-gate validation and deliverable审核
  - DOD (Definition of Done) creation and verification
  - Quality checklist verification with pass/fail tracking
  - Issue reporting and lifecycle management
  - PDCA improvement cycles at task/deliverable level
  
  Keywords: quality, dod, review, verification, checklist, audit, pdca-improvement
  
  For detailed documentation, see:
  - references/quality-processes.md

author: "张铁 (cqo)"
license: "Internal Use Only"
version: "4.2.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L3"
  os: ["darwin", "linux"]
  owner: "cqo"
  tags: ["quality", "dod", "review-gate", "checklist", "pdca-improvement"]
---

# Governance Quality - 质量管控 Skill

Tags: #governance, #quality, #dod, #review-gate, #pdca

> **触发模式**：描述匹配触发 + 模型主动 read()
> **v4.2.0**: 新增 CQO 合规闸门（Do→CQO Review→Check），CQO-01~05 审核项，spawn 协议

## 何时使用

- **Task completion**: 任何交付物在标记完成前需要审核
- **Review requested**: 用户或 Agent 请求质量审核
- **DOD creation/verification**: 创建或检查 Definition of Done 标准
- **Quality issues discovered**: 执行或审核过程中发现问题
- **Do NOT use for**: 流水线编排 — 那是 `governance-pipeline` 的职责（它会调用 quality）

## 常见陷阱

1. **自我认证检测**: 如果交付物的创建者同时执行了审核，标记为错误码 3（自我认证），要求更换审查者。
2. **零问题审核警告**: 复杂交付物审核零问题发现是可疑的 — 标记为错误码 5，需要人工确认。
3. **DOD 类别有自动化级别**: 不要尝试自动验证 `documentation`（L3+ 需要人工检查）或 `security`（L2+ 需要人工检查）。
4. **Quality PDCA ≠ Evolution PDCA**: Quality PDCA 在任务/交付物级别工作（短周期）。Evolution PDCA 在系统级别工作（长周期）。不要混淆作用域。

---

## 引用规范

| 规范 | 版本 | 说明 |
|------|------|------|
| **ZT-2026-007** | v1.1 | 交付物路径规范 |
| **governance-delegation** | v1.6.0 | Review 级别判定、审批权限 |
| **governance-task** | v6.0.2 | Task 生命周期管理 |
| **governance-evolution** | v2.0.0 | 系统级 PDCA 改进 |

---

## 一、核心功能

### 1.0 Review-Gate 职责边界

**核心原则**：Pipeline 编排时机，Quality 执行验证，Delegation 判定权限

| 职责 | 说明 | 对应函数 |
|------|------|----------|
| **规则提供** | 提供检查清单、DOD 模板、验收标准 | `create_dod()`, `check_checklist()` |
| **验证执行** | 执行实际验证逻辑，记录问题 | `review()`, `verify_dod()` |
| **问题跟踪** | 记录并跟踪质量问题闭环 | `report_issue()` |
| **改进循环** | 任务/交付物级别的 PDCA | `pdca_cycle()` |

**防自我认证机制**：
- DOD 创建者 ≠ DOD 验证者（由 delegation 判定验证权限）
- 任务执行者 ≠ 质量审查者（Quality 独立验证）

### 1.1 核心函数

| 功能 | 说明 |
|------|------|
| **review()** | 交付物审核入口 |
| **check_checklist()** | 检查清单验证 |
| **report_issue()** | 问题记录与跟踪 |
| **pdca_cycle()** | PDCA 改进循环 |
| **create_dod()** | 创建 DOD 验收标准 |
| **verify_dod()** | 验证 DOD 完成度 |
| **validate_review_gate()** | Review-gate 强制检查 |

---

## 二、审核流程（摘要）

### review() 输入/输出

**输入**：`{deliverable_path, checklist_id, sample_ratio}`
**输出**：`{result: pass|fail|reject, issues[], events[]}`

| 结果 | 状态 | 后续动作 |
|------|------|----------|
| **pass** | PASS | 标记完成，流转下一步 |
| **fail** | REVISE | 打回修改，注明修改点 |
| **reject** | REJECT | 驳回，任务重新执行 |

> 详细审核流程、检查清单规范：[references/quality-processes.md]({baseDir}/references/quality-processes.md)

---

## 三、检查清单（摘要）

**标准检查项**：

| ID | 检查项 | 级别 |
|----|--------|------|
| CHK-01 | 元数据完整性 | major |
| CHK-02 | 版本号规范 | minor |
| CHK-03 | 内容结构规范 | major |
| CHK-04 | 引用链接有效 | minor |
| CHK-05 | 审批签名完整 | major |

> 详细清单验证逻辑：[references/quality-processes.md]({baseDir}/references/quality-processes.md)

---

## 四、问题管理（摘要）

**report_issue() 输入**：`{issue_id, source, level, description, deliverable_path, owner}`

**生命周期**：`open → in_progress → resolved → verified → closed`

> 详细问题管理流程：[references/quality-processes.md]({baseDir}/references/quality-processes.md)

---

## 五、PDCA 改进循环（摘要）

### Quality PDCA vs Evolution PDCA

| 维度 | governance-quality | governance-evolution |
|------|-------------------|---------------------|
| **作用域** | 任务/交付物级别 | Governance 系统级别 |
| **触发时机** | 任务完成、审核发现问题 | 定期评估、系统改进需求 |
| **改进对象** | 单个交付物、Task-CARD 执行流程 | 治理 Skills、架构、规范 |
| **输出产物** | 问题修复、检查清单更新 | Skill 版本升级、架构重构 |
| **周期** | 短周期（随任务执行） | 长周期（版本演进） |

### PDCA 阶段

| 阶段 | 说明 |
|------|------|
| **Plan** | 识别质量问题，制定改进计划 |
| **Do** | 推动改进措施落地 |
| **Check** | 验证改进效果 |
| **Act** | 固化有效改进，更新标准 → **进入下一 PDCA 循环** |

> 详细 PDCA 递进机制、示例：[references/quality-processes.md]({baseDir}/references/quality-processes.md)

---

## 六、质量指标（摘要）

| 指标 | 计算方式 | 目标值 |
|------|----------|--------|
| **交付物合规率** | 合格数/总数 | ≥ 95% |
| **问题闭环率** | 已闭环/总问题 | ≥ 90% |
| **首次通过率** | 首审通过/总审核 | ≥ 80% |
| **改进采纳率** | 采纳数/建议数 | ≥ 70% |

---

## 七、DOD 机制（摘要）

### create_dod()
- 只能由 COO 或 Task Planner 创建
- 创建后自动锁定（Builder 不可修改）
- 标准 ID 格式：DOD-{序号}

### verify_dod()
- Reviewer ≠ Builder（自我认证防护）
- 所有 required=true 的标准必须满足
- 使用 `scripts/verify-dod.sh` 验证

### DOD 类别

| 类别 | 自动化级别建议 |
|------|----------------|
| functional | L3+ 可自动验证 |
| testing | L4+ 可自动验证 |
| documentation | L3+ 需人工检查 |
| quality | L5 可自动验证 |
| security | L2+ 需人工检查 |
| performance | L4+ 可自动验证 |

> 详细 DOD 创建/验证流程：[references/quality-processes.md]({baseDir}/references/quality-processes.md)

---

## 八、Review-gate（摘要）

### validate_review_gate() 检查项
1. 审查产物完整性
2. 自我审查检测
3. DOD 验证
4. 零问题审查警告

### 错误码

| 代码 | 描述 | 处理 |
|------|------|------|
| 0 | 验证通过 | 可以关闭任务 |
| 2 | 缺少审查产物 | 添加 review.md |
| 3 | 检测到自我审查 | 更换审查者 |
| 4 | DOD 验证缺失 | 完成 DOD 验证 |
| 5 | 零问题审查警告 | 人工确认 |

### 与自动化级别适配

| 级别 | Review-gate 行为 |
|------|------------------|
| L0 | 免审，银月直接验收 |
| L1 | 异常上报，标记 `[V]` / `[!?]` |
| L2 | 抽样核查（20-30%），标记 `[!]` |
| L3 | 全量人工，Harold 必须介入 |
| L4 | 自动通过，日志保留 |
| L5 | 无需 Review-gate |

> 详细 Review-gate 验证逻辑：[references/quality-processes.md]({baseDir}/references/quality-processes.md)

---

## 八.五、CQO 合规闸门（v4.2 新增）

> **定位**：CQO 合规闸门是 PDCA 流程中 Do→Check 之间的合规性检查，由 CQO（张铁）通过 `sessions_spawn` 执行。确保所有交付物在进入质量验收（Check）前符合 governance skill 规范。

### CQO 审核项

| 编号 | 审核项 | 检查内容 | 不通过处理 |
|------|--------|---------|-----------|
| CQO-01 | 模板匹配 | 交付物是否使用正确的 TMPL-* 模板 | revise，指定正确模板 |
| CQO-02 | 元数据完整 | frontmatter 必填字段齐全（title/id/status/owner/created/updated） | revise，列出缺失字段 |
| CQO-03 | 路径规范 | 存放路径符合 ZT-2026-007 | revise，指定正确路径 |
| CQO-04 | 结构完整 | 章节结构符合对应规范 | revise，列出缺失章节 |
| CQO-05 | 格式合规 | 标记、表格、引用格式符合 governance 规范 | 视严重程度 pass with note 或 revise |

### 判定规则

| 结果 | 条件 | 后续 |
|------|------|------|
| **pass** | CQO-01~05 全部通过 | 进入 Check |
| **revise** | CQO-01~04 有 1-2 项不通过 | 退回原 Agent 修改，同一 cycle |
| **reject** | CQO-01~04 有 3+ 项不通过 | 退回原 Agent 重做 + 通知银月，同一 cycle |

### CQO Spawn 协议

```
sessions_spawn({
    agentId: "cqo",
    task: "CQO 合规审核",
    input: {
        task_card_id: "{TASK_ID}",
        deliverable_path: "10_Projects/{PROJECT_ID}/{TOPIC_ID}/deliverables/{FILENAME}",
        review_items: ["CQO-01", "CQO-02", "CQO-03", "CQO-04", "CQO-05"]
    }
})
```

### CQO 合规报告

- **存储路径**：`10_Projects/{PROJECT_ID}/{TOPIC_ID}/deliverables/CQO-{TASK_ID}-{TIMESTAMP}.md`
- **模板**：`TMPL-CQO-COMPLIANCE-REPORT.md`
- **退回时**：CQO 合规报告附在退回通知中，原 Agent 按报告修改

### 规则

- CQO 审核超时（5 分钟）：默认 pass，记录超时告警，CQO 合规报告中标记 `timeout: true`
- CQO 审核不通过不影响 Task 状态标记（仍为 `[P]`）
- CQO 退回时 PDCA 仍在同一 cycle，不改 cycle_index
- CQO revise 上限：同一 cycle 内 CQO revise 最多 3 次。第 4 次仍 revise → 自动升级为 reject，通知银月
- CQO 合规闸门是合规性检查，不改变 PDCA 四阶段本质

## 九、错误码

| 错误码 | 说明 |
|--------|------|
| E_READ_FAIL | 读取交付物失败 |
| E_CHECKLIST_MISSING | 检查清单不存在 |
| E_ISSUE_NOT_FOUND | 问题记录不存在 |
| E_INVALID_LEVEL | 级别参数非法 |

---

*版本: 4.2.0 | 更新: 2026-05-06 | 变更: 新增 CQO 合规闸门*

## Related Skills
- [[openclaw-governance-task]] - 任务管理，质量标准应用于任务验收
- [[openclaw-governance-delegation]] - 授权与等级判定，Review 级别判定
- [[openclaw-governance-evolution]] - Governance 体系元治理，持续改进 PDCA
- [[openclaw-governance-pipeline]] - 流水线编排，Review-gate 触发入口
