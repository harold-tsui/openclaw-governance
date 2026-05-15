---
name: delegating-review
description: |
  Delegating authority, determining review levels, and managing human-in-the-loop protocols.
  
  Activates when: Review level determination, authorization check, or escalation needed
  
  Capabilities:
  - Review level judgment (L0-L5 decision automation)
  - Authorization checking for task execution
  - Human-in-the-Loop protocol (A/B/C/D structured approval)
  - Decision delegation and escalation routing
  - Automation level upgrade/downgrade evaluation
  - LESSON-LEARN integration
  
  Keywords: delegation, review-level, authorization, escalation, human-in-the-loop, approval
  
  For detailed documentation, see:
  - frameworks/HUMAN-DELEGATION.md
  - tests/test_delegation.py
  
author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "1.7.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L1"
  os: ["darwin", "linux"]
  tags: ["delegation", "review-level", "authorization", "human-in-the-loop", "decision-automation"]
  dependencies:
    - openclaw-governance-nucleus  # §10 Review request protocol (Human-in-the-Loop Check)
---

# 授权与等级判定 · Skill

Tags: #governance, #delegation, #authorization, #review-level, #decision-automation

> **触发模式**：描述匹配触发 + 模型主动 read()
> **v1.7.0**：补充 When to Use / Pitfalls 章节

## 何时使用

- **Review level determination**: 需要决定由谁来审核交付物（L0-L3）
- **Authorization check**: 验证某个 Actor 是否有权限执行某个操作
- **Automation level evaluation**: 评估 Agent 的决策自动化级别是否应该升级/降级
- **Human-in-the-Loop**: L3 任务需要 Harold 的结构化审批（A/B/C/D 协议）
- **Do NOT use for**: 任务创建/执行 — 那是 `governance-task` 的职责

## 常见陷阱

1. **禁止自我认证**: DOD 创建者 ≠ DOD 验证者。任务执行者 ≠ 质量审查者。验证必须通过不同的 Actor 进行。
2. **check_authorization vs check_route_permission**: 两者检查相同权限但时机不同 — `check_route_permission` 由 dispatch 在路由前调用，`check_authorization` 在执行具体操作前调用。
3. **不确定时默认 L3**: 如果无法确定 Review 级别（缺少策略、未知类型），默认 L3（Harold 全量审核）— 安全性优于便利性。
4. **L3 pending 7 天过期**: Harold 的 A/B/C/D 审核回复 7 天后过期。过期后通过 heartbeat Step 0 升级 — 不要无限等待。
5. **自动化级别调整只能逐级**: 不能跳级（L1→L3 是无效的）。升级需要 ≥80% DL 命中率 + 连续 3 次成功；降级在连续 2 次失败时触发。

---

## 引用规范

| 规范 | 版本 | 路径 | 说明 |
|------|------|------|------|
| **automation-levels.yaml** | v1.0 | `.system/governance/current/config/system/automation-levels.yaml` | Agent 决策自动化级别记录 |
| **governance-heartbeat** | v5.6.0 | — | 驱动器，触发评估 |
| **governance-task** | v6.0.2 | — | Task 生命周期管理 |
| **governance-hierarchy** | v2.5.0 | — | Project/Topic 管理 |
| **ARCH-001** | — | — | 治理框架 Skill 化架构（项目归档文件：`10_Projects/ZT-P009_NUCLEUS-2-0/.archive-deliverables/`） |

---

## 一、能力契约与函数索引

> **函数边界说明**：
> - `determine_review()`：判定 Review 级别（L0-L3），用于任务/主题/项目的评审路由
> - `check_authorization()`：判定 Actor 是否有权限执行某操作（create/close 等），返回 authorized true/false
> - `check_route_permission()`：路由前权限门控，由 governance-dispatch 主动调用；与 `check_authorization()` 的区别是**调用方不同**（dispatch 内部调用 vs 外部显式调用）和**场景不同**（路由决策前 vs 操作执行前）
> - `determine_automation_level()`：评估 Agent 决策自动化级别（L0-L5）
> - `adjust_automation_level()`：调整 Agent 决策自动化级别

### 1.1 determine_review()

**输入**：

```json
{
  "action": "determine_review",
  "target_type": "project|topic|task",
  "task_type": "常规|系统级|周期性|应急|一次性",
  "project_phase": "establishing|transition|cruising",
  "dl_refs": ["DL-2026-001"],
  "is_first_time": false,
  "priority": "P0|P1|P2|P3"
}
```

**输出**：

```json
{
  "status": "OK",
  "level": "L3",
  "rationale": [
    {
      "rule": "new_project",
      "source": "ARCH-002 v1.2",
      "desc": "新项目一律 L3"
    }
  ],
  "next_action": "等待 Harold 审批"
}
```

---

### 1.2 check_authorization()

> **职责**：判定 Actor 是否有权限执行某操作（如 create_project/close_task 等）。
> **调用方**：任何 Skill 或函数在执行操作前主动调用，验证操作合法性。
> **区别于 check_route_permission()**：本函数在**操作执行前**校验，check_route_permission() 在**路由决策前**校验（由 dispatch 调用）。

**输入**：

```json
{
  "action": "check_authorization",
  "actor": "main",
  "operation": "create_project",
  "target": "ZT-P010"
}
```

**输出**：

```json
{
  "status": "OK",
  "authorized": true,
  "constraints": []
}
```

---

## 二、Review 级别定义

| 级别 | 说明 | 审批人 | 抽检比例 |
|------|------|--------|----------|
| L3 | Harold 全量 Review | Harold | 100% |
| L2 | 银月抽检 + Harold Review 关键节点 | Harold | 20-30% |
| L1 | 银月验收 | 银月 | — |
| L0 | 直接验收 | 银月 | — |

> 详细级别定义、判级规则、阶段默认值：[references/level-rules.md]({baseDir}/references/level-rules.md)

---

## 三、决策自动化分级（ADAS 理念）

> **来源**：ARCH-001 v1.1 治理框架 Skill 化架构

| 级别 | 名称 | 描述 | 适用场景 |
|------|------|------|----------|
| **L5** | 完全自动化 | Agent 完全自主决策，仅定期汇报 | Routine Task，成熟流程 |
| **L4** | 高度自动化 | Agent 自主执行，异常自动上报 | 常规 Task，有明确规则 |
| **L3** | 有条件自动化 | Agent 执行 + 自动汇报，Harold 后置 Review | 已验证 Task，有 DL 支撑 |
| **L2** | 辅助决策 | Agent 提供 A/B/C/D 方案，Harold 确认后执行 | 重要 Task，需最佳实践 |
| **L1** | 人工辅助 | Agent 建议 + 关键节点等待 Harold 决策 | 复杂 Task，需人判断 |
| **L0** | 完全人工 | Harold 全程决策，Agent 仅执行 | 全新场景，无 DL 支撑 |

**升级条件**：DL 命中率 ≥ 80% + 连续 3 次成功
**降级条件**：连续 2 次失误 或 LL 驳回

> 详细评分算法、Agent 矩阵、adjust 流程：[references/automation-levels.md]({baseDir}/references/automation-levels.md)

---

## 四、判级规则（摘要）

| Target | 场景 | 级别 | 规则 |
|--------|------|------|------|
| Project | 新建/修改 | L3 | 一律 L3 |
| Topic | 首次类型/越界/跨项目 | L3 | 需 Harold 审批 |
| Topic | 范围内 | L2 | 过渡期/巡航期默认 |
| Task | 首次类型 | L3 | 新类型 |
| Task | P0 紧急 | L2 | 事后复盘 |
| Task | P1 | L1/L2 | 按阶段 |
| Task | P2/P3 | L0/L1 | 按阶段 |

> 详细决策流程和授权矩阵：[references/level-rules.md]({baseDir}/references/level-rules.md)

---

## 五、判级决策流程

```
接收判级请求 → 判断 target_type
    ├─ project → L3 → 返回
    ├─ topic → 首次/越界→L3; 范围内→按阶段
    └─ task → 首次→L3; P0→L2; 其他→按阶段
```

---

## 六、授权检查（摘要）

| 操作 | Harold | 银月 | Topic Main PIC | Task PIC |
|------|--------|------|----------------|----------|
| 创建 Project | ✅ | ❌ | ❌ | ❌ |
| 创建 Topic | ✅ | ✅ | ❌ | ❌ |
| 创建 Task | ✅ | ✅ | ✅ | ❌ |

> 完整权限矩阵和路由权限检查：[references/level-rules.md]({baseDir}/references/level-rules.md)

---

## 七、错误码

| 错误码 | 说明 |
|--------|------|
| E_UNAUTHORIZED | 未授权 |
| E_POLICY_MISSING | 策略缺失 → 返回默认 L3 |
| E_UNKNOWN_TYPE | 未知类型 → 返回 L3 |
| E_AGENT_NOT_FOUND | agent_id 不存在 |
| E_INVALID_LEVEL | 级别超出 L0-L5 |
| E_ADJUSTMENT_INVALID | 跨级调整 |

---

## 八、LESSON-LEARN 集成

> LESSON-LEARN 用于记录历史经验教训，通过四问法分析（DL 问题? Agent 错误? 新场景? 合理例外?）决定后续动作。

> 详细触发场景、四问法分析、数据源：[references/lesson-learn.md]({baseDir}/references/lesson-learn.md)

---

## 九、Review 请求协议（Human-in-the-Loop Check）

> **适用场景**：PDCA Check 阶段 `verdict=pending`（L2/L3 任务）时，向 Harold 发起结构化审批请求。

**核心流程**：
1. 按 §10.2 格式发送 A/B/C/D Review 请求到 Harold DM
2. 7 天有效期，超时 → heartbeat Step 0 升级 MISSION_BOARD `[!]`
3. Harold 回复解析：A→pass, B→partial, C→fail, D→补充信息
4. Act 阶段根据 Harold 决策触发知识沉淀（update_dl 或 create_lesson_learned）

> 完整请求模板、回复格式、解析规则、知识预加载、自动化联动：[references/review-protocol.md]({baseDir}/references/review-protocol.md)

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **1.7.0** | 2026-04-23 | 补充 When to Use / Pitfalls 章节 + frontmatter 增强（author/tags）|
| **1.6.0** | 2026-04-16 | §10.2 新增 A/B/C/D 快速回复选项 + 7 天有效期说明；§10.4 新增 A/B/C/D 解析映射表 + 超时（>7天）升级规则 |
| **1.5.0** | 2026-04-16 | 新增 §十 Review 请求协议（Human-in-the-Loop Check）：Review 请求模板、Harold 回复格式、解析规则、知识沉淀触发、知识预加载、自动化级别联动 |
| **1.4.0** | 2026-04-08 | ① header 版本号 1.2.0 统一为 1.4.0，footer 1.3.1 统一为 1.4.0；② 原两个 `## 四`（判级规则 + 判级决策流程）重编：判级规则 → `## 四`（§4.1-4.4），判级决策流程 → `## 五`；③ 原两个 `## 七`（错误码 + LESSON-LEARN）重编：错误码 → `## 七`，LESSON-LEARN → `## 九`，授权检查 → `## 六`，示例 → `## 八`，连续编号全段修复；④ 原 §四 子章节 `### 3.x` 改为 `### 4.x`；⑤ §一 头部补充函数边界说明，§1.2 `check_authorization()` 补充 vs `check_route_permission()` 区别说明，§6.5 `check_route_permission()` 同步补充对称说明；⑥ 引用规范表 `governance-task v3.3.0` 更新为 `v6.0.1`；⑦ §七 错误码表补全 E_AGENT_NOT_FOUND / E_INVALID_LEVEL / E_ADJUSTMENT_INVALID |
| 1.3.1 | 2026-04-02 | §五 新增权限检查（从 governance-dispatch 移入）；check_route_permission() 新增 |
| 1.2.0 | 2026-03-24 | 决策自动化分级（§三）、LESSON-LEARN 集成（§七）新增 |
| 1.0.0 | 2026-03-16 | 初始版本 |

---

*版本：1.7.0 | 更新：2026-04-23 | 变更：补充 When to Use / Pitfalls 章节*

## Related Skills
- [[openclaw-governance-task]] - 任务管理，授权决策应用
- [[openclaw-governance-quality]] - 质量管控，Review等级判定
- [[openclaw-governance-hierarchy]] - 层级管理，授权上下文
- [[openclaw-governance-knowledge]] - 知识管理，DL/LL 沉淀与预加载
- [[openclaw-governance-nucleus]] - PDCA Harness，Check 阶段 pending 触发入口