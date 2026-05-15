# TOPIC-BRIEF · N4-P1-T11

> **Topic ID**: N4-P1-T11
> **Topic 名称**: nucleus-abilities 开发
> **Topic PIC**: CTO (菡云芝)
> **上位 Project**: ZT-P015 NUCLEUS 4.0
> **状态**: 🟢 Active
> **创建时间**: 2026-04-19

---

## 一、Topic 目标

开发 `skills/nucleus-abilities/` 框架，为各 Agent 提供领域专业能力扩展。与 `nucleus-tools`（通用工具）互补，聚焦 Agent 的专业判断和分析能力。

---

## 二、核心需求

| 需求 | 说明 |
|------|------|
| **框架建设** | 创建 nucleus-abilities 目录结构，迁移 5 个专业能力模块 |
| **技能注册** | 通过 `skills-extension.yaml` 统一注册，关键词触发路由 |
| **Agent 绑定** | 每个能力绑定对应 Agent（cfo/cto/cio/cco/cvo） |
| **渐进实现** | 先框架，后逐步完善各 Agent 专业能力 |

---

## 三、子模块清单

| 模块 | 绑定 Agent | 状态 | 说明 |
|------|-----------|------|------|
| nucleus-abilities-intelligence | CIO (元瑶) | ✅ 已迁移 | 情报调研、竞品分析 |
| nucleus-abilities-financial | CFO (南宫婉) | ✅ 已迁移 | 预算管理、投资决策 |
| nucleus-abilities-content | CCO (紫灵) | ✅ 已迁移 | 内容运营、品牌调性 |
| nucleus-abilities-visual | CVO (宝花) | ✅ 已迁移 | 视觉设计、UI/UX |
| nucleus-abilities-infrastructure | CTO (菡云芝) | ✅ 已迁移 | 技术架构、工具链 |

---

## 四、Task 列表

> **开发者**: CTO (菡云芝) — 所有 skills 的开发由 CTO 统一负责
> **评审者**: 对应 Agent 负责人（如 intelligence 邀请 CIO 评审）

| Task ID | Task 名称 | 开发者 | 评审者 | 状态 |
|----------|-----------|--------|--------|------|
| N4-P1-T11-T01 | 框架建设：目录创建 + 模块迁移 | CTO | - | [C] 已完成 |
| N4-P1-T11-T02 | intelligence 能力完善 | CTO | CIO | [P] 待启动 |
| N4-P1-T11-T03 | financial 能力完善 | CTO | CFO | [P] 待启动 |
| N4-P1-T11-T04 | content 能力完善 | CTO | CCO | [P] 待启动 |
| N4-P1-T11-T05 | visual 能力完善 | CTO | CVO | [P] 待启动 |
| N4-P1-T11-T06 | infrastructure 能力完善 | CTO | - | [P] 待启动 |
| N4-P1-T11-T07 | 技能注册验证 | CTO | 全员 | [P] 待启动 |

---

## 五、交付物清单

| 交付物 | 路径 |
|--------|------|
| 技能扩展注册表 | `skills/nucleus-abilities/skills-extension.yaml` |
| 框架说明 | `skills/nucleus-abilities/README.md` |
| 开发路线图 | `topics/N4-P1-T11/ROADMAP.md` |
| 各模块 SKILL.md | `skills/nucleus-abilities/{module}/SKILL.md` |

---

## 六、依赖与风险

| 类型 | 描述 | 影响程度 |
|------|------|----------|
| **依赖** | nucleus-tools 保持通用工具定位 | 低（当前目录清晰分离） |
| **风险** | 与 nucleus-expert（规划中）的边界需持续明确 | 中 |
| **风险** | 各 Agent 需理解自身能力框架 | 中（需 Agent 培训） |

---

## 七、Harold Review 节点

| 里程碑 | Review 内容 | Review 级别 |
|--------|-------------|-------------|
| 框架建设完成 | 本文件 + README + skills-extension.yaml | L2 |
| 首个能力实现 | intelligence 或 financial 模块 | L3 |
| 全能力注册验证 | 关键词触发端到端测试 | L2 |

---

*创建: 2026-04-19 | PIC: CTO (菡云芝)*
