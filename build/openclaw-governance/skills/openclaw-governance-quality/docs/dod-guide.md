# DOD (Definition of Done) 使用指南

> **版本**：v1.0
> **作者**：张铁 (cqo)
> **日期**：2026-03-23
> **适用**：NUCLEUS 2.0 闭环流程验收环节

---

## 一、概述

### 1.1 定义

**DOD (Definition of Done)** 是结构化的验收标准定义，用于增强 NUCLEUS 闭环流程的验收环节。

### 1.2 核心原则

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOD 核心原则                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. 结构化：标准明确可验证，而非模糊的"通过/打回"              │
│   2. 锁定：Builder 不可修改 DOD，防止降低标准                    │
│   3. 分离验证：Reviewer 验证 DOD，防止自我认证                   │
│   4. 分级关联：与六级自动化级别关联，适配验证流程                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 与闭环流程的集成

```
创建 → 分派 → 接收 → 执行 → 【验收】→ 关闭
                          ↑
                     DOD 在此环节
                          ↓
              结构化标准 + 锁定 + 分离验证
```

---

## 二、DOD 结构

### 2.1 JSON Schema

详见 `schemas/dod.schema.json`

### 2.2 核心字段

```json
{
  "version": "1.0",
  "criteria": [
    {
      "id": "DOD-1",
      "category": "functional",
      "description": "具体可验证的标准描述",
      "required": true,
      "status": {
        "met": false,
        "verifier": null,
        "verified_at": null,
        "evidence": null
      },
      "automation_level": "L3"
    }
  ],
  "quality_standards": [...],
  "metadata": {
    "created_by": "coo",
    "created_at": "2026-03-23T13:30:00+08:00",
    "locked": true,
    "task_id": "T07-T03",
    "automation_level": "L2"
  }
}
```

### 2.3 标准类别

| 类别 | 说明 | 示例 |
|------|------|------|
| **functional** | 功能性 | 用户可以通过 API 创建任务 |
| **testing** | 测试 | 单元测试覆盖率 ≥ 80% |
| **documentation** | 文档 | API 文档已更新 |
| **quality** | 质量 | 代码通过 ESLint 检查 |
| **security** | 安全 | 敏感数据已加密 |
| **performance** | 性能 | API 响应时间 < 100ms |

---

## 三、DOD 流程

### 3.1 完整流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      DOD 流程                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [Plan 阶段]                                                    │
│       ↓                                                         │
│   1. COO/Task Planner 创建 DOD                                   │
│       ↓                                                         │
│   2. DOD 锁定（Builder 不可修改）                                │
│       ↓                                                         │
│   [Execute 阶段]                                                 │
│       ↓                                                         │
│   3. Builder 执行任务                                           │
│       ↓                                                         │
│   4. Builder 声明完成（不能标记 DOD）                            │
│       ↓                                                         │
│   [Review 阶段]                                                  │
│       ↓                                                         │
│   5. Reviewer 验证 DOD                                          │
│       ↓                                                         │
│   6. Reviewer 标记 status.met = true                            │
│       ↓                                                         │
│   [Review-Gate]                                                  │
│       ↓                                                         │
│   7. 验证所有 DOD 已标记                                         │
│       ↓                                                         │
│   8. 通过 / 打回                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 角色职责

| 角色 | 职责 | 限制 |
|------|------|------|
| **COO/Task Planner** | 创建 DOD | 创建后不可修改（需解锁） |
| **Builder** | 执行任务 | 不可修改 DOD，不可标记 DOD |
| **Reviewer** | 验证 DOD | 不能验证自己构建的任务 |
| **Review-Gate** | 强制检查 | 必须所有必须标准满足 |

---

## 四、与自动化级别的关联

### 4.1 级别适配

| 自动化级别 | DOD 设置者 | DOD 验证者 | Review-Gate |
|------------|------------|------------|-------------|
| **L0** | Harold | Harold | 必须等待 |
| **L1** | Harold + Agent | Harold | 必须等待 |
| **L2** | Agent + Harold 确认 | Harold 抽检 | 必须等待 |
| **L3** | Agent | 后置 Review | 自动 + 异常上报 |
| **L4** | Agent | Agent 自主 | 自动 |
| **L5** | Agent | Agent 完全自主 | 无 |

### 4.2 automation_level 字段

每个 criteria 可以指定适用的自动化级别：

```json
{
  "id": "DOD-1",
  "description": "单元测试覆盖率 ≥ 80%",
  "automation_level": "L4"
}
```

**含义**：此标准在 L4 及以上级别可自动验证。

---

## 五、验证脚本

### 5.1 使用方法

```bash
# 基本用法
./verify-dod.sh dod.json

# 检查自我认证
./verify-dod.sh dod.json --builder cqo

# 详细输出
./verify-dod.sh dod.json --builder cqo -v
```

### 5.2 返回码

| 返回码 | 含义 |
|--------|------|
| 0 | 验证通过 |
| 1 | DOD 文件不存在 |
| 2 | DOD JSON 格式错误 |
| 3 | 必须标准未全部满足 |
| 4 | 自我认证检测 |
| 5 | DOD 未锁定 |
| 6 | 缺少必要字段 |

### 5.3 与 Review-Gate 集成

```bash
# Review-Gate 中调用
if ! ./verify-dod.sh "$DOD_FILE" --builder "$BUILDER_ID"; then
    echo "Review-Gate 失败: DOD 验证未通过"
    exit 1
fi
```

---

## 六、最佳实践

### 6.1 标准编写原则

**好的 DOD 标准**：
```
✅ "API 响应时间 < 100ms（P95）"
✅ "单元测试覆盖率 ≥ 80%"
✅ "所有公开 API 有 JSDoc 注释"
✅ "无 ESLint error 级别问题"
```

**不好的 DOD 标准**：
```
❌ "性能良好"（模糊）
❌ "代码质量高"（主观）
❌ "用户体验好"（不可验证）
```

### 6.2 标准数量建议

| 任务规模 | 建议标准数 |
|----------|------------|
| 小型任务（<1天） | 3-5 个 |
| 中型任务（1-3天） | 5-8 个 |
| 大型任务（>3天） | 8-12 个 |

### 6.3 锁定时机

```
任务开始前 → DOD 创建 → DOD 锁定 → 任务执行
                            ↑
                     Builder 开始工作前
                     防止 Builder 降低标准
```

---

## 七、常见问题

### Q1: Builder 能否修改 DOD？

**答**：不能。DOD 锁定后，Builder 无法修改。如需修改，必须通过 COO/Task Planner 解锁。

### Q2: Reviewer 能验证自己的任务吗？

**答**：不能。自我认证检查会阻止 Reviewer 验证自己构建的任务。

### Q3: 非必须标准不满足会怎样？

**答**：只有必须标准（required=true）必须全部满足。非必须标准可以作为改进建议。

### Q4: 如何处理 DOD 灰色地带？

**答**：
1. 优先量化标准
2. 无法量化的，明确判断依据
3. 争议时，由 Harold 最终裁决

---

## 八、参考资源

- `schemas/dod.schema.json` - JSON Schema 定义
- `schemas/dod.example.json` - 示例文件
- `scripts/verify-dod.sh` - 验证脚本
- `implementation-plan-v1.1.md` - 实施方案

---

*本指南 v1.0 | 作者：张铁 (cqo) | 日期：2026-03-23*