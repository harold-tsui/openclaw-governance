# Agent 初始化与升级流程

> **文件性质**：治理流程规范（执行协议）
> **触发方**：银月（main Agent）
> **版本**：v1.0
> **日期**：2026-04-18
> **关联 Skill**：governance-core v6.1.8 + governance-agent v1.1.0

---

## 一、两种场景

| 场景 | 触发条件 | 执行范围 | 执行方 |
|------|---------|---------|--------|
| **Agent 初始化**（入职） | 新 Agent 创建 | 创建所有 7 个核心文件 | 银月 |
| **Skill 升级同步** | 模板版本号变更 | 仅更新受影响的文件 | 银月 → 各 Agent |

---

## 二、Agent 初始化流程（新 Agent 入职）

### 2.1 文件创建清单

| # | 文件 | 来源模板 | 必填变量 |
|---|------|---------|---------|
| 1 | `IDENTITY.md` | TMPL-IDENTITY-SUB.md | agent_id, agent_name, role, domain, language, authorization_scope, core_mission |
| 2 | `SOUL.md` | TMPL-SOUL-SUB.md | agent_id, agent_name, global_soul_version, agent_specific_mission, agent_specific_north_star |
| 3 | `AGENTS.md` | TMPL-AGENTS-SUB.md | agent_id, agent_name, ESCALATION_TO, ESCALATION_URGENT |
| 4 | `TOOLS.md` | TMPL-TOOLS-SUB.md | agent_id, agent_name |
| 5 | `USER.md` | TMPL-USER-SUB.md | agent_id, agent_name |
| 6 | `HEARTBEAT.md` | 参考现有 Agent 格式 | agent_id, agent_name, 职责-specific 检查项 |
| 7 | `MISSION_BOARD.md` | TMPL-MISSION_BOARD.md | AGENT_NAME, AGENT_ROLE |

### 2.2 创建步骤

```
1. 确认 persons.yaml 中注册该 Agent（id, name, role, domain）
2. 创建 60_Agents/{agent_id}/ 目录
3. 按模板逐文件展开变量 → 写入
4. 验证：每个文件顶部版本号、路径变量正确
5. 创建 Onboarding Task Card
6. 通知 Harold 审批
```

### 2.3 命名一致性

- 文件名统一使用 `MISSION_BOARD.md`（不是 `MISSIONBOARD.md`）
- 路径变量统一使用 `${OPENCLAW_*}` 前缀

---

## 三、Skill 升级同步流程

### 3.1 版本检测

银月在每次 Heartbeat Step 7 中执行版本检测：

```
1. 读取 governance-core/templates/ 下所有模板的版本号
   → 从文件底部 *Version: vX.Y* 行提取
2. 读取 60_Agents/{agent_id}/ 下对应文件的版本号
   → 从文件底部 *Version: vX.Y* 行提取
3. 比对：TEMPLATE_VERSION vs LOCAL_VERSION
4. 不一致 → 触发同步流程
```

### 3.2 同步决策矩阵

| 变更类型 | 影响范围 | 同步策略 |
|---------|---------|---------|
| **模板结构变更**（新增/删除章节） | 所有 Agent | 银月读取新模板 → 合并差异 → 写入各 Agent → 更新版本号 |
| **模板路径变量修正** | 所有 Agent | 银月执行全局替换 `${AGENT_*}` → `${OPENCLAW_AGENT_*}` |
| **模板内容精简**（删除过时章节） | 所有 Agent | 删除对应章节，保留 Agent 自定义内容 |
| **Agent 自定义内容**（如 CQO 审核标准） | 仅该 Agent | 不变更，保留 |

### 3.3 同步执行步骤

```
for 每个版本不一致的 Agent 文件:
    1. 读取新模板全文
    2. 读取 Agent 当前文件全文
    3. 识别 Agent 自定义内容（不在模板中的独有章节）
    4. 生成新版本：模板结构 + Agent 自定义内容
    5. 更新文件底部版本号 = 模板版本号
    6. 更新文件底部 LAST_SYNC_DATE = 当前日期
    7. 写入文件

    # 验证
    8. 确认路径变量格式正确（${OPENCLAW_*}）
    9. 确认版本号与模板一致
    10. 确认 Agent 自定义内容未丢失
```

### 3.4 通知策略

| 变更严重度 | 通知方式 |
|-----------|---------|
| 路径变量修正 | 静默同步，Heartbeat 汇报 |
| 模板结构变更（章节级） | Heartbeat 简报变更要点 |
| Agent 核心行为变更（如 AGENTS.md 加载策略） | 向 Harold 简报 |

---

## 四、已知的版本不一致（2026-04-18 基线）

| Agent | 文件 | 问题 | 修复动作 |
|-------|------|------|---------|
| cto | IDENTITY.md | 路径变量 `${AGENT_LOCAL_WORKSPACE}` / `${LOCAL_WORKSPACE}` → `${OPENCLAW_*}` | 已修复 |
| cto | IDENTITY.md | persons.yaml 路径指向旧 `.system/master_data/` | 已修复 |
| cto | 目录 | 同时存在 `MISSION_BOARD.md` 和 `MISSIONBOARD.md` | 需清理 MISSIONBOARD.md |
| cdo | 目录 | 同时存在 `MISSION_BOARD.md` 和 `MISSIONBOARD.md` | 需清理 MISSIONBOARD.md |
| cqo | TOOLS.md | Skill 路径仍记录 `~/.openclaw/skills/` | 需更新 |
| cqo | TOOLS.md | Skill 版本号过期（v6.1.0 vs v6.1.8） | 需更新 |
| 所有 Agent | AGENTS.md | 模板声称"自动注入"但实际手动 read | 模板已修复，待同步 |
| 所有 Agent | TOOLS.md | 模板 369 行过长，精简为 v2.0 | 模板已修复，待同步 |

---

## 五、模板同步检查清单（银月 Heartbeat 时执行）

- [ ] governance-core/templates/ 下每个模板版本已记录
- [ ] 60_Agents/{agent_id}/ 下每个文件版本已读取
- [ ] 版本号对比完成，不一致项已列出
- [ ] 同步决策矩阵已应用
- [ ] 文件已更新
- [ ] 版本号已对齐
- [ ] Agent 自定义内容未丢失
- [ ] Heartbeat 汇报中提及同步结果

---

*本流程由 N4-P1-T07 开发，v1.0 于 2026-04-18 创建。*
