# 交付物元数据规范（数据治理体系对齐版）

> **Topic**: N4-P2-T05
> **Task**: T5.3 - 交付物元数据规范设计（修订版）
> **PM**: 张铁 (CQO)
> **版本**: v2.0（对齐 ZT-2026-004 数据治理体系规范）
> **创建时间**: 2026-04-12
> **状态**: ✅ 草案（待 Harold 审批）

---

## 一、规范依据

本规范严格遵循以下数据治理体系规范：

| 规范 | 版本 | 关键条款 |
|------|------|----------|
| **ZT-2026-001** | v2.8 | 存储架构规范（文件命名、目录结构） |
| **ZT-2026-003** | - | 数据备份与归档规范 |
| **ZT-2026-004** | v2.3 | 数据治理体系规范（元数据管理、Quality Gate） |
| **ZT-2026-007** | v1.0 | 工作空间整理标准（分类处理规则） |

---

## 二、元数据规范（YAML Frontmatter）

### 2.1 通用元数据结构

所有交付物必须包含以下 YAML Frontmatter：

```yaml
---
# ==== 必填字段（Level 1）====
id: "{ZT-PXXX-TPXX-TXXX}"              # 唯一标识符，遵循命名规范
title: "{交付物标题}"                    # 交付物标题
type: "{内容类型码}"                    # REF-001：task/topic/project/decision/document
source: "{数据来源码}"                  # REF-003：generated/manual/external-report
created_at: "YYYY-MM-DDTHH:mm:ss+08:00" # 创建时间（ISO 8601, 东八区）
updated_at: "YYYY-MM-DDTHH:mm:ss+08:00" # 最后更新时间（ISO 8601, 东八区）
author: "{Agent 名称} ({角色})"          # 起草人（引用主数据 persons.yaml）
status: "draft | active | stale | archived | destroyed"  # REF-001：数据状态
privacy: "P1 | P2 | P3"                 # REF-004：隐私级别（P0 禁止进入团队知识库）

# ==== 可选字段（Level 2）====
version: "X.Y.Z"                        # 版本号
project_id: "{Project ID}"              # 归属项目
topic_id: "{Topic ID}"                  # 归属话题
task_id: "{Task ID}"                    # 归属任务
owner: "{Agent 名称} ({角色})"          # 负责人
pm: "{Agent 名称} ({角色})"             # Project Manager（项目级）
pmo: "{Agent 名称} ({角色})"            # PMO（可选）
review_level: "L0 | L1 | L2 | L3 | L4"  # Review 级别
priority: "P0 | P1 | P2 | P3"           # 优先级（Task 特有）

# ==== 扩展元数据（可选）====
tags: ["#{tag1}", "#{tag2}"]            # 标签（兼容 Obsidian）
metadata: {}                            # 扩展元数据（JSON 对象）

# ==== 质量检查字段（自动生成）====
confidence: 1.00                        # 置信度（0-1）
verified: false                         # 是否已验证
verified_by: ""                         # 验证人
verified_at: ""                         # 验证时间
---
```

### 2.2 必填字段说明（Level 1）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| **id** | string | 唯一标识符，遵循命名规范 | `ZT-P015-N4-P2-T05-T5.3` |
| **title** | string | 交付物标题 | `交付物元数据规范` |
| **type** | string | 内容类型码（REF-001） | `task` / `topic` / `project` / `document` |
| **source** | string | 数据来源码（REF-003） | `generated` / `manual` |
| **created_at** | string | 创建时间（ISO 8601, 东八区） | `2026-04-12T10:00:00+08:00` |
| **updated_at** | string | 最后更新时间（ISO 8601, 东八区） | `2026-04-12T11:00:00+08:00` |
| **author** | string | 起草人（引用主数据 persons.yaml） | `张铁 (CQO)` |
| **status** | string | 数据状态（REF-001） | `draft` / `active` / `stale` / `archived` / `destroyed` |
| **privacy** | string | 隐私级别（REF-004） | `P1` / `P2` / `P3`（P0 禁止） |

### 2.3 可选字段说明（Level 2）

| 字段 | 类型 | 说明 | 适用类型 |
|------|------|------|----------|
| **version** | string | 版本号 | 所有类型 |
| **project_id** | string | 归属项目 | Topic / Task |
| **topic_id** | string | 归属话题 | Task |
| **task_id** | string | 归属任务 | Deliverable |
| **owner** | string | 负责人 | 所有类型 |
| **pm** | string | Project Manager | Project / Topic |
| **pmo** | string | PMO | Project |
| **review_level** | string | Review 级别 | Task / Topic / Project |
| **priority** | string | 优先级 | Task |

---

## 三、参考数据代码表

### 3.1 REF-001：内容类型码

| 代码              | 名称     | 适用场景                            |
| ----------------- | -------- | ----------------------------------- |
| `task`           | 任务     | 有明确交付的行动项                  |
| `topic`          | 话题     | 项目细分主题                        |
| `project`        | 项目     | 独立的工作单元                      |
| `decision`       | 决策     | 需要证据链的决策记录                |
| `document`       | 文档     | 正式发布的文件（规范、模板等）      |
| `reference`      | 参考资料 | 外部引入的参考内容                  |
| `learning`       | 经验教训 | 复盘总结                            |
| `best-practice`  | 最佳实践 | 可复用的方法论                      |

### 3.2 REF-003：数据来源码

| 代码                | 名称     | 说明                |
| ------------------- | -------- | ------------------- |
| `generated`         | AI 生成  | Agent 推理/总结产出 |
| `manual`            | 手工录入 | 人工直接输入        |
| `external-report`   | 外部报告 | 行业报告/竞品分析等 |

### 3.3 REF-004：隐私级别码

| 代码   | 名称 | 存储限制        | Agent 访问           |
| ------ | ---- | --------------- | -------------------- |
| `P0` | 绝密 | LOCAL 加密 only | 禁止                 |
| `P1` | 内部 | LOCAL only      | 仅所属 Agent         |
| `P2` | 团队 | LOCAL + CLOUD   | 全体 Agent（按权限） |
| `P3` | 公开 | 全渠道          | 所有人               |

### 3.4 REF-001（续）：数据状态码

| 状态          | 说明                  | 下一步动作           |
| ------------- | --------------------- | -------------------- |
| `draft`       | 草稿                  | 提交审核             |
| `active`      | 活跃                  | 定期检查 Stale       |
| `stale`       | 过期                  | 归档或更新           |
| `archived`    | 已归档                | 只读访问             |
| `destroyed`   | 已销毁                | 不可访问             |

---

## 四、各类型交付物元数据规范

### 4.1 TASK-CARD 元数据

```yaml
---
# ==== 必填字段（Level 1）====
id: "N4-P2-T05-T5.3"
title: "交付物元数据规范设计"
type: "task"
source: "generated"
created_at: "2026-04-12T10:00:00+08:00"
updated_at: "2026-04-12T11:30:00+08:00"
author: "张铁 (CQO)"
status: "active"
privacy: "P2"

# ==== 可选字段（Level 2）====
version: "2.0"
project_id: "ZT-P015"
topic_id: "N4-P2-T05"
owner: "张铁 (CQO)"
pm: "张铁 (CQO)"
review_level: "L3"
priority: "P0"

# ==== 扩展元数据（可选）====
tags: ["#task", #research", "#metadata"]
metadata: {
  "deliverable_type": "spec",
  "estimated_hours": 4
}

# ==== 质量检查字段（自动生成）====
confidence: 1.00
verified: true
verified_by: "Harold Tsui"
verified_at: "2026-04-12T11:00:00+08:00"
---
```

### 4.2 TOPIC-BRIEF 元数据

```yaml
---
# ==== 必填字段（Level 1）====
id: "N4-P2-T05"
title: "OpenViking 交付物识别与 Obsidian 知识图谱兼容"
type: "topic"
source: "generated"
created_at: "2026-04-12T09:00:00+08:00"
updated_at: "2026-04-12T11:30:00+08:00"
author: "张铁 (CQO)"
status: "active"
privacy: "P2"

# ==== 可选字段（Level 2）====
version: "1.3"
project_id: "ZT-P015"
owner: "张铁 (CQO)"
pm: "张铁 (CQO)"
review_level: "L3"

# ==== 扩展元数据（可选）====
tags: ["#topic", "#openviking", "#obsidian"]
---
```

### 4.3 PROJECT-CHARTER 元数据

```yaml
---
# ==== 必填字段（Level 1）====
id: "ZT-P015"
title: "NUCLEUS 4.0 - 自动进化内核"
type: "project"
source: "generated"
created_at: "2026-04-02T10:00:00+08:00"
updated_at: "2026-04-12T11:30:00+08:00"
author: "张铁 (CQO)"
status: "active"
privacy: "P2"

# ==== 可选字段（Level 2）====
version: "3.2"
owner: "张铁 (CQO)"
pm: "张铁 (CQO)"
pmo: "银月 (PMO)"
review_level: "L4"
priority: "P0"

# ==== 扩展元数据（可选）====
tags: ["#project", "#nucleus", "#pdca"]
---
```

---

## 五、文件命名规范（对齐 ZT-2026-001）

### 5.1 标准命名格式

```
YYYY-MM-DD_{Title}_{Type}_{Duty}_{Status}.md
```

**示例**：
- `2026-04-12_Task_Metadata_Spec_cqo_active.md`
- `2026-04-12_Topic_Brief_cqo_active.md`
- `2026-04-02_Project_Charter_cqo_active.md`

### 5.2 命名规则

| 字段 | 说明 | 示例 |
|------|------|------|
| **YYYY-MM-DD** | 创建日期 | `2026-04-12` |
| **{Title}** | 标题简写（无空格，驼峰） | `Task_Metadata_Spec` |
| **{Type}** | 内容类型简写 | `Task` / `Topic` / `Project` |
| **{Duty}** | 负责人职务缩写 | `cqo` / `ceo` / `cto` |
| **{Status}** | 状态 | `draft` / `active` / `archived` |

### 5.3 版本控制

**变更时添加 `_vN` 后缀**：

```
YYYY-MM-DD_{Title}_{Type}_{Duty}_{Status}_v{N}.md
```

**示例**：
- `2026-04-12_Task_Metadata_Spec_cqo_active.md` → `2026-04-12_Task_Metadata_Spec_cqo_active_v1.md`

---

## 六、Obsidian 兼容性

### 6.1 标签格式

**方式 1**：YAML Frontmatter 中（推荐）

```yaml
tags: ["#tag1", "#tag2", "#tag3"]
```

**方式 2**：正文中（兼容）

```markdown
Tags: #tag1 #tag2 #tag3
```

### 6.2 Wikilink 规范

**基本语法**：

```markdown
[[目标名称]]
[[目标名称|显示文本]]
```

**命名规范**：

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| **Task** | `{Task ID}` | `[[N4-P2-T05-T5.3]]` |
| **Topic** | `{Topic ID}` | `[[N4-P2-T05]]` |
| **Project** | `{Project ID}` | `[[ZT-P015]]` |
| **文档** | `{文件名}` | `[[交付物元数据规范]]` |

---

## 七、Quality Gate（对齐 ZT-2026-004）

### 7.1 入库质量门禁

**Level 1：必须通过（否则拒绝入库）**

- ✅ **元数据完整性**：id / title / type / source / created_at / updated_at / author / status / privacy 必填
- ✅ **隐私级别标注**：未标注的数据默认 P1，禁止进入团队知识库
- ✅ **格式合规**：时间戳符合 ISO 8601 格式，枚举值符合数据元定义表
- ✅ **P0 隔离**：P0 数据不得进入团队知识库

**Level 2：建议通过（给出警告但允许入库）**

- ⚠️ **元数据完整率** ≥ 95%（ZT-2026-004 要求）
- ⚠️ **文件命名规范**：符合 ZT-2026-001 命名格式

### 7.2 质量检查脚本

```python
#!/usr/bin/env python3
import yaml
from datetime import datetime
from pathlib import Path

def check_metadata(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        yaml_content = content.split('---')[1]
        metadata = yaml.safe_load(yaml_content)

    # Level 1 检查
    required_fields = ['id', 'title', 'type', 'source', 'created_at', 'updated_at', 'author', 'status', 'privacy']
    missing_fields = [field for field in required_fields if field not in metadata]

    if missing_fields:
        return False, f"缺少必填字段: {missing_fields}"

    # 隐私级别检查
    if metadata.get('privacy') == 'P0':
        return False, "P0 数据禁止进入团队知识库"

    # 时间戳格式检查
    for field in ['created_at', 'updated_at']:
        try:
            datetime.fromisoformat(metadata[field].replace('+08:00', ''))
        except ValueError:
            return False, f"{field} 时间戳格式错误"

    return True, "质量检查通过"

if __name__ == '__main__':
    file_path = Path('TASK-CARD-N4-P2-T05-T5.3.md')
    passed, message = check_metadata(file_path)
    print(f"{'✅' if passed else '❌'} {message}")
```

---

## 八、向后兼容性

### 8.1 现有文件升级

**原则**：
- 保留现有字段，不删除
- 新增字段使用默认值
- 渐进式升级，不破坏现有功能

### 8.2 迁移路径

| 阶段 | 行动 | 状态 |
|------|------|------|
| **Phase 1** | 升级现有 8 个 Skill | ✅ 已完成 |
| **Phase 2** | 升级 TASK-CARD 模板 | 📋 待开始 |
| **Phase 3** | 升级 PROJECT-CHARTER 模板 | 📋 待开始 |
| **Phase 4** | 升级 TOPIC-BRIEF 模板 | 📋 待开始 |
| **Phase 5** | 批量迁移现有交付物 | 📋 待开始 |

---

## 九、审核与批准

| 日期 | 审核人 | 意见 | 状态 |
|------|--------|------|------|
| 2026-04-12 | 张铁 (CQO) | 规范草案完成（对齐 ZT-2026-004） | ⏸️ 待 Harold 审批 |

---

*v2.0 | 创建：2026-04-12 | PM：张铁 | 状态：⏸️ 待 Harold 审批 | 对齐：ZT-2026-004 数据治理体系规范*