# 失败传播矩阵详细文档

> **来源**：SKILL.md §四 失败处理行为规范分离
> **版本**：v1.0 (2026-04-22)

---

## 目录

1. [单点失败处理](#单点失败处理)
2. [组合失败传播矩阵](#组合失败传播矩阵)
3. [组合失败决策树](#组合失败决策树)
4. [级联降级雪崩检测](#级联降级雪崩检测)
5. [相关资源](#相关资源)

---

## 单点失败处理

| 失败节点 | 影响范围 | 降级策略 | 是否阻止 Phase 3 | 软降级检测 |
|----------|----------|----------|------------------|------------|
| **core** | 全部不可用 | 终止启动（致命） | ✅ 是 | - |
| **config** | 依赖 config 的模块 | 降级到内置 defaults，记录警告 | ❌ 否 | 配置文件可读性检查 |
| **dispatch** | 意图路由不可用 | 终止启动（无法路由） | ✅ 是 | - |
| **hierarchy** | task/delegation/heartbeat | 严重降级，记录错误 | ✅ 是 | Project 树配置文件完整性 |
| **data** | quality/task | 中度降级，只读模式 | ❌ 否（带警告） | 数据分级文件可读性 |
| **quality** | task 闭环 | 轻度降级，带警告继续 | ❌ 否 | DOD 模板完整性 |
| **delegation** | task 权限验证 | 阻止 task 加载（安全风险） | ✅ 是 | 授权规则文件完整性 |
| **task** | heartbeat | heartbeat 不加载 | - | - |
| **heartbeat** | 全局巡检 | 巡检中断，各 Agent 切换独立模式 | ❌ 否 | 定时器注册状态检查 |
| **knowledge** | 知识沉淀/DL 更新 | 知识沉淀延迟，不影响主流程 | ❌ 否 | DL 文件完整性检查 |
| **nucleus** | PDCA 执行引擎 | PDCA 暂停，不影响主流程 | ❌ 否 | heartbeat 触发检查 |

---

## 组合失败传播矩阵

### 触发条件矩阵

| 失败组合 | 触发条件 | 处理策略 | 阻塞 Phase 3 |
|----------|----------|----------|-------------|
| quality + delegation | `delegation.status == failed` | delegation 优先 | ✅ 是 |
| hierarchy + data | `hierarchy.status == failed` | hierarchy 优先 | ✅ 是 |
| config + data | `config.status == failed` | defaults + 只读模式 | ❌ 否 |
| quality + data | `data.status == degraded` | data 优先传播 | ❌ 否（带警告） |
| hierarchy + delegation | `hierarchy.status == failed` | hierarchy 优先 | ✅ 是 |
| config + dispatch | `dispatch.status == failed` | Phase 1 TERMINATE | N/A（系统已终止） |

---

## 组合失败决策树

> **Python 实现路径**：[scripts/decision_tree.py]({baseDir}/scripts/decision_tree.py)

```python
def handle_combined_failure(failed_modules: list[str]) -> Decision:
    """组合失败处理决策树"""
    
    # Rule 1: 安全优先
    if "delegation" in failed_modules:
        return Decision(
            action="BLOCK_PHASE_3",
            reason="delegation 失败影响权限验证",
            severity="CRITICAL"
        )
    
    # Rule 2: 架构优先
    if "hierarchy" in failed_modules:
        return Decision(
            action="BLOCK_PHASE_3",
            reason="hierarchy 失败影响 Project 树",
            severity="HIGH"
        )
    
    # Rule 3: 数据传播
    if "data" in failed_modules and "quality" in failed_modules:
        return Decision(
            action="DEGRADE_BOTH",
            reason="data 降级传播到 quality",
            severity="MEDIUM",
            impact=["只读模式", "闭环不可用"]
        )
    
    # Rule 4: 独立降级
    if "config" in failed_modules:
        return Decision(
            action="USE_DEFAULTS",
            reason="config 失败使用内置默认值",
            severity="LOW"
        )
    
    return Decision(action="CONTINUE", reason="无阻塞条件")
```

---

## 级联降级雪崩检测

```python
def detect_cascade_snowball(degraded_modules: list[str]) -> bool:
    """检测级联降级是否超过阈值"""
    DEGRADATION_THRESHOLD = 0.4  # 40% 模块降级
    total_modules = 8  # Phase 2A+2B+3+L3 有效模块数
    
    if len(degraded_modules) / total_modules > DEGRADATION_THRESHOLD:
        return True  # 触发雪崩保护（>=3 个模块降级）
    return False
```

---

## 相关资源

- [SKILL.md]({baseDir}/SKILL.md) - 核心运行机制
- [barrier-design.md]({baseDir}/references/barrier-design.md) - 屏障设计详细
- [scripts/decision_tree.py]({baseDir}/scripts/decision_tree.py) - 决策树实现