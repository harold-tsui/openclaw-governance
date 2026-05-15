---
id: "ZT-2026-009-v1.0"
title: "掌天智能 · YAML Frontmatter 规范 v1.0"
type: "official-document"
source_channel: "internal"
source_url: null
created_at: "2026-04-14T22:30:00+08:00"
updated_at: "2026-04-14T22:30:00+08:00"
author: "张铁 (CQO)"
status: "active"
privacy: "P2"
tags: ["数据治理", "规范文件", "Frontmatter", "Obsidian", "知识图谱"]
confidence: 1.00
verified: true
verified_by: "Harold Tsui"
verified_at: "2026-04-14T22:40:00+08:00"
expires_at: null
---
# ZT-2026-009 YAML Frontmatter 规范 v1.0

**文件编号**：ZT-2026-009
**版本**：v1.0
**发布日期**：2026-04-14
**起草人**：张铁 (CQO)
**审批人**：徐在红 (Harold Tsui)
**适用范围**：掌天智能所有 NUCLEUS 交付物（Project/Topic/Task/Skill）
**评审依据**：ZT-2026-004_数据治理体系规范 v2.3
**废止说明**：无（新增规范）

---

## 〇、前言

> 本规范是对《ZT-2026-004 数据治理体系规范》的补充，旨在：
> 1. 统一文档元数据格式，实现"文档即接口"
> 2. 支持 Obsidian 知识图谱可视化
> 3. 便于自动化索引、检索和关联分析
> 4. 符合"可见，即可治"的数据文化宣言

### 0.1 设计原则

| 原则 | 说明 |
|------|------|
| **最小必要** | 只定义核心元数据字段，避免过度冗余 |
| **向后兼容** | 不破坏现有文档结构（Frontmatter 置于文档顶部） |
| **可扩展** | 支持自定义业务字段，无强制字段限制 |
| **自动化友好** | 字段值可从现有文档内容提取，便于批量注入 |
| **Obsidian 兼容** | 完全兼容 Obsidian YAML frontmatter 语法规范 |
| **治理对齐** | 符合 ZT-2026-004 数据分级、路径语义化原则 |

---

## 一、核心字段定义

Frontmatter 必须置于文档顶部，以 `---` 包裹，YAML 语法规范。

### 1.1 Project 层（PROJECT-CHARTER.md）

```yaml
---
title: {Project 全称}
tags: [{分类标签}]
type: project
id: {Project ID}
status: {状态}
owner: {Agent ID}
priority: {P0-P3}
start_date: {YYYY-MM-DD}
end_date: {YYYY-MM-DD 或 null}
privacy: {P0-P3}
related_projects: [{关联 Project ID}]
related_topics: [{关联 Topic ID}]
aliases: [{别名列表}]
description: {一句话描述}
---
```

**必填字段**：`title`, `tags`, `type`, `id`, `status`, `owner`, `priority`, `privacy`

### 1.2 Topic 层（TOPIC-BRIEF.md）

```yaml
---
title: {Topic 全称}
tags: [{分类标签}]
type: topic
id: {Topic ID}
status: {状态}
owner: {Agent ID}
project: {所属 Project ID}
phase: {Phase 标识}
priority: {P0-P3}
privacy: {P0-P3}
related_tasks: [{关联 Task ID}]
related_topics: [{关联 Topic ID}]
start_date: {YYYY-MM-DD}
target_date: {YYYY-MM-DD 或 null}
---
```

**必填字段**：`title`, `tags`, `type`, `id`, `status`, `owner`, `project`, `priority`, `privacy`

### 1.3 Task 层（TASK-CARD.md）

```yaml
---
title: {Task 全称}
tags: [{分类标签}]
type: task
id: {Task ID}
status: {状态}
owner: {Agent ID}
topic: {所属 Topic ID}
project: {所属 Project ID}
priority: {P0-P3}
privacy: {P0-P3}
review_level: {L0-L3}
task_type: {任务类型}
deliverables: [{交付物文件名}]
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
due: {YYYY-MM-DD 或 null}
related_tasks: [{关联 Task ID}]
---
```

**必填字段**：`title`, `tags`, `type`, `id`, `status`, `owner`, `topic`, `project`, `priority`, `privacy`, `created`, `updated`

### 1.4 Skill 层（SKILL.md）

```yaml
---
name: {Skill 名称}
description: {简短描述}
tags: [{分类标签}]
type: skill
version: {版本号}
level: {L0-L3}
os: [{支持的操作系统}]
owner: {Agent ID}
privacy: {P0-P3}
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
related_skills: [{关联 Skill 名称}]
---
```

**必填字段**：`name`, `description`, `tags`, `type`, `version`, `owner`, `privacy`

---

## 二、字段值规范

### 2.1 Tags 命名规范

**原则**：预定义集合 + 自由命名为主

#### 2.1.1 自动注入 Tags（系统自动添加，无需手动输入）

| Tag | 来源字段 | 说明 |
|-----|----------|------|
| `#project` / `#topic` / `#task` / `#skill` | `type` | 层级标识 |
| `#active` / `#blocked` / `#completed` / `#draft` | `status` | 状态标识 |
| `#P0` / `#P1` / `#P2` / `#P3` | `priority` / `privacy` | 优先级/隐私标识 |
| `#owner:{agent-id}` | `owner` | 责任人标识 |
| `#project:{project-id}` | `project` | 所属项目标识 |

#### 2.1.2 预定义业务 Tags（可选，推荐使用）

| 分类 | Tags 示例 | 说明 |
|------|----------|------|
| **领域类** | `#governance`, `#ecommerce`, `#automotive`, `#media` | 业务领域 |
| **功能类** | `#pdca`, `#heartbeat`, `#dispatch`, `#quality`, `#data` | 核心功能 |
| **技术类** | `#python`, `#openclaw`, `#obsidian`, `#llm`, `#tts` | 技术栈 |
| **阶段类** | `#phase1`, `#phase2`, `#phase3` | 项目阶段 |

#### 2.1.3 自由命名 Tags（可选，推荐使用）

- 格式：`#领域-子领域-关键词`
- 示例：`#nucleus-cycle-aggregator`, `#ecommerce-douyin-content`, `#automotive-vehicle-design`
- 数量建议：每个文档 2-5 个 Tags，避免过度分类

### 2.2 Status 字段映射

| 文档类型 | YAML 值 | 对应系统状态 | Obsidian Graph 颜色建议 |
|----------|---------|--------------|--------------------------|
| **所有** | `draft` | 草案/待启动 | 🟡 黄色 |
| **所有** | `active` | 活跃/进行中 | 🟢 绿色 |
| **所有** | `blocked` | 阻塞/暂停 | 🔴 红色 |
| **所有** | `completed` | 完成/关闭 | 🟢 淡绿色 |
| **所有** | `archived` | 归档 | ⚪ 灰色 |

### 2.3 隐私分级（P0-P3）

完全对齐 ZT-2026-004 §1.2 隐私分级规范：

| 级别 | 说明 |
|------|------|
| **P0** | 绝密：仅限最高权限访问 |
| **P1** | 内部：仅限公司内部访问 |
| **P2** | 团队：仅限团队内部访问 |
| **P3** | 公开：可对外公开 |

---

## 三、Obsidian 知识图谱最佳实践

本规范与 N4-P2-T05 研究成果 `obsidian-graph-best-practices.md` 配套使用：

| 实践 | 说明 |
|------|------|
| **Wikilink 规范** | 参考 obsidian-graph-best-practices.md §四 |
| **Related Skills 章节** | 所有 Skill 末尾添加 Related Skills 章节 |
| **关联引用** | Task/Topic/Project 文档中使用 Wikilink 引用关联交付物 |
| **分层显示** | 按 type 字段配置 Graph 颜色（Project:蓝色, Topic:绿色, Task:白色, Skill:紫色） |
| **按状态过滤** | 可按 `status` 字段过滤显示活跃/阻塞/完成节点 |

---

## 四、自动注入与维护规范

依据 ZT-2026-004 "全生命周期管理"原则：

### 4.1 注入时机

| 时机 | 负责人 | 说明 |
|------|--------|------|
| **创建时** | 各 Agent | 新建文档时模板自动预填 Frontmatter |
| **更新时** | 各 Agent | 文档状态/负责人变更时同步更新 Frontmatter |
| **日常维护** | CDO | 依据 ZT-2026-004 数据治理理念，定期检查元数据完整性 |
| **历史迁移** | CDO | 批量注入脚本，分批次完成历史文档迁移 |

### 4.2 分批次迁移策略

| 批次 | 范围 | 优先级 | 预计数量 | 完成时间 |
|------|------|--------|----------|----------|
| **Batch 1** | 活跃核心项目（ZT-P009, ZT-P015, ZT-P001） | P0 | ~300 | 2026-04-21 |
| **Batch 2** | 进行中项目（ZT-P002, ZT-P004, ZT-P005） | P1 | ~400 | 2026-04-28 |
| **Batch 3** | 其他活跃项目 | P2 | ~300 | 2026-05-05 |
| **Batch 4** | 归档项目 | P3 | ~461 | 可选（按需执行） |

### 4.3 质量检查规则

参考 ZT-2026-004 §4 质量门：
1. 所有必填字段必须存在且非空
2. 字段值必须符合规范（如日期格式、ID 格式）
3. Tags 必须包含至少 1 个业务标签
4. 隐私分级必须准确

---

## 五、工具支持

### 5.1 批量注入脚本

CDO 将开发 `inject-frontmatter.py` 脚本，支持：
1. 自动提取文档已有字段填充 Frontmatter
2. 批量注入到指定目录下的所有文档
3. 自动校验字段值合法性
4. 生成注入报告

### 5.2 模板更新

所有交付物模板将预填充 Frontmatter 骨架：
- TMPL-PROJECT-CHARTER.md：更新版（含 Frontmatter）
- TMPL-TOPIC-BRIEF.md：更新版（含 Frontmatter）
- TMPL-TASK-CARD.md：更新版（含 Frontmatter）
- TMPL-SKILL.md：更新版（含 Frontmatter）

---

## 六、与其他规范的关系

| 规范 | 关系 | 说明 |
|------|------|------|
| **ZT-2026-004** | 上位规范 | 对齐数据治理原则、隐私分级、生命周期管理 |
| **ZT-2026-007** | 配套规范 | 与交付物路径规范协同使用 |
| **obsidian-graph-best-practices.md** | 配套规范 | Wikilink 与 Frontmatter 共同支撑知识图谱 |
| **N4-P2-T04 知识图谱构建 Topic** | 落地载体 | 本规范是 N4-P2-T04 的核心交付物之一 |
| **N4-P2-T05 Obsidian 兼容 Topic** | 前置研究 | 本规范基于 N4-P2-T05 的研究成果制定 |

---

## 七、术语定义

| 术语 | 定义 |
|------|------|
| **Frontmatter** | YAML 格式的文档元数据，置于文档顶部 |
| **Wikilink** | Obsidian 风格的双向链接语法 `[[文档名称]]` |
| **Vault** | Obsidian 工作目录，即 NUCLEUS 项目根目录 |
| **SSOT** | Single Source of Truth，单一真相源（来自 ZT-2026-004） |

---

## 八、附录

### 8.1 示例：完整 Project Frontmatter

```yaml
---
title: NUCLEUS 4.0 - 自动进化内核
tags: ["#governance", "#nucleus", "#pdca", "#automation"]
type: project
id: ZT-P015
status: active
owner: cqo
priority: P0
start_date: 2026-04-02
end_date: 2026-06-30
privacy: P2
related_projects: ["ZT-P009", "ZT-P000"]
related_topics: ["N4-P1-T01", "N4-P1-T02", "N4-P2-T04"]
aliases: ["NUCLEUS 4.0", "自动进化内核"]
description: 基于 OpenClaw Harness Engineering 的递归 PDCA 自动进化内核
---
```

### 8.2 示例：完整 Task Frontmatter

```yaml
---
title: Frontmatter 规范制定
tags: ["#data", "#governance", "#obsidian"]
type: task
id: N4-P2-T05-T5.3
status: completed
owner: cqo
topic: N4-P2-T05
project: ZT-P015
priority: P0
privacy: P2
review_level: L2
task_type: documentation
deliverables: ["ZT-2026-009_YAML-Frontmatter规范.md"]
created: 2026-04-14
updated: 2026-04-14
due: 2026-04-14
related_tasks: ["N4-P2-T05-T5.1", "N4-P2-T05-T5.2"]
---
```

---

## 九、版本变更记录

| 版本 | 日期 | 变更类型 | 变更内容 | 状态 |
|------|------|----------|----------|------|
| **v1.0** | 2026-04-14 | 初始版本 | 首次发布 Frontmatter 规范 | 草案 |

---

*本文件 v1.0 | 创建：2026-04-14 | 起草人：张铁 (CQO) | 状态：✅ 正式发布 | 审批人：Harold Tsui*
