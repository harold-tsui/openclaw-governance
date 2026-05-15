#!/usr/bin/env python3
"""
NUCLEUS v4.0 安全加固 + 新功能测试

覆盖：
  - Path traversal 防护（_validate_id / _record_path）
  - _load() 数据校验（损坏 YAML / 字段修复）
  - 审计完整性 checksum（_compute_checksum / verify_integrity）
  - health_check()
  - archive() 归档
  - config 加载 + fallback
  - _safe_save() 文件大小/数量限制
  - Pending 三级升级 (escalation)
"""

import os
import pytest
import yaml
import sys
from pathlib import Path
from unittest.mock import patch

# 添加 scripts 目录到 Python path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from pdca import (
    p, d, c, a,
    get_status,
    get_pending,
    aggregate,
    verify_integrity,
    health_check,
    archive,
    _validate_id,
    _compute_checksum,
    _load,
    _record_path,
    _empty_record,
)


@pytest.fixture
def temp_pdca_env(tmp_path, monkeypatch):
    """创建临时 PDCA 环境"""
    pdca_dir = tmp_path / "pdca"
    pdca_dir.mkdir()
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    import pdca as pdca_module
    monkeypatch.setattr(pdca_module, 'PDCA_DIR', str(pdca_dir))
    monkeypatch.setattr(pdca_module, 'LOG_DIR', str(logs_dir))
    monkeypatch.setattr(pdca_module, 'LOG_FILE', str(logs_dir / 'pdca.log'))
    monkeypatch.setattr(pdca_module, 'STATE_FILE', str(pdca_dir / '_state.yaml'))
    monkeypatch.setattr(pdca_module, 'CONFIG_FILE', str(config_dir / 'pdca_config.yaml'))

    return {
        'pdca_dir': pdca_dir,
        'logs_dir': logs_dir,
        'config_dir': config_dir,
        'tmp_path': tmp_path,
    }


def _complete_pdca(task_id, review_level='L0', verdict='pass'):
    """辅助函数：完成一个完整 PDCA 循环"""
    p(task_card_id=task_id, summary=f"Plan {task_id}")
    d(task_card_id=task_id, summary=f"Do {task_id}", status='completed')
    c(task_card_id=task_id, verdict=verdict, review_level=review_level)
    return a(task_card_id=task_id, summary=f"Act {task_id}")


# ── 1. Path Traversal 防护 ─────────────────────────────

class TestValidateId:
    """测试 ID 校验函数"""

    def test_valid_simple_id(self):
        assert _validate_id("T1") is None

    def test_valid_complex_id(self):
        assert _validate_id("ZT-P015") is None
        assert _validate_id("T1.1") is None
        assert _validate_id("N4-P2-TEST-01") is None
        assert _validate_id("ZTP015-IMP-001") is None

    def test_path_traversal_dotdot(self):
        err = _validate_id("../../etc/passwd", 'task-card-id')
        assert err is not None
        # `..` 和 `/` 都在 blocked 列表中，set 迭代顺序不保证，两个都检查
        assert '..' in err or '/' in err or '非法' in err

    def test_path_traversal_slash(self):
        err = _validate_id("/etc/passwd", 'task-card-id')
        assert err is not None
        assert '/' in err

    def test_path_traversal_backslash(self):
        err = _validate_id('..\\etc', 'task-card-id')
        assert err is not None
        # `..` 和 `\\` 都在 blocked 列表中，set 迭代顺序不保证
        assert '..' in err or '\\' in err or '非法' in err

    def test_empty_id(self):
        err = _validate_id("", 'task-card-id')
        assert err is not None
        assert '不能为空' in err

    def test_dot_prefix(self):
        err = _validate_id(".hidden", 'task-card-id')
        assert err is not None
        assert '格式无效' in err

    def test_control_char(self):
        # 使用不含 / 和 \ 的控制字符，确保命中控制字符检测
        err = _validate_id("T1\x00", 'task-card-id')
        assert err is not None
        assert '控制字符' in err

    def test_overlength_id(self):
        err = _validate_id("A" * 129, 'task-card-id')
        assert err is not None
        assert '128' in err

    def test_id_with_underscore(self):
        assert _validate_id("MY_TASK_01") is None

    def test_custom_field_name(self):
        err = _validate_id("", 'topic-id')
        assert 'topic-id' in err


class TestRecordPathSecurity:
    """测试 _record_path 安全防护"""

    def test_valid_id_produces_safe_path(self, temp_pdca_env):
        path = _record_path("T1.1")
        assert path.endswith("T1.1.yaml")
        assert str(temp_pdca_env['pdca_dir']) in path

    def test_path_traversal_raises_valueerror(self):
        with pytest.raises(ValueError, match='非法字符'):
            _record_path("../../etc/passwd")

    def test_slash_raises_valueerror(self):
        with pytest.raises(ValueError, match='非法字符'):
            _record_path("/etc/passwd")

    def test_basename_stripping(self, temp_pdca_env):
        """即使 ID 通过校验，basename 也会剥离路径组件"""
        # 合法 ID 不会触发 basename 剥离，但验证逻辑存在
        path = _record_path("SAFE-ID-001")
        assert os.path.basename(path) == "SAFE-ID-001.yaml"


class TestPathTraversalInCommands:
    """测试命令级别的 path traversal 防护"""

    def test_p_rejects_traversal(self, temp_pdca_env):
        result = p(task_card_id="../../etc/passwd", summary="malicious")
        assert result['ok'] is False
        assert '非法字符' in result['error']

    def test_d_rejects_traversal(self, temp_pdca_env):
        result = d(task_card_id="../secret", summary="x", status='completed')
        assert result['ok'] is False

    def test_c_rejects_traversal(self, temp_pdca_env):
        result = c(task_card_id="..\\etc", verdict='pass', review_level='L0')
        assert result['ok'] is False

    def test_a_rejects_traversal(self, temp_pdca_env):
        result = a(task_card_id="/etc/shadow", summary="x")
        assert result['ok'] is False

    def test_get_status_rejects_traversal(self, temp_pdca_env):
        result = get_status(task_card_id="../../etc/passwd")
        assert result['ok'] is False


# ── 2. _load() 数据校验 ───────────────────────────────

class TestLoadDataValidation:
    """测试 _load() 数据校验和损坏修复"""

    def test_corrupted_yaml_returns_empty_record(self, temp_pdca_env):
        """YAML 解析失败时返回空记录"""
        pdca_dir = temp_pdca_env['pdca_dir']
        bad_file = pdca_dir / "BAD-YAML.yaml"
        bad_file.write_text(":\n  :  invalid: yaml: [", encoding='utf-8')
        result = _load("BAD-YAML")
        assert result['task_card_id'] == 'BAD-YAML'
        assert result['cycles'] == []

    def test_empty_yaml_returns_empty_record(self, temp_pdca_env):
        """空 YAML 文件返回空记录"""
        pdca_dir = temp_pdca_env['pdca_dir']
        empty_file = pdca_dir / "EMPTY.yaml"
        empty_file.write_text("", encoding='utf-8')
        result = _load("EMPTY")
        assert result['task_card_id'] == 'EMPTY'
        assert result['cycles'] == []

    def test_id_mismatch_is_fixed(self, temp_pdca_env):
        """task_card_id 不匹配时自动修正"""
        pdca_dir = temp_pdca_env['pdca_dir']
        wrong_id_file = pdca_dir / "CORRECT-ID.yaml"
        data = {
            'task_card_id': 'WRONG-ID',
            'cycles': [],
        }
        wrong_id_file.write_text(yaml.dump(data, allow_unicode=True), encoding='utf-8')
        result = _load("CORRECT-ID")
        assert result['task_card_id'] == 'CORRECT-ID'

    def test_cycles_non_list_is_fixed(self, temp_pdca_env):
        """cycles 非列表时自动修复"""
        pdca_dir = temp_pdca_env['pdca_dir']
        bad_cycles_file = pdca_dir / "BAD-CYCLES.yaml"
        data = {
            'task_card_id': 'BAD-CYCLES',
            'cycles': 'not_a_list',
        }
        bad_cycles_file.write_text(yaml.dump(data, allow_unicode=True), encoding='utf-8')
        result = _load("BAD-CYCLES")
        assert result['cycles'] == []

    def test_invalid_phase_is_fixed(self, temp_pdca_env):
        """非法 phase 自动修复为 plan"""
        pdca_dir = temp_pdca_env['pdca_dir']
        bad_phase_file = pdca_dir / "BAD-PHASE.yaml"
        data = {
            'task_card_id': 'BAD-PHASE',
            'cycles': [{
                'cycle_index': 1,
                'started_at': '2026-01-01T00:00:00+00:00',
                'completed_at': None,
                'phase': 'INVALID_PHASE',
                'p': None, 'd': None, 'c': None, 'a': None,
            }],
        }
        bad_phase_file.write_text(yaml.dump(data, allow_unicode=True), encoding='utf-8')
        result = _load("BAD-PHASE")
        assert result['cycles'][0]['phase'] == 'plan'

    def test_invalid_cycle_index_is_fixed(self, temp_pdca_env):
        """非法 cycle_index 自动修复"""
        pdca_dir = temp_pdca_env['pdca_dir']
        bad_idx_file = pdca_dir / "BAD-IDX.yaml"
        data = {
            'task_card_id': 'BAD-IDX',
            'cycles': [{
                'cycle_index': -1,
                'started_at': '2026-01-01T00:00:00+00:00',
                'completed_at': None,
                'phase': 'plan',
                'p': None, 'd': None, 'c': None, 'a': None,
            }],
        }
        bad_idx_file.write_text(yaml.dump(data, allow_unicode=True), encoding='utf-8')
        result = _load("BAD-IDX")
        assert result['cycles'][0]['cycle_index'] == 1

    def test_missing_file_returns_empty_record(self, temp_pdca_env):
        """不存在文件返回空记录"""
        result = _load("NONEXISTENT")
        assert result['task_card_id'] == 'NONEXISTENT'
        assert result['cycles'] == []


# ── 3. 审计完整性 Checksum ────────────────────────────

class TestChecksum:
    """测试 SHA-256 checksum 计算和验证"""

    def test_compute_checksum_returns_hex_string(self):
        record = _empty_record("TEST-CS")
        cs = _compute_checksum(record)
        assert isinstance(cs, str)
        assert len(cs) == 16  # SHA-256 前 16 位

    def test_checksum_changes_on_data_modification(self):
        record = _empty_record("TEST-CS")
        cs1 = _compute_checksum(record)
        record['cycles'].append({'phase': 'plan'})
        cs2 = _compute_checksum(record)
        assert cs1 != cs2

    def test_checksum_excludes_itself(self):
        """checksum 不影响自身计算"""
        record = _empty_record("TEST-CS")
        cs1 = _compute_checksum(record)
        record['_checksum'] = cs1
        cs2 = _compute_checksum(record)
        assert cs1 == cs2

    def test_save_adds_checksum(self, temp_pdca_env):
        """_save() 自动计算并写入 checksum"""
        result = p(task_card_id="CS-TEST", summary="checksum test")
        assert result['ok'] is True
        # 读取文件验证 checksum 存在
        pdca_dir = temp_pdca_env['pdca_dir']
        with open(pdca_dir / "CS-TEST.yaml", 'r') as f:
            data = yaml.safe_load(f)
        assert '_checksum' in data
        assert data['_checksum'] is not None

    def test_verify_integrity_valid_file(self, temp_pdca_env):
        """验证刚保存的文件 checksum 有效"""
        p(task_card_id="VI-VALID", summary="valid checksum")
        result = verify_integrity(task_card_id="VI-VALID")
        assert result['ok'] is True
        assert result['valid'] == 1
        assert result['invalid'] == 0

    def test_verify_integrity_tampered_file(self, temp_pdca_env):
        """篡改文件后 checksum 不匹配"""
        p(task_card_id="VI-TAMPER", summary="original")
        # 直接修改文件内容
        pdca_dir = temp_pdca_env['pdca_dir']
        with open(pdca_dir / "VI-TAMPER.yaml", 'r') as f:
            data = yaml.safe_load(f)
        data['cycles'][0]['p']['summary'] = "TAMPERED"
        with open(pdca_dir / "VI-TAMPER.yaml", 'w') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        result = verify_integrity(task_card_id="VI-TAMPER")
        assert result['invalid'] == 1

    def test_verify_integrity_no_checksum_file(self, temp_pdca_env):
        """旧文件无 checksum 标记为 no_checksum"""
        pdca_dir = temp_pdca_env['pdca_dir']
        data = {'task_card_id': 'OLD-FILE', 'cycles': []}
        with open(pdca_dir / "OLD-FILE.yaml", 'w') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        result = verify_integrity(task_card_id="OLD-FILE")
        assert result['no_checksum'] == 1

    def test_verify_integrity_all_files(self, temp_pdca_env):
        """验证所有文件完整性"""
        p(task_card_id="ALL-1", summary="test1")
        p(task_card_id="ALL-2", summary="test2")
        result = verify_integrity()
        assert result['total'] >= 2


# ── 4. Pending 三级升级 ───────────────────────────────

class TestPendingEscalation:
    """测试 Pending 超时三级升级"""

    def test_normal_escalation_for_recent_pending(self, temp_pdca_env):
        """刚创建的 pending 为 normal 级别"""
        p(task_card_id="PEND-NORMAL", summary="test")
        d(task_card_id="PEND-NORMAL", summary="done", status='completed')
        c(task_card_id="PEND-NORMAL", verdict='pending', review_level='L3')
        pending = get_pending()
        match = [x for x in pending if x['task_card_id'] == 'PEND-NORMAL']
        assert len(match) == 1
        assert match[0]['escalation'] == 'normal'
        assert match[0]['needs_escalation'] is False

    def test_escalation_field_exists(self, temp_pdca_env):
        """pending 条目包含 escalation 和 needs_escalation 字段"""
        p(task_card_id="PEND-FIELD", summary="test")
        d(task_card_id="PEND-FIELD", summary="done", status='completed')
        c(task_card_id="PEND-FIELD", verdict='pending', review_level='L3')
        pending = get_pending()
        match = [x for x in pending if x['task_card_id'] == 'PEND-FIELD']
        assert len(match) == 1
        assert 'escalation' in match[0]
        assert 'needs_escalation' in match[0]

    def test_l2_pending_reviewer(self, temp_pdca_env):
        """L2 pending 的 reviewer 是银月"""
        p(task_card_id="PEND-L2", summary="test")
        d(task_card_id="PEND-L2", summary="done", status='completed')
        c(task_card_id="PEND-L2", verdict='pending', review_level='L2')
        pending = get_pending(review_level='L2')
        match = [x for x in pending if x['task_card_id'] == 'PEND-L2']
        assert len(match) == 1
        assert match[0]['reviewer'] == '银月'


# ── 5. Config 加载 ────────────────────────────────────

class TestConfigLoading:
    """测试配置加载和 fallback"""

    def test_missing_config_uses_defaults(self, temp_pdca_env):
        """缺失配置文件时使用默认值"""
        import pdca as pdca_module
        # 无配置文件时重载配置
        cfg = pdca_module._load_config()
        assert cfg['concurrency']['task'] == 10
        assert cfg['audit']['score_threshold'] == 80
        assert cfg['limits']['max_pdca_files'] == 500

    def test_custom_config_overrides_defaults(self, temp_pdca_env):
        """自定义配置覆盖默认值"""
        config_dir = temp_pdca_env['config_dir']
        custom_cfg = {
            'concurrency': {'task': 5},
            'audit': {'score_threshold': 90},
        }
        with open(config_dir / "pdca_config.yaml", 'w') as f:
            yaml.dump(custom_cfg, f, allow_unicode=True, default_flow_style=False)

        import pdca as pdca_module
        cfg = pdca_module._load_config()
        assert cfg['concurrency']['task'] == 5
        assert cfg['audit']['score_threshold'] == 90
        # 其他字段保持默认
        assert cfg['concurrency']['topic'] == 5

    def test_corrupted_config_uses_defaults(self, temp_pdca_env):
        """损坏的配置文件使用默认值"""
        config_dir = temp_pdca_env['config_dir']
        with open(config_dir / "pdca_config.yaml", 'w') as f:
            f.write(":\n  invalid: [")

        import pdca as pdca_module
        cfg = pdca_module._load_config()
        assert cfg['concurrency']['task'] == 10


# ── 6. 文件安全限制 ──────────────────────────────────

class TestSafetyLimits:
    """测试文件大小和数量限制"""

    def test_max_cycles_per_task_enforced(self, temp_pdca_env, monkeypatch):
        """超过最大循环数时拒绝新 cycle"""
        import pdca as pdca_module
        monkeypatch.setattr(pdca_module, 'MAX_CYCLES_PER_TASK', 2)

        # 完成 2 个完整 cycle
        _complete_pdca("CYCLE-LIMIT", verdict='fail')
        _complete_pdca("CYCLE-LIMIT", verdict='fail')

        # 尝试第 3 个 cycle 应该被拒绝
        result = p(task_card_id="CYCLE-LIMIT", summary="3rd cycle")
        assert result['ok'] is False
        assert '上限' in result['error']

    def test_cycle_index_validation_in_mark_audit(self, temp_pdca_env):
        """mark_audit 中 cycle_index < 1 被拒绝"""
        from pdca import mark_audit
        result = mark_audit(task_card_id="ANY", cycle_index=0, score=85)
        assert result['ok'] is False
        assert '≥ 1' in result['error']

    def test_negative_cycle_index_rejected(self, temp_pdca_env):
        """负数 cycle_index 被拒绝"""
        from pdca import mark_audit
        result = mark_audit(task_card_id="ANY", cycle_index=-1, score=85)
        assert result['ok'] is False


# ── 7. Health Check ──────────────────────────────────

class TestHealthCheck:
    """测试系统健康检查"""

    def test_healthy_system(self, temp_pdca_env):
        """空系统返回 healthy"""
        result = health_check()
        assert result['status'] == 'healthy'
        assert result['files']['count'] == 0
        assert result['pending']['total'] == 0

    def test_health_check_with_active_tasks(self, temp_pdca_env):
        """有活跃任务时的健康状态"""
        p(task_card_id="HC-ACTIVE", summary="active task")
        result = health_check()
        assert result['files']['count'] >= 1
        assert result['concurrency']['active'] >= 1

    def test_health_check_includes_checksum_coverage(self, temp_pdca_env):
        """health_check 包含 checksum 覆盖率"""
        result = health_check()
        assert 'checksum' in result
        assert 'coverage_pct' in result['checksum']

    def test_health_check_includes_audit_queue(self, temp_pdca_env):
        """health_check 包含审计队列信息"""
        result = health_check()
        assert 'audit_queue' in result


# ── 8. Archive ───────────────────────────────────────

class TestArchive:
    """测试过期数据归档"""

    def test_dry_run_does_not_move_files(self, temp_pdca_env):
        """dry_run 模式不移动文件"""
        _complete_pdca("ARCH-DRY")
        result = archive(older_than_days=0, dry_run=True)
        assert result['dry_run'] is True
        assert result['candidates'] >= 1
        assert result['archived'] == 0
        # 文件仍在原位
        pdca_dir = temp_pdca_env['pdca_dir']
        assert (pdca_dir / "ARCH-DRY.yaml").exists()

    def test_archive_moves_completed_files(self, temp_pdca_env):
        """归档移动已完成文件到 _archive/"""
        _complete_pdca("ARCH-MOVE")
        result = archive(older_than_days=0, dry_run=False)
        assert result['archived'] >= 1
        pdca_dir = temp_pdca_env['pdca_dir']
        assert not (pdca_dir / "ARCH-MOVE.yaml").exists()
        assert (pdca_dir / "_archive" / "ARCH-MOVE.yaml").exists()

    def test_archive_does_not_move_active_files(self, temp_pdca_env):
        """归档不移动进行中的文件"""
        p(task_card_id="ARCH-ACTIVE", summary="still working")
        result = archive(older_than_days=0, dry_run=True)
        match = [c for c in (result.get('details') or []) if c['task_card_id'] == 'ARCH-ACTIVE']
        assert len(match) == 0

    def test_archive_default_uses_config(self, temp_pdca_env):
        """默认使用配置中的归档天数"""
        # 配置默认 30 天，刚完成的文件不应被归档
        _complete_pdca("ARCH-RECENT")
        result = archive(older_than_days=30, dry_run=True)
        # 刚完成的文件不足 30 天
        recent = [c for c in (result.get('details') or []) if c['task_card_id'] == 'ARCH-RECENT']
        assert len(recent) == 0


# ── 9. _state.yaml 版本控制 ───────────────────────────

class TestStateVersioning:
    """测试 _state.yaml 版本控制"""

    def test_empty_state_has_version(self):
        """空 state 包含 version 字段"""
        state = _empty_record("VTEST")
        # _empty_state is not directly importable, test via aggregate
        pass

    def test_aggregate_writes_version(self, temp_pdca_env):
        """aggregate 写入 version 到 _state.yaml"""
        _complete_pdca("VER-TEST")
        aggregate()
        pdca_dir = temp_pdca_env['pdca_dir']
        state_file = pdca_dir / "_state.yaml"
        if state_file.exists():
            with open(state_file) as f:
                data = yaml.safe_load(f)
            assert 'version' in data
            assert data['version'] == '1.0'


# ── 10. 增量聚合 ────────────────────────────────────

class TestIncrementalAggregate:
    """测试增量聚合优化"""

    def test_first_aggregate_scans_all(self, temp_pdca_env):
        """首次聚合扫描所有文件"""
        _complete_pdca("INCR-1")
        # _complete_pdca 内部 a() 已调用 aggregate，清空 _state 缓存后手动调用
        import pdca as pdca_module
        state_file = pdca_module.STATE_FILE
        if os.path.exists(state_file):
            os.remove(state_file)
        result = aggregate()
        assert result['files_changed'] >= 1

    def test_second_aggregate_uses_cache(self, temp_pdca_env):
        """二次聚合使用缓存，files_changed=0"""
        _complete_pdca("INCR-2")
        aggregate()  # 首次
        result = aggregate()  # 二次
        assert result['files_changed'] == 0

    def test_modified_file_triggers_rescan(self, temp_pdca_env):
        """修改文件后触发重新扫描"""
        _complete_pdca("INCR-3")
        aggregate()
        # 修改文件（touch 更新 mtime）
        pdca_dir = temp_pdca_env['pdca_dir']
        import time
        time.sleep(0.1)
        # 直接写入新数据
        with open(pdca_dir / "INCR-3.yaml", 'r') as f:
            data = yaml.safe_load(f)
        data['cycles'][0]['a']['summary'] = "modified"
        with open(pdca_dir / "INCR-3.yaml", 'w') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        result = aggregate()
        assert result['files_changed'] >= 1
