# NUCLEUS 文档索引

> **维护规则**: 此文件是 docs/ 目录下所有活跃文档的索引。任何文档版本更新时同步更新此索引。
> **文档权威性**: 本索引中标注为"权威源"的文档是该领域的唯一真相源。

---

## 一、活跃文档（v2.0 架构）

| 编号 | 文件名 | 版本 | 位置 | 类型 | 说明 |
|------|--------|------|------|------|------|
| **REQ-SPEC-v2.0** | NUCLEUS-REQUIREMENTS-SPEC.md | v2.0 | `docs/` | 需求规格 | 功能性 + 非功能性需求（权威源） |
| **ARCH-v2.0** | NUCLEUS-ARCHITECTURE.md | v2.0 | `docs/` | 系统架构 | 组件关系 + 数据流 + 安全边界（权威源） |
| **DESIGN-v2.0** | NUCLEUS-DETAILED-DESIGN.md | v2.0 | `docs/` | 详细设计 | pdca.py 函数级设计 + ADAS 规则（权威源） |
| **UPGRADE-v2.0** | NUCLEUS-UPGRADE-PLAN.md | v2.0 | `docs/` | 升级方案 | Phase 2-3 实施计划 + 里程碑（权威源） |
| — | INDEX.md | v1.0 | `docs/` | 文档索引 | 本文件 |

### 文档依赖关系

```
REQ-SPEC（需求）
  ↓ 上位引用
ARCH（架构）
  ↓ 上位引用
DESIGN（详细设计）
  ↓ 上位引用
UPGRADE（升级方案）
```

读取顺序：REQ-SPEC → ARCH → DESIGN → UPGRADE

---

## 二、历史项目与文档

| 项目 | 版本 | 章程 | 状态 | 说明 |
|------|------|------|------|------|
| **ZT-P000_NUCLEUS** | v1.0 | `PROJECT-CHARTER.md` | 归档 | 灵枢计划原始项目，建立使命/飞轮/六大模块 |
| **ZT-P009_NUCLEUS-2-0** | v3.0 | `PROJECT-CHARTER.md` | 归档 | Harness Engineering 实现，11 Skill 上线，DOD + Pipeline |
| **ZT-P015_NUCLEUS-4-0** | v2.0+ | `PROJECT-CHARTER.md`（上层） | Active | pdca.py 精简版架构，当前实施 Phase 2 |

### 版本演进

```
ZT-P000 (v1.0, 2026-02)  →  ZT-P009 (v3.0, 2026-03)  →  ZT-P015 (v2.0+, 2026-04)
使命/飞轮/六大模块定义     Harness Engineering 实现       pdca.py 精简版 + 层间传播
L0-L3 Skill 建立          DOD + Review-Gate + Pipeline    零数据库 + 文件驱动
```

---

## 三、Skill 文档

| Skill | 版本 | 位置 | 说明 |
|-------|------|------|------|
| governance-nucleus | v2.5.0 | `skills/openclaw-governance/skills/openclaw-governance-nucleus/SKILL.md` | PDCA Harness（权威执行协议） |
| governance-core | v6.1.8 | `skills/openclaw-governance/skills/openclaw-governance-core/SKILL.md` | 会话运行时 |
| governance-heartbeat | v5.7.0 | `skills/openclaw-governance/skills/openclaw-governance-heartbeat/SKILL.md` | 分布式巡检 |
| governance-delegation | v4.2.0 | `skills/openclaw-governance/skills/openclaw-governance-delegation/SKILL.md` | Human-in-the-Loop A/B/C/D |
| governance-task | v6.0.4 | `skills/openclaw-governance/skills/openclaw-governance-task/SKILL.md` | Task 生命周期 |
| governance-quality | v3.2.0 | `skills/openclaw-governance/skills/openclaw-governance-quality/SKILL.md` | DOD + Review-Gate |

> **Skill SKILL.md 是 pdca.py 的权威执行协议**。需求/架构文档描述"应该是什么"，SKILL.md 定义"怎么做"。

---

## 四、代码文档

| 组件 | 版本 | 位置 | 说明 |
|------|------|------|------|
| pdca.py | v2.2.0 | `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py` | PDCA 状态记录器（唯一 Python 工具） |
| scheduler_state.py | 待开发 | `scripts/scheduler_state.py`（Phase 2） | 多粒度调度计数器 |

---

## 五、归档文档

| 文件名 | 位置 | 版本 | 归档原因 |
|--------|------|------|---------|
| pdca-check-protocol-v1.3.md | `docs/archive/` | v1.3 | 基于旧 CycleUnit 架构，已被 DESIGN-v2.0 §五/§六 替代 |
| ARCH-v1.4.3 | `docs/archive/nucleus-v1/` | v1.4.3 | CycleUnit/CycleScheduler 架构，已被 ARCH-v2.0 替代 |
| 其他 v1.x 文档 | `docs/archive/` | 各种 | Phase 1 研究/评审记录，不作为当前架构权威源 |

---

## 六、如何引用

```
引用需求：NUCLEUS-REQ-SPEC-v2.0 §3.1 REQ-PDCA-001
引用架构：NUCLEUS-ARCH-v2.0 §2.1
引用设计：NUCLEUS-DESIGN-v2.0 §1.3
引用升级：NUCLEUS-UPGRADE-v2.0 §2.2
引用执行：governance-nucleus SKILL.md v2.5.0 §四
```

---

*版本：v1.0 | 创建日期：2026-04-18 | 维护人：银月*
