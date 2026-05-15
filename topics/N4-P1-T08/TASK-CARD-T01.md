# TASK-CARD · N4-P1-T08-T01 集成测试扩展

> **Task ID**: N4-P1-T08-T01
> **上位 Topic**: N4-P1-T08-Test-Framework
> **上位 Project**: ZT-P015_NUCLEUS-4-0
> **Owner**: CQO 张铁
> **Review 级别**: L2（银月抽样）
> **创建时间**: 2026-04-19
> **更新时间**: 2026-04-19 17:30
> **状态**: [P] 已接收

---

## §一、项目上下文

| 字段 | 内容 |
|------|------|
| **Project ID** | ZT-P015 |
| **Project 名称** | NUCLEUS 4.0（自动进化内核） |
| **Topic ID** | N4-P1-T08 |
| **Topic 名称** | Test Framework（测试框架） |
| **workspace** | `/Users/haroldtsui/Workspaces/openclaw/main` |
| **task_card_path** | `10_Projects/ZT-P015_NUCLEUS-4-0/topics/N4-P1-T08/TASK-CARD-T01.md` |
| **deliverable_path** | `10_Projects/ZT-P015_NUCLEUS-4-0/test/integration/` |

---

## §二、任务定义

### 2.1 任务名称

**集成测试扩展** - 主要覆盖集成测试，支持Claude Code协同

### 2.2 任务目标

**主要覆盖集成测试**（重点调整）：
1. **集成测试目录** `test/integration/` - 16个集成测试用例
2. **Claude Code协同方案** - ACP session绑定测试
3. **跨Agent测试接口** - 其他Agent可调用测试框架
4. **pytest自动化脚本** - 可自动化执行的测试套件

**复用现有基础设施**：
- ✅ `test/integration_test_task.md` - 集成测试任务
- ✅ `test_reports/README.md` - 测试流程文档
- ✅ `test_reports/TEMPLATE.md` - 测试报告模板

### 2.3 任务类型

| 类型 | 说明 |
|------|------|
| **基础设施扩展** | 主要覆盖集成测试（16个用例） |

### 2.4 优先级

**P1** - Phase 2完成后的验收基础设施

---

## §三、执行计划

### 3.1 前置条件

- ✅ NUCLEUS 4.0 Phase 2核心功能完成
- ✅ pdca.py v2.7.1 已稳定
- ✅ 现有test/test_reports目录已存在
- ⚪ Claude Code协同机制待设计

### 3.2 工作步骤

| Step | 内容 | 预计时间 | 状态 |
|------|------|----------|------|
| **Step 1** | 创建集成测试目录 `test/integration/` | 10min | ⚪ 待开始 |
| **Step 2** | 编写集成测试用例设计文档 | 2h | ✅ 已完成（TEST-CASE-TEMPLATE.md） |
| **Step 3** | 编写pytest自动化脚本 | 3h | ⚪ 待开始 |
| **Step 4** | 执行集成测试套件A（PDCA核心7个） | 2h | ⚪ 待开始 |
| **Step 5** | 执行集成测试套件B（并发传播3个） | 1h | ⚪ 待开始 |
| **Step 6** | 设计Claude Code协同方案（ACP） | 1h | ⚪ 待开始 |
| **Step 7** | 测试Claude Code协同（TC-INT-011） | 1h | ⚪ 待开始 |
| **Step 8** | 编写跨Agent测试接口文档 | 1h | ⚪ 待开始 |
| **Step 9** | 测试跨Agent调用（TC-INT-012） | 1h | ⚪ 待开始 |
| **Step 10** | 生成集成测试报告 | 30min | ⚪ 待开始 |

### 3.3 阻塞风险

| 风险 | 影响程度 | 应对措施 |
|------|----------|----------|
| Claude Code ACP机制不熟悉 | 中 | 查阅OpenClaw文档，必要时请求CTO支持 |
| pytest环境配置问题 | 低 | 确认Python版本≥3.9，pytest已安装 |

---

## §四、交付物清单

### Zone A: 任务定义（创建时填写）

| 交付物 | 类型 | 路径 | 验收标准 |
|--------|------|------|----------|
| **集成测试用例设计** | doc | `test/integration/TEST-CASE-TEMPLATE.md` | 16个用例，覆盖4个套件 |
| **pytest自动化脚本** | code | `test/integration/test_pdca_integration.py` | 可执行，自动化测试套件A+B |
| **Claude Code协同方案** | doc | `test_reports/README.md`扩展 | ACP session绑定流程 |
| **跨Agent测试接口** | doc | `test/integration/AGENT-TEST-GUIDE.md` | CIO/其他Agent可调用 |
| **集成测试报告** | doc | `test_reports/INTEGRATION-TEST-REPORT-2026-04-19.md` | 包含16个用例执行结果 |

### Zone B: 运行时（执行时更新）

| 字段 | 内容 |
|------|------|
| **实际开始时间** | 2026-04-19 17:30 |
| **实际完成时间** | - |
| **执行日志路径** | `logs/N4-P1-T08-T01-execution.log` |

### Zone C: 后处理（完成后填写）

| 字段 | 内容 |
|------|------|
| **知识沉淀** | 待填写（经验教训） |
| **归档位置** | `topics/N4-P1-T08/archive/` |

---

## §五、验收标准

| 序号 | 验收标准 | 衡量方式 |
|------|----------|----------|
| **1** | 集成测试用例设计完整 | 16个用例，覆盖PDCA核心/并发/Claude Code/Guardrail |
| **2** | pytest自动化脚本可执行 | `pytest test/integration/test_pdca_integration.py` 通过率≥80% |
| **3** | Claude Code协同测试成功 | TC-INT-011通过，ACP session绑定正确 |
| **4** | 跨Agent测试接口清晰 | TC-INT-012通过，CIO可调用测试框架 |
| **5** | 集成测试报告完整 | 包含16个用例执行结果、发现问题、建议 |

---

## §六、集成测试用例清单

### 测试套件 A：PDCA核心流程（7个）

| 用例ID | 名称 | 目的 |
|--------|------|------|
| TC-INT-001 | 完整PDCA流程 | P→D→C→A顺序执行 |
| TC-INT-002 | Phase锁定-P跳步 | 无p()调用d()被拒绝 |
| TC-INT-003 | Phase锁定-D跳步 | 无d()调用c()被拒绝 |
| TC-INT-004 | Phase锁定-C跳步 | 无c()调用a()被拒绝 |
| TC-INT-005 | 幂等性-重复c() | 同cycle重复c()被拒绝 |
| TC-INT-006 | 多CWD测试 | 不同工作目录执行 |
| TC-INT-007 | 连续PDCA迭代 | 3轮PDCA历史完整 |

### 测试套件 B：并发与传播（3个）

| 用例ID | 名称 | 目的 |
|--------|------|------|
| TC-INT-008 | 并发上限-Task级 | 11个Task级PDCA第11个被拒绝 |
| TC-INT-009 | 并发上限-Topic级 | 6个Topic级聚合第6个被拒绝 |
| TC-INT-010 | 层间传播 | aggregate()正确计算父级verdict |

### 测试套件 C：Claude Code协同（2个）

| 用例ID | 名称 | 目的 |
|--------|------|------|
| TC-INT-011 | ACP session绑定 | Claude Code执行测试成功 |
| TC-INT-012 | 跨Agent测试 | CIO调用测试框架成功 |

### 测试套件 D：Guardrail防护（4个）

| 用例ID | 名称 | 目的 |
|--------|------|------|
| TC-INT-013 | Guardrail-P1 | Plan summary缺少差异被拒绝 |
| TC-INT-014 | Guardrail-D1 | Do summary虚操作被拒绝 |
| TC-INT-015 | Guardrail-C1 | Check缺少evidence被拒绝 |
| TC-INT-016 | Guardrail-A1 | Act缺少下次输入被拒绝 |

---

## §七、相关资源

### 7.1 参考文档

| 文档 | 路径 |
|------|------|
| 测试用例设计 | `test/integration/TEST-CASE-TEMPLATE.md` ✅ 已完成 |
| 现有测试流程 | `test_reports/README.md` |
| NUCLEUS 4.0架构 | `docs/NUCLEUS-4-0-ARCHITECTURE.md` |
| pdca.py设计 | `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py` |

### 7.2 现有基础设施（复用）

| 组件 | 路径 | 状态 |
|------|------|------|
| 集成测试任务 | `test/integration_test_task.md` | ✅ 已有 |
| 测试流程文档 | `test_reports/README.md` | ✅ 已有 |
| 测试报告模板 | `test_reports/TEMPLATE.md` | ✅ 已有 |

---

## §八、状态历史

| 时间 | 状态变更 | 变更原因 | 记录人 |
|------|----------|----------|--------|
| 2026-04-19 16:08 | 创建 → [P] | Harold发起测试框架需求 | CQO |
| 2026-04-19 17:24 | 更新任务目标 | 发现现有test/test_reports目录 | CQO |
| 2026-04-19 17:30 | **调整为重点覆盖集成测试** | Harold明确需求：主要覆盖集成测试 | CQO |
| 2026-04-19 17:31 | 完成测试用例设计 | TEST-CASE-TEMPLATE.md已创建（16个用例） | CQO |

---

## §九、PDCA 记录（首次）

| Cycle | Phase | Summary | verdict |
|-------|-------|---------|---------|
| Cycle 1 | Plan | 集成测试扩展启动，已完成测试用例设计（16个用例，4个套件） | - |

---

*版本: TASK-CARD v3.0 | 创建: 2026-04-19 | 更新: 2026-04-19 17:31 | Owner: CQO 张铁*