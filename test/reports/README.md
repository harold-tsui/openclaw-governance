# NUCLEUS 4.0 Test Reports

> **目录用途**: 存放 pdca.py 及 nucleus 组件的测试报告
> **维护人**: CQO (张铁) / 开发人
> **存放路径**: `10_Projects/ZT-P015_NUCLEUS-4-0/test_reports/`

---

## 目录结构

```
test_reports/
├── README.md                    ← 本文件（测试流程说明）
├── TEMPLATE.md                  ← 测试报告模板（复制后填写）
├── CQO-TEST-REPORT-2026-04-18.md ← 首次 CQO 测试报告
├── REVIEW-2026-04-18.md         ← 开发人复核报告
└── fixtures/                    ← 测试用 YAML fixture 文件
```

## 执行日志

pdca.py 每次 CLI 调用会自动记录 JSON line 到 `skills/openclaw-governance/skills/openclaw-governance-nucleus/logs/pdca.log`。

每条日志包含：
- `ts`: ISO 时间戳
- `cwd`: 调用时的原始工作目录（排查路径问题关键）
- `cmd`: 命令（p/d/c/a/status/history/pending/aggregate/...）
- `task_card_id`: 任务 ID
- `ok`: 成功/失败
- `error`: 错误信息（失败时）
- `verdict`: 结论（pass/fail/partial/pending/skip）
- `new_phase`: 执行后 phase
- `status`: 执行状态（do 阶段）

**排查 bug 时用**：
```bash
# 查看最近 10 条调用
tail -10 skills/.../governance-nucleus/logs/pdca.log | python3 -m json.tool

# 查看失败的调用
grep '"ok": false' skills/.../governance-nucleus/logs/pdca.log

# 查看某个 task 的完整调用历史
grep 'TASK-ID' skills/.../governance-nucleus/logs/pdca.log
```

## 测试流程

### 1. 准备

```bash
# 确保在 nucleus skill 根目录执行
cd skills/openclaw-governance/skills/openclaw-governance-nucleus
```

### 2. 单阶段测试

```bash
# Plan
python3 scripts/pdca.py p --task-card-id {TEST_ID} --summary "测试计划"

# Do
python3 scripts/pdca.py d --task-card-id {TEST_ID} --summary "测试执行" --status completed

# Check
python3 scripts/pdca.py c --task-card-id {TEST_ID} --verdict pass --level L1

# Act
python3 scripts/pdca.py a --task-card-id {TEST_ID} --summary "测试完成" --task-state "[x]"
```

### 3. 验证

```bash
# 查看状态
python3 scripts/pdca.py status --task-card-id {TEST_ID}

# 查看完整历史
python3 scripts/pdca.py history --task-card-id {TEST_ID}

# 查看原始 YAML
cat pdca/{TEST_ID}.yaml
```

### 4. 清理

```bash
rm -f pdca/{TEST_ID}.yaml
```

### 5. 报告

1. 复制 `TEMPLATE.md` 为 `CQO-TEST-REPORT-YYYY-MM-DD.md`
2. 填写测试结果
3. 放入 `test_reports/` 目录

## 测试覆盖要求

| 测试场景 | 覆盖内容 |
|---------|---------|
| **完整 PDCA** | P→D→C→A 全流程，验证每个阶段数据正确写入 |
| **Phase 锁定** | 验证跳步被拒绝：d() 无 p()、c() 无 d()、a() 无 c() |
| **幂等性** | 同一 cycle 内重复 c() 被拒绝 |
| **并发控制** | check_concurrency() 上限校验 |
| **层间传播** | aggregate() 正确聚合到 topic/project 级 |
| **多 CWD** | 从不同工作目录执行 pdca.py，验证路径正确 |
| **Guardrail 防护** | 4 项状态机防护全部生效 |

## 注意事项

- **必须在 nucleus skill 根目录下执行**：`pdca.py` 内部使用 `_setup()` 切换 CWD，但测试时请确保命令从正确位置调用
- **使用唯一 TEST_ID**：避免与已有测试文件冲突
- **测试后清理**：删除 `pdca/{TEST_ID}.yaml` 文件
- **不要在 agent workspace 下执行 pdca.py**：曾在 `60_Agents/cqo/pdca/` 发现残留测试文件（已于 2026-04-18 清理）

---

*创建：2026-04-18 | 维护：CQO / 开发人*
