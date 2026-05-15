# Data Governance — Detailed Reference

> Moved from data SKILL.md to reduce main file size.

## §二 路径校验

### 路径规则

| 规则 | 说明 | 示例 |
|------|------|------|
| 工作空间根目录 | ${OPENCLAW_LOCAL_WORKSPACE} | ~/Workspaces/openclaw/main |
| 项目目录 | 10_Projects/{PROJECT_ID}_{Name}/ | 10_Projects/ZT-P009_NUCLEUS-2-0/ |
| Topic 目录 | {project_dir}/T{序号}-{描述}/ | ZT-P009/T01-Architecture-Design/ |
| Agent 目录 | 60_Agents/{agent_id}/ | 60_Agents/cto/ |
| 技能目录 | skills/{skill-name}/ | skills/openclaw-governance-core/ |

### 黑名单路径

| 黑名单 | 说明 |
|--------|------|
| /tmp/ | 临时目录 |
| /etc/ | 系统目录 |
| ../ | 父目录遍历 |
| .env* | 环境文件 |
| *.key | 密钥文件 |

### validate_path() 函数
- **Input**: `{path, expected_type: project|topic|agent|skill}`
- **Output**: `{valid, error?, suggestion?}`
- **Logic**: 检查根目录 → 检查格式 → 检查黑名单 → 返回结果

## §三 数据分级

| 级别 | 名称 | 存储位置 | 同步策略 | 示例 |
|------|------|---------|---------|------|
| **P0 (绝密)** | 最高机密 | 仅本地 | 禁止同步 | 密码、密钥、API Token |
| **P1 (内部)** | 内部使用 | 仅本地 | 禁止同步 | 内部文档、会议纪要 |
| **P2 (团队)** | 团队共享 | 本地 + 飞书 | 按需同步 | 项目文档、交付物 |
| **P3 (公开)** | 公开可分享 | 本地 + 飞书 + 外部 | 全量同步 | 公开报告、博客 |

## §四 Gate Check

| 检查项 | 说明 | 失败处理 |
|--------|------|---------|
| 路径格式 | 符合 ZT-2026-007 | 建议正确格式 |
| 数据分级 | 有明确 P0-P3 级别 | 拒绝操作 |
| 黑名单 | 不在黑名单中 | 拒绝操作 |
| 权限 | 操作者有权限 | 拒绝 + 上报 |

## §五 备份策略

| 类型 | 频率 | 内容 | 保留期 |
|------|------|------|--------|
| **全量备份** | 每周 | 所有 P2/P3 文件 | 30 天 |
| **增量备份** | 每日 | 变更的 P2/P3 文件 | 7 天 |
| **归档** | 项目结项时 | 项目全部交付物 | 永久 |

### backup() 函数
- **Input**: `{scope: full|incremental, target_dir}`
- **Logic**: 扫描文件 → 按分级过滤 → 复制/压缩 → 记录备份元数据
- **Output**: `{status, backup_path, file_count}`

### restore() 函数
- **Input**: `{backup_path, target_dir}`
- **Logic**: 验证备份完整性 → 解压 → 恢复文件
- **Output**: `{status, restored_count, errors}`
