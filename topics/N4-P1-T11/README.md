# N4-P1-T11 · nucleus-abilities 开发说明

> **Topic 名称**: nucleus-abilities 开发
> **PIC**: CTO (菡云芝)
> **创建日期**: 2026-04-19

---

## 一、开发背景

NUCLEUS 4.0 技能体系需要区分两类能力：

1. **nucleus-tools** — 通用工具集（自动化脚本、流程工具、通用函数）
2. **nucleus-abilities** — Agent 专业能力（领域知识、分析能力、决策支持）

本 Topic 负责 nucleus-abilities 框架建设和能力实现。

---

## 二、开发内容

### Phase 1: 框架建设

- [x] 创建 `skills/nucleus-abilities/` 目录
- [x] 迁移 5 个专业能力模块
- [x] 创建 `skills-extension.yaml`
- [x] 创建 README.md 和 TOPIC-BRIEF.md
- [x] 创建 ROADMAP.md

### Phase 2: 能力实现（详见 ROADMAP.md）

- 各 Agent 专业能力模块的完善和验证

### Phase 3: expert 系统（详见 ROADMAP.md）

- 规划 nucleus-expert，构建三层能力体系

---

## 三、与 N4-P1-T09 的关系

| Topic | 定位 | 内容 |
|-------|------|------|
| N4-P1-T09 | nucleus-tools 开发 | 通用工具集（nucleus-tools-sider-automation 等） |
| N4-P1-T11 | nucleus-abilities 开发 | Agent 专业能力（5 个模块） |

两个 Topic 并行推进，定位清晰互补。

---

*创建: 2026-04-19 | PIC: CTO (菡云芝)*
