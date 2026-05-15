# N4-P1-T09 · nucleus-tools 实现说明

> **实现依据**：`skills/nucleus-tools/` 目录现有内容整理
> **整理日期**：2026-04-19

---

## 一、目录结构

```
skills/nucleus-tools/
├── skills-extension.yaml              # 技能注册表 + 关键词触发路由
├── openclaw-governance-financial/     # 财务治理技能
│   └── SKILL.md
├── openclaw-governance-infrastructure/# 基础设施技能
│   └── SKILL.md
├── openclaw-governance-intelligence/  # 情报调研技能
│   └── SKILL.md
├── openclaw-governance-content/       # 内容运营技能
│   └── SKILL.md
├── openclaw-governance-visual/        # 视觉设计技能
│   └── SKILL.md
└── nucleus-tools-sider-automation/          # Sider.ai 自动化技能
    └── SKILL.md
```

---

## 二、子模块详细说明

### 2.1 skills-extension.yaml（注册中枢）

- **版本**: v1.1
- **功能**: 定义 6 个 L3 可扩展技能的注册信息和触发关键词
- **触发路由**: 将用户输入的关键词映射到对应技能模块

### 2.2 openclaw-governance-financial（财务治理）

| 属性 | 值 |
|------|-----|
| 负责人 | CFO (南宫婉) |
| 版本 | v1.0 |
| 状态 | ⏸️ 框架已定义，核心逻辑待实现 |
| 触发词 | 预算、投资、ROI、财务 |

**功能模块**:
- `budget_create / budget_track / budget_adjust` — 预算编制/跟踪/调整
- `investment_evaluate / investment_roi / investment_risk` — 投资评估/ROI/风险
- `analysis_report / analysis_data / analysis_forecast` — 财务报告/数据/预测

### 2.3 openclaw-governance-infrastructure（基础设施）

| 属性 | 值 |
|------|-----|
| 负责人 | CTO (菡云芝) |
| 版本 | v1.1.0 |
| 状态 | ✅ 已实现（规范定义） |
| 触发词 | 技术选型、架构设计、工具评估、流程优化、性能问题、安全审计、代码审查 |

**核心能力**:
- 技术选型评估
- 系统架构/微服务/数据流设计
- CI/CD、测试、监控工具集成
- 性能分析与优化
- 安全审计与加固

### 2.4 openclaw-governance-intelligence（情报调研）

| 属性 | 值 |
|------|-----|
| 负责人 | CIO (元瑶) |
| 版本 | v1.0.0 |
| 状态 | ⏸️ 框架已定义，核心逻辑待实现 |
| 触发词 | 调研、情报、竞品、市场、分析 |

**功能模块**:
- `competitor_analysis` — 竞品分析
- `market_research` — 市场情报收集
- `industry_scan` — 行业趋势扫描
- `info_collection` — 特定信息收集

### 2.5 openclaw-governance-content（内容运营）

| 属性 | 值 |
|------|-----|
| 负责人 | CCO (紫灵) |
| 版本 | v1.0.0 |
| 状态 | ⏸️ 框架已定义，核心逻辑待实现 |
| 触发词 | 内容、文案、品牌、传播、策划 |

**功能模块**:
- `content_review` — 文案内容审核
- `brand_check` — 品牌调性检查
- `copy_suggest` — 文案优化建议
- `strategy_review` — 传播策略审核

### 2.6 openclaw-governance-visual（视觉设计）

| 属性 | 值 |
|------|-----|
| 负责人 | CVO (宝花) |
| 版本 | v1.0.0 |
| 状态 | ⏸️ 框架已定义，核心逻辑待实现 |
| 触发词 | 视觉、设计、UI、UX、配色、布局 |

**功能模块**:
- `visual_review` — 视觉设计审核
- `ui_check` — UI 规范性检查
- `design_suggest` — 设计优化建议
- `brand_visual` — 品牌视觉一致性检查

### 2.7 nucleus-tools-sider-automation（Sider.ai 自动化）

| 属性 | 值 |
|------|-----|
| 负责人 | 通用（非 Agent 绑定） |
| 版本 | v1.4 |
| 状态 | ✅ 已实现 |
| 触发场景 | AI 模型对比评审、深度思考分析、联网搜索验证 |

**核心能力**:
- 浏览器自动化操作 Sider.ai 聊天界面
- 模型切换（支持 GPT/Gemini/Claude/DeepSeek/Qwen/GLM/Kimi/Grok）
- 思考模式/搜索模式切换
- 模型对比评审（标准/中文/深度/快速 4 种组合）
- 失败重试策略与降级规则

---

## 三、实现状态总结

| 模块 | 框架定义 | 触发路由 | 核心逻辑 | 端到端验证 |
|------|----------|----------|----------|------------|
| financial | ✅ | ✅ | ⏸️ 待实现 | ⏸️ |
| infrastructure | ✅ | ✅ | ✅ 规范完备 | ⏸️ |
| intelligence | ✅ | ✅ | ⏸️ 待实现 | ⏸️ |
| content | ✅ | ✅ | ⏸️ 待实现 | ⏸️ |
| visual | ✅ | ✅ | ⏸️ 待实现 | ⏸️ |
| nucleus-tools-sider-automation | ✅ | — | ✅ 已实现 | ✅ |

**总体进度**: 2/6 模块可用，4/6 模块待实现核心逻辑。

---

*整理: 2026-04-19 | 整理人: 张铁 (CQO)*
