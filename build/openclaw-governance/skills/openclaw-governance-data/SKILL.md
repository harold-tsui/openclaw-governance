---
name: governing-data
description: |
  Governing data, documentation, and knowledge base with validation, classification, and backup.
  
  Activates when: Data governance, path validation, backup operations, or data classification needed
  
  Capabilities:
  - Path validation and suggestion
  - Data classification (P0-P3 security levels)
  - Gate check for data operations
  - Full backup strategy and recovery
  - YAML Frontmatter compliance
  
  Keywords: data, governance, path-validation, backup, classification, documentation
  
  For detailed documentation, see:
  - references/data-details.md
  - scripts/ (backup and recovery scripts)

author: "辛如音 (cdo)"
license: "Internal Use Only"
version: "5.1.0"
allowed-tools: [bash, filesystem]
metadata:
  level: "L1"
  os: ["darwin", "linux"]
  tags: ["data-governance", "path-validation", "backup", "classification", "p0-p3"]
---

# 数据治理 · Skill

Tags: #governance, #data, #documentation, #knowledge-base, #path-validation

> **触发模式**：描述匹配触发 + 模型主动 read()
> **v5.1.0**: 补充 When to Use / Pitfalls 章节

## 何时使用

- **Path validation**: 创建或访问任何文件前（按 ZT-2026-007 验证路径格式）
- **Data classification**: 确定文件或操作的 P0-P3 分级
- **Backup/restore**: P2/P3 文件的全量或增量备份
- **Gate check**: 任何数据操作前，运行 Gate 检查
- **Do NOT use for**: 配置加载 — 那是 `governance-config` 的职责

## 常见陷阱

1. **黑名单路径是绝对的**: `/tmp/`、`/etc/`、`../`、`.env*`、`*.key` 永远被拒绝 — 没有例外。如果合法文件匹配黑名单模式，使用替代位置。
2. **P0 数据绝不同步**: 绝密数据（密码、密钥、API Token）绝不能离开本地存储。不飞书同步、不云备份、没有例外。
3. **备份范围仅限 P2/P3**: 全量和增量备份只包含 P2（团队）和 P3（公开）文件。P0 和 P1 按设计排除在备份之外。
4. **Gate check 失败 = 拒绝**: 任何 Gate check 项失败（路径格式、分级、黑名单、权限），操作被拒绝 — 不是延期、不是警告。

---

## 一、规范引用

| 规范/配置 | 版本 | 路径 | 用途 |
|------|------|------|------|
| **ZT-2026-007** | v1.1 | standards/ZT-2026-007_工作空间整理标准.md | 路径校验依据 |
| **ZT-2026-004** | v2.0 | standards/ZT-2026-004_数据治理体系规范.md | 数据分级依据 |
| **ZT-2026-003** | v4.0 | standards/ZT-2026-003_数据备份与归档规范.md | 备份策略依据 |
| **data-classification.yaml** | v1.0 | .system/governance/current/config/system/data-classification.yaml | 数据分级配置表 |

---

## 二、路径校验（摘要）

### 路径规则

| 类型 | 格式 | 示例 |
|------|------|------|
| 项目目录 | `10_Projects/{PROJECT_ID}_{Name}/` | 10_Projects/ZT-P009_NUCLEUS-2-0/ |
| Topic 目录 | `{project_dir}/T{序号}-{描述}/` | ZT-P009/T01-Architecture-Design/ |
| Agent 目录 | `60_Agents/{agent_id}/` | 60_Agents/cto/ |
| 技能目录 | `skills/{skill-name}/` | skills/openclaw-governance-core/ |

**黑名单**：`/tmp/`, `/etc/`, `../`, `.env*`, `*.key`

### validate_path()
- **输入**：`{path, expected_type}`
- **输出**：`{valid, error?, suggestion?}`

> 详细路径规则、验证函数：[references/data-details.md]({baseDir}/references/data-details.md)

---

## 三、数据分级（摘要）

| 级别 | 名称 | 存储 | 同步 | 示例 |
|------|------|------|------|------|
| **P0** | 绝密 | 仅本地 | 禁止 | 密码、密钥 |
| **P1** | 内部 | 仅本地 | 禁止 | 内部文档 |
| **P2** | 团队 | 本地 + 飞书 | 按需 | 项目文档 |
| **P3** | 公开 | 本地 + 飞书 + 外部 | 全量 | 公开报告 |

---

## 四、Gate Check（摘要）

| 检查项 | 说明 | 失败处理 |
|--------|------|---------|
| 路径格式 | 符合 ZT-2026-007 | 建议正确格式 |
| 数据分级 | 有明确 P0-P3 级别 | 拒绝操作 |
| 黑名单 | 不在黑名单中 | 拒绝操作 |
| 权限 | 操作者有权限 | 拒绝 + 上报 |

---

## 五、备份策略（摘要）

| 类型 | 频率 | 内容 | 保留期 |
|------|------|------|--------|
| **全量备份** | 每周 | 所有 P2/P3 文件 | 30 天 |
| **增量备份** | 每日 | 变更的 P2/P3 文件 | 7 天 |
| **归档** | 项目结项时 | 项目全部交付物 | 永久 |

### backup() / restore()
- **backup**: `{scope: full|incremental, target_dir}` → `{status, backup_path, file_count}`
- **restore**: `{backup_path, target_dir}` → `{status, restored_count, errors}`

> 详细备份策略、恢复流程：[references/data-details.md]({baseDir}/references/data-details.md)

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **5.0.0** | 2026-04-22 | SKILL.md 瘦身至 <200 行，详细内容移至 references/data-details.md |

---

*版本: 5.1.0 | 更新: 2026-04-23 | 变更: 补充 When to Use / Pitfalls 章节*

## Related Skills
- [[openclaw-governance-config]] - 配置管理，data-classification.yaml 加载
- [[openclaw-governance-hierarchy]] - 层级管理，路径校验规则
- [[openclaw-governance-knowledge]] - 知识管理，数据同步到飞书
