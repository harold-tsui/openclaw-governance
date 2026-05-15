# NUCLEUS 升级方案

> **文档编号**: NUCLEUS-UPGRADE-v2.0
> **创建日期**: 2026-04-16
> **修订日期**: 2026-04-18
> **上位引用**: NUCLEUS-ARCH-v2.0 · NUCLEUS-DESIGN-v2.0 · NUCLEUS-REQ-SPEC-v2.0
> **评审状态**: 待 Harold 评审

---

## 一、当前状态评估

### 1.1 Phase 0-1 完成情况

| Phase | 目标 | 完成度 | 说明 |
|-------|------|--------|------|
| **Phase 0** | 接入边界定义 | ✅ 100% | T0.1 接入契约 + T0.2 PDCA Check 策略协议 |
| **Phase 1** | MVP 可进化 | ✅ 95% | pdca.py v2.2.0 + SKILL.md v2.5.0 + 99 测试通过 |

### 1.2 已实现功能清单

| 功能模块 | 状态 | 实现方式 |
|---------|------|---------|
| **PDCA 状态记录器** | ✅ | `scripts/pdca.py` v2.2.0（单文件，~725 行） |
| **ADAS L0-L3 Review** | ✅ | `c()` 内置规则校验 |
| **Human-in-the-Loop** | ✅ | delegation §10.2 A/B/C/D 协议 + 7 天超时 |
| **审计出口** | ✅ | `audit_eligible` + `get_audit_queue()` + `mark_audit()` |
| **两条触发路径** | ✅ | Path A（直接）+ Path B（heartbeat Step 3a） |
| **Harness 规则** | ✅ | P1/D1/C1/C2/A1 在 SKILL.md 中定义 |
| **consecutive_fails 熔断** | ✅ | `get_status()` → `needs_escalation` |
| **原子写入** | ✅ | `_save()` 先 .tmp 再 os.replace |

### 1.3 未实现功能清单

| 功能模块 | 计划 Phase | 优先级 | 说明 |
|---------|-----------|--------|------|
| **层间传播** | Phase 2 | P0 | pdca.py aggregate() 轻量函数（非 CycleAggregator 类） |
| **并发上限** | Phase 2 | P0 | pdca.py check_concurrency() 前置校验 |
| **多粒度调度** | Phase 2 | P0 | scheduler_state.py 计数器 |
| **知识沉淀** | Phase 2 | P1 | knowledge/lessons/ 轻量存储 |
| **System 级自进化** | Phase 3 | P0 | 完整递归 PDCA 基础设施 |
| **预测性监控** | Phase 3 | P1 | 需要历史数据积累 |
| **自主决策（白名单）** | Phase 3 | P0 | 需要治理框架成熟 |

### 1.4 架构变更历史

| 问题 | 发现时间 | 修复方案 | 修复版本 |
|------|---------|---------|---------|
| Python 试图建模 LLM 判断逻辑 | 2026-04-16 | 用 pdca.py 单文件替代 modules/ + core/ | v2.0.0 |
| c() 未校验 ADAS 规则 | 2026-04-16 | 在 c() 中增加 L0/L1 拒 pending + L3 首次必须 pending | v2.1.0 |
| p() 实现与文档冲突 | 2026-04-16 | 重写 p() cycle 创建逻辑 | v2.0.0 |
| Step 0 缺少 pdca.py c 调用 | 2026-04-16 | Harold 回复后先 c() 再 Act | v2.1.0 |
| Heartbeat Step 0 缺少 Harold 回复分支 | 2026-04-16 | 三分支结构（有回复/超时/等待中） | v2.1.0 |
| Act 阶段硬编码 LL/DL 触发 | 2026-04-16 | 移除，属 governance-knowledge 关注点 | v2.2.0 |

---

## 二、Phase 2 升级方案（Week 8-14）

### 2.1 pdca.py 差距修复

**目标**：补齐 Phase 1 到 Phase 2 的差距。

| # | 内容 | 改动 |
|---|------|------|
| 1 | escalation 集成：heartbeat 消费 needs_escalation 信号 | nucleus SKILL.md Step 1 增加 "consecutive_fails≥3 → 上报 Harold" |
| 2 | 无 [P] 任务时系统健康检查（REQ-DISPATCH-003） | nucleus SKILL.md Step 1 增加 "无 [P] → 健康检查 → verdict=skip" |
| 3 | 向后兼容验证（REQ-NF-007） | 测试：现有 pdca/*.yaml 能否被 pdca.py 正确读取 |

### 2.2 轻量级层间传播

**目标**：task verdict 自动聚合到 topic/project 级。

**方案**：pdca.py 新增 `aggregate(scope, scope_id)` 函数。

```python
def aggregate(scope: str, scope_id: str) -> Dict:
    """扫描子项 pdca/*.yaml，聚合 verdict 到父级"""
```

**聚合规则**：

| 子项组合 | 父项 verdict |
|---------|-------------|
| 全部 pass | pass |
| 任一 fail | fail |
| 部分 pass + 部分 partial | partial |
| 全部 skip | skip |
| 混合 | partial |

**存储**：topic/project 级也有 pdca/*.yaml，但不由 LLM 填写，由 aggregate() 自动派生。

**触发**：a() 完成后自动调用聚合（scope=task 完成后聚合到 topic）。

### 2.3 并发上限约束

**目标**：REQ-NF-009 并发上限。

**方案**：pdca.py 新增 `check_concurrency(scope)` 函数。

| Scope | 上限 | 说明 |
|-------|------|------|
| task | ≤10 | 单 topic 下活跃 task 数 |
| topic | ≤5 | 单 project 下活跃 topic 数 |
| project | ≤3 | 全局活跃 project 数 |

**校验**：p() 调用前执行，扫描 pdca/*.yaml 统计各 scope 下 phase != completed 的数量。

**超限**：返回 `{ok: false, error: '{scope} 并发上限 {N}，当前活跃 {M}，请等待完成'}`。

### 2.4 多粒度调度

**目标**：UPGRADE §2.2 多粒度调度。

**方案**：持久化计数器 `config/scheduler_state.yaml` + 轻量 `scripts/scheduler_state.py`。

| Scope | 触发频率 | 对应 Heartbeat 数 |
|-------|---------|------------------|
| task | 每 30 分钟 | 1 |
| topic | 每 2 小时 | 4 |
| project | 每 1 天 | 48 |
| system | 每 1 周 | 336 |

**实现**：heartbeat 中读取计数器，判断 scope 是否达到阈值。

### 2.5 知识沉淀

**目标**：REQ-KNOWLEDGE-001 + REQ-KNOWLEDGE-004。

**方案**：`knowledge/lessons/` 目录，每份 lesson 一个 .md 文件。

| 约束 | 说明 |
|------|------|
| Phase 2 笔记上限 | ≤500 |
| Plan C 触发 | ≥5000 |
| 老化机制 | 每周清理孤立笔记（无反向链接） |
| 存储格式 | 纯 .md 文件，不依赖 Obsidian 外部工具 |

**触发**：LLM 在 a() 时传入 lessons，nucleus SKILL.md 指导 LLM 沉淀到 knowledge/。

---

## 三、Phase 3 升级方案（Week 15-21）

### 3.1 系统级自进化环

**目标**：System 级别的 PDCA 自动执行，无需人工干预。

**能力**：
- 预测性监控：基于历史 logs/executions 识别趋势
- 自主决策：在操作白名单内自动调整配置
- 自适应执行：动态调整 heartbeat 频率、并发上限

**安全边界**：
```yaml
# config/act-whitelist.yaml
allowed_operations:
  - type: "config_update"
    scope: "skill_parameters"
    max_change_ratio: 0.2
  - type: "task_retry"
    scope: "failed_tasks"
    max_retries: 3

blocked_operations:
  - "file_delete"
  - "skill_disable"
  - "config_schema_change"
```

### 3.2 预测性监控

**输入源**：
- `logs/YYYY-MM-DD.jsonl`：观测日志
- `executions/YYYY-MM-DD.jsonl`：执行日志
- `pdca/*.yaml`：PDCA 历史

**检测能力**：
- 异常模式识别（连续 fail 趋势）
- 性能退化（heartbeat 延迟增长）
- 资源耗尽预警（pdca 目录文件数增长）

---

## 四、技能模块升级计划

### 4.1 优先级矩阵

| Skill | Phase 2 升级内容 | Phase 3 升级内容 | 优先级 |
|-------|-----------------|-----------------|--------|
| **governance-nucleus** | aggregate() + check_concurrency() + SKILL.md 差距修复 | System 级 PDCA | P0 |
| **governance-heartbeat** | 多粒度调度器 + scheduler_state.yaml 集成 | 动态频率调整 | P0 |
| **governance-knowledge** | knowledge/lessons/ 目录 + 老化机制 | 在线学习 + 知识更新 | P1 |
| **governance-delegation** | escalation 消费 | 自主决策白名单 | P0 |
| **governance-task** | 多粒度 Task-CARD | 自动任务创建 | P1 |
| **governance-quality** | 审计出口完整流程 | 质量趋势预测 | P2 |

### 4.2 升级顺序

```
Week 8-9:    pdca.py 差距修复 + aggregate() + check_concurrency()
Week 10-11:  scheduler_state.py + 多粒度调度集成
Week 12-13:  knowledge/lessons/ + 审计出口完整流程
Week 14:     集成测试 + Phase 2 验收
---
Week 15-16:  governance-delegation 自主决策
Week 17-18:  governance-nucleus System 级 PDCA
Week 19-20:  预测性监控 + 自适应执行
Week 21:     集成测试 + Phase 3 验收
```

---

## 五、风险与缓解

### 5.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| aggregate() 聚合边界不清 | 中 | 低 | 先实现 Task→Topic 两层，验证后再扩展 |
| 并发校验误判 | 高 | 低 | 单元测试覆盖所有边界条件 |
| scheduler_state 并发写入 | 中 | 低 | 原子写入 + heartbeat 单线程保证 |
| 文件 I/O 性能瓶颈 | 中 | 低 | 单文件存储 + 批量写入 + 增量检查 |

### 5.2 业务风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| Harold 审批延迟导致 PDCA 停滞 | 中 | 高 | L3 超时升级机制已实现 |
| DL 条目置信度下降过快 | 中 | 中 | 审计阈值 80 分留有 20 分缓冲 |
| Agent 间职责重叠 | 低 | 低 | SKILL.md Activate 条件明确职责边界 |

---

## 六、里程碑

| 里程碑 | 计划日期 | 交付物 | 状态 |
|--------|----------|--------|------|
| **M0: Phase 0 完成** | 2026-04-05 | T0.1/T0.2 签字确认 | ✅ 已完成 |
| **M1: Phase 1 完成** | 2026-04-06 | pdca.py v2.2.0 + SKILL.md v2.5.0 + 99 测试通过 | ✅ 已完成 |
| **M2: 文档完整** | 2026-04-18 | REQ-SPEC + ARCH + DESIGN + UPGRADE 四文档 v2.0 | 🟡 进行中 |
| **M3: Phase 2 完成** | 2026-07-11 | aggregate() + scheduler_state.py + knowledge/lessons/ | ⏸️ 待开始 |
| **M4: Phase 3 完成** | 2026-08-29 | 系统级自进化环 + 自主决策 + 预测性监控 | ⏸️ 待开始 |

---

## 七、验收标准更新

### 7.1 Phase 2 验收

| 指标 | 目标值 | 验证方式 |
|------|--------|---------|
| aggregate() 聚合准确率 | ≥95% | 集成测试（四层嵌套验证） |
| check_concurrency() 准确率 | 100% | 单元测试（所有边界条件） |
| 多粒度调度准确率 | ≥99% | scheduler_state.yaml 计数器验证 |
| 知识笔记数 | ≤500 | knowledge/lessons/ 统计 |
| 文档完整性 | REQ/ARCH/DESIGN/UPGRADE 四文档 v2.0 | 人工审查 |

### 7.2 Phase 3 验收

| 指标 | 目标值 | 验证方式 |
|------|--------|---------|
| 自动化率 | ≥90% | Heartbeat/Task 比例 ≤1.1:1 |
| 自主决策准确率 | ≥90% | 操作审计日志验证 |
| 预测性监控准确率 | ≥80% | 异常检测 vs 实际异常对比 |
| 响应时间 | ≤30s | 压力测试 |

---

*版本：v2.0 | 创建日期：2026-04-16 | 修订日期：2026-04-18 | PM：张铁 | PMO：银月*
