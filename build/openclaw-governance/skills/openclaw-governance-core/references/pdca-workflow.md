# PDCA 工作流说明

> **版本**: v7.0.0
> **更新**: 2026-04-22
> **引用**: governance-core SKILL.md §三.5

---

## 目录

1. [设计理念](#设计理念)
2. [PDCA 定义](#pdca-定义)
3. [正确理解](#正确理解)
4. [循环示例](#循环示例)
5. [核心要点](#核心要点)
6. [对 NUCLEUS 的影响](#对-nucleus-的影响)
7. [相关资源](#相关资源)

---

## 设计理念

### PDCA 来源

> **来源**：Harold Tsui 2026-04-15 指令，通过 BotLearn 的 Recheck 机制修正 PDCA-A 理解

### 修正原因

**BotLearn 的理解**：A (Act) = Recheck（复测验证）

**Harold 的修正**：A 之后**不仅是复测，而是进入下一个 PDCA 循环**。根据提升要求，P、D、C 的要求都可能不一样了。

---

## PDCA 定义

### PDCA 四阶段

| 阶段 | 定义 | 说明 |
|------|------|------|
| **P (Plan)** | 计划 | 制定目标、指标、方案 |
| **D (Do)** | 执行 | 按 Plan 执行任务 |
| **C (Check)** | 检查 | 对比结果与目标，发现问题 |
| **A (Act)** | 行动 | 根据检查结果改进，进入下一循环 |

### BotLearn vs 正确理解

| PDCA 阶段 | BotLearn Recheck | 正确的 PDCA-A |
|-----------|------------------|---------------|
| **A (Act)** | Recheck（复测验证） | ✅ 复测 + 进入下一循环 |
| **下一循环的 P** | 无变化（同样的 benchmark） | ⚠️ **根据提升要求重新 Plan** |
| **下一循环的 D** | 无变化（同样的 exam） | ⚠️ **根据新 Plan 调整 Do** |
| **下一循环的 C** | 无变化（同样的 report） | ⚠️ **根据新 D 调整 Check** |

---

## 正确理解

### Act 不只是验证

**核心要点**：

1. **Act 不只是验证**，而是承上启下的转折点
2. **下一循环的 P/D/C 必须根据提升要求重新定义**，不能简单重复上一轮
3. **复测只是下一循环中 Check 的一部分**，不是全部
4. **Plan 阶段必须读取上轮 Act 的条件/建议**，确保改进方向正确

---

## 循环示例

### Benchmark 发现问题

**场景**：Benchmark 发现"Memory" 维度得分低（10/20）

```
第一轮 PDCA：
  P: 测试 Memory 能力
  D: 回答 Memory 相关问题
  C: 得分 10/20，发现问题
  A: 安装 memory-enhancement skill

第二轮 PDCA（不是简单重复第一轮）：
  P: 测试 memory-enhancement 安装后的效果 + 探索其他维度
  D: 回答 Memory 问题 + 测试新 skill 是否生效
  C: 对比前后分数（10/20 → ?/20），评估改进效果
  A: 根据新分数决定下一步（继续改进 / 已达标 / 换其他维度）
```

### 关键区别

| 维度 | 第一轮 | 第二轮 |
|------|--------|--------|
| **Plan** | 测试 Memory 能力 | 测试 skill 安装效果 + 探索其他维度 |
| **Do** | 回答 Memory 问题 | 回答 Memory 问题 + 测试新 skill |
| **Check** | 得分 10/20 | 对比前后分数，评估改进效果 |
| **Act** | 安装 memory-enhancement | 根据新分数决定下一步 |

---

## 核心要点

### 1. Act 是转折点

**Act 不只是验证**，而是承上启下的转折点：
- 完成 A 后，必须进入下一个 PDCA 循环
- A 的结果决定下一循环的 P

### 2. 重新定义 Plan

**下一循环的 P/D/C 必须根据提升要求重新定义**：
- 不能简单重复上一轮
- P 必须读取 A 的结果
- D 必须根据 P 调整
- C 必须根据 D 调整

### 3. 复测是 Check 的子集

**复测只是下一循环中 Check 的一部分**：
- 不是全部
- Check 还包括：评估改进效果、发现问题、分析原因

### 4. Plan 必须读取 Act

**Plan 阶段必须读取上轮 Act 的条件/建议**：
- 确保改进方向正确
- 避免"盲目重复"

---

## 对 NUCLEUS 的影响

### nucleus a() 阶段

**PDCA 循环的 `a()` 阶段必须包含 `--next-task`**：
- 指向同一任务或新任务
- 明确下一循环的目标

### nucleus p() 阶段

**下一循环的 `p()` 必须引用上轮 Act summary**：
- 说明"本轮相比上次做了什么不同"
- 不能简单重复上一轮

### 禁止行为

**不允许连续 2 次 Do 阶段内容完全相同**：
- `status=blocked` 除外
- 其他情况必须根据 Act 调整

---

## 相关资源

- [SKILL.md]({baseDir}/SKILL.md) - 核心运行机制 §三.5
- [barrier-design.md]({baseDir}/references/barrier-design.md) - 屏障设计详细文档
- [phase-sequence.md]({baseDir}/references/phase-sequence.md) - Phase 序列详细说明
- [governance-nucleus SKILL.md]({baseDir}/../openclaw-governance-nucleus/SKILL.md) - NUCLEUS 执行引擎

---

*文档版本: v7.0.0 | 更新: 2026-04-22*