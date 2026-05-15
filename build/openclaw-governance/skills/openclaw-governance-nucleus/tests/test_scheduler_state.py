#!/usr/bin/env python3
"""
NUCLEUS v4.0 scheduler_state.py 测试

测试覆盖目标：bump(), check(), reset(), read_state()
重点：计数器递增、阈值触发、自动重置、并发安全
"""

import os
import pytest
import sys
import tempfile
import yaml
from pathlib import Path

# 添加 scripts 目录到 Python path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

# Import after path setup — import fresh per test via reload pattern
# We can't import at module level because STATE_PATH is set at import time.
# Instead we import inside tests and monkeypatch.


def _import_scheduler(monkeypatch, tmp_path):
    """Import scheduler_state with patched STATE_PATH"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    state_file = config_dir / "scheduler_state.yaml"

    # Import fresh module
    if 'scheduler_state' in sys.modules:
        del sys.modules['scheduler_state']

    import scheduler_state as ss

    monkeypatch.setattr(ss, 'STATE_PATH', str(state_file))

    return ss, state_file


class TestReadState:

    def test_read_initial_state(self, monkeypatch, tmp_path):
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        result = ss.read_state()
        assert result['ok'] is True
        assert result['tick'] == 0
        assert result['counters']['task'] == 0
        assert result['counters']['topic'] == 0
        assert result['counters']['project'] == 0
        assert result['counters']['system'] == 0
        assert result['thresholds']['task'] == 1
        assert result['thresholds']['topic'] == 4

    def test_read_persisted_state(self, monkeypatch, tmp_path):
        ss, state_file = _import_scheduler(monkeypatch, tmp_path)
        # Write a pre-existing state
        state_file.write_text(yaml.dump({
            'tick': 42,
            'task_tick': 10,
            'topic_tick': 3,
            'project_tick': 20,
            'system_tick': 50,
        }))
        result = ss.read_state()
        assert result['tick'] == 42
        assert result['counters']['task'] == 10
        assert result['counters']['project'] == 20


class TestBump:

    def test_bump_increments_all_counters(self, monkeypatch, tmp_path):
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        result = ss.bump()
        assert result['ok'] is True
        assert result['tick'] == 1
        assert result['counters']['task'] == 1
        assert result['counters']['topic'] == 1
        assert result['counters']['project'] == 1
        assert result['counters']['system'] == 1

    def test_bump_multiple_times(self, monkeypatch, tmp_path):
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        for _ in range(5):
            ss.bump()
        result = ss.read_state()
        assert result['tick'] == 5
        assert result['counters']['task'] == 5
        assert result['counters']['topic'] == 5

    def test_bump_persists_state(self, monkeypatch, tmp_path):
        ss, state_file = _import_scheduler(monkeypatch, tmp_path)
        ss.bump()
        assert state_file.exists()
        data = yaml.safe_load(state_file.read_text())
        assert data['tick'] == 1


class TestCheck:

    def test_no_triggers_initial(self, monkeypatch, tmp_path):
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        result = ss.check()
        assert result['ok'] is True
        assert len(result['triggered']) == 0

    def test_task_triggers_after_one_bump(self, monkeypatch, tmp_path):
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        ss.bump()
        result = ss.check()
        triggered_scopes = [t['scope'] for t in result['triggered']]
        assert 'task' in triggered_scopes
        # task threshold is 1, so it triggers
        assert len(result['triggered']) == 1

    def test_topic_triggers_at_threshold(self, monkeypatch, tmp_path):
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        for _ in range(3):
            ss.bump()
        result = ss.check()
        # After 3 bumps: task_tick=3 (>=1 triggered), topic_tick=3 (<4 not triggered)
        triggered_scopes = [t['scope'] for t in result['triggered']]
        assert 'task' in triggered_scopes
        assert 'topic' not in triggered_scopes

        # 4th bump → topic should trigger
        ss.bump()
        result = ss.check()
        triggered_scopes = [t['scope'] for t in result['triggered']]
        assert 'topic' in triggered_scopes

    def test_check_auto_resets_triggered_counters(self, monkeypatch, tmp_path):
        """⭐ v6.2.0 核心修复：check() 自动重置已触发计数器"""
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        ss.bump()

        # First check: task triggers, counter should be auto-reset
        result1 = ss.check()
        assert 'task' in [t['scope'] for t in result1['triggered']]

        # Immediately check again — task should NOT trigger (counter was reset)
        result2 = ss.check()
        assert 'task' not in [t['scope'] for t in result2['triggered']]

    def test_check_preserves_non_triggered_counters(self, monkeypatch, tmp_path):
        """未达阈值的计数器不应被重置"""
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        for _ in range(3):
            ss.bump()

        result = ss.check()
        # task triggered and reset, but topic (tick=3, threshold=4) should NOT be reset
        assert 'task' in [t['scope'] for t in result['triggered']]
        assert 'topic' not in [t['scope'] for t in result['triggered']]

        # After next bump: topic should be at 4 (3 + 1), NOT at 1
        ss.bump()
        result2 = ss.check()
        assert 'topic' in [t['scope'] for t in result2['triggered']]

    def test_check_records_auto_reset_timestamp(self, monkeypatch, tmp_path):
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        ss.bump()
        ss.check()

        # Read state file directly to verify auto-reset timestamp
        import scheduler_state
        state = yaml.safe_load(Path(ss.STATE_PATH).read_text())
        assert 'last_reset' in state
        assert 'auto' in state['last_reset']


class TestReset:

    def test_reset_task_counter(self, monkeypatch, tmp_path):
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        for _ in range(5):
            ss.bump()
        result = ss.reset('task')
        assert result['ok'] is True
        assert result['counter'] == 0

        read = ss.read_state()
        assert read['counters']['task'] == 0
        # Other counters should still be at 5
        assert read['counters']['topic'] == 5

    def test_reset_unknown_scope(self, monkeypatch, tmp_path):
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        result = ss.reset('invalid_scope')
        assert result['ok'] is False
        assert 'error' in result

    def test_reset_records_timestamp(self, monkeypatch, tmp_path):
        ss, state_file = _import_scheduler(monkeypatch, tmp_path)
        ss.bump()
        ss.reset('task')

        data = yaml.safe_load(state_file.read_text())
        assert 'last_reset' in data
        assert 'task' in data['last_reset']


class TestIntegration:

    def test_bump_check_reset_cycle(self, monkeypatch, tmp_path):
        """模拟 heartbeat 完整流程：bump → check → reset"""
        ss, _ = _import_scheduler(monkeypatch, tmp_path)

        # Simulate 10 heartbeats
        for i in range(10):
            ss.bump()
            result = ss.check()

            # task should trigger every heartbeat (but auto-reset prevents double trigger)
            if i >= 3:
                assert 'task' in [t['scope'] for t in result['triggered']]

            # After first check, task counter is auto-reset
            if i == 3:
                assert 'task' in [t['scope'] for t in result['triggered']]
                # Next check without bump should not trigger task
                result2 = ss.check()
                assert 'task' not in [t['scope'] for t in result2['triggered']]

    def test_project_triggers_after_48_bumps(self, monkeypatch, tmp_path):
        ss, _ = _import_scheduler(monkeypatch, tmp_path)
        for _ in range(47):
            ss.bump()
            ss.check()  # auto-reset will keep task/topic from re-triggering

        result = ss.check()
        assert 'project' not in [t['scope'] for t in result['triggered']]

        ss.bump()
        result = ss.check()
        assert 'project' in [t['scope'] for t in result['triggered']]
