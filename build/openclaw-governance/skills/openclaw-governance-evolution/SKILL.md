---
name: evolving-governance
description: |
  Evolving the governance skill system through PDCA evaluation, version upgrades, and lifecycle management.
  
  Activates when: User requests system evaluation, skill evolution, or governance improvement (explicit trigger)
  
  Capabilities:
  - PDCA evaluation framework for all governance skills
  - Skill version upgrade decisions (patch/minor/major)
  - Architecture improvement (new skills, mergers, deprecation)
  - Quality gate monitoring and error threshold detection
  - NUCLEUS execution engine integration (policy vs execution)
  
  Keywords: evolution, meta-governance, skill-lifecycle, pdca-evaluation, upgrade, architecture
  
  For detailed documentation, see:
  - references/evolution-details.md

author: "银月 (Silver Moon)"
license: "Internal Use Only"
version: "2.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L4"
  os: ["darwin", "linux"]
  tags: ["evolution", "meta-governance", "pdca", "skill-lifecycle", "upgrade"]
  engine: "openclaw-governance-nucleus"
  dependencies:
    - openclaw-governance-core
    - openclaw-governance-hierarchy
    - openclaw-governance-quality
    - openclaw-governance-config
---

# Governance Evolution - 元治理层

Tags: #governance, #evolution, #pdca, #lifecycle, #nucleus

> **核心定位**：Governance Skill 体系的"操作系统更新程序"
> **v2.1.0**: 补充 When to Use / Pitfalls 章节

## 何时使用

- **System evaluation**: Harold 请求治理系统健康评估
- **Periodic review**: 每月/每季度自动评估（通过 heartbeat）
- **Skill upgrade decisions**: 判定 Skill 是否需要 patch/minor/major 版本升级
- **Architecture changes**: 合并、拆分或废弃 Skill
- **Do NOT use for**: 任务级别的 PDCA 循环 — 那是 `governance-quality` 的职责

## 常见陷阱

1. **Evolution PDCA ≠ Quality PDCA**: Evolution 在系统级别工作（Skill 版本、架构）。Quality 在任务/交付物级别工作。不要混淆作用域。
2. **SemVer 决策是严格的**: 架构重构或 Skill 合并 = Major。新功能/协议 = Minor。Bug 修复/文档更新 = Patch。不要低估破坏性变更的版本号。
3. **质量门控阈值是累积的**: 错误率 > 10% 触发立即 PDCA。但如果 SKILL.md > 500 行且依赖数 > 5，两个问题会叠加 — 解决所有门控，而不只是最严重的那个。
4. **废弃需要迁移指南**: 标记 Skill 为废弃时，必须提供清晰的迁移路径。不要在没有指引的情况下移除功能。

---

## 一、定位与架构关系

### 1.1 职责边界

| governance-evolution（本模块） | governance-nucleus（执行引擎） |
|---|---|
| 决策"改什么"，输出改进方案 | 自动执行 PDCA 循环，持久化调度 |
| SKILL.md 框架描述 | SKILL.md + Python 可执行代码 |
| 输出：Skill 版本升级、架构改进 | 输出：cycles/ 运行时数据 |

### 1.2 触发路径

| 路径 | 触发方 | 说明 |
|------|--------|------|
| 用户显式请求 | Harold | 评估系统健康度 |
| 定期评估 | heartbeat | 每月/季度自动触发 |

---

## 二、PDCA 评估框架（摘要）

### 指标采集

| 指标 | 来源 | 采集方式 |
|------|------|---------|
| 错误率 | governance-quality | 审查问题数/交付物数 |
| 使用频率 | governance-heartbeat | 加载次数/周期 |
| 版本迭代速度 | SKILL.md 版本历史 | 版本数/月 |

### 评估等级

| 等级 | 条件 | 行动 |
|------|------|------|
| **优秀** | 错误率 < 2% | 维持现状 |
| **良好** | 错误率 2-5% | 观察改进 |
| **需改进** | 错误率 > 5% | 启动 PDCA 改进 |
| **待废弃** | 长期未使用/功能重复 | 标记 deprecated |

> 详细评估框架、等级定义：[references/evolution-details.md]({baseDir}/references/evolution-details.md)

---

## 三、版本升级决策（摘要）

### SemVer 规则

| 变更类型 | 版本增量 | 示例 |
|---------|---------|------|
| 架构重构、Skill 合并/拆分 | Major | v2 → v3 |
| 新功能、新函数、新协议 | Minor | v2.1 → v2.2 |
| Bug 修复、文档更新 | Patch | v2.1.0 → v2.1.1 |

---

## 四、架构改进（摘要）

| 类型 | 说明 | 输出 |
|------|------|------|
| **新 Skill** | 新增独立能力 | 新 SKILL.md + 注册表更新 |
| **Skill 合并** | 减少职责重叠 | 合并后 SKILL.md + 废弃旧文件 |
| **Skill 废弃** | 功能不再需要 | 标记 deprecated + 迁移指南 |
| **层级调整** | 调整加载优先级 | 更新 governance-core 注册表 |

> 详细改进流程、质量门控：[references/evolution-details.md]({baseDir}/references/evolution-details.md)

---

## 五、执行流程（摘要）

```
用户请求系统评估 → 采集各 Skill 质量指标 → 评估等级判定
    ↓
生成改进建议 → 版本升级决策 → 执行架构改进
    ↓
更新注册表和文档
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **2.0.0** | 2026-04-22 | SKILL.md 瘦身至 <200 行，详细内容移至 references/evolution-details.md |

---

*版本: 2.1.0 | 更新: 2026-04-23 | 变更: 补充 When to Use / Pitfalls 章节*

## Related Skills
- [[openclaw-governance-nucleus]] - PDCA Harness，路径 A 执行引擎
- [[openclaw-governance-quality]] - 质量管控，评估指标来源
- [[openclaw-governance-core]] - 核心运行机制，Skill 注册表
- [[openclaw-governance-hierarchy]] - 层级管理，架构改进对象
