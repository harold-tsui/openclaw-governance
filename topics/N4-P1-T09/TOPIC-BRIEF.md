# TOPIC-BRIEF · N4-P1-T09

> **Topic ID**: N4-P1-T09
> **Topic 名称**: nucleus-tools 开发
> **Topic PIC**: CTO (菡云芝)
> **上位 Project**: ZT-P015 NUCLEUS 4.0
> **状态**: 🟢 Active
> **创建时间**: 2026-04-19

---

## 一、Topic 目标

开发和完善 `skills/nucleus-tools` 目录下的通用工具模块，聚焦**通用工具集**（自动化脚本、流程工具、通用函数），与 `nucleus-abilities`（Agent 专业能力）形成互补。

---

## 二、核心需求

| 需求 | 说明 |
|------|------|
| **技能注册** | 通过 `skills-extension.yaml` 统一注册，关键词触发路由 |
| **模块解耦** | 每个子模块独立 SKILL.md，按需加载 |
| **Agent 绑定** | 每个技能绑定对应 Agent（cfo/cto/cio/cco/cvo） |
| **渐进实现** | 当前为框架/规范定义阶段，核心逻辑待实现 |

---

## 三、子模块清单

> **注意**：5 个 Agent 专业能力模块（intelligence/financial/content/visual/infrastructure）已迁移至 `skills/nucleus-abilities/`（见 N4-P1-T11）。nucleus-tools 保留通用工具定位。

| 模块 | 负责人 | 状态 | 说明 |
|------|--------|------|------|
| nucleus-tools-sider-automation | 通用 | v1.4 ✅ | Sider.ai 浏览器自动化（模型对比评审） |
| openclaw-governance-infrastructure | CTO (菡云芝) | v1.1.0 ⚠️ | 原模块在 nucleus-tools，专业版本已迁移至 nucleus-abilities |
| openclaw-governance-financial | CFO (南宫婉) | ⏸️ ⚠️ | 原模块在 nucleus-tools，专业版本已迁移至 nucleus-abilities |
| openclaw-governance-intelligence | CIO (元瑶) | ⏸️ ⚠️ | 原模块在 nucleus-tools，专业版本已迁移至 nucleus-abilities |
| openclaw-governance-content | CCO (紫灵) | ⏸️ ⚠️ | 原模块在 nucleus-tools，专业版本已迁移至 nucleus-abilities |
| openclaw-governance-visual | CVO (宝花) | ⏸️ ⚠️ | 原模块在 nucleus-tools，专业版本已迁移至 nucleus-abilities |

---

## 四、Task 列表

| Task ID | Task 名称 | 状态 | 说明 |
|----------|-----------|------|------|
| N4-P1-T09-T01 | 现状盘点与框架整理 | [C] 已完成 | 本 Topic 创建任务 |
| N4-P1-T09-T02 | 通用工具持续完善 | [P] 待启动 | 新增通用自动化/流程工具 |
| N4-P1-T09-T03 | 模块迁移确认 | [C] 已完成 | 5 个 Agent 模块已迁移至 nucleus-abilities（N4-P1-T11） |

---

## 五、交付物清单

| 交付物 | 路径 |
|--------|------|
| 技能扩展注册表 | `skills/nucleus-tools/skills-extension.yaml` |
| 各模块 SKILL.md | `skills/nucleus-tools/{module}/SKILL.md` |
| Topic 实现说明 | `topics/N4-P1-T09/README.md` |

---

## 六、依赖与风险

| 类型 | 描述 | 影响程度 |
|------|------|----------|
| **依赖** | 各 Agent 需理解自身技能框架 | 中 |
| **风险** | 模块间触发词可能冲突 | 低（当前关键词差异明显） |
| **风险** | Python 核心逻辑尚未实现 | 中（需逐步开发） |

---

## 七、Harold Review 节点

| 里程碑 | Review 内容 | Review 级别 |
|--------|-------------|-------------|
| 框架整理完成 | 本文件 + README.md | L2 |
| 首个模块实现 | financial 或 infrastructure | L3 |
| 全模块注册验证 | 关键词触发端到端测试 | L2 |

---

*创建: 2026-04-19 | PIC: CTO (菡云芝)*
