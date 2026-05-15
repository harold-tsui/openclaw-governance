# CQO 测试报告 · NUCLEUS 4.0

> **测试日期**：YYYY-MM-DD
> **测试人**：姓名 (Agent ID)
> **测试范围**：测试的组件和功能
> **测试结论**：✅ 全部通过 / ❌ 发现 N 个 bug

---

## 一、测试环境

| 项目 | 信息 |
|------|------|
| **测试 Agent** | agent_id (name) |
| **测试目录** | 执行测试时的 CWD |
| **Python 版本** | python3 |
| **测试方法** | CLI 命令调用 / 脚本 |

---

## 二、测试结果

### 2.1 完整 PDCA 流程

| 步骤 | 命令 | 预期 | 实际 | 状态 |
|------|------|------|------|------|
| **P** | `pdca.py p --task-card-id TEST-XXX --summary "测试"` | phase=plan | — | ⬜ |
| **D** | `pdca.py d --task-card-id TEST-XXX --summary "执行" --status completed` | phase=do | — | ⬜ |
| **C** | `pdca.py c --task-card-id TEST-XXX --verdict pass --level L1` | phase=act, verdict=pass | — | ⬜ |
| **A** | `pdca.py a --task-card-id TEST-XXX --summary "完成" --task-state "[x]"` | phase=completed | — | ⬜ |

### 2.2 Guardrail 防护测试

| 测试项 | 操作 | 预期结果 | 实际结果 | 状态 |
|--------|------|---------|---------|------|
| d() 无 p() | 直接调用 d() | error: "Do 阶段不能在没有 Plan 的情况下调用" | — | ⬜ |
| c() 无 d() | p() → c() | error: 取决于 phase | — | ⬜ |
| a() 无 c() | p() → a() | error: "Act 阶段不能在没有 PDCA 历史的情况下调用" | — | ⬜ |
| c() 幂等性 | c() pass → c() fail | warning: 不可静默覆盖 | — | ⬜ |
| aggregate 陈旧过滤 | cycle 2 进行中时聚合 | 只聚合 completed cycle | — | ⬜ |

### 2.3 多 CWD 测试

| CWD | 结果 | 状态 |
|-----|------|------|
| nucleus skill root | — | ⬜ |
| / (根目录) | — | ⬜ |
| agent workspace | — | ⬜ |

---

## 三、Bug 详情（如无 bug 则写"无"）

### Bug #N：简要描述

**错误信息**：
```
（粘贴错误堆栈）
```

**根因分析**：
（分析原因）

**修复建议**：
（建议的修复方案）

---

## 四、测试结论

| 组件 | 状态 | Bug 数量 |
|------|------|---------|
| pdca.py | ✅ / ❌ | N |
| scheduler_state.py | ✅ / ❌ | N |

---

*报告人：姓名 (Agent ID)*
*报告日期：YYYY-MM-DD*
