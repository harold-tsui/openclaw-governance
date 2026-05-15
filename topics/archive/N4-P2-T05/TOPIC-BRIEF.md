# TOPIC-BRIEF · N4-P2-T05

> **文件性质**：执行记录文件（非定义文档）
> **唯一真相源**：`active/NUCLEUS-4.0-ARCH-v1.4.3.md`
> **版本**：v1.0
> **Topic ID**：N4-P2-T05
> **Topic 名称**：OpenViking 交付物识别与 Obsidian 知识图谱兼容
> **PM**：张铁 (CQO)
> **Review 级别**：L3（Harold 必须介入）
> **状态**：✅ 草案完成（待 Harold 审批）

---

## 一、Topic 执行概要

| 字段 | 内容 |
|------|------|
| **Topic ID** | N4-P2-T05 |
| **Topic 名称** | OpenViking 交付物识别与 Obsidian 知识图谱兼容 |
| **PM** | 张铁 (CQO) |
| **Phase** | Phase 2（Week 8-14） |
| **状态** | 🔄 进行中 |

---

## 二、背景说明

### 2.1 需求来源

Harold 提出需求（2026-04-12）：

1. **OpenViking 识别需求**：让 OpenViking（https://github.com/volcengine/OpenViking）能更好地识别 Skill 和 NUCLEUS 生产的交付物
2. **Obsidian 知识图谱兼容**：兼容 Obsidian 的知识图谱，便于技能关联发现、上下文推荐和检索

### 2.2 当前状态

**已完成（2026-04-11）**：
- 8 个 Skill 的 SKILL.md 文件已完成改造：
  - 系统路径：edge-tts、video-generator-seedance、remotion-video-toolkit、image、test-nucleus-integration、youtube-transcript
  - 本地 workspace：sider-automation、openclaw-governance

**改造内容**：
1. 文件头部添加功能标签（Tags: #tag1, #tag2）
2. 文件末尾添加 `[[skill-name]]` 格式的相关技能内部链接
3. 兼容 Obsidian 知识图谱

### 2.3 待升级的交付物类型

| 交付物类型 | 当前状态 | 优先级 |
|-----------|---------|--------|
| **SKILL.md** | ✅ 已完成（8 个） | P0 |
| **TASK-CARD** | ❌ 未升级 | P0 |
| **PROJECT-CHARTER** | ❌ 未升级 | P1 |
| **TOPIC-BRIEF** | ❌ 未升级 | P1 |
| **其他模板文件** | ❌ 未升级 | P2 |

---

## 三、研究目标

### 3.1 OpenViking 识别需求分析

**待确认**：
1. OpenViking 如何识别交付物？
   - YAML frontmatter 解析？
   - 特定标签/元数据？
   - 文件路径约定？

2. OpenViking 需要哪些元数据字段？
   - 交付物类型标识（Skill / Task / Topic / Project）
   - 优先级、状态、负责人？
   - 依赖关系？

3. OpenViking 与 NUCLEUS 交付物的交互方式？

### 3.2 Obsidian 知识图谱兼容

**已验证（2026-04-11）**：
- `[[wikilink]]` 格式可用于技能关联
- 需要在文档末尾添加 "Related Skills" 或类似章节

**待研究**：
1. 任务之间的关联（Task → Task 依赖）
2. Topic → Topic 的关联
3. Project → Skill 的引用
4. 交付物路径的规范化命名（便于 `[[wikilink]]` 引用）

---

## 四、Task 执行记录

| Task ID | Task 名称 | 执行日期 | 状态 | 交付物 |
|---------|-----------|----------|------|--------|
| **T5.1** | OpenViking 识别机制研究 | 2026-04-12 | ✅ 完成 | `docs/openviking-identification-analysis.md` |
| **T5.2** | Obsidian 知识图谱最佳实践 | 2026-04-12 | ✅ 完成 | `docs/obsidian-graph-best-practices.md` |
| **T5.3** | 交付物元数据规范设计 | 2026-04-14 | ✅ 完成 | `ZT-2026-009_YAML-Frontmatter规范.md` (已正式发布) |
| **T5.4** | 模板升级实施方案 | 2026-04-12 | ✅ 完成 | `docs/template-upgrade-plan.md` |
| **T5.5** | TASK-CARD 模板升级 | 2026-04-12 | 📋 待开始 | `TASK-CARD-v4.0.md` |
| **T5.6** | 其他模板升级 | 2026-04-12 | 📋 待开始 | 模板文件更新 |

---

## 五、执行记录

| 日期 | 事件 | 说明 |
|------|------|------|
| 2026-04-12 | Topic 创建 | Harold 提出 OpenViking 识别 + Obsidian 知识图谱兼容需求 |
| 2026-04-12 | 现状分析 | 确认 8 个 Skill 已完成改造，其他交付物待升级 |
| 2026-04-12 | T5.1 完成 | OpenViking 识别机制研究完成（基于现有 Skill 元数据分析） |
| 2026-04-12 | T5.2 完成 | Obsidian 知识图谱最佳实践研究完成 |
| 2026-04-12 | T5.3 完成 | 交付物元数据规范设计完成 |
| 2026-04-12 | T5.4 完成 | 模板升级实施方案制定完成 |
| 2026-04-12 | T5.7 撤回 | Governance 文件 skills 化已完成，无需迁移 |
| 2026-04-14 | T5.3 正式发布 | 交付物元数据规范（Frontmatter）通过 Harold 审批，正式发布为 ZT-2026-009 标准，纳入数据治理体系 |

---

## 六、关键问题与假设

### 6.1 OpenViking 识别机制（待验证）

**假设 1**：OpenViking 通过 YAML frontmatter 解析交付物元数据
- 需要字段：`deliverable_type`、`id`、`title`、`status`、`owner`
- 参考格式：
  ```yaml
  ---
  name: edge-tts
  deliverable_type: skill
  id: NUCLEUS-SKILL-001
  version: 1.0.0
  ---
  ```

**假设 2**：OpenViking 支持自定义标签识别
- Tags: #skill, #task, #topic, #project
- 便于按类型过滤和分类

### 6.2 Obsidian 知识图谱最佳实践（待验证）

**已验证**：
- `[[skill-name]]` 可用于技能关联

**待验证**：
1. 跨目录引用是否需要完整路径？
   - 例如：`[[../../skills/edge-tts]]` 还是 `[[edge-tts]]`？
2. 交付物路径是否需要统一到根目录？
   - 便于 `[[wikilink]]` 引用

---

## 七、下一步行动

### 短期（本周）

- [x] T5.1: 研究 OpenViking 识别机制 ✅
- [x] T5.2: 研究 Obsidian 知识图谱最佳实践 ✅
- [x] T5.3: 设计交付物元数据规范（对齐 ZT-2026-004）✅
- [x] T5.4: 制定模板升级实施方案 ✅
- [ ] T5.5: 升级 TASK-CARD 模板（等待 Harold 审批）
- [ ] T5.6: 升级其他模板（等待 Harold 审批）

### 中期（下周）

- [ ] 批量迁移现有交付物
- [ ] 测试验证 OpenViking 识别效果
- [ ] 测试验证 Obsidian 知识图谱构建效果

### 长期（Phase 2 结束前）

- [ ] 验证 OpenViking 识别效果
- [ ] 验证 Obsidian 知识图谱构建效果
- [ ] 总结经验，固化规范

---

*v1.4 | 更新：2026-04-12 | PM：张铁 | 状态：✅ 草案完成（待 Harold 审批） | 进度：4/6 Task 完成 | 对齐：ZT-2026-004 数据治理体系规范*