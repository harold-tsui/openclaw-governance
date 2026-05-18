# openclaw-governance 本地初始化报告

> 生成时间：2026-05-18
> 分析范围：ZT-P015_NUCLEUS-4-0（NUCLEUS 4.0 PDCA Harness）

---

## 一、项目结构概览

```
/data/claude/openclaw-governance/
├── src/                     # 开发源码（Python 工具）
│   ├── pdca.py             # PDCA 状态记录器（~2000行，核心）
│   ├── scheduler_state.py  # 多粒度调度计数器
│   ├── dashboard.py        # 仪表板渲染
│   └── migrate_legacy.py   # Phase 1 迁移工具
├── build/                   # 生产 skill 包（由 build-skill.sh 生成）
│   └── openclaw-governance/skills/openclaw-governance-nucleus/
│       ├── SKILL.md        # PDCA Harness 执行协议（289行，v2.5.0）
│       ├── scripts/        # ← src/ 同步目标
│       ├── tests/          # pytest 测试套件
│       └── config/         # 外部化配置
├── scripts/
│   ├── build-skill.sh      # src → build 同步脚本
│   ├── install-skill.sh    # build → $LOCAL_WORKSPACE/skills/ 安装
│   ├── pdca_dashboard.py   # 项目级仪表板
│   ├── pdca_analyzer.py    # 执行数据深度分析
│   └── pdca_optimizer.py   # 瓶颈识别
├── config/                  # 项目级配置
│   ├── business_hours.yaml
│   ├── escalation_policy.yaml
│   └── state_sync_rules.yaml
├── runtime/                 # 运行时状态（gitignore）
│   ├── cycles/             # Cycle 记录
│   ├── logs/               # 执行日志 (.jsonl)
│   └── pdca/               # PDCA YAML 状态 + _state.yaml
├── topics/                  # Topic 工作区 (N4-P*-T*)
├── tasks/                   # Task 卡片
├── decisions/               # 架构决策记录 (ADR)
├── test/                    # 非正式验证脚本
└── docs/                    # 架构文档（唯一权威源）
```

---

## 二、本地初始化步骤

### Step 1：基础依赖检查

```bash
cd /data/claude/openclaw-governance

# Python 3.12+（已满足）
python3 --version  # Python 3.12.3 ✅

# PyYAML（已满足）
python3 -c "import yaml"  # ✅

# jsonschema（已满足）
python3 -c "import jsonschema"  # ✅

# pytest（未安装，需要安装）
which pytest  # ❌ not found → pip install pytest

# 可选依赖
pip install pytest pytest-cov  # 测试 + 覆盖率
```

**⚠️ 缺失：没有 `requirements.txt` 或 `pyproject.toml` 记录依赖。**

### Step 2：构建 Skill 包

```bash
./scripts/build-skill.sh
```

- 将 `src/*.py` → `build/openclaw-governance/skills/openclaw-governance-nucleus/scripts/`
- 当前版本：v2.5.0
- **结果：✅ 构建成功**

### Step 3：创建运行时目录结构

pdca.py 的 `health-check` 返回 `"degraded"` 是因为 `runtime/pdca/` 缺失：

```bash
mkdir -p runtime/pdca
mkdir -p runtime/logs
mkdir -p runtime/cycles
```

**再次验证：**
```bash
python3 build/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py health-check
```

### Step 4：安装到 OpenClaw Skill 目录

```bash
# 设置环境变量
export LOCAL_WORKSPACE="$HOME/.openclaw/workspace"

# 安装
./scripts/install-skill.sh
```

**⚠️ 当前 `LOCAL_WORKSPACE` 未设置，install-skill.sh 会回退到 `$HOME/Workspaces/openclaw/main`**，在当前机器上不存在，安装会失败。

### Step 5：运行测试

```bash
cd build/openclaw-governance/skills/openclaw-governance-nucleus
pytest  # 需要 pytest 已安装
```

### Step 6：试运行 PDCA 命令

```bash
cd build/openclaw-governance/skills/openclaw-governance-nucleus

# 健康检查
python3 scripts/pdca.py health-check

# Plan 示例
python3 scripts/pdca.py p \
  --task-card-id T1.1 \
  --summary "测试 Plan 阶段" \
  --topic-id T06 \
  --project-id ZT-P015
```

---

## 三、skill 中不足的地方

### 🔴 严重缺陷

#### 1. 缺少 `requirements.txt` / `pyproject.toml`
- 没有记录 Python 依赖（yaml, jsonschema, pytest）
- 新环境无法快速安装依赖
- 建议：创建 `requirements.txt` 或 `pyproject.toml`

#### 2. `install-skill.sh` 依赖未设置的 `LOCAL_WORKSPACE`
- 脚本假设 `LOCAL_WORKSPACE` 环境变量已定义
- 在当前机器上 `$HOME/Workspaces/openclaw/main` 不存在
- 安装会静默失败或安装到不存在的目录
- 建议：脚本中添加 `LOCAL_WORKSPACE` 检测和提示，或支持传入参数

#### 3. 运行时目录 `runtime/pdca/` 不会自动创建
- pdca.py 尝试写入但目录不存在
- health-check 返回 `degraded`
- 建议：pdca.py 在启动时自动创建缺失目录（使用 `os.makedirs(exist_ok=True)`）

#### 4. SKILL.md 版本 (v2.5.0) 与 build 脚本打印的版本不一致
- `_meta.json` 显示版本 2.5.0
- build-skill.sh 读取并打印 2.5.0
- 但 CLAUDE.md 中提到 SKILL.md 版本是 v2.7.1，pdca.py 也是 v2.7.1
- 存在版本号漂移（_meta.json 可能是旧版本）

### 🟡 中等问题

#### 5. `runtime/` 目录在 build/ 中有重复
- `build/openclaw-governance/skills/openclaw-governance-nucleus/pdca/` 也在 `.gitignore` 中
- 容易混淆哪个是"主" runtime 目录
- 建议：明确区分项目级 runtime/ 和 skill 级 runtime/

#### 6. 测试目录分散
- `test/`（项目根）放的是非正式验证脚本
- `build/.../tests/` 放的是 pytest 正式测试
- 开发者容易混淆应该在哪写测试
- 建议：根目录 `test/` 改名为 `scripts/verification/` 或明确文档说明

#### 7. `build/` 目录被 git 追踪
- build/ 是一个派生目录（由 src/ 生成）
- 通常派生目录不应被 git 追踪
- 当前将 build/ 提交到 git，容易导致 src/ 和 build/ 不同步
- 建议：
  - 方案 A：build/ 加入 .gitignore，CI/CD 时生成
  - 方案 B：保留 build/ 但添加 git hook 或 CI 检查确保同步

#### 8. 缺少 CLI 使用示例
- SKILL.md 定义了完整的 PDCA Harness 协议
- 但没有提供从 OpenClaw 环境中调用这些工具的示例
- 用户不知道如何在 OpenClaw 的 agent 调用中使用这些 skill

### 🟢 改进建议

#### 9. 缺少 `Makefile` 或 `task` 文件
- 常用的构建/测试/安装命令分散在文档中
- 建议添加 Makefile 统一入口：
  ```makefile
  build:
      ./scripts/build-skill.sh
  test:
      cd build/... && pytest
  install:
      ./scripts/install-skill.sh
  init:
      mkdir -p runtime/pdca runtime/logs runtime/cycles
  ```

#### 10. 缺少 CI/CD 配置
- 没有 `.github/workflows/` 自动测试/构建
- 没有 pre-commit hook 确保 src/ → build/ 同步

#### 11. `pdca.py` 输出为 JSON 但缺少结构化日志
- 输出到 stdout 的 JSON 难以在 OpenClaw 环境中消费
- 建议：考虑输出到 `runtime/logs/` 并按日期轮转

---

## 四、立即执行的修复清单

| 优先级 | 问题 | 修复方案 |
|--------|------|---------|
| 🔴 P0 | 缺少依赖声明 | 创建 `requirements.txt` 或 `pyproject.toml` |
| 🔴 P0 | runtime/pdca/ 不自动创建 | pdca.py 启动时 `os.makedirs` |
| 🔴 P0 | install-skill.sh 目标目录不存在 | 脚本添加目录检测 + mkdir -p |
| 🟡 P1 | 版本号漂移 | 同步 _meta.json / SKILL.md / pdca.py 版本 |
| 🟡 P1 | build/ 被 git 追踪 | 评估是否需要加入 .gitignore |
| 🟢 P2 | 缺少 Makefile | 添加常用命令快捷入口 |
| 🟢 P2 | 缺少 CI/CD | 添加 GitHub Actions 自动测试 |

---

## 五、OpenClaw 集成建议

当前 skill 是一个**纯 Python CLI 工具集**，与 OpenClaw 的集成存在以下挑战：

1. **调用方式**：OpenClaw Agent 如何调用 `pdca.py`？通过 `exec` 还是 skill 机制？
2. **状态共享**：PDCA 状态存储在 `runtime/pdca/` 的 YAML 文件中，OpenClaw 如何读取这些状态？
3. **Heartbeat 集成**：PDCA 的 `pending` 和 `audit-queue` 命令需要在 heartbeat 中调用，如何配置？

建议的集成方案：
- 将 `build/openclaw-governance/skills/openclaw-governance-nucleus/` 安装到 `~/.openclaw/workspace/skills/`
- 在 `HEARTBEAT.md` 中添加 PDCA heartbeat 检查逻辑
- 使用 `exec` 调用 `python3 scripts/pdca.py pending` 获取待办任务

---

*报告生成完毕。需要我执行上述修复吗？*
