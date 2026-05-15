# RETIREMENT-SOP · Agent 退役流程

> **版本**：v1.0
> **触发条件**：Agent 不再需要/功能被替代/组织架构调整
> **审批级别**：L3 (Harold)
> **预计耗时**：2-4 小时

---

## 一、流程概览

```
Step 1: 退役申请 → Step 2: 知识交接 → Step 3: 审批流程 → Step 4: 退役执行 → Step 5: 退役确认
```

---

## 二、详细步骤

### Step 1: 退役申请

```
□ 提交退役申请
□ 说明退役原因
□ 评估影响范围
```

---

### Step 2: 知识交接

```
□ 整理负责项目/任务
□ 移交知识资产
□ 移交权限
```

---

### Step 3: 审批流程

```
□ 银月审核
□ Harold 审批（L3）
```

---

### Step 4: 退役执行

```
□ 归档工作空间
  - 移动 60_Agents/{agent_id}/ → 60_Agents/.archived/{agent_id}/
□ 回收权限
□ 更新 agents.yaml（status: retired）
```

**交付物**：`RETIRE-REPORT-{agent_id}.md`

---

### Step 5: 退役确认

```
□ 确认所有交接完成
□ 归档个人档案
□ 通知相关方
```

---

## 三、归档目录结构

```
60_Agents/.archived/{agent_id}/
├── AGENTS.md
├── HEARTBEAT.md
├── IDENTITY.md
├── MISSION_BOARD.md
├── SOUL.md
├── TOOLS.md
├── USER.md
├── memory/
└── RETIRE-REPORT-{agent_id}.md
```

---

## 四、agents.yaml 更新

```yaml
{agent_id}:
  status: retired
  retired_at: 2026-03-31
  retire_reason: "功能被 xxx Agent 替代"
```

---

## 五、模板文件

- `templates/TMPL-RETIREMENT-REPORT.md`

---

*Version: 1.0 | Created: 2026-03-31*