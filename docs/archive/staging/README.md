# 归档说明

**归档日期**：2026-04-16

## 内容

- `interfaces/`：早期原型的抽象接口层（IMonitor、IDecide、IAct、ILearn、IEventBus）
- `models/`：早期原型的领域模型（AnomalyEvent、RPNCalculation）

## 归档原因

1. **领域错误**：`AnomalyEvent`（severity×occurrence×detection_difficulty）和 `RPNCalculation` 来自 FMEA 汽车故障分析方法论，与 OpenClaw 治理系统无关。
2. **架构不兼容**：`IEventBus` 使用内存 pub/sub，与 `isolatedSession:true`（每次 heartbeat 独立 LLM 会话）根本不兼容。
3. **已被替代**：实际实现在 `skills/openclaw-governance/skills/openclaw-governance-nucleus/`（`core/` + `modules/`），不依赖此目录的任何代码。

## 不要恢复

这些代码不应被恢复到生产路径。如需参考历史设计思路，可在此目录查阅。
