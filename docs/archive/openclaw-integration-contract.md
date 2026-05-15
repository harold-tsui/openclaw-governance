# OpenClaw Skills + Python Integration Contract

> **版本**：v1.0
> **日期**：2026-04-05
> **状态**：待 Harold 确认

---

## 一、接入方式选型

**结论**：通过 exec tool 调用 Python 脚本

**调用链**：

```
User Request → Skill(SKILL.md) → LLM理解 → exec tool → Python脚本 → 输出 → LLM处理
```

---

## 二、标准模式

### 2.1 Skill 文件结构

```
skill-name/
├── SKILL.md                    # 声明式协议（必需）
│   ├── YAML frontmatter        # name + description（必需）
│   └── Markdown instructions   # 执行指导（必需）
└── scripts/                    # Python 脚本（可选）
    ├── xxx.py                  # 主脚本
    └── test_xxx.py             # 测试脚本
```

### 2.2 SKILL.md 调用格式

```markdown
## Quick start

python {baseDir}/scripts/xxx.py --arg1 value1 --arg2 value2
```

**变量说明**：

- `{baseDir}`：Skill 基准目录（OpenClaw 自动替换）
- 示例：`/opt/homebrew/lib/node_modules/openclaw/skills/model-usage`

### 2.3 Python 脚本规范

**输入方式**：

1. **命令行参数**：`argparse` 处理
2. **stdin**：`sys.stdin.read()`
3. **文件**：读取指定路径

**输出方式**：

1. **stdout**：正常输出（JSON/Text）
2. **stderr**：错误信息
3. **返回码**：0=成功，非0=失败

**错误处理示例**：

```python
import sys
import json

try:
    result = process_data(args)
    print(json.dumps(result))
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

---

## 三、调用示例

### 3.1 基本调用

**SKILL.md**：

```markdown
python {baseDir}/scripts/hello.py --name "NUCLEUS"
```

**LLM 执行**：

```json
{
  "tool": "exec",
  "command": "python /path/to/skill/scripts/hello.py --name NUCLEUS"
}
```

**输出**：

```json
{"message": "Hello, NUCLEUS!", "status": "success"}
```

### 3.2 复杂调用（文件输入）

**SKILL.md**：

```markdown
python {baseDir}/scripts/process.py --input /path/to/input.yaml --output /path/to/output.json
```

**Python 脚本**：

```python
import argparse
import yaml
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    with open(args.input, 'r') as f:
        data = yaml.safe_load(f)
    
    result = process(data)
    
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
```

---

## 四、错误传递规范

### 4.1 错误类型

| 错误类型 | 处理方式 | 返回码 |
|---------|---------|-------|
| **参数错误** | stderr 输出错误信息 | 1 |
| **文件不存在** | stderr 输出错误信息 | 2 |
| **处理错误** | stderr 输出错误信息 | 3 |
| **系统错误** | stderr 输出错误信息 | 4 |

### 4.2 错误处理模式

**Python 脚本**：

```python
import sys

def main():
    try:
        args = parse_args()
        result = process(args)
        print(json.dumps(result))
    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"Invalid input: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    main()
```

**LLM 处理**：

1. 读取 stderr 输出
2. 根据返回码判断错误类型
3. 决定是否重试或报错

---

## 五、性能考虑

### 5.1 Token 效率

**优势**：Python 脚本不需要加载到 context window

**示例**：

- **不使用脚本**：LLM 每次生成相同代码（浪费 tokens）
- **使用脚本**：LLM 只需调用脚本（节省 tokens）

### 5.2 执行效率

**考虑**：Python 脚本启动时间（约 50-100ms）

**建议**：

- 简单操作（<10 行代码）：直接在 Skill 中描述
- 复杂操作（>10 行代码）：使用 Python 脚本

---

## 六、测试规范

### 6.1 单元测试

**目录结构**：

```
scripts/
├── xxx.py          # 主脚本
└── test_xxx.py     # 测试脚本
```

**测试示例**：

```python
import unittest
import subprocess
import json

class TestXXX(unittest.TestCase):
    def test_basic(self):
        result = subprocess.run(
            ["python", "scripts/xxx.py", "--arg1", "value1"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "success")

if __name__ == "__main__":
    unittest.main()
```

### 6.2 集成测试

**测试流程**：

1. 创建测试 Skill
2. 手动测试 Python 脚本
3. LLM 测试（通过 Skill 调用）
4. 验证输出正确

---

## 七、NUCLEUS 4.0 应用

### 7.1 governance-heartbeat 增强

**现有结构**：

```
governance-heartbeat/
├── SKILL.md
└── frameworks/
    └── heartbeat-framework.md
```

**增强结构**：

```
governance-heartbeat/
├── SKILL.md                    # 增强：新增 CycleScheduler 调用指导
├── frameworks/                 # 现有框架（不变）
│   └── heartbeat-framework.md
└── scripts/                    # 新增：Python 脚本
    ├── cycle_scheduler.py
    ├── cycle_unit.py
    ├── monitor.py
    ├── business_time.py
    └── state_machine.py
```

### 7.2 调用示例

**CycleScheduler tick**：

```bash
python {baseDir}/scripts/cycle_scheduler.py --scope task --action tick
```

**CycleUnit load**：

```bash
python {baseDir}/scripts/cycle_unit.py --id ZT-001 --scope task --action load
```

**Human time calculation**：

```bash
python {baseDir}/scripts/business_time.py --expression "2 business days" --start "2026-04-05T17:00:00Z"
```

---

## 八、兼容性保障

### 8.1 现有 Skills 兼容性

**原则**：

- 现有 Skills 继续使用 frameworks/ 和 references/
- 新增功能使用 scripts/ 目录
- SKILL.md 追加调用指导（不覆盖现有内容）

### 8.2 错误降级

**策略**：

1. Python 脚本失败 → 记录错误日志
2. 不影响现有巡检逻辑
3. 可配置是否启用新功能

---

## 八、Slash Commands 可选接入方式

### 8.1 概述

OpenClaw 支持 **Skill Commands**，将 Skill 暴露为 slash 命令。

**配置方式**：

```yaml
# SKILL.md
---
name: governance-nucleus
user-invocable: true  # 启用 slash commands
---
```

### 8.2 NUCLEUS 4.0 计划命令

| 命令 | 功能 | 状态 |
|------|------|------|
| `/gov` | 触发 NUCLEUS 调度器 | 🔜 Coming Soon |
| `/gov status` | 查看系统状态 | 🔜 Coming Soon |
| `/gov on/off` | 启用/禁用自动调度 | 🔜 Coming Soon |

**当前实现**：空实现，返回 "Coming Soon"

**理由**：
- 先定义接口规范
- 验证 CLI 调用流程
- 后续按需填充功能

### 8.3 适用场景

| 场景 | 说明 |
|------|------|
| **手动触发** | 需要立即触发 Heartbeat 时 |
| **状态查看** | 查看当前 CycleUnit、调度器状态 |
| **调试** | 调试 PDCA 流程时 |

**不适用场景**：
- 正常运行时（Heartbeat 自动触发）

---

## 九、参考案例

### 9.1 model-usage Skill

**路径**：`/opt/homebrew/lib/node_modules/openclaw/skills/model-usage/`

**调用方式**：

```bash
python {baseDir}/scripts/model_usage.py --provider codex --mode current
```

**Python 脚本**：标准 Python 3，使用 argparse + subprocess

### 9.2 skill-creator Skill

**路径**：`/opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/`

**调用方式**：

```bash
python {baseDir}/scripts/package_skill.py --skill-dir /path/to/skill
```

---

## 十、确认清单

- [x] 接入方式有明确选型结论
- [x] 有参考案例（model-usage, skill-creator）
- [ ] Hello World 示例验证通过
- [ ] Harold 确认签字

---

*v1.0 · 2026-04-05 · 待 Harold 确认*