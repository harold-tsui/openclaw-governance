# Phase 屏障设计详细文档

> **来源**：SKILL.md §三 Phase 屏障规则分离
> **版本**：v1.0 (2026-04-22)

---

## 目录

1. [设计理念](#设计理念)
2. [屏障类型定义](#屏障类型定义)
3. [状态锁定机制](#状态锁定机制)
4. [屏障执行流程](#屏障执行流程)
5. [降级状态传播规则](#降级状态传播规则)
6. [就绪探针机制](#就绪探针机制)
7. [相关资源](#相关资源)

---

## 设计理念

### 核心定义

> **"完成" ≠ "成功"**，降级状态也是一种"完成"

| 模块状态 | 定义 | 是否算"完成" | 是否可进入下一 Phase |
|----------|------|---------------|----------------------|
| **success** | 模块正常加载，所有功能可用 | ✅ 是 | ✅ 可 |
| **degraded** | 模块降级加载，部分功能受限 | ✅ 是 | ✅ 可（带警告） |
| **failed** | 模块加载失败，不可用 | ✅ 是（但触发阻塞检查） | ❌ 视阻塞条件而定 |
| **loading** | 模块正在加载 | ❌ 否 | ❌ 必须等待 |

### 降级容忍度上限

| Phase | 最大降级模块数 | 阻塞条件 |
|-------|---------------|----------|
| Phase 1 | 0 | 任一降级 → 终止（致命） |
| Phase 2A | 1 | hierarchy 降级 → 阻塞 Phase 2B |
| Phase 2B | 1 | delegation 降级 → 阻塞 Phase 3 |
| Phase 3 | 2 | task + heartbeat 降级 → 警告继续 |

---

## 屏障类型定义

| 屏障 | 类型 | 触发条件 | 强制行为 |
|------|------|----------|----------|
| **Phase 1→2A** | 硬屏障 | 所有 Phase 1 模块完成（含降级） | 必须等待，不可跳过 |
| **Phase 2A→2B** | 硬屏障 + 状态广播 | 所有 2A 模块完成 + 广播健康快照 | 2B 必须读取快照后初始化 |
| **Phase 2B→3** | 条件屏障 | hierarchy/delegation 非 failed | 阻塞条件满足时终止 Phase 3 |
| **Phase 3→4** | 软屏障 | Phase 3 完成 | Phase 4 惰性加载，不影响主流程 |

---

## 状态锁定机制

### PhaseBarrierLock 实现

> **Python 实现路径**：[scripts/barrier_lock.py]({baseDir}/scripts/barrier_lock.py)

**核心功能**：
- 锁定状态快照，Phase 执行期间状态冻结
- 上下文管理器，确保异常退出时锁释放
- 状态快照获取（锁定时返回快照值，未锁定返回实时状态）

**使用示例**：
```python
with PhaseBarrierLock() as barrier:
    barrier.lock_snapshot(current_module_states)
    execute_phase()  # Phase 执行过程中使用快照状态
    # 离开 with 块时自动 unlock，异常也不例外
```

---

## 屏障执行流程

```
屏障检查时：
    ↓
1. 检查所有模块当前状态
    ↓
2. 锁定状态快照（Phase 执行期间冻结）
    ↓
3. Phase 开始执行（使用快照状态）
    ↓
4. 模块异步探针更新 → 写入内存 pending_updates 字典
    ↓
5. Phase 完成后释放锁
    ↓
6. 下一屏障检查时，pending_updates 合并到状态快照
```

**pending_updates 结构**（内存字典，不持久化）：
```python
{
    "module_name": "new_status",  # e.g., {"quality": "failed"}
    ...
}
```
- 写入时机：模块探针检测到状态变化时
- 生效时机：下一屏障检查时合并
- 清理时机：合并后立即清空

---

## 降级状态传播规则

```
模块 A 降级 → 检查下游依赖
    ↓
if 下游模块 B 依赖 A 的降级功能:
    B 也降级（传播）
elif 下游模块 B 不依赖 A 的降级功能:
    B 正常加载（不传播）
```

**示例**：
- data 降级 → quality 降级（quality 依赖 data 的分级检查）
- data 降级 → task 正常（task 不依赖 data 的核心功能）

---

## 就绪探针机制

### 探针角色定义

| 角色 | 阻塞行为 | 失败处理 | 示例 |
|------|----------|----------|------|
| **阻塞型** | 阻止 Phase 进入 | 记录错误，终止 | core 路径变量 |
| **咨询型** | 不阻塞，记录警告 | 降级继续 | config 文件语法 |
| **可选型** | 不阻塞，静默记录 | 忽略 | evolution 增强功能 |

### 咨询型探针升级机制

```yaml
advisory_probe_upgrade:
  escalate_after_failures: 5
  escalate_to: blocking
  cooldown_period: 300s
```

> **计数器持久化**：`.system/governance/current/probe-failures.yaml`

---

## 相关资源

- [SKILL.md]({baseDir}/SKILL.md) - 核心运行机制
- [failure-matrix.md]({baseDir}/references/failure-matrix.md) - 失败传播矩阵
- [phase-sequence.md]({baseDir}/references/phase-sequence.md) - Phase 序列详细
- [scripts/barrier_lock.py]({baseDir}/scripts/barrier_lock.py) - Python 实现