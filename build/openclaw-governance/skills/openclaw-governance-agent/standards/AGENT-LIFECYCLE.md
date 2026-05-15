# AGENT-LIFECYCLE · Agent 生命周期管理规范

> **版本**：v1.0
> **归属**：SYS-AGENT 项目
> **用途**：标准化 Agent 生命周期各阶段管理流程

---

## 一、生命周期阶段概览

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌───────────────────┐   ┌─────────┐
│  入职   │ → │  培训   │ → │  在岗   │ → │ 升级/调岗/降级    │ → │  退役   │
└─────────┘   └─────────┘   └─────────┘   └───────────────────┘   └─────────┘
    ↓             ↓             ↓                   ↓                 ↓
 ONBOARD-001   TRAIN-*       日常运维         CHANGE-*            RETIRE-001
 L3(Harold)    L1/L2         Heartbeat        L2/L3              L3(Harold)
```

---

## 二、入职（Onboarding）

### 2.1 触发条件
- 新 Agent 创建（`agents.yaml` 新增条目）
- `onboard_required: true`

### 2.2 执行流程
详见 `TMPL-ONBOARDING-TASK-CARD.md`

### 2.3 关键步骤
1. 环境熟悉 → 环境自检报告
2. 工具熟悉 → 工具可用性清单
3. 定位理解 → 职责理解确认书
4. 上下文创建 → 工作空间初始化
5. 入职汇报 → ONBOARD-REPORT
6. 银月初审 → Harold 终审

### 2.4 审批级别
- **L3 (Harold)** - 必须经过 Harold 最终批准

### 2.5 完成后状态更新
```yaml
# agents.yaml
onboarding_status: completed
onboarded_at: 2026-03-31
```

---

## 三、培训（Training）

### 3.1 触发条件
- Skill 安装/更新
- 能力升级需求
- 定期培训计划

### 3.2 培训类型

| 类型 | 触发 | 内容 | 审批 |
|------|------|------|------|
| **Skill 培训** | Skill 变更 | 新 Skill 学习、能力验证 | L1 |
| **能力升级培训** | 需求申请 | 进阶技能、新领域 | L2 |
| **定期培训** | 季度/年度 | 复习、新知识更新 | L1 |

### 3.3 执行流程

```
Step 1: 培训需求识别
  □ 识别培训触发条件
  □ 确定培训内容（Skill/能力）
  □ 制定培训计划
  → Step 2

Step 2: 培训执行
  □ 学习相关文档/Skill
  □ 完成练习任务
  □ 记录学习笔记
  → Step 3

Step 3: 能力验证
  □ 完成验证任务
  □ 输出培训报告
  □ 提交银月审核
  → Step 4

Step 4: 能力档案更新
  □ 更新 agents.yaml 能力清单
  □ 记录培训历史到个人档案
  □ 通知 Harold（如涉及重要能力）
```

### 3.4 交付物
- `TRAIN-REPORT-{agent_id}-{date}.md` - 培训报告
- `agents.yaml` 能力清单更新

### 3.5 审批级别
- **L1** - Skill 培训（银月审批）
- **L2** - 能力升级培训（银月 + Harold 知情）

---

## 四、升级（Promotion）

### 4.1 触发条件
- 自动化级别评估达标（DL 命中率 >= 80%，连续成功 >= 3 次）
- Agent 主动申请
- 银月推荐

### 4.2 升级类型

| 类型 | 说明 | 审批 |
|------|------|------|
| **自动化级别升级** | L0 → L1 → L2 → L3 → L4 | L3 (Harold) |
| **职责扩展** | 新增职责领域 | L2 |
| **权限提升** | 获得更多系统权限 | L3 (Harold) |

### 4.3 执行流程

```
Step 1: 升级评估
  □ 检查自动化级别指标
    - DL 命中率
    - 连续成功次数
    - 错误率
  □ 评估是否满足升级条件
  → Step 2

Step 2: 升级申请
  □ 填写升级申请
  □ 提供支持数据
  □ 提交银月初审
  → Step 3

Step 3: 审批流程
  □ 银月审核（L2）
  □ Harold 审批（L3）
  □ 记录审批意见
  → Step 4

Step 4: 升级实施
  □ 更新 agents.yaml 级别
  □ 更新权限配置
  □ 通知相关 Agent
  □ 记录到个人档案
```

### 4.4 交付物
- `PROMOTE-REPORT-{agent_id}-{date}.md` - 升级报告
- `agents.yaml` 级别更新
- `HAROLD-DECISION-LIBRARY.md` 可能新增条目

### 4.5 审批级别
- **自动化级别升级**: L3 (Harold)
- **职责扩展**: L2 (银月)
- **权限提升**: L3 (Harold)

---

## 五、调岗（Transfer）

### 5.1 触发条件
- 业务需求变更
- Agent 能力匹配调整
- 组织架构调整

### 5.2 调岗类型

| 类型 | 说明 | 审批 |
|------|------|------|
| **职责调整** | 调整职责范围 | L2 |
| **项目调动** | 调整负责项目 | L2 |
| **协作关系变更** | 调整汇报对象/协作对象 | L1 |

### 5.3 执行流程

```
Step 1: 调岗需求识别
  □ 识别调岗原因
  □ 确定调整内容
  □ 评估影响范围
  → Step 2

Step 2: 调岗计划
  □ 制定交接计划
  □ 确定时间节点
  □ 通知相关方
  → Step 3

Step 3: 交接执行
  □ 知识交接（文档、任务）
  □ 权限交接
  □ 项目交接
  → Step 4

Step 4: 配置更新
  □ 更新 IDENTITY.md
  □ 更新 agents.yaml
  □ 更新项目配置
  → Step 5

Step 5: 调岗确认
  □ 银月审核确认
  □ 更新个人档案
  □ 通知 Harold
```

### 5.4 交付物
- `TRANSFER-REPORT-{agent_id}-{date}.md` - 调岗报告
- `IDENTITY.md` 更新
- `agents.yaml` 更新

### 5.5 审批级别
- **职责/项目调整**: L2 (银月)
- **汇报关系变更**: L2 (银月 + Harold 知情)

---

## 六、降级（Demotion）

### 6.1 触发条件
- 连续任务失败
- 错误率过高
- 能力不匹配
- 主动申请降级

### 6.2 降级类型

| 类型 | 说明 | 审批 |
|------|------|------|
| **自动化级别降级** | L4 → L3 → L2 → L1 → L0 | L2 (银月) |
| **职责缩减** | 减少职责范围 | L2 |
| **权限回收** | 回收部分权限 | L3 (Harold) |

### 6.3 执行流程

```
Step 1: 问题识别
  □ 监控指标异常（错误率、失败率）
  □ 分析降级原因
  □ 评估影响
  → Step 2

Step 2: 降级评估
  □ 确认降级必要性
  □ 确定降级幅度
  □ 制定改进计划（可选）
  → Step 3

Step 3: 审批流程
  □ 银月审核（L2）
  □ Harold 知情/审批（视严重程度）
  → Step 4

Step 4: 降级实施
  □ 更新 agents.yaml 级别
  □ 回收相应权限
  □ 调整任务分配
  → Step 5

Step 5: 降级记录
  □ 记录降级原因
  □ 制定改进计划（如有）
  □ 更新个人档案
```

### 6.4 交付物
- `DEMOTION-REPORT-{agent_id}-{date}.md` - 降级报告
- `agents.yaml` 级别更新
- 改进计划（可选）

### 6.5 审批级别
- **自动化级别降级**: L2 (银月 + Harold 知情)
- **职责缩减**: L2 (银月)
- **权限回收**: L3 (Harold)

---

## 七、退役（Retirement）

### 7.1 触发条件
- Agent 不再需要
- 功能被其他 Agent 替代
- 组织架构调整

### 7.2 执行流程

```
Step 1: 退役申请
  □ 提交退役申请
  □ 说明退役原因
  □ 评估影响范围
  → Step 2

Step 2: 知识交接
  □ 整理负责项目/任务
  □ 移交知识资产
  □ 移交权限
  → Step 3

Step 3: 审批流程
  □ 银月审核
  □ Harold 审批（L3）
  → Step 4

Step 4: 退役执行
  □ 归档工作空间
  □ 回收权限
  □ 更新 agents.yaml（status: retired）
  □ 移动到归档目录
  → Step 5

Step 5: 退役确认
  □ 确认所有交接完成
  □ 归档个人档案
  □ 通知相关方
```

### 7.3 交付物
- `RETIRE-REPORT-{agent_id}.md` - 退役报告
- 归档目录：`60_Agents/.archived/{agent_id}/`
- `agents.yaml` 状态更新

### 7.4 审批级别
- **L3 (Harold)** - 必须经过 Harold 批准

---

## 八、集中 vs 分散管理

### 8.1 集中管理（SYS-AGENT 项目）

| 事件 | 原因 |
|------|------|
| 入职 | 关键事件，Harold 审批 |
| 退役 | 关键事件，Harold 审批 |
| 权限变更 | 安全相关 |
| 自动化级别升级/降级 | 系统级配置变更 |

### 8.2 分散跟踪（各 Agent MISSION_BOARD）

| 事件 | 原因 |
|------|------|
| 培训记录 | 个人成长档案 |
| 能力清单变更 | Skill 变更历史 |
| 职责微调 | 日常调整 |
| 任务历史 | 个人工作记录 |

### 8.3 同步机制

```
集中事件（SYS-AGENT）
    ↓
触发更新
    ↓
分散记录（各 Agent MISSION_BOARD）
```

---

## 九、模板清单

| 模板 | 用途 | 路径 |
|------|------|------|
| TMPL-ONBOARDING-TASK-CARD | 入职培训 | `templates/` |
| TMPL-TRAINING-REPORT | 培训报告 | `templates/` |
| TMPL-PROMOTION-REPORT | 升级报告 | `templates/` |
| TMPL-TRANSFER-REPORT | 调岗报告 | `templates/` |
| TMPL-DEMOTION-REPORT | 降级报告 | `templates/` |
| TMPL-RETIREMENT-REPORT | 退役报告 | `templates/` |

---

## 十、自动化级别定义（L0-L4）

### 10.1 级别定义

| 级别 | 名称 | 说明 | 审批权限 |
|------|------|------|----------|
| **L0** | 观察级 | 仅观察学习，无自主执行权限 | 需 L1 审核 |
| **L1** | 受控级 | 在明确指令下执行，需审核确认 | L2 (银月) |
| **L2** | 协作级 | 可独立执行常规任务，复杂任务需审核 | L2 (银月) |
| **L3** | 自主级 | 可独立完成复杂任务，仅结果汇报 | L3 (Harold) |
| **L4** | 战略级 | 可参与战略决策，自主规划执行 | L3 (Harold) |

### 10.2 升级量化指标

| 目标级别 | DL 命中率 | 连续成功次数 | 错误率 | 审批级别 |
|----------|-----------|--------------|--------|----------|
| L0 → L1 | >= 60% | >= 2 | < 20% | L2 (银月) |
| L1 → L2 | >= 70% | >= 3 | < 15% | L2 (银月) |
| L2 → L3 | >= 80% | >= 5 | < 10% | L3 (Harold) |
| L3 → L4 | >= 90% | >= 10 | < 5% | L3 (Harold) |

### 10.3 降级量化指标

| 当前级别 | 错误率阈值 | 连续失败次数 | 触发降级 | 审批级别 |
|----------|------------|--------------|----------|----------|
| L4 | >= 10% | >= 2 | → L3 | L2 (银月 + Harold 知情) |
| L3 | >= 15% | >= 3 | → L2 | L2 (银月 + Harold 知情) |
| L2 | >= 20% | >= 3 | → L1 | L2 (银月) |
| L1 | >= 30% | >= 5 | → L0 | L2 (银月) |

---

## 十一、agents.yaml 字段定义

### 11.1 必需字段

```yaml
agent_id: string          # Agent 唯一标识
duty: string              # 职位名称
role: string              # 角色描述
level: L0|L1|L2|L3|L4     # 自动化级别
capabilities: list        # 能力标签列表
required: boolean         # 是否系统必需
status: active|retired   # 当前状态
```

### 11.2 入职相关字段

```yaml
onboard_required: boolean      # 是否需要入职流程
onboarding_status: pending|in_progress|completed  # 入职状态
onboarded_at: date|null        # 入职完成日期 (YYYY-MM-DD)
```

### 11.3 完整示例

```yaml
extensible_agents:
  cqo:
    agent_id: cqo
    duty: 首席质量官
    role: CQO - 质量管控
    capabilities:
      - 质量
      - 审核
      - 验收
    level: L3
    required: false
    onboard_required: true
    onboarding_status: completed
    onboarded_at: 2026-03-15
    status: active
    triggers:
      - 质量
      - 审核
      - 验收
```

### 11.4 字段更新时机

| 事件 | 更新字段 |
|------|----------|
| 入职开始 | `onboarding_status: in_progress` |
| 入职完成 | `onboarding_status: completed`, `onboarded_at: YYYY-MM-DD` |
| 升级 | `level: 新级别` |
| 降级 | `level: 新级别` |
| 退役 | `status: retired` |

---

## 十二、触发机制说明

### 12.1 自动触发（系统监听）

| 事件类型 | 触发条件 | 监听方式 |
|----------|----------|----------|
| **入职** | `agents.yaml` 新增条目 + `onboard_required: true` | 配置文件变更监听 |
| **升级评估** | DL 命中率达标 + 连续成功次数达标 | Heartbeat 周期检查 |
| **降级评估** | 错误率超阈值 + 连续失败次数超阈值 | Heartbeat 周期检查 |

### 12.2 手动触发（关键词激活）

当用户消息包含以下关键词时，自动加载本 Skill：

```
入职、onboard、新 Agent
培训、training、Skill 学习
升级、promotion、自动化级别
调岗、transfer、职责变更
降级、demotion、能力下降
退役、retire、Agent 废弃
```

### 12.3 触发后动作

```
触发检测 → 加载本 Skill → 匹配对应 SOP → 执行流程 → 生成报告
```

---

## 十三、版本信息

- **Version**: v1.1
- **Created At**: 2026-03-31
- **Updated At**: 2026-03-31
- **Author**: 张铁 (cqo)
- **Changes**:
  - 修正模板路径引用（`governance-task/templates/` → `templates/`）
  - 添加 agents.yaml 字段定义（含 `onboarding_status`、`onboarded_at`）
  - 统一 Level 定义（L0-L4，含 L0 观察级）
  - 添加触发机制说明（自动触发 + 手动触发）
  - 添加升级/降级量化指标汇总
- **Status**: 已修订，待银月确认

---

*本规范由 SYS-AGENT 项目维护，各 Agent 生命周期事件按此流程执行。*