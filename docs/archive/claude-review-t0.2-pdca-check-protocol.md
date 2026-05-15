# Claude 评审材料：T0.2 PDCA Check 策略协议

> **评审目标**：验证 PDCA Check 策略协议设计是否完整、合理、可实施  
> **评审版本**：v1.0 草案  
> **上下文版本**：WBS v1.2 + ARCH v1.4.2 + governance-delegation v1.2.0  
> **评审重点**：接口完整性、流程合理性、与现有系统集成度

---

## 一、背景说明

### 1.1 变更原因
原 T0.2 定义为 "sessions/*.jsonl 字段规范"，但经过深度分析发现：
- Check 阶段验收机制缺失是更核心的问题
- 需要明确定义 PDCA 环中 Check 阶段的验收策略
- 与 governance-delegation 的 L0-L5 分级体系集成

### 1.2 新定义范围
**T0.2：PDCA Check 策略协议**
- 定义 Check 阶段验收机制：谁来 review、用什么标准、如何驱动 Act
- 输出：`docs/pdca-check-protocol.md` + T1.1 Schema `check_reference` 字段

---

## 二、核心设计

### 2.1 整体流程
```
Plan → determine_review() → check_reference → Do → Check → verdict → Act → adjust_automation_level()
```

### 2.2 关键接口

#### determine_review() 接口
- **调用时机**：Plan 阶段开始时
- **输入**：target_type, task_type, project_phase, dl_refs, is_first_time, priority, agent_id
- **输出**：
  ```json
  {
    "review_level": "L0-L5",
    "acceptance_criteria": ["标准1", "标准2"],
    "reviewer": "harold|agent_id|null", 
    "references": ["docs/pdca-check-protocol.md", "DL-xxx"]
  }
  ```

#### adjust_automation_level() 接口  
- **触发条件**：Act 阶段开始时，基于 verdict
- **调整规则**：
  - pass → 连续3次可升级
  - fail → 连续2次需降级  
  - partial → 维持现状
- **约束**：逐级调整，L0/L5 为边界

### 2.3 L0-L5 级别映射

| 级别 | 名称 | 审批方式 | reviewer |
|------|------|----------|----------|
| L5 | 完全自动化 | 自动通过 | null |
| L4 | 高度自动化 | 机器自检 | null |
| L3 | 有条件自动化 | Agent 自评 | null |
| L2 | 辅助决策 | 同伴评审 | Agent ID |
| L1 | 人工辅助 | 人工审批 | Harold ID |
| L0 | 完全人工 | 人工+审计 | Harold ID |

### 2.4 LESSON-LEARN 集成
- **触发时机**：Task 关闭时（verdict != null 且 next_cycle = null）
- **四问法**：
  1. What worked well?
  2. What didn't work?  
  3. What would you do differently?
  4. What knowledge should be shared?

---

## 三、架构约束对齐

### 3.1 ARCH v1.4.2 check_reference 字段
```yaml
check_reference:
  review_level: enum[L0, L1, L2, L3, L4, L5]
  acceptance_criteria: list[string]
  reviewer: string | null
  references: list[string]
```

### 3.2 CycleUnit 字段职责
- **Plan 阶段**：`determine_review()` 写入 `plan.check_reference`
- **Check 阶段**：按 `check_reference` 执行验收
- **Act 阶段**：`adjust_automation_level()` 调整级别

### 3.3 与 governance-delegation 集成
- 复用 L0-L5 分级定义
- 调用现有 `determine_review()` 判级逻辑
- 更新 `automation-levels.yaml` 记录

---

## 四、评审问题清单

请 Claude Sonnet 4.6 重点评审以下问题：

### P0 级问题（必须回答）
1. **接口完整性**：`determine_review()` 和 `adjust_automation_level()` 的输入/输出是否完整？是否有遗漏的关键参数？
2. **流程合理性**：P→D→C→A 流程是否存在逻辑漏洞或死循环风险？
3. **L0-L5 映射**：级别定义是否清晰？是否存在模糊地带？

### P1 级问题（建议回答）  
4. **安全性**：自动化级别调整是否存在安全风险？是否需要额外的防护机制？
5. **可扩展性**：协议设计是否支持未来新增的评审级别或验收方式？
6. **错误处理**：接口失败或字段缺失时的降级策略是否合理？

### P2 级问题（可选回答）
7. **性能影响**：Check 阶段的验收过程是否会成为性能瓶颈？
8. **用户体验**：human_review 的飞书通知和超时处理是否合理？

---

## 五、相关文件引用

### 主要交付物
- `docs/pdca-check-protocol.md`（本评审主文档）

### 上下文文件
- `NUCLEUS-4.0-WBS-v1.2.md`（T0.2 任务定义）
- `NUCLEUS-4.0-ARCH-v1.4.2.md`（架构约束，§2.1.3 check_reference）
- `~/.openclaw/skills/openclaw-governance/skills/openclaw-governance-delegation/SKILL.md`（L0-L5 定义）

### 使用说明
1. 在 sider.ai 中打开 NUCLEUS-4.0 历史会话
2. 复制本文件内容到输入框
3. 提交评审请求
4. 等待 Claude Sonnet 4.6 的详细反馈

---

*准备完毕，等待 Claude 评审*