# TOPIC-BRIEF · N4-P1-T08 Test Framework

> **Topic ID**: N4-P1-T08
> **Topic 名称**: Test Framework（测试框架）
> **Topic PIC**: CQO 张铁
> **上位 Project**: ZT-P015 NUCLEUS 4.0
> **状态**: 🟢 Active
> **创建时间**: 2026-04-19

---

## 一、Topic 目标

建立统一的测试基础设施，支持：
1. NUCLEUS 4.0 核心功能测试（pdca.py、scheduler_state.py）
2. 所有 Governance Skills 的单元测试
3. 跨 Agent 协作测试（其他 Agent 可调用）
4. 与 Claude Code 协同工作（ACP session + thread绑定）

---

## 二、核心需求

| 需求 | 说明 |
|------|------|
| **测试框架** | pytest + YAML驱动测试 |
| **专有工作空间** | `10_Projects/ZT-P015_NUCLEUS-4-0/test_framework/` |
| **Claude Code协同** | ACP session + thread绑定 |
| **跨Agent接口** | 其他Agent可调用测试框架 |

---

## 三、Task 列表

| Task ID | Task 名称 | 状态 | 说明 |
|----------|-----------|------|------|
| N4-P1-T08-T01 | 测试框架设计 | [P] 已接收 | 首个任务，建立基础框架 |

---

## 四、交付物清单

| 交付物 | 路径 |
|--------|------|
| 测试框架设计文档 | `test_framework/TEST-DESIGN.md` |
| 专有工作空间 | `test_framework/` |
| 样例单元测试 | `tests/test_pdca.py` |
| 集成测试模板 | `configs/integration-test-template.yaml` |

---

## 五、依赖与风险

| 类型 | 描述 | 影响程度 |
|------|------|----------|
| **依赖** | Claude Code ACP机制需熟悉 | 中 |
| **风险** | 跨Agent测试接口设计复杂度 | 低 |

---

## 六、Harold Review 节点

| 里程碑 | Review 内容 | Review 级别 |
|--------|-------------|-------------|
| 测试框架设计完成 | TEST-DESIGN.md | L2 |
| 样例测试通过 | pytest执行结果 | L1 |

---

*创建: 2026-04-19 | PIC: CQO 张铁*