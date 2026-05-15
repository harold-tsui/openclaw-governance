# N4-P1-T11 · 开发路线图

> **Topic**: nucleus-abilities 开发
> **PIC**: CTO (菡云芝)
> **创建日期**: 2026-04-19

---

## Phase 1: 框架建设（本周）

| 任务 | 状态 | 说明 |
|------|------|------|
| 创建 nucleus-abilities 目录 | ✅ 已完成 | skills/nucleus-abilities/ |
| 迁移 5 个专业能力模块 | ✅ 已完成 | nucleus-abilities-intelligence/nucleus-abilities-financial/nucleus-abilities-content/nucleus-abilities-visual/nucleus-abilities-infrastructure |
| 创建 skills-extension.yaml | ✅ 已完成 | 技能注册 + 关键词路由 |
| 创建 README.md | ✅ 已完成 | 框架定位与模块说明 |
| 创建 TOPIC-BRIEF.md | ✅ 已完成 | Topic 级别定义 |
| 更新 N4-P1-T09 Topic | ✅ 已完成 | 明确 nucleus-tools 聚焦通用工具 |

**Phase 1 目标**: 建立清晰的框架边界，完成模块迁移和注册。

---

## Phase 2: 能力实现（2-8 周）

> **开发者**: CTO (菡云芝)
> **评审者**: 对应 Agent 负责人（如 intelligence 邀请 CIO 评审）

### 2.1 nucleus-abilities-intelligence（使用者：CIO）

| 任务 | 预计 | 说明 | 评审者 |
|------|------|------|--------|
| 竞品分析函数 | Week 2-3 | 功能对比、优劣势、定价分析 | CIO |
| 市场调研函数 | Week 3-4 | 行业趋势、用户画像、市场规模 | CIO |
| 信息收集函数 | Week 4-5 | 多源信息聚合、资料汇总 | CIO |
| 端到端验证 | Week 5 | 关键词触发 → 分析输出 | CIO |

### 2.2 nucleus-abilities-financial（使用者：CFO）

| 任务 | 预计 | 说明 | 评审者 |
|------|------|------|--------|
| 预算管理函数 | Week 2-3 | 预算编制、跟踪、调整 | CFO |
| 投资决策函数 | Week 3-4 | ROI 计算、风险评估 | CFO |
| 财务分析函数 | Week 4-5 | 报表分析、数据预测 | CFO |
| 端到端验证 | Week 5 | 关键词触发 → 决策输出 | CFO |

### 2.3 nucleus-abilities-content（使用者：CCO）

| 任务 | 预计 | 说明 | 评审者 |
|------|------|------|--------|
| 文案审核函数 | Week 2-3 | 内容质量、品牌调性检查 | CCO |
| 文案优化函数 | Week 3-4 | 风格建议、传播力评估 | CCO |
| 品牌策略函数 | Week 4-5 | 品牌一致性检查 | CCO |
| 端到端验证 | Week 5 | 关键词触发 → 内容输出 | CCO |

### 2.4 nucleus-abilities-visual（使用者：CVO）

| 任务 | 预计 | 说明 | 评审者 |
|------|------|------|--------|
| 视觉审核函数 | Week 2-3 | 设计稿评审 | CVO |
| UI/UX 检查函数 | Week 3-4 | 规范性检查、交互建议 | CVO |
| 品牌视觉函数 | Week 4-5 | 视觉一致性 | CVO |
| 端到端验证 | Week 5 | 关键词触发 → 视觉建议 | CVO |

### 2.5 nucleus-abilities-infrastructure（使用者：CTO）

| 任务 | 预计 | 说明 | 评审者 |
|------|------|------|--------|
| 架构评估函数 | Week 2-3 | 技术选型评估、架构设计建议 | - |
| 工具链集成 | Week 3-4 | CI/CD、测试、监控工具 | - |
| 安全审计函数 | Week 4-5 | 安全加固建议 | - |
| 端到端验证 | Week 5 | 关键词触发 → 技术建议 | - |

**Phase 2 目标**: CTO 完成 5 个能力模块（nucleus-abilities-intelligence/financial/content/visual/infrastructure）的核心函数实现 + 邀请对应 Agent 评审 + 端到端验证。

---

## Phase 3: expert 系统（8-16 周）

### 3.1 规划与设计（Week 8-10）

| 任务 | 说明 |
|------|------|
| 定义 expert 系统边界 | 与 abilities/tools 的区别 |
| 设计 cross-domain 分析流程 | 多 Agent 协同分析 |
| 制定 expert 报告模板 | 深度调研、战略分析格式 |

### 3.2 核心实现（Week 10-14）

| 任务 | 说明 |
|------|------|
| 创建 nucleus-expert 目录 | skills/nucleus-expert/ |
| 投资决策专家系统 | 市场 + 财务 + 技术综合分析 |
| 战略分析专家系统 | 行业 + 竞品 + 内部能力综合评估 |
| 产品规划专家系统 | 用户需求 + 技术可行 + 商业价值 |

### 3.3 集成与验证（Week 14-16）

| 任务 | 说明 |
|------|------|
| 三层能力体系集成 | tools → abilities → expert |
| 触发路由完善 | 自动判断复杂度，选择合适层级 |
| 全链路验证 | 端到端测试 |

**Phase 3 目标**: 建立三层能力体系，实现复杂场景下的专家级分析能力。

---

## 里程碑总览

| 里程碑 | 时间 | 交付物 |
|--------|------|--------|
| 框架完成 | Week 1（本周） | 目录结构 + skills-extension.yaml + README |
| 首批能力可用 | Week 5 | intelligence + financial 端到端可用 |
| 全能力可用 | Week 8 | 5 个能力模块全部端到端可用 |
| expert 设计完成 | Week 10 | nucleus-expert 框架 + 设计文档 |
| expert 可用 | Week 16 | 三层能力体系完整可用 |

---

*创建: 2026-04-19 | PIC: CTO (菡云芝)*
