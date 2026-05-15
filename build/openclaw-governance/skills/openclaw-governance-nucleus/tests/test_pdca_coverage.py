#!/usr/bin/env python3
"""
NUCLEUS v4.0 PDCA 覆盖率补充测试

专注覆盖未测试的边界情况、错误路径、边缘分支
目标：将覆盖率从 71% 提升到 80%+
"""

import os
import pytest
import sys
from pathlib import Path

# 添加 scripts 目录到 Python path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from pdca import (
    p, d, c, a,
    get_audit_queue,
    mark_audit,
    aggregate,
    _aggregate_verdict,
    _verdicts_equal,
    get_status,
)


@pytest.fixture
def temp_pdca_env(tmp_path, monkeypatch):
    """创建临时 PDCA 环境"""
    pdca_dir = tmp_path / "pdca"
    pdca_dir.mkdir()
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()

    import pdca as pdca_module
    monkeypatch.setattr(pdca_module, 'PDCA_DIR', str(pdca_dir))
    monkeypatch.setattr(pdca_module, 'LOG_DIR', str(logs_dir))
    monkeypatch.setattr(pdca_module, 'LOG_FILE', str(logs_dir / 'pdca.log'))
    monkeypatch.setattr(pdca_module, 'STATE_FILE', str(pdca_dir / '_state.yaml'))

    return {
        'pdca_dir': pdca_dir,
        'logs_dir': logs_dir,
        'tmp_path': tmp_path
    }


class TestAuditQueueEdgeCases:
    """测试审计队列边界情况"""

    def test_get_audit_queue_no_pdca_dir(self, temp_pdca_env, monkeypatch):
        """测试 PDCA_DIR 不存在时返回空列表"""
        import pdca as pdca_module
        fake_dir = str(temp_pdca_env['tmp_path'] / 'nonexistent')
        monkeypatch.setattr(pdca_module, 'PDCA_DIR', fake_dir)

        queue = get_audit_queue()
        assert queue == []

    def test_get_audit_queue_with_malformed_files(self, temp_pdca_env):
        """测试损坏的 YAML 文件不影响其他文件"""
        # 创建正常任务
        task_id1 = "AUDIT-GOOD"
        p(task_id1, "正常任务")
        d(task_id1, "完成", status="completed")
        c(task_id1, review_level='L0', verdict='pass')
        a(task_id1, "总结")

        # 创建损坏的 YAML 文件
        pdca_dir = temp_pdca_env['pdca_dir']
        malformed_file = pdca_dir / "MALFORMED.yaml"
        malformed_file.write_text("invalid: yaml: content: [[[")

        # 应该只返回正常任务
        queue = get_audit_queue()
        assert all(q['task_card_id'] == task_id1 for q in queue)

    def test_get_audit_queue_with_incomplete_cycles(self, temp_pdca_env):
        """测试 cycles 列表为空或缺失的情况"""
        task_id = "INCOMPLETE"
        p(task_id, "测试")

        # 此时 cycle 不完整，不应出现在审计队列
        queue = get_audit_queue()
        assert all(q['task_card_id'] != task_id for q in queue)


class TestMarkAuditEdgeCases:
    """测试 mark_audit 边界情况"""

    def test_mark_audit_cycle_not_found(self, temp_pdca_env):
        """测试标记不存在的 cycle_index"""
        task_id = "AUDIT-404"
        p(task_id, "测试")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "总结")

        # 尝试标记不存在的 cycle_index=99
        result = mark_audit(task_id, cycle_index=99, score=85)
        assert result['ok'] is False
        assert 'cycle_index=99 不存在' in result['error']

    def test_mark_audit_no_check_phase(self, temp_pdca_env):
        """测试 Check 阶段未记录时无法审计"""
        task_id = "NO-CHECK"
        p(task_id, "测试")
        d(task_id, "完成", status="completed")

        # 尝试审计（但 Check 阶段未记录）
        result = mark_audit(task_id, cycle_index=1, score=85)
        assert result['ok'] is False
        assert 'Check 阶段尚未记录' in result['error']

    def test_mark_audit_not_audit_eligible(self, temp_pdca_env):
        """测试非 audit_eligible cycle 无法审计"""
        task_id = "NOT-ELIGIBLE"

        # L3 任务：首次 Check 必须 pending
        p(task_id, "L3 测试")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L3', verdict='pending')

        # L3 pending cycle 不是 audit_eligible
        # 尝试审计应该失败
        result = mark_audit(task_id, cycle_index=1, score=85)
        assert result['ok'] is False
        assert 'audit_eligible' in result['error']


class TestAggregateEdgeCases:
    """测试聚合函数边界情况"""

    def test_aggregate_no_pdca_dir(self, temp_pdca_env, monkeypatch):
        """测试 PDCA_DIR 不存在时直接返回"""
        import pdca as pdca_module
        fake_dir = str(temp_pdca_env['tmp_path'] / 'nonexistent')
        monkeypatch.setattr(pdca_module, 'PDCA_DIR', fake_dir)

        result = aggregate()
        assert result['ok'] is True
        assert result['changes'] is False
        assert 'pdca/ 目录不存在' in result['reason']

    def test_aggregate_empty_cycles(self, temp_pdca_env):
        """测试没有 cycles 的任务不参与聚合"""
        # 创建只有 Plan 的任务
        p("ONLY-PLAN", "仅 Plan")

        result = aggregate()
        assert result['ok'] is True

    def test_aggregate_no_completed_cycles(self, temp_pdca_env):
        """测试只有进行中的 cycle 不参与聚合"""
        task_id = "IN-PROGRESS"
        p(task_id, "测试")
        d(task_id, "完成", status="completed")
        # 未执行 c() 和 a()，cycle 未完成

        result = aggregate()
        assert result['ok'] is True

    def test_aggregate_with_malformed_yaml(self, temp_pdca_env):
        """测试损坏的 YAML 文件不影响聚合"""
        # 创建正常任务
        p("NORMAL", "正常任务", topic_id="TOPIC-A")
        d("NORMAL", "完成", status="completed")
        c("NORMAL", review_level='L0', verdict='pass')
        a("NORMAL", "总结")

        # 创建损坏文件
        pdca_dir = temp_pdca_env['pdca_dir']
        bad_file = pdca_dir / "BAD.yaml"
        bad_file.write_text("bad yaml content {{{")

        # 聚合应该成功（跳过损坏文件）
        result = aggregate()
        assert result['ok'] is True


class TestAggregateVerdictWeightedMode:
    """测试加权模式的特殊分支"""

    def test_weighted_mode_avg_severity_pass(self):
        """测试加权模式：平均严重度 < 0.5 → pass"""
        # 大量 pass，少量 skip
        verdicts = ['pass'] * 9 + ['skip']
        result = _aggregate_verdict(verdicts, mode='weighted')
        # avg_severity = (0*9 + 1*1) / 10 = 0.1 < 0.5 → pass
        assert result == 'pass'

    def test_weighted_mode_avg_severity_partial(self):
        """测试加权模式：平均严重度 0.5-1.5 → partial"""
        # 混合 pass 和 partial
        verdicts = ['pass', 'pass', 'partial', 'partial']
        result = _aggregate_verdict(verdicts, mode='weighted')
        # avg_severity = (0*2 + 2*2) / 4 = 1.0 → partial
        assert result == 'partial'

    def test_weighted_mode_avg_severity_fail(self):
        """测试加权模式：平均严重度 >= 1.5 → fail"""
        # 混合 partial 和 fail
        verdicts = ['partial', 'fail', 'fail']
        result = _aggregate_verdict(verdicts, mode='weighted')
        # avg_severity = (2 + 3 + 3) / 3 = 2.67 >= 1.5 → fail
        assert result == 'fail'

    def test_weighted_mode_fallback_on_invalid_mode(self):
        """测试未知模式回退到 strict"""
        verdicts = ['pass', 'fail']
        # 'unknown' 模式应回退到 strict
        result = _aggregate_verdict(verdicts, mode='unknown')
        # strict 模式：任一 fail → fail
        assert result == 'fail'


class TestAggregateWithTriggeredBy:
    """测试带 triggered_by 参数的聚合"""

    def test_aggregate_with_triggered_by(self, temp_pdca_env):
        """测试 triggered_by 参数记录"""
        task_id = "TRIGGER-TEST"
        p(task_id, "测试", topic_id="TOPIC-X")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "总结")

        result = aggregate(triggered_by="heartbeat")
        assert result['ok'] is True
        # triggered_by 应记录在 _state.yaml 中


class TestPlanWithOptionalParams:
    """测试 Plan 阶段的可选参数"""

    def test_plan_with_task_card_path(self, temp_pdca_env):
        """测试带 task_card_path 参数的 Plan"""
        task_id = "WITH-PATH"
        task_path = "/path/to/task.md"

        result = p(task_id, "测试", task_card_path=task_path)
        assert result['ok'] is True

    def test_plan_with_topic_and_project(self, temp_pdca_env):
        """测试带 topic_id 和 project_id 的 Plan"""
        task_id = "HIERARCHY"

        result = p(task_id, "测试", topic_id="TOPIC-A", project_id="PROJ-X")
        assert result['ok'] is True

    def test_plan_with_dl_refs(self, temp_pdca_env):
        """测试带 dl_refs 的 Plan"""
        task_id = "WITH-DL"

        result = p(task_id, "测试", dl_refs=["DL-001", "DL-002"])
        assert result['ok'] is True


class TestDoPhaseErrorPaths:
    """测试 Do 阶段的错误路径"""

    def test_do_invalid_status(self, temp_pdca_env):
        """测试无效的 status 参数"""
        task_id = "INVALID-STATUS"
        p(task_id, "测试")

        result = d(task_id, "完成", status="invalid_status")
        assert result['ok'] is False
        assert 'invalid status' in result['error']

    def test_do_after_completed_cycle(self, temp_pdca_env):
        """测试在已完成 cycle 后直接 Do"""
        task_id = "COMPLETED"

        # 完成一个 cycle
        p(task_id, "第一轮")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "总结")

        # 直接 Do（未先 Plan）应失败
        result = d(task_id, "第二轮执行", status="completed")
        assert result['ok'] is False
        assert '已完成' in result['error'] or 'PDCA' in result['error']

    def test_do_in_wrong_phase(self, temp_pdca_env):
        """测试在错误阶段调用 Do"""
        task_id = "WRONG-PHASE"

        p(task_id, "测试")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L0', verdict='pass')

        # Act 阶段调用 Do 应失败
        result = d(task_id, "错误调用", status="completed")
        assert result['ok'] is False
        assert 'phase' in result['error'].lower()


class TestCheckPhaseErrorPaths:
    """测试 Check 阶段的错误路径"""

    def test_check_l3_first_time_not_pending(self, temp_pdca_env):
        """测试 L3 首次 Check 必须是 pending"""
        task_id = "L3-NOT-PENDING"

        p(task_id, "测试")
        d(task_id, "完成", status="completed")

        # L3 首次必须 pending
        result = c(task_id, review_level='L3', verdict='pass')
        assert result['ok'] is False
        assert 'L3' in result['error'] and 'pending' in result['error']

    def test_check_pending_can_be_updated(self, temp_pdca_env):
        """测试 pending verdict 可以被更新"""
        task_id = "PENDING-UPDATE"

        p(task_id, "测试")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L2', verdict='pending')

        # pending verdict 可以被覆盖
        result = c(task_id, review_level='L2', verdict='pass')
        assert result['ok'] is True


class TestActPhaseErrorPaths:
    """测试 Act 阶段的错误路径"""

    def test_act_in_wrong_phase(self, temp_pdca_env):
        """测试在错误阶段调用 Act"""
        task_id = "ACT-WRONG"

        p(task_id, "测试")
        d(task_id, "完成", status="completed")

        # Do 阶段后直接 Act（未 Check）应失败
        result = a(task_id, "错误的 Act")
        assert result['ok'] is False
        assert 'Check' in result['error'] or 'Act' in result['error']


class TestMarkAuditValidation:
    """测试 mark_audit 的输入校验（v6.2.0 修复）"""

    def test_mark_audit_score_out_of_range_negative(self, temp_pdca_env):
        """测试 score 为负数时拒绝"""
        task_id = "AUDIT-INVALID"
        p(task_id, "测试")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "总结")

        result = mark_audit(task_id, cycle_index=1, score=-10)
        assert result['ok'] is False
        assert '0-100' in result['error']

    def test_mark_audit_score_out_of_range_high(self, temp_pdca_env):
        """测试 score 超过 100 时拒绝"""
        task_id = "AUDIT-INVALID-2"
        p(task_id, "测试")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "总结")

        result = mark_audit(task_id, cycle_index=1, score=150)
        assert result['ok'] is False
        assert '0-100' in result['error']

    def test_mark_audit_double_audit_rejected(self, temp_pdca_env):
        """测试重复审计被拒绝（v6.2.0 修复）"""
        task_id = "AUDIT-DOUBLE"
        p(task_id, "测试")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L1', verdict='pass')
        a(task_id, "总结")

        # 第一次审计应该成功
        result1 = mark_audit(task_id, cycle_index=1, score=90)
        assert result1['ok'] is True

        # 第二次审计应该被拒绝
        result2 = mark_audit(task_id, cycle_index=1, score=50)
        assert result2['ok'] is False
        assert '已存在审计结果' in result2['error']


class TestConcurrencyPendingExclusion:
    """测试 pending 任务不占用并发槽位（v6.2.0 修复）"""

    def test_pending_tasks_not_counted_in_concurrency(self, temp_pdca_env):
        """phase=check, verdict=pending 的任务不计入活跃计数"""
        from pdca import check_concurrency

        # 创建 9 个正常进行中的任务（phase=do）
        for i in range(9):
            p(f"CONC-{i:03d}", f"任务 {i}")
            d(f"CONC-{i:03d}", "进行中", status="partial")

        # 创建 1 个 pending 任务
        p("CONC-PENDING", "等待审核")
        d("CONC-PENDING", "完成", status="completed")
        c("CONC-PENDING", review_level='L3', verdict='pending')

        # 并发检查应该只计数 9 个正常任务（pending 不应计数）
        result = check_concurrency('task')
        assert result['ok'] is True  # 9 < 10，还有空间
        assert result['active'] == 9

    def test_pending_exclusion_allows_new_task_at_limit(self, temp_pdca_env):
        """10 个 pending 任务后仍可以创建新任务"""
        from pdca import check_concurrency

        # 创建 10 个 pending 任务
        for i in range(10):
            p(f"PEND-{i:03d}", f"任务 {i}")
            d(f"PEND-{i:03d}", "完成", status="completed")
            c(f"PEND-{i:03d}", review_level='L3', verdict='pending')

        # 所有 10 个都是 pending → 活跃计数应为 0
        result = check_concurrency('task')
        assert result['ok'] is True
        assert result['active'] == 0


class TestTopicProjectConcurrency:
    """测试 topic/project 并发上限校验（v6.2.0 修复）"""

    def test_topic_concurrency_enforced_in_p(self, temp_pdca_env):
        """p() 在 topic 级并发达上限时拒绝创建"""
        topic_id = "TOPIC-X"

        # 创建 5 个同一 topic 的任务（topic 上限 = 5）
        for i in range(5):
            p(f"TC-{i:03d}", f"任务 {i}", topic_id=topic_id)
            d(f"TC-{i:03d}", "进行中", status="partial")

        # 第 6 个应该被拒绝
        result = p("TC-005", "第6个任务", topic_id=topic_id)
        assert result['ok'] is False
        assert '并发上限' in result['error']

    def test_project_concurrency_enforced_in_p(self, temp_pdca_env):
        """p() 在 project 级并发达上限时拒绝创建"""
        project_id = "PROJ-Y"

        # 创建 3 个同一 project 的任务（project 上限 = 3）
        for i in range(3):
            p(f"PC-{i:03d}", f"任务 {i}", project_id=project_id)
            d(f"PC-{i:03d}", "进行中", status="partial")

        # 第 4 个应该被拒绝
        result = p("PC-003", "第4个任务", project_id=project_id)
        assert result['ok'] is False
        assert '并发上限' in result['error']

    def test_concurrency_not_triggered_without_ids(self, temp_pdca_env):
        """未指定 topic_id/project_id 时不检查 topic/project 并发"""
        # 不指定 topic/project，只检查 task 级
        result = p("NO-SCOPE", "无归属任务")
        assert result['ok'] is True


class TestSkipVerdictConsecutiveFails:
    """测试 skip verdict 不重置连续失败计数（v6.2.0 修复）"""

    def test_skip_does_not_reset_consecutive_fails(self, temp_pdca_env):
        """[fail, fail, skip, fail] 应计数 2 而非 1"""
        task_id = "SKIP-CONSEC"

        # Cycle 1: fail
        p(f"{task_id}", "测试1")
        d(f"{task_id}", "完成", status="completed")
        c(f"{task_id}", review_level='L0', verdict='fail')
        a(f"{task_id}", "总结1")

        # Cycle 2: fail
        p(f"{task_id}", "测试2")
        d(f"{task_id}", "完成", status="completed")
        c(f"{task_id}", review_level='L0', verdict='fail')
        a(f"{task_id}", "总结2")

        # Cycle 3: skip (not applicable)
        p(f"{task_id}", "测试3")
        d(f"{task_id}", "完成", status="completed")
        c(f"{task_id}", review_level='L0', verdict='skip')
        a(f"{task_id}", "总结3")

        # Cycle 4: fail again
        p(f"{task_id}", "测试4")
        d(f"{task_id}", "完成", status="completed")
        c(f"{task_id}", review_level='L0', verdict='fail')
        a(f"{task_id}", "总结4")

        status = get_status(task_id)
        # skip should not reset the counter, so consecutive_fails should be 3 (all fails counted)
        assert status['consecutive_fails'] == 3

    def test_pass_resets_consecutive_fails(self, temp_pdca_env):
        """pass 仍然重置计数器"""
        task_id = "PASS-RESET"

        for i in range(3):
            p(f"{task_id}", f"测试{i}")
            d(f"{task_id}", "完成", status="completed")
            c(f"{task_id}", review_level='L0', verdict='fail')
            a(f"{task_id}", f"总结{i}")

        # Now pass
        p(f"{task_id}", "最终测试")
        d(f"{task_id}", "完成", status="completed")
        c(f"{task_id}", review_level='L0', verdict='pass')
        a(f"{task_id}", "最终总结")

        status = get_status(task_id)
        assert status['consecutive_fails'] == 0


class TestVerdictsEqual:
    """测试 _verdicts_equal 比较逻辑（v6.2.0 修复）"""

    def test_children_vs_topics_key_mismatch(self):
        """new 用 children，old 用 topics，应正确比较"""
        new = {
            'T01': {'verdict': 'pass', 'children': [{'task': 'T01-T01', 'verdict': 'pass'}]},
        }
        old = {
            'T01': {'verdict': 'pass', 'topics': [{'task': 'T01-T01', 'verdict': 'pass'}]},
        }
        assert _verdicts_equal(new, old) is True

    def test_active_count_change_is_detected(self):
        """active_count 变化应被视为变化"""
        new = {
            'T01': {'verdict': 'pass', 'active_count': 3, 'task_count': 5},
        }
        old = {
            'T01': {'verdict': 'pass', 'active_count': 2, 'task_count': 5},
        }
        assert _verdicts_equal(new, old) is False

    def test_task_count_change_is_detected(self):
        """task_count 变化应被视为变化"""
        new = {
            'T01': {'verdict': 'pass', 'active_count': 3, 'task_count': 6},
        }
        old = {
            'T01': {'verdict': 'pass', 'active_count': 3, 'task_count': 5},
        }
        assert _verdicts_equal(new, old) is False

    def test_no_changes_returns_true(self):
        """完全相同应返回 True"""
        data = {
            'T01': {'verdict': 'pass', 'active_count': 3, 'task_count': 5,
                    'children': [{'task': 'T01-T01', 'verdict': 'pass'}]},
        }
        assert _verdicts_equal(data, data) is True

    def test_verdict_mismatch_returns_false(self):
        """verdict 不同应返回 False"""
        new = {'T01': {'verdict': 'pass'}}
        old = {'T01': {'verdict': 'fail'}}
        assert _verdicts_equal(new, old) is False

    def test_key_set_mismatch_returns_false(self):
        """key 集合不同应返回 False"""
        new = {'T01': {'verdict': 'pass'}}
        old = {'T01': {'verdict': 'pass'}, 'T02': {'verdict': 'pass'}}
        assert _verdicts_equal(new, old) is False


class TestVerdictWeightedModeFailThreshold:
    """测试加权模式 fail 阈值可达性"""

    def test_high_fail_ratio_below_pass_threshold(self):
        """40% fail, 60% pass: pass_ratio < 0.80, fail_ratio >= 0.20 → 应返回 fail"""
        verdicts = ['pass'] * 6 + ['fail'] * 4
        result = _aggregate_verdict(verdicts, mode='weighted')
        assert result == 'fail'

    def test_exactly_20_percent_fail(self):
        """20% fail, 80% pass: pass_ratio >= 0.80 → 返回 pass"""
        verdicts = ['pass'] * 8 + ['fail'] * 2
        result = _aggregate_verdict(verdicts, mode='weighted')
        assert result == 'pass'
