# Knowledge Management — Detailed Reference

> Moved from knowledge SKILL.md to reduce main file size.

## §二 核心函数详情

### create_lesson_learned()
- **Input**: `{project_id, task_id, type: success|failure, title, description, impact, suggestion}`
- **Trigger**: Pipeline Complete 阶段 / 任务完成后 / 发现重要经验教训
- **Output**: `{status, ll_id, file, template_used}`

### search_lessons()
- **Input**: `{query, limit}`
- **Output**: `{lessons: [{ll_id, title, type, project_id, relevance}]}`

### apply_lesson()
- **Input**: `{ll_id, project_id, application}`
- **Output**: `{status, ll_id, applied_to, applied_at}`

### update_dl()
- **Trigger**: Harold 给出重要意见 / 项目重大决策 / 流程变更
- **Input**: `{decision, context, made_by, date}`
- **Output**: `{status, dl_id, file: HAROLD-DECISION-LIBRARY.md}`

### sync_to_feishu()
- **Input**: `{project_id, items: ["lessons", "deliverables", "decisions"]}`
- **Output**: `{status, synced: {lessons, deliverables, decisions}, feishu_folder}`

## §三 知识增强路径

### 完整流程
```
Task 执行 → 知识沉淀 → 知识索引 → 知识检索 → 知识复用 → 效率提升 → 新知识沉淀
```

### 自动检索触发点

| 触发点 | 检索内容 | 应用场景 |
|--------|---------|---------|
| 新 Task 创建 | 相似 Task 的 Wiki | 参考历史执行经验 |
| Harold 决策时 | 相关 DL 条目 | 快速找到决策偏好 |
| 问题阻塞时 | 相关问题解决记录 | 避免重复踩坑 |

### enhance_knowledge() 流程
```
[Step 1] 提取关键词（从 Task 标题 + 目标）
[Step 2] 检索知识库（搜索 LL + DL + Wiki）
[Step 3] 返回增强建议（历史经验 + 决策偏好 + 模板）
```

**Output**: `{status, enhancements: {lessons[], decisions[], templates[]}}`

### 效率提升指标

| 指标 | 目标 | 测量方式 |
|------|------|---------|
| 重复问题减少率 | > 50% | 统计相同问题出现次数 |
| 决策时间缩短 | > 30% | 对比有/无 DL 的决策时长 |
| Task 执行加速 | > 20% | 对比有/无 Wiki 参考的执行时间 |

## §四 洞察飞轮模型

### 洞察模型结构

| 维度 | 内容 |
|------|------|
| **输入源** | 外部情报（CIO）、内部产出（DL/LL/Wiki）、环境变化、思维碎片 |
| **洞察类型** | 机会洞察、风险洞察、模式洞察、空白洞察 |
| **洞察评估** | 时效性（当前/短期/长期）、置信度（高/中/低）、行动建议 |
| **输出** | 关联 DL、生成 LL、更新 Wiki、触发新 Task |

### DL/LL/Wiki 联动规则

| 洞察结果 | 联动动作 |
|---------|---------|
| 与现有 DL 相关 | 补充到 DL 的"延伸适用"字段 |
| 发现新决策模式 | 生成新 DL 草稿 |
| 发现假设错误 | 触发 LL 流程 |
| 文档价值变化 | 更新 Wiki 的 tags |
| 需要采取行动 | 生成新 Task-CARD |

## §五 对齐机制

| 场景 | 触发 | 内部文件 | 外部（飞书） |
|------|------|---------|-------------|
| 创建 LL | 任务完成 | lessons/LL-*.md | — |
| 更新 DL | 重要决策 | HAROLD-DECISION-LIBRARY.md | 飞书文档 |
| Heartbeat 巡检 | 每日 | 检查 LL 填写状态 | — |
| 项目结项 | Pipeline Complete | — | 飞书知识库 |
| 重大教训 | 发现重大教训 | — | 飞书文档 → Harold |

## §六 与 PMBOK 对应

| PMBOK 过程 | 本 Skill |
|------------|----------|
| 管理项目知识 | create_lesson_learned() |
| 结束项目或阶段 | sync_to_feishu() |
| 组织过程资产更新 | update_dl() |
