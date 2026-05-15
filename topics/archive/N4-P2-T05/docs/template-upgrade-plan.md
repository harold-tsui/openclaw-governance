# 模板升级实施方案

> **Topic**: N4-P2-T05
> **Task**: T5.4 - 模板升级实施方案
> **PM**: 张铁 (CQO)
> **版本**: v1.0
> **创建时间**: 2026-04-12
> **状态**: 🔄 进行中

---

## 一、升级目标

1. 升级 TASK-CARD 模板（v3.0 → v4.0）
2. 升级 PROJECT-CHARTER 模板（v3.2 → v4.0）
3. 升级 TOPIC-BRIEF 模板（v3.1 → v4.0）
4. 批量迁移现有交付物

---

## 二、升级原则

### 2.1 向后兼容

- 保留现有字段，不删除
- 新增字段使用默认值
- 渐进式升级，不破坏现有功能

### 2.2 最小侵入

- 优先在文件头部/末尾添加内容
- 避免修改核心章节
- 保持原有结构

### 2.3 一致性

- 所有模板使用相同的元数据格式
- 所有模板添加相同的 "相关知识" 章节
- 所有模板使用相同的标签格式

---

## 三、TASK-CARD 模板升级（v3.0 → v4.0）

### 3.1 升级内容

#### 升级 1：头部添加 YAML Frontmatter

**位置**：文件头部（第一个 `---` 之前）

**内容**：
```yaml
---
deliverable_type: task
id: {Task ID}
title: "{Task 标题}"
version: 4.0.0
status: draft
created_at: {CREATED_AT}
updated_at: {LAST_UPDATED}
owner: {Task PIC}

priority: {优先级}
topic_id: {Topic ID}
project_id: {PROJECT_ID}
review_level: {Review 级别}
---
```

#### 升级 2：正文中添加 Tags 行

**位置**："## 声明" 章节后

**内容**：
```markdown
Tags: #task, {功能标签}
```

#### 升级 3：末尾添加 "相关知识" 章节

**位置**：文件末尾（版本信息之前）

**内容**：
```markdown
## 八、相关知识

### 相关技能
- [[skill-name]] - 描述

### 相关任务
- [[Task-ID]] - 描述

### 相关话题
- [[Topic-ID]] - 描述

### 相关项目
- [[Project-ID]] - 描述

### 外部参考
- [文档标题](URL)
```

### 3.2 升级步骤

| 步骤 | 行动 | 负责人 | 状态 |
|------|------|--------|------|
| **Step 1** | 备份现有模板 | 张铁 | 📋 待开始 |
| **Step 2** | 添加 YAML Frontmatter | 张铁 | 📋 待开始 |
| **Step 3** | 添加 Tags 行 | 张铁 | 📋 待开始 |
| **Step 4** | 添加 "相关知识" 章节 | 张铁 | 📋 待开始 |
| **Step 5** | 测试验证 | 张铁 | 📋 待开始 |
| **Step 6** | 部署新模板 | 张铁 | 📋 待开始 |

---

## 四、PROJECT-CHARTER 模板升级（v3.2 → v4.0）

### 4.1 升级内容

#### 升级 1：头部添加 YAML Frontmatter

**位置**：文件头部

**内容**：
```yaml
---
deliverable_type: project
id: {Project ID}
title: "{Project 名称}"
version: {版本号}
status: active
created_at: {创建时间}
updated_at: {最后更新时间}
owner: {PM}

pm: {PM}
pmo: {PMO}
review_level: {Review 级别}
priority: {优先级}
---
```

#### 升级 2：正文中添加 Tags 行

**位置**：文件标题后

**内容**：
```markdown
Tags: #project, {功能标签}
```

#### 升级 3：末尾添加 "相关项目" 章节

**位置**：文件末尾（审批记录之前）

**内容**：
```markdown
## 十、相关项目

### 父项目
- [[Project-ID]] - {Project 名称}

### 子项目
- （无）

### 依赖项目
- [[Project-ID]] - {Project 名称}
```

### 4.2 升级步骤

| 步骤 | 行动 | 负责人 | 状态 |
|------|------|--------|------|
| **Step 1** | 备份现有模板 | 张铁 | 📋 待开始 |
| **Step 2** | 添加 YAML Frontmatter | 张铁 | 📋 待开始 |
| **Step 3** | 添加 Tags 行 | 张铁 | 📋 待开始 |
| **Step 4** | 添加 "相关项目" 章节 | 张铁 | 📋 待开始 |
| **Step 5** | 测试验证 | 张铁 | 📋 待开始 |
| **Step 6** | 部署新模板 | 张铁 | 📋 待开始 |

---

## 五、TOPIC-BRIEF 模板升级（v3.1 → v4.0）

### 5.1 升级内容

#### 升级 1：头部添加 YAML Frontmatter

**位置**：文件头部

**内容**：
```yaml
---
deliverable_type: topic
id: {Topic ID}
title: "{Topic 名称}"
version: 1.0.0
status: draft
created_at: {创建时间}
updated_at: {最后更新时间}
owner: {PM}

pm: {PM}
review_level: {Review 级别}
project_id: {Project ID}
phase: {Phase}
---
```

#### 升级 2：正文中添加 Tags 行

**位置**：文件标题后

**内容**：
```markdown
Tags: #topic, {功能标签}
```

#### 升级 3：末尾添加 "相关知识" 章节

**位置**：文件末尾（版本信息之前）

**内容**：
```markdown
## 七、相关知识

### 相关技能
- [[skill-name]] - 描述

### 相关任务
- [[Task-ID]] - 描述

### 相关话题
- [[Topic-ID]] - 描述

### 相关项目
- [[Project-ID]] - 描述
```

### 5.2 升级步骤

| 步骤 | 行动 | 负责人 | 状态 |
|------|------|--------|------|
| **Step 1** | 备份现有模板 | 张铁 | 📋 待开始 |
| **Step 2** | 添加 YAML Frontmatter | 张铁 | 📋 待开始 |
| **Step 3** | 添加 Tags 行 | 张铁 | 📋 待开始 |
| **Step 4** | 添加 "相关知识" 章节 | 张铁 | 📋 待开始 |
| **Step 5** | 测试验证 | 张铁 | 📋 待开始 |
| **Step 6** | 部署新模板 | 张铁 | 📋 待开始 |

---

## 六、批量迁移现有交付物

### 6.1 迁移范围

| 交付物类型 | 数量 | 优先级 |
|-----------|------|--------|
| **TASK-CARD** | 约 50 个 | P0 |
| **PROJECT-CHARTER** | 约 5 个 | P1 |
| **TOPIC-BRIEF** | 约 20 个 | P1 |
| **Skill** | 8 个 | ✅ 已完成 |

### 6.2 迁移策略

#### 策略 1：渐进式迁移

**原则**：
- 先升级模板
- 新交付物使用新模板
- 旧交付物按需升级

**优先级**：
1. ✅ Skill（已完成）
2. 📋 TASK-CARD（本次升级）
3. 📋 PROJECT-CHARTER（本次升级）
4. 📋 TOPIC-BRIEF（本次升级）

#### 策略 2：脚本自动化

**工具**：Python 脚本批量添加元数据

```python
#!/usr/bin/env python3
import os
import re
from pathlib import Path

def add_yaml_frontmatter(file_path, deliverable_type, metadata):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已有 YAML Frontmatter
    if content.startswith('---'):
        print(f"跳过 {file_path}：已有 YAML Frontmatter")
        return

    # 生成 YAML Frontmatter
    yaml_content = "---\n"
    yaml_content += f"deliverable_type: {deliverable_type}\n"
    for key, value in metadata.items():
        yaml_content += f"{key}: {value}\n"
    yaml_content += "---\n\n"

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content + content)

    print(f"✅ 完成 {file_path}")

if __name__ == '__main__':
    # TASK-CARD 批量升级
    tasks_dir = Path('main/10_Projects')
    for task_card in tasks_dir.rglob('TASK-CARD-*.md'):
        # 提取元数据
        task_id = task_card.stem.replace('TASK-CARD-', '')
        add_yaml_frontmatter(task_card, 'task', {
            'id': task_id,
            'title': task_id,
            'version': '4.0.0',
            'status': 'draft',
            'created_at': '2026-04-12',
            'updated_at': '2026-04-12',
            'owner': '待填写'
        })
```

### 6.3 迁移步骤

| 步骤 | 行动 | 负责人 | 状态 |
|------|------|--------|------|
| **Step 1** | 升级模板文件 | 张铁 | 📋 待开始 |
| **Step 2** | 编写迁移脚本 | 张铁 | 📋 待开始 |
| **Step 3** | 测试脚本 | 张铁 | 📋 待开始 |
| **Step 4** | 备份现有文件 | 张铁 | 📋 待开始 |
| **Step 5** | 执行迁移脚本 | 张铁 | 📋 待开始 |
| **Step 6** | 验证迁移结果 | 张铁 | 📋 待开始 |
| **Step 7** | 提交到 Git | 张铁 | 📋 待开始 |

---

## 七、测试验证

### 7.1 功能测试

| 测试项 | 测试方法 | 状态 |
|--------|----------|------|
| YAML Frontmatter 解析 | 使用 Python/Node.js 解析 | 📋 待测试 |
| Wikilink 正常工作 | 在 Obsidian 中测试 | 📋 待测试 |
| 标签显示正确 | 在 Obsidian 中测试 | 📋 待测试 |
| 向后兼容性 | 使用旧数据测试 | 📋 待测试 |

### 7.2 OpenViking 集成测试

| 测试项 | 测试方法 | 状态 |
|--------|----------|------|
| OpenViking 识别交付物 | 待网络恢复后测试 | ⏸️ 待测试 |
| 元数据字段完整性 | 待网络恢复后测试 | ⏸️ 待测试 |
| 知识图谱构建 | 待网络恢复后测试 | ⏸️ 待测试 |

---

## 八、风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 模板升级破坏现有功能 | 高 | 中 | 备份 + 渐进式升级 |
| 批量迁移脚本出错 | 高 | 中 | 测试脚本 + 备份 |
| OpenViking 识别机制不匹配 | 中 | 低 | 待网络恢复后验证 |
| Harold 不接受方案 | 高 | 低 | 先提交草案审批 |

---

## 九、时间估算

| 任务 | 估算时间 | 负责人 |
|------|---------|--------|
| TASK-CARD 模板升级 | 2 小时 | 张铁 |
| PROJECT-CHARTER 模板升级 | 1 小时 | 张铁 |
| TOPIC-BRIEF 模板升级 | 1 小时 | 张铁 |
| 迁移脚本编写 | 2 小时 | 张铁 |
| 批量迁移 | 1 小时 | 张铁 |
| 测试验证 | 2 小时 | 张铁 |
| **总计** | **9 小时** | - |

---

## 十、下一步行动

### 立即行动

- [ ] T5.5: 升级 TASK-CARD 模板
- [ ] T5.6: 升级其他模板

### 待 Harold 审批

- [ ] 交付物元数据规范审批
- [ ] 模板升级方案审批

### 待网络恢复

- [ ] 验证 OpenViking 识别机制
- [ ] 验证 Obsidian 知识图谱

---

*v1.0 | 创建：2026-04-12 | PM：张铁 | 状态：🔄 进行中*