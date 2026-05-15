# Obsidian 知识图谱最佳实践

> **Topic**: N4-P2-T05
> **Task**: T5.2 - Obsidian 知识图谱最佳实践研究
> **PM**: 张铁 (CQO)
> **版本**: v1.0
> **创建时间**: 2026-04-12

---

## 一、研究目标

1. 研究 Obsidian 知识图谱的工作原理
2. 确定最佳实践，便于技能关联发现、上下文推荐和检索
3. 制定 NUCLEUS 交付物的 Obsidian 集成规范

---

## 二、Obsidian 知识图谱核心概念

### 2.1 Wikilink 语法

**基本语法**：`[[链接文本]]`

**示例**：
- `[[edge-tts]]` - 链接到名为 "edge-tts" 的笔记
- `[[edge-tts|TTS 工具]]` - 链接到 "edge-tts" 笔记，显示 "TTS 工具"
- `[[SKILL.md]]` - 链接到 "SKILL.md" 文件

### 2.2 链接类型

| 类型 | 语法 | 用途 |
|------|------|------|
| **内部链接** | `[[笔记名称]]` | 链接到同一 Vault 中的笔记 |
| **外部链接** | `[文本](URL)` | 链接到外部 URL |
| **嵌入链接** | `![[笔记名称]]` | 嵌入笔记内容（transclusion） |
| **块链接** | `[[笔记名称#^块ID]]` | 链接到特定块 |

### 2.3 嵌套与层级

Obsidian 支持嵌套链接，可以构建复杂的知识网络：

```markdown
- [[remotion-video-toolkit]] 使用 [[edge-tts]] 生成的音频
- [[video-generator-seedance]] 可使用 [[image]] 处理后的图片
```

---

## 三、已验证的实践

### 3.1 Skill 末尾的 "Related Skills" 章节

**已改造的 8 个 Skill**：

```markdown
## Related Skills
- [[remotion-video-toolkit]] - 视频生成工具包，支持TTS音频集成
- [[youtube-transcript]] - YouTube视频转录，可与TTS结合使用
```

**效果**：
- ✅ 兼容 Obsidian 知识图谱
- ✅ 便于技能关联发现
- ✅ 便于上下文推荐

### 3.2 标签系统（Tags）

**格式**：`#tag1 #tag2 #tag3`

**示例**：
```markdown
Tags: #tts, #audio, #speech, #microsoft-edge
```

**效果**：
- ✅ 在知识图谱中以节点显示
- ✅ 可按标签过滤和搜索
- ✅ 便于技能分类

---

## 四、NUCLEUS 交付物的 Obsidian 集成规范

### 4.1 通用规范

#### 4.1.1 Wikilink 命名规范

**原则**：使用唯一、简洁、易读的名称

| 交付物类型 | 命名格式 | 示例 |
|-----------|---------|------|
| **Skill** | `{slug}` 或 `{skill-name}` | `edge-tts`, `image` |
| **Task** | `{Task ID}` 或 `{Task 标题简写}` | `N4-P2-T05-T5.1`, `OpenViking研究` |
| **Topic** | `{Topic ID}` | `N4-P2-T05` |
| **Project** | `{Project ID}` | `ZT-P015` |

#### 4.1.2 跨目录引用

**规则**：Obsidian 默认支持跨目录引用，无需完整路径

```markdown
# 在 Task-CARD 中引用 Skill
## 依赖的 Skills
- [[edge-tts]] - 用于音频生成
- [[image]] - 用于图像处理

# 在 Topic 中引用 Task
## Task 列表
- [[N4-P2-T05-T5.1]] - OpenViking 识别机制研究
- [[N4-P2-T05-T5.2]] - Obsidian 知识图谱最佳实践
```

**注意事项**：
- 如果有重名，Obsidian 会提示选择
- 建议使用唯一的 ID（如 `N4-P2-T05-T5.1`）避免重名

### 4.2 各类型交付物的 Wikilink 规范

#### 4.2.1 SKILL.md

**末尾添加**：

```markdown
## Related Skills

### 相关技能
- [[skill-name-1]] - 技能描述
- [[skill-name-2]] - 技能描述

### 相关任务
- [[Task-ID]] - 任务描述

### 相关话题
- [[Topic-ID]] - 话题描述
```

**示例**：

```markdown
## Related Skills

### 相关技能
- [[remotion-video-toolkit]] - 视频生成工具包，支持TTS音频集成

### 相关任务
- [[N4-P2-T05-T5.1]] - OpenViking 识别机制研究
```

#### 4.2.2 TASK-CARD.md

**§三 "输入物" 章节**：使用 Wikilink 引用依赖的交付物

```markdown
## 三、输入物（Inputs）

| 输入物 | 类型 | 来源 | 状态 |
|---|---|---|---|
| [[OpenViking 识别机制分析]] | 前置研究 | T5.1 输出 | ✅ 已就绪 |
| [[edge-tts]] | 技能参考 | ~\.openclaw/skills/edge-tts/ | ✅ 已就绪 |
```

**§八 "相关知识" 章节**（新增）：

```markdown
## 八、相关知识

### 相关技能
- [[skill-name-1]] - 描述
- [[skill-name-2]] - 描述

### 相关任务
- [[Task-ID-1]] - 描述
- [[Task-ID-2]] - 描述

### 相关话题
- [[Topic-ID-1]] - 描述

### 相关项目
- [[Project-ID-1]] - 描述

### 外部参考
- [OpenViking GitHub](https://github.com/volcengine/OpenViking)
- [Obsidian 帮助](https://help.obsidian.md/)
```

#### 4.2.3 TOPIC-BRIEF.md

**§三 "Task 执行记录" 章节**：使用 Wikilink 引用 Task

```markdown
## 三、Task 执行记录

| Task ID | Task 名称 | 执行日期 | 状态 | 交付物 |
|---------|-----------|----------|------|--------|
| [[N4-P2-T05-T5.1]] | OpenViking 识别机制研究 | 2026-04-12 | ✅ 完成 | [[OpenViking 识别机制分析]] |
| [[N4-P2-T05-T5.2]] | Obsidian 知识图谱最佳实践 | 2026-04-12 | 🔄 进行中 | [[Obsidian 知识图谱最佳实践]] |
```

**§七 "相关知识" 章节**（新增）：

```markdown
## 七、相关知识

### 相关技能
- [[skill-name-1]] - 描述

### 相关任务
- [[Task-ID-1]] - 描述
- [[Task-ID-2]] - 描述

### 相关话题
- [[Topic-ID-1]] - 描述

### 相关项目
- [[ZT-P015]] - NUCLEUS 4.0 项目
```

#### 4.2.4 PROJECT-CHARTER.md

**§九 "相关项目" 章节**（新增）：

```markdown
## 十、相关项目

### 父项目
- [[ZT-P009]] - NUCLEUS 3.0

### 子项目
- （无）

### 依赖项目
- [[Project-ID-1]] - 描述
```

---

## 五、知识图谱最佳实践

### 5.1 命名一致性

**规则**：
- 同一交付物在不同文件中使用相同的 Wikilink 名称
- 使用 ID 作为唯一标识符（Task ID、Topic ID、Project ID）

**示例**：
- Task `N4-P2-T05-T5.1` 在所有地方都使用 `[[N4-P2-T05-T5.1]]`
- 不要混用 `[[OpenViking 识别机制研究]]` 和 `[[N4-P2-T05-T5.1]]`

### 5.2 描述性文本

**规则**：在 Wikilink 后添加描述，便于理解

**示例**：
```markdown
- [[edge-tts]] - 文本到语音转换工具
- [[N4-P2-T05-T5.1]] - OpenViking 识别机制研究
```

### 5.3 分组展示

**规则**：按类型分组展示 Wikilink

**示例**：
```markdown
## Related Skills

### 相关技能
- [[skill-name-1]] - 描述
- [[skill-name-2]] - 描述

### 相关任务
- [[Task-ID-1]] - 描述

### 相关话题
- [[Topic-ID-1]] - 描述
```

### 5.4 避免循环引用

**规则**：避免不必要的循环引用

**示例**：
```markdown
# Task A 引用 Task B
- [[N4-P2-T05-T5.1]] - 研究 OpenViking 识别机制

# Task B 引用 Task A（避免重复）
- （不需要再次引用 Task A）
```

---

## 六、Obsidian Vault 配置建议

### 6.1 Vault 结构

```
~/
├── .obsidian/              # Obsidian 配置
├── Workspaces/
│   └── openclaw/
│       ├── main/
│       │   ├── 10_Projects/     # Project、Topic、Task
│       │   └── 60_Agents/       # Agent 配置
│       └── .openclaw/
│           └── skills/          # Skills
```

### 6.2 忽略文件

在 `.obsidian/ignore` 中配置：

```
**/.pytest_cache/**
**/__pycache__/**
**/node_modules/**
**/.git/**
**/logs/**
**/*.jsonl
```

### 6.3 插件推荐

| 插件 | 用途 |
|------|------|
| **Graph Analysis** | 图谱分析，查找孤立节点 |
| **Dataview** | 数据查询和索引 |
| **Breadcrumbs** | 层级导航（Project → Topic → Task） |
| **Excalidraw** | 绘图工具 |

---

## 七、待验证项

| 实践 | 验证方法 | 状态 |
|------|----------|------|
| 跨目录 Wikilink 正常工作 | 在 Obsidian 中测试 | ⏸️ 待验证 |
| ID 作为唯一标识符不冲突 | 测试多个 Project | ⏸️ 待验证 |
| 分组展示便于理解 | 用户反馈 | ⏸️ 待验证 |

---

## 八、下一步行动

1. **立即行动**：应用本规范到现有交付物
2. **测试验证**：在 Obsidian 中导入并测试
3. **用户反馈**：收集 Harold 的反馈

---

*v1.0 | 创建：2026-04-12 | PM：张铁 | 状态：✅ 完成（待验证）*