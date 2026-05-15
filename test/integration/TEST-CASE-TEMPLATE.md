# 集成测试用例设计

> **用途**: NUCLEUS 4.0 集成测试用例模板
> **覆盖范围**: PDCA核心功能、Claude Code协同、跨Agent测试

---

## 一、集成测试用例列表

### 测试套件 A：PDCA核心流程（7个）

| 用例ID | 名称 | 目的 | 验证点 |
|--------|------|------|--------|
| **TC-INT-001** | 完整PDCA流程 | P→D→C→A四阶段顺序执行 | YAML状态正确、phase顺序正确 |
| **TC-INT-002** | Phase锁定-P跳步 | 无p()直接调用d() | 被拒绝，错误码E_PHASE_LOCK |
| **TC-INT-003** | Phase锁定-D跳步 | 无d()直接调用c() | 被拒绝，错误码E_PHASE_LOCK |
| **TC-INT-004** | Phase锁定-C跳步 | 无c()直接调用a() | 被拒绝，错误码E_PHASE_LOCK |
| **TC-INT-005** | 幂等性-重复c() | 同一cycle内重复调用c() | 第二次被拒绝，错误码E_IDEMPOTENT |
| **TC-INT-006** | 多CWD测试 | 从不同工作目录执行pdca.py | 路径正确，YAML写入正确位置 |
| **TC-INT-007** | 连续PDCA迭代 | 同一任务执行3轮PDCA | cycle计数正确、历史完整 |

---

### 测试套件 B：并发与传播（3个）

| 用例ID | 名称 | 目的 | 验证点 |
|--------|------|------|--------|
| **TC-INT-008** | 并发上限-Task级 | 同时启动11个Task级PDCA | 第11个被拒绝，错误码E_CONCURRENCY |
| **TC-INT-009** | 并发上限-Topic级 | 同时启动6个Topic级聚合 | 第6个被拒绝 |
| **TC-INT-010** | 层间传播 | 完成Task→触发Topic聚合 | aggregate()正确计算父级verdict |

---

### 测试套件 C：Claude Code协同（2个）

| 用例ID | 名称 | 目的 | 验证点 |
|--------|------|------|--------|
| **TC-INT-011** | ACP session绑定 | 通过sessions_spawn启动Claude Code | thread绑定、测试执行、结果返回 |
| **TC-INT-012** | 跨Agent测试 | CIO调用测试框架验证pdca.py | 接口清晰、执行成功、报告生成 |

---

### 测试套件 D：Guardrail防护（4个）

| 用例ID | 名称 | 目的 | 验证点 |
|--------|------|------|--------|
| **TC-INT-013** | Guardrail-P1 | Plan summary缺少差异说明 | 被拒绝 |
| **TC-INT-014** | Guardrail-D1 | Do summary是虚操作 | 被拒绝 |
| **TC-INT-015** | Guardrail-C1 | Check verdict=fail但缺少evidence | 被拒绝 |
| **TC-INT-016** | Guardrail-A1 | Act summary缺少下次输入 | 被拒绝 |

---

## 二、测试用例详细设计

### TC-INT-001：完整PDCA流程 ⭐

**前置条件**：
- nucleus skill根目录：`skills/openclaw-governance/skills/openclaw-governance-nucleus`
- 唯一TEST_ID：`TEST-INT-001-20260419`

**执行步骤**：

```bash
# Step 1: Plan
python3 scripts/pdca.py p \
  --task-card-id TEST-INT-001-20260419 \
  --summary "测试完整PDCA流程：依次执行P→D→C→A四阶段，验证每个阶段状态正确写入YAML"

# Step 2: Do
python3 scripts/pdca.py d \
  --task-card-id TEST-INT-001-20260419 \
  --summary "执行测试：调用status/history验证P阶段写入正确，准备进入C阶段" \
  --status completed

# Step 3: Check
python3 scripts/pdca.py c \
  --task-card-id TEST-INT-001-20260419 \
  --verdict pass \
  --level L1 \
  --evidence "✅ P阶段YAML写入正确；✅ D阶段状态为completed；✅ phase顺序正确"

# Step 4: Act
python3 scripts/pdca.py a \
  --task-card-id TEST-INT-001-20260419 \
  --summary "测试通过，验证完整PDCA流程可行。下次输入：测试Phase锁定机制" \
  --task-state "[x]"

# Step 5: 验证
python3 scripts/pdca.py status --task-card-id TEST-INT-001-20260419
python3 scripts/pdca.py history --task-card-id TEST-INT-001-20260419
cat pdca/TEST-INT-001-20260419.yaml

# Step 6: 清理
rm -f pdca/TEST-INT-001-20260419.yaml
```

**预期结果**：
- ✅ 每个阶段返回 `ok: true`
- ✅ YAML文件phase顺序：`plan → do → check → act`
- ✅ status显示：`cycle: 1, phase: act, verdict: pass`
- ✅ history包含4条记录

---

### TC-INT-002：Phase锁定-P跳步

**前置条件**：
- TEST_ID：`TEST-INT-002-20260419`

**执行步骤**：

```bash
# 直接调用d()，跳过p()
python3 scripts/pdca.py d \
  --task-card-id TEST-INT-002-20260419 \
  --summary "测试跳步" \
  --status completed

# 预期：被拒绝
```

**预期结果**：
- ❌ 返回 `ok: false`
- ❌ 错误码：`E_PHASE_LOCK`
- ❌ 错误信息：`"Do阶段需要先执行Plan阶段"`

---

### TC-INT-011：ACP session绑定（Claude Code协同）

**前置条件**：
- OpenClaw ACP配置正确
- 测试Task-CARD路径：`test/integration/TASK-CARD-ACP-TEST.md`

**执行步骤**：

```python
# 通过sessions_spawn启动Claude Code
{
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session",
  "task": "执行pdca.py集成测试：TC-INT-001完整PDCA流程",
  "cwd": "/Users/haroldtsui/Workspaces/openclaw/main/skills/openclaw-governance/skills/openclaw-governance-nucleus"
}
```

**预期结果**：
- ✅ Claude Code会话启动成功
- ✅ thread绑定正确
- ✅ 执行pdca.py命令成功
- ✅ 返回测试结果报告

---

### TC-INT-012：跨Agent测试（CIO调用测试框架）

**前置条件**：
- CIO Agent有测试权限
- 测试接口文档：`test/unit/AGENT-TEST-GUIDE.md`

**执行步骤**：

```bash
# CIO在自己的workspace调用测试框架
# 方式1：直接执行CLI
cd /Users/haroldtsui/Workspaces/openclaw/main/skills/openclaw-governance/skills/openclaw-governance-nucleus
python3 scripts/pdca.py status --task-card-id TEST-CIO-001

# 方式2：通过sessions_spawn
{
  "runtime": "subagent",
  "agentId": "cqo",
  "task": "执行pdca.py测试：验证CIO的情报收集Task的PDCA状态"
}
```

**预期结果**：
- ✅ CIO可调用测试框架
- ✅ 测试结果返回给CIO
- ✅ 测试报告生成到test_reports/

---

## 三、测试报告格式

### 集成测试报告模板

```markdown
# 集成测试报告 - {DATE}

> **测试套件**: {Suite ID}
> **执行人**: {Agent}
> **测试环境**: {cwd}
> **总体结果**: ✅ Pass / ❌ Fail

---

## 一、测试概览

| 用例ID | 名称 | 结果 | 错误码（如有） |
|--------|------|------|----------------|
| TC-INT-001 | 完整PDCA流程 | ✅ | - |
| TC-INT-002 | Phase锁定-P跳步 | ✅ | E_PHASE_LOCK |
| ... | ... | ... | ... |

---

## 二、详细结果

### TC-INT-001

**执行时间**: {timestamp}
**输入命令**: `{full_command}`
**实际输出**: `{output}`
**预期结果**: ✅ 四阶段顺序执行
**实际结果**: ✅ 符合预期
**YAML验证**: ✅ phase顺序正确

---

## 三、发现的问题

| 问题ID | 用例ID | 描述 | 严重程度 | 状态 |
|--------|--------|------|----------|------|
| - | - | 无 | - | - |

---

## 四、建议

1. {suggestion_1}
2. {suggestion_2}

---

*测试完成时间: {timestamp}*
```

---

## 四、测试自动化脚本（pytest集成）

```python
# test/integration/test_pdca_integration.py

import pytest
import subprocess
import os

class TestPDCAIntegration:
    """PDCA核心集成测试套件"""

    def setup_method(self):
        """每个测试前清理环境"""
        self.test_id = f"TEST-{self.__class__.__name__}-{pytest.__version__}"
        self.cwd = os.path.abspath(
            "skills/openclaw-governance/skills/openclaw-governance-nucleus"
        )

    def teardown_method(self):
        """每个测试后清理YAML"""
        yaml_path = f"{self.cwd}/pdca/{self.test_id}.yaml"
        if os.path.exists(yaml_path):
            os.remove(yaml_path)

    def test_tc_int_001_full_pdca_flow(self):
        """TC-INT-001: 完整PDCA流程"""
        # P阶段
        result_p = subprocess.run(
            ["python3", "scripts/pdca.py", "p",
             "--task-card-id", self.test_id,
             "--summary", "测试完整PDCA流程"],
            cwd=self.cwd, capture_output=True, text=True
        )
        assert result_p.returncode == 0

        # D阶段
        result_d = subprocess.run(
            ["python3", "scripts/pdca.py", "d",
             "--task-card-id", self.test_id,
             "--summary", "执行测试",
             "--status", "completed"],
            cwd=self.cwd, capture_output=True, text=True
        )
        assert result_d.returncode == 0

        # C阶段
        result_c = subprocess.run(
            ["python3", "scripts/pdca.py", "c",
             "--task-card-id", self.test_id,
             "--verdict", "pass",
             "--level", "L1"],
            cwd=self.cwd, capture_output=True, text=True
        )
        assert result_c.returncode == 0

        # A阶段
        result_a = subprocess.run(
            ["python3", "scripts/pdca.py", "a",
             "--task-card-id", self.test_id,
             "--summary", "测试完成",
             "--task-state", "[x]"],
            cwd=self.cwd, capture_output=True, text=True
        )
        assert result_a.returncode == 0

        # 验证YAML
        yaml_path = f"{self.cwd}/pdca/{self.test_id}.yaml"
        assert os.path.exists(yaml_path)

    def test_tc_int_002_phase_lock_skip_p(self):
        """TC-INT-002: Phase锁定-跳过P阶段"""
        result = subprocess.run(
            ["python3", "scripts/pdca.py", "d",
             "--task-card-id", self.test_id,
             "--summary", "测试跳步"],
            cwd=self.cwd, capture_output=True, text=True
        )
        # 预期：被拒绝
        assert result.returncode != 0
        assert "E_PHASE_LOCK" in result.stderr

# ... 更多测试用例
```

---

*创建: 2026-04-19 | 用途: NUCLEUS 4.0集成测试设计*