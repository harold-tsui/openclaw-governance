# DOD (Definition of Done) 模板

> **用途**：结构化验收标准定义
> **版本**：v1.0
> **所属 Skill**：openclaw-governance-quality

---

## 使用说明

1. 在 TASK-CARD 中复制此模板
2. 根据任务特点填写具体标准
3. DOD 创建后自动锁定，Builder 不可修改
4. 由 Reviewer 验证并标记状态

---

## 模板内容

### 必须完成

| # | 验收标准 | 状态 | 验证人 | 验证时间 |
|---|----------|------|--------|----------|
| 1 | [具体标准 1] | ⬜ | [reviewer] | [date] |
| 2 | [具体标准 2] | ⬜ | [reviewer] | [date] |
| 3 | [具体标准 3] | ⬜ | [reviewer] | [date] |

### 质量标准

- [ ] 所有设计决策有理由说明
- [ ] 代码/文档符合格式规范
- [ ] 无遗留 TODO 或调试代码
- [ ] 相关文档已更新

### DOD 元数据（锁定）

```json
{
  "dod_version": "1.0",
  "dod_set_by": "[agent]",
  "dod_set_at": "[timestamp]",
  "dod_locked": true,
  "dod_automation_level": "[L0-L5]"
}
```

---

## 标准类别参考

| 类别 | 说明 | 示例 |
|------|------|------|
| **functional** | 功能性 | 用户可以通过 API 创建任务 |
| **testing** | 测试 | 单元测试覆盖率 ≥ 80% |
| **documentation** | 文档 | API 文档已更新 |
| **quality** | 质量 | 代码通过 ESLint 检查 |
| **security** | 安全 | 敏感数据已加密 |
| **performance** | 性能 | API 响应时间 < 100ms |

---

## 状态标记

| 标记 | 含义 |
|------|------|
| ⬜ | 待验证 |
| ✅ | 已通过 |
| ❌ | 未通过 |
| ⚠️ | 部分通过 |

---

*模板版本：v1.0 | 所属 Skill：openclaw-governance-quality v3.0.0*