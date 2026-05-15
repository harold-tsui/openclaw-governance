# TOPIC-BRIEF · N4-P1-T07

> **文件性质**：Topic 工作简报
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/10_Projects/ZT-P015_NUCLEUS-4-0/topics/N4-P1-T07/TOPIC-BRIEF.md`
> **版本**：v1.0
> **上位引用**：NUCLEUS 4.0 PROJECT-CHARTER.md

---

## 一、Topic 基本信息

| 字段 | 内容 |
|---|---|
| **Topic ID** | N4-P1-T07 |
| **Topic 名称** | Skill 流程化设计研究（BotLearn 学习） |
| **所属 Project** | ZT-P015 NUCLEUS 4.0 |
| **Topic PM** | 张铁 (cqo) |
| **创建日期** | 2026-04-15 |
| **当前状态** | 🟡 Active |
| **优先级** | P1 |
| **研究性质** | 方法论建设（为 NUCLEUS 4.0 提供设计参考） |

---

## 二、Topic 使命

> **研究 BotLearn Skill 的流程化设计，提炼可复用的设计模式，逐步应用到 governance skills，让我们的流程也能如 BotLearn 一样流畅清晰。**

---

## 三、研究范围

### 3.1 BotLearn 核心设计理念

| 设计理念 | 说明 | BotLearn 实现方式 |
|----------|------|------------------|
| **CLI-via-markdown** | Agent IS the runtime，SKILL.md 即 CLI 定义 | SKILL.md 定义命令路由、术语表、操作原则 |
| **懒加载机制** | 只加载需要的模块，不一次性加载所有 | Intent → Module Mapping（意图到模块映射） |
| **状态感知路由** | 根据 state.json 决定下一步 | State-Aware Routing |
| **Config-First 原则** | 敏感操作前检查 config.json 权限 | Operational Principles §1 |
| **命令规范格式** | 每个命令有固定的定义结构 | Command Spec（Command/Script/API/Required/Optional/Returns/State/Display/Errors） |
| **模板文件机制** | 标准化的初始配置 | templates/config.json、templates/state.json |

### 3.2 关键文件结构

| 文件 | 作用 | 对应我们的文件 |
|------|------|---------------|
| `skill.md` | 命令路由器 + 术语表 + 操作原则 | SKILL.md |
| `core/commands.md` | 命令规范定义（Command Spec） | 需新增 |
| `core/api-patterns.md` | API 调用模式（统一请求/响应/错误处理） | 需新增 |
| `templates/state.json` | 状态模板 | 需新增 |
| `templates/config.json` | 权限配置模板 | 需新增 |

### 3.3 对比分析

| 维度 | BotLearn | governance-core（当前） | 改进方向 |
|------|----------|------------------------|----------|
| **命令定义** | 结构化 Command Spec | 协议描述式 | 建立命令规范格式 |
| **错误处理** | 统一的 HTTP 错误码映射表 | 散落在各处 | 集中到 api-patterns |
| **状态管理** | state.json 模板 + 状态感知路由 | 状态文件散落 | 建立统一状态模板 |
| **懒加载** | Intent → Module Mapping | 一次性加载全部 | 建立命令路由器 |
| **术语表** | Glossary 章节 | 无 | 建立术语表 |

---

## 四、研究方法

### Phase 1：理解 BotLearn 设计（当前）

- [ ] 读取 BotLearn SKILL.md、commands.md、api-patterns.md
- [ ] 提炼 6 个核心设计理念
- [ ] 建立对比分析表（BotLearn vs governance-core）

### Phase 2：设计改进方案

- [ ] 定义 governance-core 命令规范格式
- [ ] 设计状态模板（state.json）
- [ ] 设计权限配置模板（config.json）
- [ ] 建立术语表

### Phase 3：试点应用

- [ ] 先应用到 governance-heartbeat（最简单的 Skill）
- [ ] 建立 heartbeat 命令规范
- [ ] 建立 heartbeat-state.json 模板

### Phase 4：推广验证

- [ ] 应用到 governance-task
- [ ] 应用到 governance-quality
- [ ] 验证效果（是否更流畅清晰）

---

## 五、Task 列表

| Task ID | Task 名称 | 状态 | 说明 |
|---|---|---|---|
| N4-P1-T07-T01 | BotLearn 设计理念提炼 | ✅ Done | Phase 1 核心任务 |
| N4-P1-T07-T02 | Dispatch 引导入口设计 | ⬜ Pending | Harold 建议的改进 |
| N4-P1-T07-T03 | PDCA-A 正确理解修正 | ⬜ Pending | Harold 的理论修正 |
| N4-P1-T07-T04 | 治理体系P0问题修复 | 🟡 Active | 银月诊断的P0+🔴问题 |
| N4-P1-T07-T05 | governance-core 命令规范设计 | ⬜ Pending | Phase 2 任务 |
| N4-P1-T07-T06 | heartbeat 试点应用 | ⬜ Pending | Phase 3 任务 |

---

## ⭐ 紧急任务：治理体系P0问题修复（N4-P1-T07-T04）

> **来源**：银月诊断报告 GOV-FIX-2026-001
> **执行人**：张铁
> **优先级**：P0（最高）
> **预计完成**：今天下午

**修复内容**：

| 优先级 | 问题 | 修复动作 | 预估时间 |
|--------|------|----------|----------|
| **P0** | AGENTS.md/IDENTITY.md 引用断裂 | 修正为通过Skill间接引用 | 30分钟 |
| **🔴** | automation-levels.yaml 缺失 | 创建配置文件 | 30分钟 |
| **🔴** | data-classification.yaml 缺失 | 创建配置文件 | 30分钟 |
| **🔴** | TMPL-DOD.md 缺失 | 创建模板文件 | 30分钟 |
| **🔴** | governance-hierarchy 引用声明缺失 | 补充agents.yaml/persons.yaml声明 | 30分钟 |

**总计**：约2.5小时

---

## 六、交付物

| 交付物 | 路径 | 频率 |
|---|---|---|
| 设计理念提炼报告 | `SYS-GOV-TP06/outputs/botlearn-design-analysis.md` | Phase 1 结束时 |
| 命令规范格式定义 | `SYS-GOV-TP06/outputs/command-spec-template.md` | Phase 2 结束时 |
| 状态模板设计 | `SYS-GOV-TP06/templates/state.json` | Phase 2 结束时 |
| heartbeat 试点报告 | `SYS-GOV-TP06/outputs/heartbeat-pilot-report.md` | Phase 3 结束时 |

---

## 七、验收标准

| 标准 | 说明 |
|---|---|
| Phase 1 完成 | BotLearn 设计理念提炼报告完成，Harold 审阅通过 |
| Phase 2 完成 | 命令规范格式定义完成，至少 1 个 Skill 应用验证 |
| Phase 3 完成 | heartbeat 试点报告完成，效果验证（更流畅清晰） |
| Phase 4 完成 | 至少 3 个 governance skills 应用新设计 |

---

## 八、关键里程碑

| 里程碑 | 目标日期 | 验收标准 |
|---|---|---|
| Phase 1 完成 | 2026-04-17 | BotLearn 设计理念提炼报告 |
| Phase 2 完成 | 2026-04-20 | 命令规范格式定义 + 状态模板 |
| Phase 3 完成 | 2026-04-25 | heartbeat 试点报告 |
| Phase 4 完成 | 2026-04-30 | 3 个 Skills 应用验证 |

---

## 九、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| BotLearn 设计过于复杂 | 学习曲线陡峭 | 分阶段学习，先掌握核心理念 |
| governance-core 改动太大 | 影响现有流程 | 先用新 Skill 验证，再逐步改造旧 Skill |
| Harold 时间有限 | 无法及时审阅 | 先完成技术验证，再申请审阅 |

---

## 十、BotLearn 核心文件清单

> 研究时需读取的关键文件

| 文件路径 | 内容摘要 |
|----------|----------|
| `/Users/haroldtsui/Workspaces/openclaw/main/skills/botlearn/skill.md` | 命令路由器 + 术语表 + 操作原则 |
| `/Users/haroldtsui/Workspaces/openclaw/main/skills/botlearn/core/commands.md` | 命令规范定义（Command Spec） |
| `/Users/haroldtsui/Workspaces/openclaw/main/skills/botlearn/core/api-patterns.md` | API 调用模式 + 错误处理 |
| `/Users/haroldtsui/Workspaces/openclaw/main/skills/botlearn/templates/state.json` | 状态模板 |
| `/Users/haroldtsui/Workspaces/openclaw/main/skills/botlearn/templates/config.json` | 权限配置模板 |

---

*Version: v1.0 | 创建日期: 2026-04-15 | 创建人: cqo*