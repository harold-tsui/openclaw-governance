# OpenClaw Governance Skill 测试报告

**测试日期**: 2026-05-18
**测试者**: 冰凤 (掌天智能团队 Agent)
**项目**: harold-tsui/openclaw-governance
**测试目标**: 以陌生 Agent 身份初始化并使用 openclaw-governance skill，发现 Bug 并评估 MVP 可用性

---

## 一、测试环境

- **OS**: Ubuntu 24.04 (Linux 6.8.0)
- **Python**: 3.12.3
- **测试路径**: `/data/claude/openclaw-governance`
- **Skill 版本**: v3.2.0 (主 SKILL.md) / v4.1.0 (governance-nucleus)

---

## 二、测试过程

### 2.1 项目克隆与构建

```bash
cd /data/claude && gh repo clone harold-tsui/openclaw-governance
cd openclaw-governance && ./scripts/build-skill.sh
```

✅ **构建成功** — 4 个 Python 文件正确同步到 build 目录

### 2.2 安装测试

```bash
./scripts/install-skill.sh
```

✅ **安装成功** — skill 包正确复制到目标目录，health-check 返回 healthy

### 2.3 单元测试

```bash
cd build/openclaw-governance/skills/openclaw-governance-nucleus
pytest tests/ -v
```

✅ **174/174 测试全部通过** (6.72s)
- test_pdca.py: 29 passed
- test_pdca_extended.py: 21 passed
- test_pdca_coverage.py: passed
- test_cqo_integration.py: passed
- test_scheduler_state.py: passed
- test_security_and_features.py: passed

**覆盖率**: pdca.py 77%, scheduler_state.py 77%, dashboard.py 0%, migrate_legacy.py 0%

### 2.4 完整 PDCA Cycle 手动测试

测试了完整的 Plan → Do → CQO Review → Check → Act 流程：

✅ 所有阶段正常推进
✅ aggregate 层级传播正确（task → topic → project）
✅ 并发控制正常工作（task 上限 10）
✅ 安全校验有效（路径遍历、非法字符均被阻止）

---

## 三、发现的 Bug

### 🐛 Bug #1: Race Condition 并发写入崩溃 **[严重]**

**现象**: 当两个进程同时写入同一个 PDCA 文件时，触发 `FileNotFoundError`

```
FileNotFoundError: [Errno 2] No such file or directory:
  '.../pdca/RACE.yaml.tmp'
```

**复现步骤**:
```bash
python3 scripts/pdca.py p --task-card-id RACE --summary "Race test"
python3 scripts/pdca.py d --task-card-id RACE --summary "Done" --status completed &
python3 scripts/pdca.py d --task-card-id RACE --summary "Done2" --status completed &
```

**根因**: `_save()` 函数使用固定的 `.tmp` 后缀：
```python
tmp = path + '.tmp'
# 并发时两个进程使用同一个 tmp 文件名，一个进程的 os.replace()
# 会在另一个进程读取文件大小时导致 FileNotFoundError
```

**影响**: 高并发场景（如 heartbeat 同时触发多个任务）可能导致数据丢失或崩溃

**修复建议**: 使用 `tempfile.mkstemp()` 或 UUID 生成唯一临时文件名

---

### 🐛 Bug #2: 多 Cycle 流程文档不清晰 **[中]**

**现象**: 当 check 返回 fail 后，新用户（如我）误以为可以直接继续 `d` 开始下一轮，实际上需要：
1. 先调用 `a` 完成当前 cycle
2. 再调用 `p` 开启新 cycle

**复现步骤**:
```bash
python3 scripts/pdca.py p --task-card-id T --summary "Test"
python3 scripts/pdca.py d --task-card-id T --summary "Done" --status completed
python3 scripts/pdca.py cqo-review --task-card-id T --result pass
python3 scripts/pdca.py c --task-card-id T --verdict fail --level L1
# 用户以为可以直接继续：
python3 scripts/pdca.py d --task-card-id T --summary "Retry" --status completed
# 结果: "Do 不能在 phase='act' 时调用"
```

**根因**: 文档未明确说明多 cycle 的正确流程

**修复建议**:
1. 在 `p()` 返回的错误信息中增加提示："当前 cycle 已完成/进行中，如需新 cycle 请先执行 pdca.py a，再执行 pdca.py p"
2. 在 README/CLAUDE.md 中增加 "多 Cycle 工作流" 章节

---

### 🐛 Bug #3: 缺少 `pdca_config.yaml` 示例 **[低]**

**现象**: 代码支持从 `config/pdca_config.yaml` 加载配置，但项目中没有提供示例文件

**影响**: 用户不知道有哪些可配置项，全部使用硬编码默认值

**修复建议**: 在 `src/config/` 或项目根目录 `config/` 中添加 `pdca_config.yaml.example`：

```yaml
adas:
  levels_self_approve: ['L0', 'L1']
  level_full_human: 'L3'
concurrency:
  task: 10
  topic: 5
  project: 3
audit:
  score_threshold: 80
pending_timeout:
  warning_days: 7
  critical_days: 14
weighted_aggregate:
  pass_threshold: 0.80
  fail_threshold: 0.20
limits:
  max_yaml_size_kb: 1024
  archive_older_than_days: 30
  max_pdca_files: 500
  max_cycles_per_task: 20
```

---

## 四、改进建议（第二优先级）

### ⚠️ 建议 #1: 增强错误提示的引导性

当前错误信息:
```
"Do 不能在 phase='act' 时调用。当前应在 plan 或 do 阶段"
```

建议改进为:
```
"Do 不能在 phase='act' 时调用。当前 cycle 状态为 'act'，请执行以下操作之一：
  1. 完成当前 cycle: pdca.py a --task-card-id {id} --summary '...'
  2. 如需新 cycle: 先执行 a，再执行 p"
```

### ⚠️ 建议 #2: 增加 Quick Start 引导

作为陌生 Agent，我花了不少时间理解：
1. 应该先 build 还是直接 install？
2. runtime/ 目录需要手动创建吗？
3. 第一步该调用什么命令？

建议在 README.md 顶部增加:
```markdown
## 🚀 Quick Start

```bash
# 1. 构建
./scripts/build-skill.sh

# 2. 安装
./scripts/install-skill.sh

# 3. 验证
python3 scripts/pdca.py health-check

# 4. 第一个 PDCA cycle
python3 scripts/pdca.py p --task-card-id T1 --summary "My first task"
python3 scripts/pdca.py d --task-card-id T1 --summary "Done" --status completed
python3 scripts/pdca.py cqo-review --task-card-id T1 --result pass
python3 scripts/pdca.py c --task-card-id T1 --verdict pass --level L1
python3 scripts/pdca.py a --task-card-id T1 --summary "Completed"
```
```

### ⚠️ 建议 #3: dashboard.py 和 migrate_legacy.py 增加测试

当前覆盖率:
- dashboard.py: 0%
- migrate_legacy.py: 0%

建议至少增加基础功能测试，确保 import 和主要函数不会崩溃。

### ⚠️ 建议 #4: `build-skill.sh` 同步 config 目录

项目根目录 `config/` 中的 `business_hours.yaml`、`escalation_policy.yaml`、`state_sync_rules.yaml` 未被同步到 build 目录。如果这些是 governance-nucleus 的依赖配置，需要在 build 脚本中处理。

---

## 五、总体评价

### 作为陌生 Agent 的初体验

| 维度 | 评分 | 说明 |
|------|------|------|
| **构建流程** | ⭐⭐⭐⭐⭐ | build/install 脚本清晰，一步完成 |
| **测试覆盖** | ⭐⭐⭐⭐ | 174 测试全过，但 dashboard/migrate 0% 覆盖 |
| **文档完整度** | ⭐⭐⭐ | 架构文档详尽，但缺少 Quick Start 和多 cycle 流程说明 |
| **错误处理** | ⭐⭐⭐⭐ | 边界校验完善，但错误提示可以更有引导性 |
| **并发安全** | ⭐⭐ | 存在 Race Condition，高并发可能崩溃 |
| **MVP 可用性** | ⭐⭐⭐⭐ | 核心 PDCA 流程稳定可用，小团队可放心使用 |

### 结论

**OpenClaw Governance Skill 的 MVP 核心功能（PDCA cycle）已经跑通**，代码质量较高，安全校验到位。

**当前最需要修复的是 Bug #1（Race Condition）**，这是唯一可能导致数据损坏的严重问题。

**Bug #2 和 Bug #3 是文档/体验问题**，修复成本低但能显著提升新用户上手体验。

---

*报告生成: 2026-05-18 | 测试者: 冰凤 | 状态: 待团队评审*
