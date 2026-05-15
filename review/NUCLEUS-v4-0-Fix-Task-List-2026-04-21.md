# NUCLEUS v4.0 修复任务清单

**生成时间**: 2026-04-21  
**基于**: Code Review Report v1.0  
**项目**: ZT-P015_NUCLEUS-4-0  
**优先级分级**: P0 (立即) → P1 (1月内) → P2 (3月内) → P3 (6月内)

---

## P0 - 立即修复（本周内完成）

### 🔴 P0-1: 并发控制强制执行

**问题描述**:
- `pdca.py` L856-925 `check_concurrency()` 只检查不阻止
- LLM 可能忽略返回值继续调用 `p()`，导致超出并发上限

**影响**: 高并发场景下可能突破 task/topic/project 并发限制

**修复方案**:
```python
# 在 p() 函数开头强制检查
def p(...):
    # 第一步：强制并发检查
    concurrency_check = check_concurrency('task')
    if not concurrency_check['ok']:
        return concurrency_check  # 直接返回错误，阻止执行
    
    # 原有逻辑...
```

**验证方式**:
1. 创建测试：同时创建 11 个 task（超过上限 10）
2. 第 11 个应返回 `ok=false` 且不创建 cycle

**文件位置**: `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py`

**估算工时**: 2 小时

---

### 🔴 P0-2: CWD 漂移修复

**问题描述**:
- `pdca.py` L72-77 `_setup()` 使用 `os.chdir(skill_root)`
- 多线程场景下可能导致 CWD 冲突

**影响**: 路径解析错误，文件读写失败

**修复方案**:
```python
# 方案1：使用绝对路径，移除 os.chdir()
SKILL_ROOT = Path(__file__).parent.parent.resolve()
PDCA_DIR = SKILL_ROOT / "pdca"
STATE_FILE = SKILL_ROOT / "pdca" / "_state.yaml"

# 方案2：如果必须使用相对路径，每次操作时临时切换
def _with_correct_cwd(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        original_cwd = os.getcwd()
        try:
            os.chdir(SKILL_ROOT)
            return func(*args, **kwargs)
        finally:
            os.chdir(original_cwd)
    return wrapper
```

**推荐**: 方案 1（移除 CWD 依赖）

**验证方式**:
1. 在不同目录下运行 `python -c "from pdca import p; p(...)"`
2. 验证所有路径操作正确

**文件位置**: `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py`

**估算工时**: 3 小时

---

### 🔴 P0-3: 审计闭环集成

**问题描述**:
- README.md §Phase 2 剩余：T06.6 审计出口集成标注"待开始"
- 审计队列已设计（`audit-queue` 命令）但无消费者

**影响**: 质量闭环断裂，L0/L1 通过的任务无后续审计

**修复方案**:

#### 步骤 1: 创建 heartbeat-audit Task-CARD

```yaml
# 路径: 10_Projects/SYS-GOV/tasks/HEARTBEAT-AUDIT_TASK-CARD.md

task_id: HEARTBEAT-AUDIT
task_name: 每日审计队列处理
task_pm: 银月
review_level: L1
schedule: "0 7 * * *"  # 每日 07:00

description: |
  每日自动获取审计队列，LLM 评分后记录审计结果。
  
  执行步骤：
  1. 调用 `pdca.py audit-queue` 获取待审计列表
  2. 对每个 cycle_id，LLM 读取 Task-CARD 和执行日志
  3. 评分 0-100（依据质量标准）
  4. 调用 `pdca.py mark-audit --cycle-id {id} --score {score}`
```

#### 步骤 2: 集成到 HEARTBEAT.md

```markdown
# 60_Agents/main/HEARTBEAT.md

Step 3: 任务巡检与推进
  3.4 审计队列处理 ⭐ 新增
    - 调用 `pdca.py audit-queue`
    - 若有待审计项，逐个评分并调用 `mark-audit`
```

#### 步骤 3: 测试审计流程

1. 手工创建一个 L0 task 并 pass
2. 验证 `audit-queue` 能列出该 cycle
3. 调用 `mark-audit --cycle-id xxx --score 85`
4. 验证 pdca/xxx.yaml 中 `audit_score: 85` 已记录

**文件位置**: 
- `10_Projects/SYS-GOV/tasks/HEARTBEAT-AUDIT_TASK-CARD.md`
- `60_Agents/main/HEARTBEAT.md`

**估算工时**: 4 小时

---

## P1 - 高优先级（1 个月内完成）

### 🟡 P1-1: 写穿透校验函数

**问题描述**:
- `pdca.py` L399 注释：依赖 LLM 纪律更新 Task-CARD 和 MISSION_BOARD
- 无强制校验机制

**影响**: 状态不一致风险，MISSION_BOARD 可能与 pdca 实际状态不同步

**修复方案**:

```python
# 新增函数：verify_writethrough()

def verify_writethrough(cycle_id: str) -> Dict[str, Any]:
    """
    校验 Task-CARD 和 MISSION_BOARD 状态是否与 pdca 一致
    
    Returns:
        {
            'ok': bool,
            'cycle_id': str,
            'pdca_phase': str,
            'pdca_verdict': str,
            'task_card_status': str,  # 从 Task-CARD 读取
            'mission_board_status': str,  # 从 MISSION_BOARD 读取
            'inconsistencies': List[str]  # 不一致项列表
        }
    """
    # 1. 读取 pdca/{cycle_id}.yaml
    cycle_data = _read_cycle(cycle_id)
    pdca_phase = cycle_data.get('last_phase')
    pdca_verdict = cycle_data.get('check', {}).get('verdict')
    
    # 2. 解析 cycle_id 获取 task_card_path
    # 假设 cycle_id 格式: task:ZT-P015-T001
    parts = cycle_id.split(':')
    if len(parts) != 2:
        return {'ok': False, 'error': 'Invalid cycle_id format'}
    
    entity_type, entity_id = parts
    task_card_path = f'10_Projects/{entity_id}_TASK-CARD.md'
    
    # 3. 读取 Task-CARD 状态标记
    task_card_status = _parse_task_card_status(task_card_path)
    
    # 4. 读取 MISSION_BOARD 对应行
    mission_board_status = _parse_mission_board_status(entity_id)
    
    # 5. 一致性检查
    inconsistencies = []
    
    # 规则1: phase=completed + verdict=pass → Task-CARD 应为 [x]
    if pdca_phase == 'completed' and pdca_verdict == 'pass':
        if task_card_status != '[x]':
            inconsistencies.append(f'Task-CARD 应为 [x]，实际为 {task_card_status}')
        if mission_board_status != 'done':
            inconsistencies.append(f'MISSION_BOARD 应为 done，实际为 {mission_board_status}')
    
    # 规则2: phase=check + verdict=pending → Task-CARD 应为 [V]
    if pdca_phase == 'check' and pdca_verdict == 'pending':
        if task_card_status != '[V]':
            inconsistencies.append(f'Task-CARD 应为 [V]，实际为 {task_card_status}')
    
    return {
        'ok': len(inconsistencies) == 0,
        'cycle_id': cycle_id,
        'pdca_phase': pdca_phase,
        'pdca_verdict': pdca_verdict,
        'task_card_status': task_card_status,
        'mission_board_status': mission_board_status,
        'inconsistencies': inconsistencies
    }


def _parse_task_card_status(task_card_path: str) -> str:
    """从 Task-CARD 中解析状态标记 [ ] / [V] / [x] / [?]"""
    # 实现：读取文件，正则匹配状态标记
    pass


def _parse_mission_board_status(task_id: str) -> str:
    """从 MISSION_BOARD 中解析任务状态"""
    # 实现：读取 MISSION_BOARD.md，找到对应行，解析状态
    pass
```

**使用方式**:
```python
# LLM 在 a() 返回 ok=true 后，建议调用：
result = verify_writethrough(cycle_id)
if not result['ok']:
    print(f"⚠️ 写穿透检查失败: {result['inconsistencies']}")
```

**验证方式**:
1. 创建测试 cycle，故意不更新 Task-CARD
2. 调用 `verify_writethrough(cycle_id)`
3. 应返回 `ok=false` 并列出不一致项

**文件位置**: `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py`

**估算工时**: 6 小时

---

### 🟡 P1-2: 数据迁移脚本

**问题描述**:
- v1/v2 数据无法平滑迁移到 v4
- README.md §项目 lineage 描述了演进路径但无实现

**影响**: 历史数据丢失，无法追溯演进过程

**修复方案**:

```python
# scripts/migrate_v1_to_v4.py

import yaml
from pathlib import Path
from typing import Dict, List

def migrate_v1_to_v4(v1_pdca_dir: Path, v4_pdca_dir: Path, dry_run: bool = True) -> Dict:
    """
    将 v1.0 的 PDCA cycle 数据迁移到 v4.0 格式
    
    v1 结构:
        pdca/
          task/
            ZT-P005-T001.yaml
          topic/
            ZT-P005-T001.yaml
    
    v4 结构:
        pdca/
          task:ZT-P005-T001.yaml
          topic:ZT-P005-T001.yaml
    
    字段映射:
        v1                    v4
        ─────────────────     ─────────────────
        cycle_id             → cycle_id
        entity_type          → (从 cycle_id 提取)
        entity_id            → (从 cycle_id 提取)
        last_phase           → last_phase
        plan.review_level    → plan.review_level
        check.verdict        → check.verdict
        check.reviewed_by    → check.reviewed_by
        (新增)               → audit_eligible
        (新增)               → audit_score
    """
    migrated = []
    errors = []
    
    # 遍历 v1 pdca 目录
    for entity_type_dir in v1_pdca_dir.iterdir():
        if not entity_type_dir.is_dir():
            continue
        
        entity_type = entity_type_dir.name  # task / topic / project
        
        for cycle_file in entity_type_dir.glob('*.yaml'):
            try:
                # 读取 v1 数据
                with open(cycle_file, 'r', encoding='utf-8') as f:
                    v1_data = yaml.safe_load(f)
                
                # 转换为 v4 格式
                entity_id = cycle_file.stem
                v4_cycle_id = f"{entity_type}:{entity_id}"
                
                v4_data = {
                    'cycle_id': v4_cycle_id,
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'last_phase': v1_data.get('last_phase'),
                    'plan': v1_data.get('plan', {}),
                    'do': v1_data.get('do', {}),
                    'check': v1_data.get('check', {}),
                    'act': v1_data.get('act', {}),
                    'created_at': v1_data.get('created_at'),
                    'updated_at': v1_data.get('updated_at'),
                }
                
                # 计算 audit_eligible (v4 新增)
                review_level = v4_data['plan'].get('review_level')
                verdict = v4_data['check'].get('verdict')
                if review_level in ('L0', 'L1') and verdict == 'pass':
                    v4_data['audit_eligible'] = True
                
                # 写入 v4 目录
                v4_file = v4_pdca_dir / f"{v4_cycle_id}.yaml"
                
                if not dry_run:
                    v4_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(v4_file, 'w', encoding='utf-8') as f:
                        yaml.dump(v4_data, f, allow_unicode=True, default_flow_style=False)
                
                migrated.append({
                    'v1_file': str(cycle_file),
                    'v4_file': str(v4_file),
                    'cycle_id': v4_cycle_id
                })
                
            except Exception as e:
                errors.append({
                    'file': str(cycle_file),
                    'error': str(e)
                })
    
    return {
        'migrated_count': len(migrated),
        'error_count': len(errors),
        'migrated': migrated,
        'errors': errors
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--v1-dir', required=True, help='v1.0 pdca 目录路径')
    parser.add_argument('--v4-dir', required=True, help='v4.0 pdca 目录路径')
    parser.add_argument('--dry-run', action='store_true', help='仅模拟，不实际写入')
    parser.add_argument('--execute', action='store_true', help='执行迁移')
    
    args = parser.parse_args()
    
    result = migrate_v1_to_v4(
        Path(args.v1_dir),
        Path(args.v4_dir),
        dry_run=not args.execute
    )
    
    print(f"✅ 迁移成功: {result['migrated_count']}")
    print(f"❌ 迁移失败: {result['error_count']}")
    
    if result['errors']:
        print("\n错误详情:")
        for err in result['errors']:
            print(f"  - {err['file']}: {err['error']}")
```

**使用方式**:
```bash
# 1. 先 dry-run 检查
python scripts/migrate_v1_to_v4.py \
  --v1-dir /path/to/nucleus-v1-archive/pdca \
  --v4-dir /path/to/nucleus-4.0/pdca \
  --dry-run

# 2. 确认无误后执行
python scripts/migrate_v1_to_v4.py \
  --v1-dir /path/to/nucleus-v1-archive/pdca \
  --v4-dir /path/to/nucleus-4.0/pdca \
  --execute
```

**文件位置**: `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/migrate_v1_to_v4.py`

**估算工时**: 8 小时

---

### 🟡 P1-3: 测试覆盖补充

**问题描述**:
- test/ 目录只有零散测试文件，无 CI 流程
- 当前覆盖率估计 30%

**目标**: 80% 覆盖率

**修复方案**:

#### 步骤 1: 创建 test_pdca.py

```python
# test/test_pdca.py

import pytest
import yaml
from pathlib import Path
from scripts.pdca import p, d, c, a, check_concurrency, verify_writethrough

@pytest.fixture
def temp_pdca_dir(tmp_path):
    """创建临时 pdca 目录"""
    pdca_dir = tmp_path / "pdca"
    pdca_dir.mkdir()
    return pdca_dir


class TestPlanFunction:
    """测试 p() 函数"""
    
    def test_p_success(self, temp_pdca_dir):
        """正常创建 plan"""
        result = p(
            cycle_id='task:TEST-001',
            review_level='L0',
            context='测试任务'
        )
        assert result['ok'] is True
        assert (temp_pdca_dir / 'task:TEST-001.yaml').exists()
    
    def test_p_duplicate_fails(self, temp_pdca_dir):
        """重复创建应失败"""
        p(cycle_id='task:TEST-001', review_level='L0', context='第一次')
        result = p(cycle_id='task:TEST-001', review_level='L1', context='第二次')
        assert result['ok'] is False
        assert 'already exists' in result['error']
    
    def test_p_concurrency_limit(self, temp_pdca_dir):
        """并发上限测试"""
        # 创建 10 个 task（上限）
        for i in range(10):
            p(cycle_id=f'task:TEST-{i:03d}', review_level='L0', context=f'Task {i}')
        
        # 第 11 个应失败
        result = p(cycle_id='task:TEST-011', review_level='L0', context='超限')
        assert result['ok'] is False
        assert 'concurrency limit' in result['error']


class TestDoFunction:
    """测试 d() 函数"""
    
    def test_d_after_plan(self, temp_pdca_dir):
        """Plan 后可调用 Do"""
        p(cycle_id='task:TEST-001', review_level='L0', context='测试')
        result = d(cycle_id='task:TEST-001', execution_log='执行中')
        assert result['ok'] is True
    
    def test_d_without_plan_fails(self, temp_pdca_dir):
        """未 Plan 不能 Do"""
        result = d(cycle_id='task:TEST-001', execution_log='直接执行')
        assert result['ok'] is False
        assert 'not found' in result['error']
    
    def test_d_phase_lock(self, temp_pdca_dir):
        """Phase 锁定测试"""
        p(cycle_id='task:TEST-001', review_level='L0', context='测试')
        c(cycle_id='task:TEST-001', verdict='pass')  # 跳到 check
        result = d(cycle_id='task:TEST-001', execution_log='回退到 Do')
        assert result['ok'] is False
        assert 'phase=' in result['error']


class TestCheckFunction:
    """测试 c() 函数"""
    
    def test_c_idempotency_protection(self, temp_pdca_dir):
        """幂等性防护测试"""
        p(cycle_id='task:TEST-001', review_level='L0', context='测试')
        c(cycle_id='task:TEST-001', verdict='pass')
        
        # 尝试覆盖 verdict
        result = c(cycle_id='task:TEST-001', verdict='fail')
        assert result['ok'] is False
        assert '不可静默覆盖' in result['warning']
    
    def test_c_l0_l1_no_pending(self, temp_pdca_dir):
        """L0/L1 不允许 verdict=pending"""
        p(cycle_id='task:TEST-001', review_level='L0', context='测试')
        result = c(cycle_id='task:TEST-001', verdict='pending')
        assert result['ok'] is False
        assert 'L0/L1' in result['error']


class TestActFunction:
    """测试 a() 函数"""
    
    def test_a_complete_cycle(self, temp_pdca_dir):
        """完整 PDCA 循环"""
        p(cycle_id='task:TEST-001', review_level='L0', context='测试')
        d(cycle_id='task:TEST-001', execution_log='执行完成')
        c(cycle_id='task:TEST-001', verdict='pass')
        result = a(cycle_id='task:TEST-001', action='归档')
        assert result['ok'] is True
        
        # 验证 phase=completed
        with open(temp_pdca_dir / 'task:TEST-001.yaml', 'r') as f:
            data = yaml.safe_load(f)
        assert data['last_phase'] == 'completed'


class TestConcurrency:
    """测试并发控制"""
    
    def test_check_concurrency_task_limit(self):
        """Task 并发上限 10"""
        # 创建 10 个活跃 task
        for i in range(10):
            p(cycle_id=f'task:TEST-{i:03d}', review_level='L0', context=f'Task {i}')
        
        result = check_concurrency('task')
        assert result['ok'] is False
        assert result['active_count'] == 10
        assert result['limit'] == 10


class TestWritethrough:
    """测试写穿透校验"""
    
    def test_verify_writethrough_consistent(self, temp_pdca_dir, tmp_path):
        """一致性检查通过"""
        # 创建 cycle
        p(cycle_id='task:TEST-001', review_level='L0', context='测试')
        c(cycle_id='task:TEST-001', verdict='pass')
        a(cycle_id='task:TEST-001', action='归档')
        
        # 同步更新 Task-CARD 和 MISSION_BOARD
        task_card = tmp_path / 'TEST-001_TASK-CARD.md'
        task_card.write_text('状态: [x]')
        
        result = verify_writethrough('task:TEST-001')
        assert result['ok'] is True
        assert len(result['inconsistencies']) == 0
    
    def test_verify_writethrough_inconsistent(self, temp_pdca_dir, tmp_path):
        """不一致检查失败"""
        # 创建 cycle 但不更新 Task-CARD
        p(cycle_id='task:TEST-001', review_level='L0', context='测试')
        c(cycle_id='task:TEST-001', verdict='pass')
        a(cycle_id='task:TEST-001', action='归档')
        
        task_card = tmp_path / 'TEST-001_TASK-CARD.md'
        task_card.write_text('状态: [ ]')  # 状态未更新
        
        result = verify_writethrough('task:TEST-001')
        assert result['ok'] is False
        assert len(result['inconsistencies']) > 0
        assert 'Task-CARD 应为 [x]' in result['inconsistencies'][0]


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=scripts.pdca', '--cov-report=term-missing'])
```

#### 步骤 2: 配置 pytest 和 coverage

```ini
# pytest.ini
[pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# .coveragerc
[run]
source = scripts
omit = 
    */test/*
    */migrations/*

[report]
precision = 2
skip_covered = False
show_missing = True
```

#### 步骤 3: 配置 CI (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: NUCLEUS Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install pytest pytest-cov pyyaml
      - run: pytest test/ --cov=scripts --cov-report=xml
      - uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

**文件位置**: 
- `test/test_pdca.py`
- `pytest.ini`
- `.coveragerc`
- `.github/workflows/test.yml`

**估算工时**: 12 小时

---

## P2 - 中优先级（3 个月内完成）

### 🟢 P2-1: 聚合算法增强

**问题描述**:
- `pdca.py` L678-688 `_aggregate_verdict()` 只有 4 条简单规则
- 无权重、无优先级、无阻塞任务特殊处理

**修复方案**:

```python
def _aggregate_verdict_v2(child_verdicts: List[Dict], weights: Dict[str, float] = None) -> str:
    """
    增强版聚合算法
    
    Args:
        child_verdicts: [
            {'cycle_id': 'task:T001', 'verdict': 'pass', 'priority': 'high', 'blocking': True},
            {'cycle_id': 'task:T002', 'verdict': 'fail', 'priority': 'low', 'blocking': False},
        ]
        weights: {'high': 2.0, 'medium': 1.0, 'low': 0.5}
    
    规则:
        1. 任一 blocking task fail → 父级 fail
        2. 所有 task pass → 父级 pass
        3. 加权评分 >= 80% → 父级 pass
        4. 加权评分 < 80% → 父级 partial
    """
    if not child_verdicts:
        return 'skip'
    
    # 规则1: 阻塞任务失败
    blocking_fails = [v for v in child_verdicts if v.get('blocking') and v['verdict'] == 'fail']
    if blocking_fails:
        return 'fail'
    
    # 规则2: 全部通过
    if all(v['verdict'] == 'pass' for v in child_verdicts):
        return 'pass'
    
    # 规则3: 加权评分
    weights = weights or {'high': 2.0, 'medium': 1.0, 'low': 0.5}
    
    total_weight = 0
    pass_weight = 0
    
    for v in child_verdicts:
        priority = v.get('priority', 'medium')
        weight = weights.get(priority, 1.0)
        total_weight += weight
        
        if v['verdict'] == 'pass':
            pass_weight += weight
    
    pass_rate = pass_weight / total_weight if total_weight > 0 else 0
    
    if pass_rate >= 0.8:
        return 'pass'
    else:
        return 'partial'
```

**文件位置**: `skills/openclaw-governance/skills/openclaw-governance-nucleus/scripts/pdca.py`

**估算工时**: 6 小时

---

### 🟢 P2-2: 监控仪表板

**问题描述**:
- 无实时可视化，难以快速了解系统状态

**修复方案**:

创建简单的 Web Dashboard（使用 Flask + Chart.js）

```python
# dashboard/app.py

from flask import Flask, render_template
import yaml
from pathlib import Path

app = Flask(__name__)

@app.route('/')
def index():
    """主仪表板"""
    pdca_dir = Path('../pdca')
    
    # 统计各层级 verdict 分布
    stats = {
        'task': {'pass': 0, 'fail': 0, 'partial': 0, 'pending': 0, 'skip': 0},
        'topic': {'pass': 0, 'fail': 0, 'partial': 0, 'pending': 0, 'skip': 0},
        'project': {'pass': 0, 'fail': 0, 'partial': 0, 'pending': 0, 'skip': 0},
    }
    
    for cycle_file in pdca_dir.glob('*.yaml'):
        with open(cycle_file, 'r') as f:
            data = yaml.safe_load(f)
        
        entity_type = data['entity_type']
        verdict = data.get('check', {}).get('verdict', 'unknown')
        
        if verdict in stats[entity_type]:
            stats[entity_type][verdict] += 1
    
    # 审计队列
    audit_queue = []
    for cycle_file in pdca_dir.glob('*.yaml'):
        with open(cycle_file, 'r') as f:
            data = yaml.safe_load(f)
        if data.get('audit_eligible') and not data.get('audit_score'):
            audit_queue.append({
                'cycle_id': data['cycle_id'],
                'entity_id': data['entity_id'],
                'review_level': data.get('plan', {}).get('review_level')
            })
    
    return render_template('index.html', stats=stats, audit_queue=audit_queue)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**文件位置**: 
- `dashboard/app.py`
- `dashboard/templates/index.html`

**估算工时**: 16 小时

---

## P3 - 低优先级（6 个月内完成）

### 🔵 P3-1: 函数命名改进

**问题**: `p() / d() / c() / a()` 可读性差

**修复方案**:
```python
# 保留简写别名，新增完整函数名
plan = p
do = d
check = c
act = a
```

**估算工时**: 1 小时

---

### 🔵 P3-2: 类型标注完整

**问题**: 部分函数缺少类型标注

**修复方案**:
```python
from typing import Dict, Any, Optional

def p(
    cycle_id: str,
    review_level: str,
    context: str,
    parent_cycle_id: Optional[str] = None
) -> Dict[str, Any]:
    ...
```

**估算工时**: 4 小时

---

### 🔵 P3-3: 魔法数字提取

**问题**: 硬编码常量散布各处

**修复方案**:
```python
# constants.py
REVIEW_TIMEOUT_DAYS = 7
CONCURRENCY_LIMITS = {'task': 10, 'topic': 5, 'project': 3}
LEVELS_SELF_APPROVE = ('L0', 'L1')
LEVELS_NEED_HUMAN = ('L2', 'L3')
```

**估算工时**: 2 小时

---

## 任务总览

| 优先级 | 任务数 | 总工时估算 | 完成期限 |
|--------|--------|-----------|---------|
| **P0** | 3 | 9 小时 | 1 周内 |
| **P1** | 3 | 26 小时 | 1 个月内 |
| **P2** | 2 | 22 小时 | 3 个月内 |
| **P3** | 3 | 7 小时 | 6 个月内 |
| **总计** | **11** | **64 小时** | — |

---

## 下一步行动

### 本周（P0 任务）
1. ✅ P0-1: 并发控制强制执行（2h）
2. ✅ P0-2: CWD 漂移修复（3h）
3. ✅ P0-3: 审计闭环集成（4h）

### 本月（P1 任务）
4. ✅ P1-1: 写穿透校验函数（6h）
5. ✅ P1-2: 数据迁移脚本（8h）
6. ✅ P1-3: 测试覆盖补充（12h）

### Q3 2026（P2 任务）
7. ⏸️ P2-1: 聚合算法增强（6h）
8. ⏸️ P2-2: 监控仪表板（16h）

### Q4 2026（P3 任务）
9. ⏸️ P3-1: 函数命名改进（1h）
10. ⏸️ P3-2: 类型标注完整（4h）
11. ⏸️ P3-3: 魔法数字提取（2h）

---

**任务清单版本**: v1.0  
**生成时间**: 2026-04-21  
**状态**: 待审批

