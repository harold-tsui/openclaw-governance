---
name: managing-knowledge
description: |
  Managing lessons learned, decision library, knowledge sharing, and insight flywheel.
  
  Activates when: Task completed, lessons discovered, project closed, or knowledge search needed
  
  Capabilities:
  - Lessons learned creation and search (create_lesson_learned, search_lessons)
  - Decision library updates (update_dl for Harold's decisions)
  - Knowledge enhancement path (auto-retrieval at task creation)
  - Insight flywheel model (external + internal insights)
  - Feishu sync for knowledge assets
  
  Keywords: knowledge, lessons-learned, decision-library, insight, wiki, feishu-sync
  
  For detailed documentation, see:
  - references/knowledge-details.md

author: "辛如音 (cdo)"
license: "Internal Use Only"
version: "2.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L2"
  os: ["darwin", "linux"]
  owner: "cdo"
  tags: ["knowledge", "lessons-learned", "decision-library", "insight-flywheel", "feishu-sync"]
---

# Governance Knowledge - 知识管理 Skill

> **触发模式**：任务完成/发现经验教训/项目结项/新任务创建
> **v2.1.0**: 补充 When to Use / Pitfalls 章节

## 何时使用

- **Task completion**: 任务完成后沉淀经验教训
- **New task creation**: `enhance_knowledge()` 在启动前检索历史经验
- **Project closure**: `sync_to_feishu()` 归档所有知识资产
- **Harold decisions**: `update_dl()` 记录重要决策供未来参考
- **Knowledge search**: 查找过往教训避免重复犯错

## 常见陷阱

1. **Lesson type 很重要**: 必须分类为 `success` 或 `failure` — 通用的教训很难搜索和复用。
2. **DL 更新需要 Harold 的明确输入**: 不要仅从 Agent 的意见创建 DL 条目。只有 Harold 的决策才能进入决策库。
3. **Feishu 同步仅限 P2/P3**: P0 和 P1 数据（绝密/内部）按数据分级策略绝不能同步到飞书。
4. **知识增强是自动的**: 创建新任务时，必须调用 `enhance_knowledge()` 检索相关过往教训 — 不要跳过这一步。

---

## 引用规范

| 规范 | 版本 | 说明 |
|------|------|------|
| **ZT-2026-008** | v1.1 | 知识增强路径，洞察飞轮模型 |

---

## 一、核心功能

| 功能 | 说明 |
|------|------|
| **create_lesson_learned()** | 创建经验教训 |
| **search_lessons()** | 搜索经验教训 |
| **apply_lesson()** | 应用经验教训 |
| **update_dl()** | 更新决策库 |
| **enhance_knowledge()** | 新任务知识增强 |
| **sync_to_feishu()** | 同步到飞书文档 |

---

## 二、核心函数（摘要）

### create_lesson_learned()
- **输入**：`{project_id, task_id, type: success|failure, title, description, impact, suggestion}`
- **触发**：Pipeline Complete / 任务完成 / 发现重要经验
- **输出**：`{status, ll_id, file}`

### search_lessons()
- **输入**：`{query, limit}`
- **输出**：`{lessons: [{ll_id, title, type, project_id, relevance}]}`

### update_dl()
- **触发**：Harold 重要意见 / 项目重大决策 / 流程变更
- **输出**：`{status, dl_id, file: HAROLD-DECISION-LIBRARY.md}`

### sync_to_feishu()
- **输入**：`{project_id, items: ["lessons", "deliverables", "decisions"]}`
- **输出**：`{status, synced: {lessons, deliverables, decisions}, feishu_folder}`

> 详细函数参数、JSON 格式：[references/knowledge-details.md]({baseDir}/references/knowledge-details.md)

---

## 三、知识增强路径（摘要）

```
Task 执行 → 知识沉淀 → 知识索引 → 知识检索 → 知识复用 → 效率提升 → 新知识沉淀
```

### enhance_knowledge()
```
[Step 1] 提取关键词（从 Task 标题 + 目标）
[Step 2] 检索知识库（搜索 LL + DL + Wiki）
[Step 3] 返回增强建议（历史经验 + 决策偏好 + 模板）
```

### 自动检索触发点

| 触发点 | 检索内容 | 应用场景 |
|--------|---------|---------|
| 新 Task 创建 | 相似 Task 的 Wiki | 参考历史执行经验 |
| Harold 决策时 | 相关 DL 条目 | 快速找到决策偏好 |
| 问题阻塞时 | 相关问题解决记录 | 避免重复踩坑 |

> 详细增强流程、效率指标：[references/knowledge-details.md]({baseDir}/references/knowledge-details.md)

---

## 四、洞察飞轮（摘要）

| 洞察类型 | 说明 |
|---------|------|
| **机会洞察** | 外部变化带来的新机会 |
| **风险洞察** | 潜在威胁和风险 |
| **模式洞察** | 从重复经验中提取的规律 |
| **空白洞察** | 尚未被覆盖的领域 |

### DL/LL/Wiki 联动

| 洞察结果 | 联动动作 |
|---------|---------|
| 与现有 DL 相关 | 补充到 DL 的"延伸适用"字段 |
| 发现新决策模式 | 生成新 DL 草稿 |
| 发现假设错误 | 触发 LL 流程 |
| 需要采取行动 | 生成新 Task-CARD |

> 详细洞察模型、评估维度、联动规则：[references/knowledge-details.md]({baseDir}/references/knowledge-details.md)

---

## 五、对齐机制（摘要）

| 场景 | 内部文件 | 外部（飞书） |
|------|---------|-------------|
| 创建 LL | lessons/LL-*.md | — |
| 更新 DL | HAROLD-DECISION-LIBRARY.md | 飞书文档 |
| 项目结项 | — | 飞书知识库 |
| 重大教训 | — | 飞书文档 → Harold |

---

## 六、与 PMBOK 对应

| PMBOK 过程 | 本 Skill |
|------------|----------|
| 管理项目知识 | create_lesson_learned() |
| 结束项目或阶段 | sync_to_feishu() |
| 组织过程资产更新 | update_dl() |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **2.0.0** | 2026-04-22 | SKILL.md 瘦身至 <300 行，详细内容移至 references/knowledge-details.md |
| **v1.1.0** | 2026-03-24 | 新增知识增强路径、洞察飞轮模型、enhance_knowledge() |

---

*版本: 2.1.0 | 更新: 2026-04-23 | 变更: 补充 When to Use / Pitfalls 章节*

## Related Skills
- [[openclaw-governance-task]] - 任务管理，知识增强应用于任务执行
- [[openclaw-governance-delegation]] - 授权与等级判定，LESSON-LEARN 集成
- [[openclaw-governance-pipeline]] - 流水线编排，Complete 阶段触发知识沉淀
- [[openclaw-governance-hierarchy]] - 层级管理，项目结项知识归档
