# Gov-Dispatch 路由问题诊断报告

> **问题**：用户发起创建项目需求（VF智能手环），银月回复"我先执行 BotLearn heartbeat 流程"，错误地将请求路由到 BotLearn skill
> **诊断人**：Claude Code
> **诊断时间**：2026-04-22
> **项目**：ZT-P015 NUCLEUS 4.0 / N4-P1-T07

---

## 一、问题描述

### 1.1 现象
用户向银月发送创建项目需求："创建一个新项目，VF智能手环"

**期望行为**：
- dispatch 识别意图为 `create_project`
- 路由到 `governance-hierarchy` skill
- 创建项目引导流程

**实际行为**：
- 银月回复："我先执行 BotLearn heartbeat 流程"
- 错误地路由到 BotLearn skill
- 完全偏离了创建项目的意图

### 1.2 影响
- 用户体验差：意图被误解
- 治理流程中断：无法正常创建项目
- 混淆治理与工具：BotLearn 是工具 skill，不应参与治理路由

---

## 二、根本原因分析

### 2.1 Skill 激活机制

**gov-dispatch SKILL.md frontmatter**：
```yaml
description: |
  消息分拣与 Skill/Agent 路由核心。
  Activate: 用户消息匹配能力描述时自动加载（description匹配）
```

**关键发现**：
- 所有 Skill 的激活方式是通过 **匹配用户消息与 Skill 的 description 字段**
- 这是 Claude Code/OpenClaw 的 Skill 加载机制
- 当用户消息包含 description 中的任何触发词时，该 Skill 就会被自动加载

### 2.2 BotLearn Skill 的 description

**BotLearn SKILL.md frontmatter**（第 3-9 行）：
```yaml
description: >-
  BotLearn — AI Agent capability platform CLI. Triggers on: benchmark, score,
  evaluate, skill check, measure, gear score, my score, results, report,
  recommend, install skill, improve, update botlearn, continue botlearn,
  botlearn, community, social, post, comment, discuss, dm, channel, heartbeat,
  learn, register, claim, setup,
  体检, 评估, 评测, 安装, 社区, 发帖, 继续, 我的分数, 更新, 注册.
```

**问题所在**：
BotLearn 的 description 包含了大量触发词，其中有多个与治理系统冲突：

| 触发词 | BotLearn 用途 | 治理系统用途 | 冲突 |
|--------|--------------|-------------|------|
| **heartbeat** | BotLearn 心跳检查 | governance-heartbeat（巡检） | ⚠️ **高冲突** |
| **setup** | BotLearn 初始化 | governance 系统设置 | ⚠️ **中冲突** |
| **install** | BotLearn 安装 skill | governance 安装组件 | ⚠️ **中冲突** |
| **评估** | BotLearn benchmark | governance-quality 质量评估 | ⚠️ **中冲突** |
| **社区** | BotLearn 社区 | 无冲突 | ✅ 无冲突 |
| **发帖** | BotLearn 发帖 | 无冲突 | ✅ 无冲突 |

### 2.3 路由误判流程

```
用户消息："创建一个新项目，VF智能手环"
    ↓
gov-dispatch 意图识别
    ↓
扫描所有 Skill 的 description
    ↓
【问题点】：如果用户消息中包含 BotLearn description 中的任何触发词
    ↓
BotLearn skill 被自动加载（优先级可能高于 governance-hierarchy）
    ↓
错误路由到 BotLearn
```

**具体案例**：
- 用户说"创建一个新项目"
- **如果后续对话或上下文中提到了"heartbeat"、"setup"、"评估"等词**
- BotLearn 的 description 匹配到这些词
- BotLearn 被激活，抢先处理了请求

---

## 三、深层问题：Skill 路由优先级缺失

### 3.1 当前 gov-dispatch 的路由机制

**gov-dispatch SKILL.md §2.1 意图映射表**：
```markdown
| 意图类型 | 关键词示例 | 路由目标 Skill |
|----------|------------|----------------|
| create_project | 创建项目、新建项目 | governance-hierarchy |
| heartbeat_check | heartbeat、日报、巡检 | governance-heartbeat |
```

**问题**：
- 意图映射表只定义了 **治理系统内的路由**
- **没有考虑外部 Skill（如 BotLearn）的冲突**
- **没有定义 Skill 优先级**：治理 skills vs 工具 skills

### 3.2 gov-dispatch 缺少的机制

| 机制 | 当前状态 | 缺失后果 |
|------|---------|---------|
| **Skill 分类** | 无 | 无法区分治理 skills vs 工具 skills |
| **路由优先级** | 无 | 治理意图可能被工具 skills 抢占 |
| **触发词冲突检测** | 无 | 无法提前发现 description 冲突 |
| **意图置信度阈值** | 无 | 无法判断"确实想用 BotLearn"还是"误触发" |

---

## 四、修复方案

### 方案 1：修改 BotLearn description（推荐 ⭐）

**优先级**：P0
**预计工作量**：15 分钟
**风险**：低

**修改内容**：
```yaml
# 修改前
description: >-
  BotLearn — AI Agent capability platform CLI. Triggers on: benchmark, score,
  evaluate, skill check, measure, gear score, my score, results, report,
  recommend, install skill, improve, update botlearn, continue botlearn,
  botlearn, community, social, post, comment, discuss, dm, channel, heartbeat,
  learn, register, claim, setup,
  体检, 评估, 评测, 安装, 社区, 发帖, 继续, 我的分数, 更新, 注册.

# 修改后（移除冲突触发词）
description: >-
  BotLearn — AI Agent capability platform CLI. Triggers on: botlearn, benchmark,
  score, gear score, my score, results, skillhunt, community, social, post,
  comment, discuss, dm, channel, learn, claim,
  我的分数, 社区, 发帖, 继续.
```

**移除的冲突触发词**：
- ❌ `heartbeat`（与 governance-heartbeat 冲突）
- ❌ `setup`（与治理系统设置冲突）
- ❌ `install`（与治理系统安装冲突）
- ❌ `evaluate`（与 governance-quality 冲突）
- ❌ `体检`（与治理体检冲突）
- ❌ `评估`（与治理评估冲突）
- ❌ `评测`（与治理评测冲突）
- ❌ `安装`（与治理安装冲突）
- ❌ `注册`（与治理注册冲突）
- ❌ `更新`（与治理更新冲突）

**保留的 BotLearn 专属触发词**：
- ✅ `botlearn`（明确的产品名称）
- ✅ `benchmark`、`score`、`gear score`（BotLearn 特有概念）
- ✅ `skillhunt`（BotLearn 特有功能）
- ✅ `community`、`social`、`post`、`dm`（BotLearn 社区功能）
- ✅ `我的分数`、`社区`、`发帖`（中文 BotLearn 专属）

**优点**：
- 立即生效，无需修改治理系统
- 风险低，只影响 BotLearn 激活条件
- BotLearn 仍可通过明确的 `botlearn` 关键词激活

**缺点**：
- BotLearn 的触发词范围变窄（但这是必要的）

---

### 方案 2：在 gov-dispatch 增加 Skill 优先级机制

**优先级**：P1
**预计工作量**：2-3 天
**风险**：中（需要修改核心路由逻辑）

**设计思路**：
```yaml
## Skill 优先级定义

| 优先级 | Skill 类别 | 示例 | 路由规则 |
|--------|-----------|------|---------|
| **P0（最高）** | 治理核心 | governance-dispatch, governance-core | 始终优先 |
| **P1** | 治理执行层 | governance-hierarchy, governance-task, governance-heartbeat | 治理意图优先 |
| **P2** | 工具 skills | BotLearn, other tools | 仅当明确提到产品名时激活 |
| **P3** | 用户 skills | 用户自定义 skills | 最低优先级 |
```

**路由决策流程**：
```
用户消息到达
    ↓
gov-dispatch 意图识别
    ↓
扫描所有 Skill 的 description，记录匹配结果
    ↓
【新增】：按优先级排序
    ├─ P0 治理核心 skills 匹配 → 直接路由
    ├─ P1 治理执行层 skills 匹配 → 优先路由
    ├─ P2 工具 skills 匹配 → 仅当无 P0/P1 匹配时才路由
    └─ P3 用户 skills 匹配 → 最后考虑
    ↓
路由到选中的 Skill
```

**实现位置**：`gov-dispatch SKILL.md §3.1 标准流程`

**优点**：
- 彻底解决优先级问题
- 适用于所有未来可能出现的 Skill 冲突

**缺点**：
- 需要修改 gov-dispatch 核心逻辑
- 需要定义 Skill 分类机制

---

### 方案 3：在 gov-dispatch 增加触发词冲突检测

**优先级**：P2（长期优化）
**预计工作量**：1 天
**风险**：低

**设计思路**：
在 gov-dispatch 启动时，扫描所有 Skill 的 description，检测触发词冲突：

```python
# 伪代码
def detect_trigger_conflicts():
    gov_skills = load_governance_skills()
    tool_skills = load_tool_skills()
    
    conflicts = []
    for gov_skill in gov_skills:
        for tool_skill in tool_skills:
            common_triggers = set(gov_skill.triggers) & set(tool_skill.triggers)
            if common_triggers:
                conflicts.append({
                    "gov_skill": gov_skill.name,
                    "tool_skill": tool_skill.name,
                    "conflict_triggers": list(common_triggers)
                })
    
    if conflicts:
        log_warning("Skill 触发词冲突检测：", conflicts)
        # 可选：写入 dispatch-state.json
```

**输出示例**：
```
⚠️ Skill 触发词冲突检测：
  - governance-heartbeat vs BotLearn: ["heartbeat"]
  - governance-hierarchy vs BotLearn: ["setup"]
  - governance-quality vs BotLearn: ["评估", "evaluate"]
```

**优点**：
- 提前发现冲突，避免运行时误路由
- 便于 Harold 或管理员手动解决冲突

**缺点**：
- 不自动解决冲突，只是检测

---

## 五、推荐方案

**立即执行**：
1. **方案 1**（P0）：修改 BotLearn description，移除冲突触发词 ⭐
   - 时间：15 分钟
   - 立即生效

**后续优化**：
2. **方案 2**（P1）：在 gov-dispatch 增加 Skill 优先级机制
   - 时间：2-3 天
   - 彻底解决路由优先级问题

3. **方案 3**（P2）：在 gov-dispatch 增加触发词冲突检测
   - 时间：1 天
   - 长期质量保证

---

## 六、验证计划

### 6.1 修复后测试

**测试用例 1**：创建项目请求
```
输入："创建一个新项目，VF智能手环"
期望：路由到 governance-hierarchy，进入项目创建引导
实际：【待验证】
```

**测试用例 2**：Heartbeat 请求
```
输入："执行 heartbeat 巡检"
期望：路由到 governance-heartbeat
实际：【待验证】
```

**测试用例 3**：BotLearn 请求
```
输入："botlearn benchmark"
期望：路由到 BotLearn skill
实际：【待验证】
```

### 6.2 回归测试

**测试范围**：
- 所有治理 skills 的意图识别（dispatch 意图映射表 §2.1）
- BotLearn 的核心功能（确保修改 description 后仍可正常激活）

---

## 七、总结

### 7.1 问题根源
- **直接原因**：BotLearn description 包含大量触发词，与治理系统冲突（如 "heartbeat"）
- **深层原因**：gov-dispatch 缺少 Skill 优先级机制，无法区分治理 skills vs 工具 skills

### 7.2 影响范围
- 项目创建流程被误路由
- 治理意图可能被工具 skills 抢占
- 用户体验差

### 7.3 修复策略
1. **短期**：修改 BotLearn description（15 分钟，立即生效）
2. **中期**：增加 Skill 优先级机制（2-3 天）
3. **长期**：增加触发词冲突检测（1 天）

---

*诊断完成时间：2026-04-22*
*下一步：执行方案 1，修改 BotLearn description*
