# T0.1 调研报告：OpenClaw Skills + Python 集成方式

> **调研时间**：2026-04-05
> **调研目标**：明确 Python 模块如何被 OpenClaw Skill 调用，定死接入契约

---

## 一、调研结论

### 1.1 选型结论

**答案：选项 (A) 修正版 - 通过 exec tool 调用 Python 脚本**

**完整流程**：

```
User Request → Skill(SKILL.md) → LLM理解指导 → exec tool → Python脚本 → 输出 → LLM继续处理
```

**关键发现**：

1. **Skill 本质**：Skill 是声明式 Markdown 文件（SKILL.md），**不是可执行代码**
2. **Python 脚本位置**：放在 Skill 的 `scripts/` 目录下
3. **调用方式**：LLM 通过 `exec` tool 调用 Python 脚本
4. **变量替换**：`{baseDir}` 自动替换为 Skill 的基准目录

---

## 二、调研证据

### 2.1 OpenClaw 架构本质

**核心架构**：

```
OpenClaw Gateway (Node.js daemon)
    ↓
Agent (LLM)
    ↓
Tools (exec, read, write, edit, browser, etc.)
    ↓
Skills (SKILL.md - 声明式协议)
    ↓
Bundled Resources (scripts/, references/, assets/)
```

**Skills 定义**（来自 skill-creator SKILL.md）：

> Skills are modular, self-contained packages that extend Codex's capabilities by providing specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains or tasks—they transform Codex from a general-purpose agent into a specialized agent equipped with procedural knowledge that no model can fully possess.

**关键理解**：

- Skills 是"onboarding guides"，不是可执行代码
- Skills 提供"procedural knowledge"，指导 LLM 如何执行
- Skills 包含 Bundled Resources（scripts/references/assets）

---

### 2.2 Python Scripts 使用场景

**官方定义**（来自 skill-creator SKILL.md）：

> **Scripts (`scripts/`)**
> Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.
>
> - **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
> - **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
> - **Benefits**: Token efficient, deterministic, may be executed without loading into context
> - **Note**: Scripts may still need to be read by Codex for patching or environment-specific adjustments

**使用场景**：

1. **确定性可靠性**：需要精确执行的复杂操作
2. **避免重复编写**：LLM 不需要每次都生成相同代码
3. **Token 效率**：Scripts 不需要加载到 context window

---

### 2.3 实际案例：model-usage Skill

**Skill 目录结构**：

```
model-usage/
├── SKILL.md                    # 声明式协议
└── scripts/
    ├── model_usage.py          # Python 脚本
    └── test_model_usage.py     # 测试脚本
```

**调用方式**（SKILL.md 内容）：

```markdown
## Quick start

python {baseDir}/scripts/model_usage.py --provider codex --mode current
python {baseDir}/scripts/model_usage.py --provider codex --mode all
python {baseDir}/scripts/model_usage.py --provider claude --mode all --format json --pretty
```

**Python 脚本特点**：

```python
#!/usr/bin/env python3
"""
Summarize CodexBar local cost usage by model.
"""

import argparse
import json
import subprocess
import sys

def run_codexbar_cost(provider: str):
    cmd = ["codexbar", "cost", "--format", "json", "--provider", provider]
    output = subprocess.check_output(cmd, text=True)
    payload = json.loads(output)
    return payload

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True)
    parser.add_argument("--mode", choices=["current", "all"])
    args = parser.parse_args()
    
    data = run_codexbar_cost(args.provider)
    # ... 处理逻辑 ...
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

**关键特点**：

1. **标准 Python 脚本**：使用 argparse 处理参数
2. **输入输出**：stdin/stdout/stderr
3. **错误处理**：标准异常处理
4. **可测试**：包含 test_model_usage.py

---

## 三、接入契约定义

### 3.1 标准模式

**Skill 文件结构**：

```
skill-name/
├── SKILL.md                    # 声明式协议（必需）
│   ├── YAML frontmatter        # name + description（必需）
│   └── Markdown instructions   # 执行指导（必需）
└── scripts/                    # Python 脚本（可选）
    ├── xxx.py                  # 主脚本
    └── test_xxx.py             # 测试脚本
```

**SKILL.md 调用指导格式**：

```markdown
## Quick start

python {baseDir}/scripts/xxx.py --arg1 value1 --arg2 value2
```

**变量替换**：

- `{baseDir}` → Skill 的基准目录（OpenClaw 自动替换）
- 例如：`/opt/homebrew/lib/node_modules/openclaw/skills/model-usage`

---

### 3.2 Python 脚本规范

**输入方式**：

1. **命令行参数**：`argparse` 处理
2. **stdin**：`sys.stdin.read()`
3. **文件**：读取指定文件路径

**输出方式**：

1. **stdout**：正常输出（JSON/Text）
2. **stderr**：错误信息
3. **返回码**：0=成功，非0=失败

**错误处理**：

```python
try:
    result = process_data(args)
    print(json.dumps(result))
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

---

### 3.3 LLM 调用模式

**LLM 执行流程**：

```
1. LLM 读取 SKILL.md，理解需要执行什么操作
2. LLM 决定调用 Python 脚本（根据 SKILL.md 指导）
3. LLM 使用 exec tool：
   exec command="python {baseDir}/scripts/xxx.py --arg1 value1"
4. OpenClaw 替换 {baseDir} 为实际路径
5. Python 脚本执行，输出到 stdout/stderr
6. LLM 读取 exec 的输出，继续执行后续任务
```

**exec tool 示例**：

```json
{
  "tool": "exec",
  "command": "python /opt/homebrew/lib/node_modules/openclaw/skills/model-usage/scripts/model_usage.py --provider codex --mode current"
}
```

---

## 四、为什么不是其他选项

### 4.1 为什么不是 (B) import 内联？

**原因**：

- Skill 是 Markdown 文件，不是 Python 模块
- LLM 无法"import"一个 Markdown 文件
- OpenClaw runtime 是 Node.js，不是 Python runtime

**错误理解**：

❌ "Skill 是 Python 模块，可以被 import"

✅ "Skill 是 Markdown 文件，提供执行指导"

---

### 4.2 为什么不是 (C) 文件触发？

**原因**：

- 文件触发需要轮询机制，效率低
- OpenClaw 是事件驱动架构（User Request → Skill → exec）
- 文件触发引入不必要的复杂性

**适用场景**：

- 文件触发适合"异步触发"场景（如监听文件变化）
- 但 NUCLEUS 4.0 的需求是同步执行（heartbeat → CycleScheduler → Python）

---

### 4.3 为什么不是 (D) Skill 本身就是 Python？

**原因**：

- Skill 的定义是"onboarding guides"，不是可执行代码
- OpenClaw 架构设计：Skill = Markdown + Bundled Resources
- 如果 Skill 是 Python，会破坏 OpenClaw 的统一架构

**官方设计意图**：

> Skills transform Codex from a general-purpose agent into a specialized agent equipped with procedural knowledge that no model can fully possess.

**关键**：Skill 提供"procedural knowledge"（指导），不是"executable code"（代码）

---

## 五、NUCLEUS 4.0 应用

### 5.1 CycleScheduler 实现

**Skill 文件结构**：

```
governance-heartbeat/
├── SKILL.md                    # 现有 Skill
└── scripts/                    # 新增 scripts 目录
    ├── cycle_scheduler.py      # CycleScheduler 核心逻辑
    ├── cycle_unit.py           # CycleUnit 读写工具
    ├── business_time.py        # 人类时间计算
    └── state_machine.py        # 状态转换引擎
```

**SKILL.md 增强**：

```markdown
## CycleScheduler 调用

python {baseDir}/scripts/cycle_scheduler.py --scope task --action tick
python {baseDir}/scripts/cycle_unit.py --id ZT-001 --scope task --action load
python {baseDir}/scripts/business_time.py --expression "2 business days" --start "2026-04-05T17:00:00Z"
```

---

### 5.2 Monitor 模块实现

**Skill 文件结构**：

```
governance-heartbeat/
├── SKILL.md                    # 现有 Skill
└── scripts/
    ├── monitor.py              # Monitor 模块核心逻辑
    └── cycle_scheduler.py      # CycleScheduler
```

**SKILL.md 增强**：

```markdown
## Monitor 调用

python {baseDir}/scripts/monitor.py --sessions-dir ~/.openclaw/agents/main/sessions --output logs/YYYY-MM-DD.jsonl
```

---

### 5.3 与现有 Skill 的兼容性

**governance-heartbeat 现有结构**：

```
governance-heartbeat/
├── SKILL.md                    # 现有巡检协议
└── frameworks/                 # 现有框架
    └── heartbeat-framework.md
```

**增强方案**：

```
governance-heartbeat/
├── SKILL.md                    # 增强：新增 CycleScheduler 调用指导
├── frameworks/                 # 现有框架（不变）
│   └── heartbeat-framework.md
└── scripts/                    # 新增：Python 脚本
    ├── cycle_scheduler.py
    ├── monitor.py
    └── business_time.py
```

**兼容性原则**：

- 现有巡检逻辑不变（继续使用 frameworks/）
- 新增 CycleScheduler 调用指导（SKILL.md 追加）
- 新增 Python 脚本（scripts/ 目录）
- 两套逻辑独立运行，互不干扰

---

## 六、Hello World 示例

### 6.1 创建测试 Skill

**目录结构**：

```
test-integration/
├── SKILL.md
└── scripts/
    └── hello.py
```

**SKILL.md**：

```markdown
---
name: test-integration
description: Test OpenClaw + Python integration
---

# Test Integration

## Quick start

python {baseDir}/scripts/hello.py --name "NUCLEUS"
```

**hello.py**：

```python
#!/usr/bin/env python3
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="World")
    args = parser.parse_args()
    
    result = {
        "message": f"Hello, {args.name}!",
        "status": "success"
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

---

### 6.2 验证步骤

1. **创建 Skill 目录**：

```bash
mkdir -p ~/.openclaw/skills/test-integration/scripts
```

2. **创建文件**：

- SKILL.md
- scripts/hello.py

3. **手动测试 Python 脚本**：

```bash
python ~/.openclaw/skills/test-integration/scripts/hello.py --name "NUCLEUS"
```

**预期输出**：

```json
{"message": "Hello, NUCLEUS!", "status": "success"}
```

4. **LLM 测试**：

向 Agent 发送："测试 test-integration skill"

Agent 应：

- 读取 SKILL.md
- 使用 exec tool 调用 hello.py
- 返回执行结果

---

## 七、调研结论总结

### 7.1 核心结论

**答案**：**选项 (A) 修正版 - 通过 exec tool 调用 Python 脚本**

**完整定义**：

1. **Skill 本质**：声明式 Markdown 文件（SKILL.md）
2. **Python 位置**：Skill 的 `scripts/` 目录
3. **调用方式**：LLM 通过 `exec` tool 调用
4. **变量替换**：`{baseDir}` 自动替换为 Skill 基准目录
5. **输入输出**：stdin/stdout/stderr + argparse

---

### 7.2 为什么选择这种方式

1. **符合 OpenClaw 架构**：Skill = Markdown + Bundled Resources
2. **Token 效率**：Scripts 不需要加载到 context window
3. **确定性可靠性**：Python 脚本提供精确执行
4. **可测试性**：标准 Python 测试框架
5. **向后兼容**：不影响现有 Skills

---

### 7.3 下一步行动

1. **创建 `docs/openclaw-integration-contract.md`**：正式接入契约文档
2. **验证 Hello World 示例**：确认流程可行
3. **设计 NUCLEUS 4.0 的 scripts 目录结构**：确定各模块的 Python 脚本位置
4. **更新 WBS T0.1 DoD**：标记调研完成

---

*调研完成：2026-04-05*
*调研人：张铁 (cqo)*
*状态：待 Harold 确认*