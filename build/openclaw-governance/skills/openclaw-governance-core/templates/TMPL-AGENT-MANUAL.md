# TMPL-AGENT-MANUAL.md

> **文件性质**：Agent 管理整合手册模板
> **存放路径**：`${OPENCLAW_LOCAL_WORKSPACE}/skills/openclaw-governance/skills/openclaw-governance-task/templates/`
> **版本**：v1.0

---

# Agent 管理手册 · Agent Management Manual

> 本手册整合 Agent 完整生命周期的所有流程规范，供银月执行管理任务时参考。

---

## 一、目录

1. [概述](#一概述)
2. [Agent 创建流程](#二agent-创建流程)
3. [Onboarding 流程](#三onboarding-流程)
4. [日常管理](#四日常管理)
5. [Training 流程](#五training-流程)
6. [Performance Review](#六performance-review)
7. [Role Change](#七role-change)
8. [Retire 流程](#八retire-流程)
9. [Emergency Stop](#九emergency-stop)
10. [附录](#十附录)

---

## 二、Agent 创建流程

### 2.1 触发条件

- Harold 决策新增 Agent 角色
- 业务发展需要新专业能力

### 2.2 执行步骤

```
Step 1: 角色定义
  □ 确定 Agent ID 和名称
  □ 定义角色和 Domain
  □ 明确汇报关系

Step 2: 模板实例化
  □ 使用 TMPL-IDENTITY-SUB.md 创建 IDENTITY.md
  □ 使用 TMPL-SOUL-SUB.md 创建 SOUL.md
  □ 创建其他必要文件

Step 3: 数据录入
  □ 在 persons.yaml 添加条目
  □ 设置 onboarding_status = pending

Step 4: 资源分配
  □ 创建 Agent 工作目录
  □ 配置权限

Step 5: 启动 Onboarding
  □ 创建 ONBOARDING Task Card
  □ 启动 Agent 会话
```

---

## 三、Onboarding 流程

### 3.1 触发条件

- 新 Agent 创建完成

### 3.2 流程文档

详见 `TMPL-ONBOARDING-TASK-CARD.md`

### 3.3 关键节点

| 节点 | 负责人 | 验收标准 |
| --- | --- | --- |
| 环境自检 | Agent 自身 | 产出环境自检报告 |
| 工具熟悉 | Agent 自身 | 产出工具可用性清单 |
| 定位理解 | Agent 自身 | 产出职责理解确认书 |
| 银月初审 | 银月 | 审核通过 |
| Harold 批准 | Harold | 批准 onboarding |

### 3.4 状态流转

```
pending → in_progress → submitted → approved → completed
```

---

## 四、日常管理

### 4.1 任务派发

- 银月通过 MISSION_BOARD 派发任务
- Agent 从 MISSION_BOARD.md 接收任务

### 4.2 进度跟踪

- Agent 定期向银月汇报进度
- 银月通过 Heartbeat 巡检整体状态

### 4.3 问题处理

| 问题类型 | 处理方式 |
| --- | --- |
| 执行阻塞 | 向银月请求协调 |
| 能力不足 | 申请 Training |
| 规则疑问 | 查阅 SOUL.md / 咨询银月 |
| 严重异常 | 触发 Emergency Stop |

---

## 五、Training 流程

### 5.1 触发条件

- 新工具/流程引入
- 绩效评估发现短板
- 规则/政策更新
- 业务需要新领域知识

### 5.2 流程文档

详见 `TMPL-TRAINING-TASK-CARD.md`

### 5.3 培训类型

| 类型 | 频率 | 审批 |
| --- | --- | --- |
| 技能升级 | 按需 | 银月批准 |
| 能力补强 | 季度 | 银月批准 |
| 合规培训 | 按需 | 银月批准 |
| 跨域拓展 | 按需 | 银月批准 |

---

## 六、Performance Review

### 6.1 评审周期

- **常规评审**：每季度一次
- **专项评审**：如发现异常可触发

### 6.2 评审维度

| 维度 | 指标 |
| --- | --- |
| 任务完成率 | 按时完成任务数 / 总任务数 |
| 质量评分 | Harold/银月满意度 |
| 合规情况 | 违反规则次数 |
| 知识沉淀 | Wiki 贡献数量 |
| 协作评价 | 其他 Agent 反馈 |

### 6.3 评审结果

| 评级 | 说明 | 后续动作 |
| --- | --- | --- |
| 优秀 | 超出预期 | 考虑授权扩大 |
| 良好 | 符合预期 | 保持现状 |
| 需改进 | 有差距 | 启动 Training |
| 不达标 | 严重不足 | 启动 Retire |

---

## 七、Role Change

### 7.1 触发条件

- 业务调整导致职责变化
- Agent 能力提升需要晋升
- 角色合并或拆分

### 7.2 执行步骤

```
Step 1: 变更评估
  □ 分析变更原因和影响
  □ 制定变更方案

Step 2: 方案审批
  □ 提交 Harold 审批

Step 3: 执行变更
  □ 更新 IDENTITY.md
  □ 更新 persons.yaml
  □ 如需培训，执行 Training

Step 4: 归档
  □ 记录变更历史
```

---

## 八、Retire 流程

### 8.1 触发条件

- 角色合并
- 功能停用
- 性能不达标（多次警告后）
- 严重违规
- Harold 主动决策

### 8.2 流程文档

详见 `TMPL-RETIRE-TASK-CARD.md`

### 8.3 关键节点

| 节点 | 负责人 | 验收标准 |
| --- | --- | --- |
| 知识资产盘点 | 银月 | 产出知识资产清单 |
| 知识交接 | 银月 | 确认交接完成 |
| 工作状态报告 | 银月 | 产出状态报告 |
| 资源清理 | 银月 | 确认清理完成 |
| persons.yaml 更新 | 银月 | 状态更新为 retired |
| Harold 批准 | Harold | 批准退休 |

---

## 九、Emergency Stop

### 9.1 触发条件

详见 `TMPL-EMERGENCY-STOP.md`

### 9.2 执行原则

- **即时响应**：发现触发条件立即执行
- **事后汇报**：执行后立即向 Harold 汇报
- **完整记录**：详细记录停用原因和影响

### 9.3 恢复流程

根据停用原因和恢复条件，决定是否恢复 Agent 运行。

---

## 十、附录

### 10.1 相关模板索引

| 模板 | 用途 |
| --- | --- |
| TMPL-IDENTITY-SUB.md | Agent 身份定义 |
| TMPL-ONBOARDING-TASK-CARD.md | 入职培训流程 |
| TMPL-RETIRE-TASK-CARD.md | 退休流程 |
| TMPL-TRAINING-TASK-CARD.md | 培训流程 |
| TMPL-EMERGENCY-STOP.md | 紧急停用协议 |
| TMPL-AGENT-MANUAL.md | 本手册 |

### 10.2 关键文件路径

| 文件 | 路径 |
| --- | --- |
| persons.yaml | `${OPENCLAW_LOCAL_WORKSPACE}/.system/governance/current/config/user/persons.yaml` |
| MISSION_BOARD | `${OPENCLAW_LOCAL_WORKSPACE}/MISSION_BOARD.md` |
| AGENTS.md | `${OPENCLAW_LOCAL_WORKSPACE}/AGENTS.md` |

---

## 版本信息

- **Version**: v1.0
- **Created At**: 2026-03-07
- **Approved By**: Harold Tsui
- **Status**: Draft

*本手册由银月创建，整合 Agent 生命周期管理的完整流程规范。*