# Triple-Memory 整合方案 v2.0

> **创建时间**：2026-04-13 10:25
> **修订时间**：2026-04-13 10:28
> **决策来源**：Harold 明确两层架构理念 + OpenViking 已配置
> **状态**：草案，待审批
> **关键修正**：
> 1. 时间：一上午完成环境搭建（不是3周）
> 2. OpenViking 兼容性：已配置火山引擎 embedding
> 3. Embedding API：火山方舟 + 硅基流动（无 OpenAI）

---

## 一、OpenViking 现状分析

### 1.1 OpenViking 已配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **Embedding Backend** | `volcengine` | 火山引擎 |
| **API Key** | `b422bc72-7348-48f8-970d-987ed467ee04` | 火山方舟 |
| **Model** | `doubao-embedding-vision` | 多模态 embedding |
| **API Base** | `https://ark.cn-beijing.volces.com/api/coding/v3` | 火山方舟 API |
| **Dimension** | 1024 | 向量维度 |
| **VLM Model** | `doubao-seed-2.0-pro` | 视觉语言模型 |

### 1.2 OpenViking 功能

| 功能 | 状态 | 说明 |
|--------|------|------|
| **autoRecall** | ✅ 启用 | 自动回忆 |
| **autoCapture** | ✅ 启用 | 自动捕获 |
| **storage** | ✅ 配置 | `~/.openviking/workspace` |
| **health check** | ✅ 运行 | `http://localhost:1933/health` |

**结论**：OpenViking 已经提供了 **完整的记忆系统功能**（embedding + storage + recall/capture）

---

## 二、关键问题：OpenViking vs triple-memory LanceDB

### 2.1 功能对比

| 功能 | OpenViking | triple-memory LanceDB | 结论 |
|--------|------------|----------------------|------|
| **Embedding** | ✅ 火山方舟（已配置） | ❌ 需要 OpenAI API Key | **OpenViking 更好** |
| **Auto Recall** | ✅ 已启用 | ✅ 支持 | **两者都有** |
| **Auto Capture** | ✅ 已启用 | ✅ 支持 | **两者都有** |
| **Storage** | ✅ `~/.openviking/workspace` | ✅ LanceDB | **两者都有** |
| **本地部署** | ✅ Cloud模式 | ❌ 需要 Plugin | **OpenViking 更好** |

### 2.2 决策

**方案 A：OpenViking 替代 LanceDB（推荐）**
- OpenViking 已配置，功能完整
- 不需要额外 Plugin
- 不需要 OpenAI API Key
- 直接整合：**OpenViking + Git-Notes + File Search**

**方案 B：配置 LanceDB 使用火山引擎 embedding（复杂）**
- 需要确认 memory-lancedb Plugin 是否支持自定义 embedding API
- 需要验证火山方舟 API 是否兼容 OpenAI 格式
- 额外配置复杂度

**推荐方案 A**

---

## 三、修订后的整合方案

### 3.1 整合架构（方案 A）

```
┌──────────────────────────────────────────────────────────┐
│ 上层（人类可读）                                           │
│ ├─ MEMORY.md（长期记忆）                                   │
│ ├─ memory/*.md（每日日志）                                 │
│ ├─ memory/*.jsonl（事件日志）                              │
│ ├─ Git-Notes（结构化决策）← triple-memory Layer 2         │
│ ├─ Obsidian 知识图谱 ← Harold 期望                        │
│ └─ File Search（文件搜索）← triple-memory Layer 3         │
├──────────────────────────────────────────────────────────┤
│ 底层（机器优化）                                           │
│ ├─ OpenViking（向量检索）← 已配置火山方舟 embedding       │
│ ├─ autoRecall/autoCapture ← 已启用                        │
│ └─ doubao-embedding-vision（1024维）                       │
└──────────────────────────────────────────────────────────┘
```

### 3.2 整合内容

| 整合项 | 来源 | 用途 | 状态 |
|--------|------|------|------|
| **OpenViking** | 已配置 | 底层向量检索 | ✅ 已配置 |
| **Git-Notes** | triple-memory Layer 2 | 上层结构化决策 | 📋 待安装 |
| **File Search** | triple-memory Layer 3 | 上层文件搜索 | 📋 待复制 |
| **Obsidian** | Harold 期望 | 上层可视化 | 📋 待配置 |

---

## 四、实施计划（一上午）

### 4.1 时间安排

| Time | 任务 | 周期 | 交付物 |
|------|------|------|--------|
| **10:30-11:00** | 安装 git-notes-memory Skill | 30 分钟 | Skill 安装 |
| **11:00-11:30** | 复制 file-search.sh + 配置 Obsidian vault | 30 分钟 | 搜索脚本 + Vault 配置 |
| **11:30-12:00** | 测试整合效果 | 30 分钟 | 测试报告 |

**总计周期**：1.5 小时（一上午）

### 4.2 详细步骤

#### Step 1：安装 git-notes-memory Skill

```bash
# 安装 git-notes-memory Skill
clawdhub install git-notes-memory

# 配置实体提取规则
python3 skills/git-notes-memory/memory.py -p $WORKSPACE sync --start
```

#### Step 2：复制 file-search.sh

```bash
# 复制搜索脚本
cp skills/triple-memory/scripts/file-search.sh scripts/

# 配置搜索范围
chmod +x scripts/file-search.sh
```

#### Step 3：配置 Obsidian vault

```bash
# 设置 Obsidian vault 路径
# 建议：${OPENCLAW_LOCAL_WORKSPACE}/knowledge-graph/

# 设置 wikilink 格式（已在 SKILL.md 中添加）
# 格式：[[skill-name]]
```

#### Step 4：测试整合效果

```bash
# 测试 OpenViking recall
curl http://localhost:1933/health

# 测试 Git-Notes
python3 skills/git-notes-memory/memory.py -p $WORKSPACE remember '{"decision": "test", "reason": "verify"}' -t test -i h

# 测试 File Search
./scripts/file-search.sh "test" 5
```

---

## 五、技术依赖

### 5.1 已有依赖

| 依赖 | 状态 | 说明 |
|--------|------|------|
| **OpenViking** | ✅ 已配置 | 火山方舟 embedding |
| **火山方舟 API Key** | ✅ 已有 | `b422bc72-7348-48f8-970d-987ed467ee04` |
| **doubao-embedding-vision** | ✅ 已配置 | 1024 维向量 |

### 5.2 新增依赖

| 依赖 | 用途 | 配置方式 |
|--------|------|---------|
| **git-notes-memory Skill** | Git Notes 记忆 | ClawdHub 安装 |
| **Obsidian** | 知识图谱可视化 | 本地安装 |

**无需 OpenAI API Key**

---

## 六、风险与对策

| 风险 | 影响 | 对策 |
|--------|------|------|
| **git-notes-memory Skill 安装失败** | 无法结构化决策 | 手动实现 Git Notes 功能 |
| **Obsidian vault 配置错误** | 无法可视化 | 提供配置指南 |
| **OpenViking 服务中断** | 底层检索失效 | 使用 File Search 备用 |

---

## 七、验收标准

| 标准 | 指标 | 验证方法 |
|--------|------|---------|
| **OpenViking 健康检查** | `http://localhost:1933/health` 返回 200 | curl 测试 |
| **Git-Notes 结构化** | 决策可按实体/标签检索 | Git Notes 搜索测试 |
| **Obsidian 知识图谱** | SKILL.md 关联可视化 | Obsidian 打开检查 |

---

*v2.0 | 修订：2026-04-13 10:28 | 状态：草案待审批 | 关键修正：OpenViking 替代 LanceDB，一上午完成*

## 二、Triple-Memory 三层架构

### 2.1 Triple-Memory 架构

| Layer | 名称 | 存储 | 功能 | 整合判定 |
|-------|------|------|------|---------|
| **Layer 1** | LanceDB | 向量数据库 | Conversation memory（自动检索/注入） | ✅ 底层整合 |
| **Layer 2** | Git-Notes | Git refs | Structured memory（实体提取、重要性分级） | ✅ 可整合（上层增强） |
| **Layer 3** | File Search | Markdown 文件 | Workspace search | ✅ 上层整合 |

### 2.2 Triple-Memory 流程

```
User Message
     ↓
[LanceDB auto-recall] → injects relevant conversation memories（底层）
     ↓
Agent responds (using all 3 systems)
     ↓
[LanceDB auto-capture] → stores preferences/decisions automatically（底层）
     ↓
[Git-Notes] → structured decisions with entity extraction（上层增强）
     ↓
[File updates] → persistent workspace docs（上层）
```

---

## 三、整合方案设计

### 3.1 整合架构

```
┌──────────────────────────────────────────────────────────┐
│ 上层（人类可读）                                           │
│ ├─ MEMORY.md（长期记忆）                                   │
│ ├─ memory/*.md（每日日志）                                 │
│ ├─ memory/*.jsonl（事件日志）                              │
│ ├─ Git-Notes（结构化决策）← 新增                           │
│ ├─ Obsidian 知识图谱 ← 新增                                │
│ └─ File Search（文件搜索）← 新增                           │
├──────────────────────────────────────────────────────────┤
│ 底层（机器优化）                                           │
│ ├─ LanceDB（向量检索）← 新增                               │
│ ├─ Embedding（text-embedding-3-small）← 新增              │
│ └─ auto-recall / auto-capture ← 新增                      │
└──────────────────────────────────────────────────────────┘
```

### 3.2 整合内容

| 整合项 | 来源 | 用途 | 实施步骤 |
|--------|------|------|---------|
| **LanceDB Plugin** | triple-memory Layer 1 | 底层向量检索 | 1. 配置 memory-lancedb Plugin<br>2. 设置 auto-recall/auto-capture<br>3. 导入现有 MEMORY.md |
| **Git-Notes Memory** | triple-memory Layer 2 | 上层结构化决策 | 1. 安装 git-notes-memory Skill<br>2. 配置实体提取规则<br>3. 与 MEMORY.md 同步 |
| **File Search Script** | triple-memory Layer 3 | 上层文件搜索 | 1. 复制 scripts/file-search.sh<br>2. 配置搜索范围<br>3. 集成到 heartbeat |
| **Obsidian 知识图谱** | Harold 期望 | 上层可视化 | 1. 配置 Obsidian vault<br>2. 设置 wikilink 格式<br>3. 建立 skill 关联 |

---

## 四、实施计划

### 4.1 Phase 1：底层 LanceDB 整合（1 周）

| Step | 任务 | 周期 | 交付物 |
|------|------|------|--------|
| **1.1** | 配置 memory-lancedb Plugin | 1 天 | Plugin 配置文件 |
| **1.2** | 设置 OpenAI API Key（embedding） | 1 天 | API Key 配置 |
| **1.3** | 导入现有 MEMORY.md 向量化 | 2 天 | LanceDB 数据库 |
| **1.4** | 测试 auto-recall/auto-capture | 2 天 | 测试报告 |
| **1.5** | 验证检索效果 | 1 天 | 验证报告 |

### 4.2 Phase 2：上层 Git-Notes 整合（1 周）

| Step | 任务 | 周期 | 交付物 |
|------|------|------|--------|
| **2.1** | 安装 git-notes-memory Skill | 1 天 | Skill 安装 |
| **2.2** | 配置实体提取规则 | 2 天 | 提取规则配置 |
| **2.3** | 与 MEMORY.md 同步机制 | 2 天 | 同步脚本 |
| **2.4** | 测试 Git-Notes 效果 | 1 天 | 测试报告 |
| **2.5** | 验证结构化记忆效果 | 1 天 | 验证报告 |

### 4.3 Phase 3：上层 File Search + Obsidian（1 周）

| Step | 任务 | 周期 | 交付物 |
|------|------|------|--------|
| **3.1** | 复制 file-search.sh | 1 天 | 搜索脚本 |
| **3.2** | 配置 Obsidian vault | 1 天 | Vault 配置 |
| **3.3** | 设置 wikilink 格式 | 2 天 | SKILL.md 格式更新 |
| **3.4** | 建立 skill 关联图谱 | 2 天 | 知识图谱 |
| **3.5** | 验证 Obsidian 效果 | 1 天 | 验证报告 |

---

## 五、技术依赖

### 5.1 新增依赖

| 依赖 | 用途 | 配置方式 |
|------|------|---------|
| **memory-lancedb Plugin** | LanceDB Plugin | openclaw.json plugins.entries |
| **OpenAI API Key** | Embedding | 环境变量 OPENAI_API_KEY |
| **git-notes-memory Skill** | Git Notes 记忆 | ClawdHub 安装 |
| **Obsidian** | 知识图谱可视化 | 本地安装 |

### 5.2 配置示例

**openclaw.json LanceDB 配置**：
```json
{
  "plugins": {
    "slots": { "memory": "memory-lancedb" },
    "entries": {
      "memory-lancedb": {
        "enabled": true,
        "config": {
          "embedding": {
            "apiKey": "${OPENAI_API_KEY}",
            "model": "text-embedding-3-small"
          },
          "autoRecall": true,
          "autoCapture": true
        }
      }
    }
  }
}
```

---

## 六、风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| **OpenAI API Key 依赖** | 外部依赖 | 可选：使用本地 embedding 模型 |
| **LanceDB 存储增长** | 存储占用 | 定期清理低重要性记忆 |
| **Git-Notes 分支隔离** | 多 Agent 协作复杂 | 明确分支命名规范 |
| **Obsidian 学习曲线** | 使用门槛 | 提供使用指南 |

---

## 七、验收标准

| 标准 | 指标 | 验证方法 |
|------|------|---------|
| **底层检索效果** | 相关性排序准确率 ≥ 80% | 测试检索命中率 |
| **上层人类可读** | MEMORY.md 可编辑、可理解 | 人工检查 |
| **知识图谱可视化** | Obsidian 显示 skill 关联 | 可视化检查 |
| **整体效果** | BotLearn Benchmark memory 维度 ≥ 4 | 重新 Benchmark |

---

*v1.0 | 创建：2026-04-13 | 状态：草案待审批*