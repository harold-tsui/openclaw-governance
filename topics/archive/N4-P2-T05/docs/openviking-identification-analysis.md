# OpenViking 识别机制分析

> **Topic**: N4-P2-T05
> **Task**: T5.1 - OpenViking 识别机制研究
> **PM**: 张铁 (CQO)
> **版本**: v1.0
> **创建时间**: 2026-04-12

---

## 一、研究目标

1. 分析 OpenViking 如何识别和解析交付物
2. 明确 OpenViking 需要的元数据字段
3. 制定 NUCLEUS 交付物与 OpenViking 的对接规范

---

## 二、研究方法

### 2.1 约束条件

由于网络限制（IP 解析失败），无法直接访问 OpenViking GitHub 仓库和文档。

### 2.2 替代方法

1. **基于现有 Skill 元数据分析**：分析已改造的 8 个 Skill 的元数据格式
2. **基于 YAML Frontmatter 最佳实践**：参考行业标准（Jekyll、Hugo、Obsidian）
3. **基于 OpenClaw 框架**：了解 OpenClaw 对交付物的识别方式
4. **假设验证**：提出假设，待 OpenViking 文档可访问时验证

---

## 三、现有 Skill 元数据分析

### 3.1 edge-tts 元数据示例

```yaml
---
name: edge-tts
slug: edge-tts
version: 1.0.4
homepage: https://clawic.com/skills/image
description: "Text-to-speech conversion using node-edge-tts npm package..."
changelog: "Expanded the skill with branding..."
metadata: {"clawdbot":{"emoji":"🖼️","os":["linux","darwin","win32"]}}
---
```

### 3.2 image 元数据示例

```yaml
---
name: Image
slug: image
version: 1.0.4
homepage: https://clawic.com/skills/image
description: "Create, inspect, process, and optimize image files..."
changelog: "Expanded the skill with branding..."
metadata: {"clawdbot":{"emoji":"🖼️","os":["linux","darwin","win32"]}}
---
```

### 3.3 共同字段分析

| 字段 | 类型 | 用途 | OpenViking 可能用途 |
|------|------|------|-------------------|
| `name` | string | Skill 名称 | 唯一标识 |
| `slug` | string | URL 友好的标识符 | 路径引用 |
| `version` | string | 版本号 | 版本管理 |
| `homepage` | URL | 官方主页 | 文档链接 |
| `description` | string | 功能描述 | 搜索索引 |
| `changelog` | string | 更新日志 | 变更追踪 |
| `metadata` | object | 扩展元数据 | 框架特定配置 |

---

## 四、OpenViking 识别机制假设

### 4.1 假设 1：基于 YAML Frontmatter 解析

**识别方式**：
- 解析文件头部的 `---` 包裹的 YAML 块
- 提取关键字段进行分类和索引

**需要的字段**：
```yaml
---
deliverable_type: skill | task | topic | project
id: NUCLEUS-SKILL-001  # 唯一标识符
title: "Skill 标题"
version: 1.0.0
status: active | archived
owner: 张铁 (CQO)
priority: P0 | P1 | P2 | P3
tags: #tts, #audio, #speech
created_at: 2026-04-01
updated_at: 2026-04-12
dependencies: []
---
```

### 4.2 假设 2：基于标签分类

**识别方式**：
- 通过 `Tags:` 行或 YAML `tags` 字段
- 按标签进行分类和过滤

**标签规范**：
- `#skill` - 技能文件
- `#task` - 任务卡片
- `#topic` - 话题简报
- `#project` - 项目章程
- `#deliverable` - 通用交付物标签

### 4.3 假设 3：基于文件路径约定

**识别方式**：
- 通过文件路径推断交付物类型
- 例如：`skills/` 目录下的是 Skill，`tasks/` 目录下的是 Task

**路径约定**：
```
~/.openclaw/skills/              # Skill 目录
main/10_Projects/{PROJECT}/tasks/    # Task 目录
main/10_Projects/{PROJECT}/topics/   # Topic 目录
main/10_Projects/{PROJECT}/          # Project 目录（PROJECT-CHARTER.md）
```

---

## 五、交付物元数据规范设计

### 5.1 通用元数据字段（所有交付物）

```yaml
---
# 基础信息
deliverable_type: skill | task | topic | project
id: NUCLEUS-{TYPE}-{SEQUENCE}  # 唯一标识符
title: "交付物标题"
version: X.Y.Z

# 状态管理
status: draft | active | completed | archived
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD

# 责任人
owner: Agent 名称 (角色)
pm: Project Manager（可选）
reviewer: Reviewer（可选）

# 优先级（Task/Topic 特有）
priority: P0 | P1 | P2 | P3 | null

# 分类与搜索
tags: #tag1, #tag2, #tag3
category: string（可选）

# 依赖关系
dependencies: [ID1, ID2, ...]（可选）
depends_on: string（可选）

# 扩展元数据
metadata: {}（可选）
---
```

### 5.2 Skill 特有字段

```yaml
---
deliverable_type: skill
id: NUCLEUS-SKILL-001
title: "Edge-TTS Skill"
version: 1.0.4

slug: edge-tts
homepage: https://clawic.com/skills/edge-tts
description: "Text-to-speech conversion..."
changelog: "Updated on 2026-04-11"

# OpenClaw 特定
metadata: {
  "clawdbot": {
    "emoji": "🎤",
    "os": ["linux", "darwin", "win32"]
  }
}

# NUCLEUS 特有（新增）
nucleus: {
  "phase": "Phase 2",
  "topic": "N4-P2-T04",
  "integration_status": "active"
}
---
```

### 5.3 Task 特有字段

```yaml
---
deliverable_type: task
id: N4-P2-T05-T5.1
title: "OpenViking 识别机制研究"
version: 1.0.0

status: in_progress
created_at: 2026-04-12
updated_at: 2026-04-12

owner: 张铁 (CQO)
pm: 张铁 (CQO)
priority: P0

tags: #research, #openviking, #metadata
category: research

# 依赖
topic_id: N4-P2-T05
project_id: ZT-P015
dependencies: []

# 验收标准
review_level: L3
deliverables: ["docs/openviking-identification-analysis.md"]
---
```

### 5.4 Topic 特有字段

```yaml
---
deliverable_type: topic
id: N4-P2-T05
title: "OpenViking 交付物识别与 Obsidian 知识图谱兼容"
version: 1.0.0

status: in_progress
created_at: 2026-04-12
updated_at: 2026-04-12

owner: 张铁 (CQO)
pm: 张铁 (CQO)
priority: P0

tags: #openviking, #obsidian, #metadata, #template
category: infrastructure

# 层级关系
project_id: ZT-P015
phase: Phase 2
tasks: [T5.1, T5.2, T5.3, T5.4, T5.5, T5.6]

# 验收标准
review_level: L3
---
```

### 5.5 Project 特有字段

```yaml
---
deliverable_type: project
id: ZT-P015
title: "NUCLEUS 4.0 - 自动进化内核"
version: 3.2

status: active
created_at: 2026-04-02
updated_at: 2026-04-12

owner: 张铁 (CQO) - PM
pm: 张铁 (CQO)
pmo: 银月

priority: P0

tags: #nucleus, #pdca, #automation, #governance
category: infrastructure

# 层级关系
parent_project: ZT-P009 (NUCLEUS 3.0)
phases: [Phase 0, Phase 1, Phase 2, Phase 3]
topics: [N4-P0-T01, N4-P1-T01, ..., N4-P2-T05]

# 验收标准
review_level: L4（Harold 必须介入）
---
```

---

## 六、OpenViking 集成建议

### 6.1 识别流程

```
OpenViking 扫描交付物
    ↓
解析 YAML Frontmatter
    ↓
提取 deliverable_type
    ↓
根据类型加载特定字段
    ↓
构建索引和知识图谱
```

### 6.2 推荐的 YAML 解析库

- **Python**: `PyYAML`、`ruamel.yaml`
- **Node.js**: `js-yaml`、`yaml`
- **Go**: `gopkg.in/yaml.v3`

### 6.3 OpenViking 推荐配置

```yaml
# openviking-config.yaml
scan_paths:
  - ~/.openclaw/skills/
  - ~/Workspaces/openclaw/main/10_Projects/

file_patterns:
  skill: "**/SKILL.md"
  task: "**/TASK-CARD-*.md"
  topic: "**/TOPIC-BRIEF.md"
  project: "**/PROJECT-CHARTER.md"

metadata_required:
  - deliverable_type
  - id
  - title
  - status
  - owner

metadata_optional:
  - tags
  - dependencies
  - priority
  - version
```

---

## 七、待验证项

| 假设 | 验证方法 | 状态 |
|------|----------|------|
| OpenViking 支持 YAML Frontmatter | 待访问文档 | ⏸️ 待验证 |
| OpenViking 需要特定字段 | 待访问文档 | ⏸️ 待验证 |
| OpenViking 支持标签分类 | 待访问文档 | ⏸️ 待验证 |
| OpenViking 支持文件路径约定 | 待访问文档 | ⏸️ 待验证 |

---

## 八、下一步行动

1. **待网络恢复**：访问 OpenViking 文档，验证假设
2. **立即行动**：基于本分析设计完整的元数据规范
3. **模板升级**：升级 TASK-CARD、PROJECT-CHARTER、TOPIC-BRIEF 模板
4. **测试验证**：使用工具验证 YAML 解析正确性

---

*v1.0 | 创建：2026-04-12 | PM：张铁 | 状态：✅ 完成（待验证）*