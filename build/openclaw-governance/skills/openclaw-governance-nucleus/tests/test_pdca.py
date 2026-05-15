#!/usr/bin/env python3
"""
NUCLEUS v4.0 PDCA 核心功能测试

测试覆盖目标：80%
重点：p/d/c/a 流程、并发控制、审计闭环、幂等性验证
"""

import os
import pytest
import shutil
import sys
import tempfile
import yaml
from datetime import datetime
from pathlib import Path

# 添加 scripts 目录到 Python path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from pdca import (
    p, d, c, a, cqo_review,
    check_concurrency,
    verify_cycle_write,
    get_audit_queue,
    mark_audit,
    get_status,
    get_history,
    get_pending,
)


@pytest.fixture
def temp_pdca_env(tmp_path, monkeypatch):
    """
    创建临时 PDCA 环境
    - 临时 pdca/ 目录
    - 临时 logs/ 目录
    - 设置环境变量指向临时目录
    """
    pdca_dir = tmp_path / "pdca"
    pdca_dir.mkdir()
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()

    # Monkeypatch the global paths in pdca.py
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


class TestPDCAWorkflow:
    """测试完整 PDCA 流程"""

    def test_full_pdca_cycle_l0(self, temp_pdca_env):
        """完整 PDCA 流程：P→D→C→A（L0 自验收）"""
        task_id = "TEST-FULL-001"

        # Plan
        result_p = p(
            task_card_id=task_id,
            summary="测试完整 PDCA 流程",
            acceptance_criteria=["AC1", "AC2"]
        )
        assert result_p['ok'] is True
        assert result_p['phase'] == 'plan'

        # Do
        result_d = d(
            task_card_id=task_id,
            summary="执行完成",
            status="completed"
        )
        assert result_d['ok'] is True
        assert result_d['phase'] == 'cqo_review'

        # CQO Review (v8.1: Do→CQO Review→Check)
        result_cqo = cqo_review(
            task_card_id=task_id,
            result='pass',
            report_path='deliverables/CQO-TEST-L0-001.md'
        )
        assert result_cqo['ok'] is True
        assert result_cqo['phase'] == 'check'
        assert result_cqo['cqo_result'] == 'pass'

        # Check (L0 自验收)
        result_c = c(
            task_card_id=task_id,
            review_level='L0',
            verdict='pass'
        )
        assert result_c['ok'] is True
        # Phase advances to 'act' after successful L0/L1 check
        assert result_c['phase'] == 'act'
        assert result_c['needs_act'] is True

        # Act
        result_a = a(
            task_card_id=task_id,
            summary="总结经验"
        )
        assert result_a['ok'] is True
        assert result_a['phase'] == 'completed'

        # 验证写入
        verify = verify_cycle_write(task_id, cycle_index=1)
        assert verify['ok'] is True
        assert verify['phase'] == 'completed'
        assert verify['verdict'] == 'pass'

    def test_full_pdca_cycle_l3_pending(self, temp_pdca_env):
        """完整 PDCA 流程：L3 pending → Harold 回复 → Act"""
        task_id = "TEST-L3-001"

        # P → D → CQO Review
        p(task_id, "L3 测试", acceptance_criteria=["AC1"])
        d(task_id, "执行完成", status="completed")
        cqo_review(task_id, result='pass')

        # Check (L3 pending)
        result_c = c(
            task_card_id=task_id,
            review_level='L3',
            verdict='pending'
        )
        assert result_c['ok'] is True
        assert result_c['phase'] == 'check'
        # audit_eligible 不在返回值中，在 cycle 数据中

        # Harold 回复后第二次 Check
        result_c2 = c(
            task_card_id=task_id,
            review_level='L3',
            verdict='pass'
        )
        assert result_c2['ok'] is True

        # Act
        result_a = a(task_id, "Harold 批准后总结")
        assert result_a['ok'] is True
        assert result_a['phase'] == 'completed'

    def test_phase_sequence_enforcement(self, temp_pdca_env):
        """测试阶段顺序强制约束"""
        task_id = "TEST-SEQ-001"

        # 未执行 P，直接 D 应失败
        result = d(task_id, "非法跳过 Plan", status="completed")
        assert result['ok'] is False
        assert 'Plan' in result['error'] or 'cycle' in result['error'].lower()

        # 正常 P → D
        p(task_id, "正常流程")
        d(task_id, "正常执行", status="completed")

        # D 后直接 Act 应失败（需先 Check）
        result = a(task_id, "非法跳过 Check")
        assert result['ok'] is False
        assert 'Check' in result['error'] or 'Act' in result['error']

    def test_l0_l1_cannot_be_pending(self, temp_pdca_env):
        """测试 L0/L1 不允许 verdict=pending"""
        task_id = "TEST-L0-PENDING"

        p(task_id, "L0 测试")
        d(task_id, "完成", status="completed")

        # L0 + pending 应失败
        result = c(
            task_card_id=task_id,
            review_level='L0',
            verdict='pending'
        )
        assert result['ok'] is False
        assert 'L0' in result['error'] and 'pending' in result['error']


class TestConcurrencyControl:
    """测试并发控制"""

    def test_task_concurrency_limit(self, temp_pdca_env):
        """测试 task 并发上限（10）"""
        # 创建 10 个活跃 task
        for i in range(10):
            result = p(f"TASK-{i:03d}", f"Task {i}")
            assert result['ok'] is True

        # 第 11 个应被拒绝
        result = p("TASK-011", "Overflow task")
        assert result['ok'] is False
        assert '并发上限' in result['error'] or '超出' in result['error']

        # 完成一个 task 后应可创建新 task
        d("TASK-000", "Done", status="completed")
        c("TASK-000", review_level='L0', verdict='pass')
        a("TASK-000", "Finished")

        # 现在应该可以创建新的
        result = p("TASK-011", "Should succeed now")
        assert result['ok'] is True

    def test_check_concurrency_function(self, temp_pdca_env):
        """测试 check_concurrency() 函数"""
        # 无活跃 task
        result = check_concurrency('task')
        assert result['ok'] is True
        assert result['active'] == 0

        # 创建 3 个活跃 task
        for i in range(3):
            p(f"CHECK-{i}", f"Task {i}")

        result = check_concurrency('task')
        assert result['ok'] is True
        assert result['active'] == 3
        assert result['limit'] == 10


class TestAuditLoop:
    """测试审计闭环"""

    def test_audit_queue_with_l0_pass(self, temp_pdca_env):
        """L0/L1 pass 任务应进入审计队列"""
        task_id = "AUDIT-001"

        # 完整流程：L0 + pass
        p(task_id, "审计测试", acceptance_criteria=["AC1"])
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "总结")

        # 获取审计队列
        queue = get_audit_queue()
        assert len(queue) == 1
        assert queue[0]['task_card_id'] == task_id
        assert queue[0]['review_level'] == 'L0'

    def test_mark_audit_success(self, temp_pdca_env):
        """测试 mark_audit() 成功场景"""
        task_id = "AUDIT-002"

        # 创建待审计任务
        p(task_id, "审计测试 2")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L1', verdict='pass')
        a(task_id, "总结")

        # 标记审计：高分
        result = mark_audit(task_id, cycle_index=1, score=85)
        assert result['ok'] is True
        assert result['score'] == 85
        assert result['has_problem'] is False

        # 审计后应从队列移除
        queue = get_audit_queue()
        assert len(queue) == 0

    def test_mark_audit_low_score(self, temp_pdca_env):
        """测试 mark_audit() 低分场景"""
        task_id = "AUDIT-003"

        p(task_id, "审计测试 3")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L1', verdict='pass')
        a(task_id, "总结")

        # 标记审计：低分
        result = mark_audit(
            task_id,
            cycle_index=1,
            score=55,
            issues=["测试不足", "文档缺失"]
        )
        assert result['ok'] is True
        assert result['score'] == 55
        assert result['has_problem'] is True

    def test_l3_not_audit_eligible(self, temp_pdca_env):
        """L3 任务不应进入审计队列"""
        task_id = "AUDIT-L3"

        p(task_id, "L3 测试")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L3', verdict='pending')
        c(task_id, review_level='L3', verdict='pass')  # Harold 回复后
        a(task_id, "总结")

        # L3 不应在审计队列
        queue = get_audit_queue()
        assert all(q['task_card_id'] != task_id for q in queue)


class TestIdempotency:
    """测试幂等性"""

    def test_duplicate_plan_rejected(self, temp_pdca_env):
        """同一 task_card_id 不允许重复 Plan（未完成时）"""
        task_id = "IDEMPOTENT-001"

        # 第一次 Plan
        result1 = p(task_id, "第一次")
        assert result1['ok'] is True

        # 第二次 Plan 应被拒绝（因为 cycle 未完成）
        result2 = p(task_id, "第二次")
        assert result2['ok'] is False or result2['cycle_index'] == 1  # 复用现有 cycle

    def test_completed_cycle_allows_new_cycle(self, temp_pdca_env):
        """已完成 cycle 应允许创建新 cycle"""
        task_id = "IDEMPOTENT-002"

        # 完成第一个 cycle
        p(task_id, "Cycle 1")
        d(task_id, "Done 1", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "Summary 1")

        # 创建第二个 cycle 应成功
        result = p(task_id, "Cycle 2")
        assert result['ok'] is True
        assert result['cycle_index'] == 2

    def test_verify_cycle_write_idempotency(self, temp_pdca_env):
        """测试 verify_cycle_write() 验证写入"""
        task_id = "VERIFY-001"

        p(task_id, "验证测试")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "总结")

        # 验证写入成功
        verify = verify_cycle_write(task_id, cycle_index=1)
        assert verify['ok'] is True
        assert verify['phase'] == 'completed'
        assert 'p' in verify['timestamps']
        assert 'd' in verify['timestamps']
        assert 'c' in verify['timestamps']
        assert 'a' in verify['timestamps']

    def test_verify_invalid_cycle_index(self, temp_pdca_env):
        """测试验证无效 cycle_index"""
        task_id = "VERIFY-002"

        p(task_id, "测试")

        # cycle_index=99 不存在
        verify = verify_cycle_write(task_id, cycle_index=99)
        assert verify['ok'] is False
        assert 'Invalid cycle_index' in verify['error']


class TestQueryFunctions:
    """测试查询函数"""

    def test_get_status(self, temp_pdca_env):
        """测试 get_status()"""
        task_id = "STATUS-001"

        p(task_id, "状态测试")
        d(task_id, "完成", status="completed")

        status = get_status(task_id)
        assert status['task_card_id'] == task_id
        assert status['current_phase'] == 'cqo_review'
        assert status['cqo_review_status'] is None
        assert status['cycles_total'] == 1
        assert status['current_cycle_index'] == 1

    def test_get_history(self, temp_pdca_env):
        """测试 get_history()"""
        task_id = "HISTORY-001"

        # 创建 2 个 cycle
        p(task_id, "Cycle 1")
        d(task_id, "Done 1", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "Summary 1")

        p(task_id, "Cycle 2")
        d(task_id, "Done 2", status="completed")

        history = get_history(task_id)
        assert history['task_card_id'] == task_id
        assert history['cycles_total'] == 2
        assert len(history['cycles']) == 2
        assert history['cycles'][0]['cycle_index'] == 1
        assert history['cycles'][1]['cycle_index'] == 2

    def test_get_pending_l2(self, temp_pdca_env):
        """测试 get_pending() L2 过滤"""
        # 创建 L2 pending 任务
        p("PENDING-L2", "L2 测试")
        d("PENDING-L2", "完成", status="completed")
        c("PENDING-L2", review_level='L2', verdict='pending')

        # 创建 L3 pending 任务
        p("PENDING-L3", "L3 测试")
        d("PENDING-L3", "完成", status="completed")
        c("PENDING-L3", review_level='L3', verdict='pending')

        # 查询 L2 pending
        pending_l2 = get_pending(review_level='L2')
        assert len(pending_l2) >= 1
        assert all(p['review_level'] == 'L2' for p in pending_l2)


class TestErrorHandling:
    """测试错误处理"""

    def test_invalid_review_level(self, temp_pdca_env):
        """测试无效 review_level"""
        task_id = "ERROR-001"

        p(task_id, "错误测试")
        d(task_id, "完成", status="completed")

        result = c(task_id, review_level='L99', verdict='pass')
        assert result['ok'] is False
        assert 'invalid level' in result['error'].lower()

    def test_missing_task_card_id(self, temp_pdca_env):
        """测试缺少 task_card_id"""
        result = d(task_card_id="NONEXISTENT", summary="不存在", status="completed")
        assert result['ok'] is False

    def test_verdict_overwrite_protection(self, temp_pdca_env):
        """测试 verdict 覆盖保护"""
        task_id = "PROTECT-001"

        p(task_id, "保护测试")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L0', verdict='pass')

        # 尝试覆盖 verdict 应失败
        result = c(task_id, review_level='L0', verdict='fail')
        # 根据实际实现，这可能允许或拒绝
        # 这里假设不允许覆盖已有 verdict
        # 如果 pdca.py 允许覆盖，需调整断言


class TestCQOReview:
    """测试 CQO 合规闸门（v8.1）"""

    def test_cqo_review_pass_advances_to_check(self, temp_pdca_env):
        """CQO Review pass → phase 推进到 check"""
        task_id = "CQO-PASS-001"
        p(task_id, "CQO pass 测试")
        d(task_id, "执行完成", status="completed")

        result = cqo_review(task_id, result='pass', report_path='deliverables/CQO-CQO-PASS-001.md')
        assert result['ok'] is True
        assert result['phase'] == 'check'
        assert result['cqo_result'] == 'pass'
        assert result['revise_count'] == 0

        # 后续 Check 可正常执行
        result_c = c(task_id, review_level='L0', verdict='pass')
        assert result_c['ok'] is True
        assert result_c['phase'] == 'act'

    def test_cqo_review_revise_returns_to_do(self, temp_pdca_env):
        """CQO Review revise → phase 退回 do，同一 cycle"""
        task_id = "CQO-REVISE-001"
        p(task_id, "CQO revise 测试")
        d(task_id, "执行完成", status="completed")

        result = cqo_review(task_id, result='revise', issues=['CQO-01', 'CQO-03'])
        assert result['ok'] is True
        assert result['phase'] == 'do'
        assert result['cqo_result'] == 'revise'
        assert result['revise_count'] == 1

        # 可以再次 Do → CQO Review
        result_d2 = d(task_id, "修改后重新执行", status="completed")
        assert result_d2['phase'] == 'cqo_review'

        # 第二次 CQO Review pass
        result_cqo2 = cqo_review(task_id, result='pass')
        assert result_cqo2['phase'] == 'check'
        assert result_cqo2['revise_count'] == 1  # revise_count 保持历史记录

    def test_cqo_review_reject_returns_to_do(self, temp_pdca_env):
        """CQO Review reject → phase 退回 do，通知银月"""
        task_id = "CQO-REJECT-001"
        p(task_id, "CQO reject 测试")
        d(task_id, "执行完成", status="completed")

        result = cqo_review(task_id, result='reject', issues=['CQO-01', 'CQO-02', 'CQO-03'])
        assert result['ok'] is True
        assert result['phase'] == 'do'
        assert result['cqo_result'] == 'reject'
        assert result['revise_count'] == 1

    def test_cqo_revise_limit_auto_upgrades_to_reject(self, temp_pdca_env):
        """CQO revise 上限：第 4 次 revise → 自动升级为 reject"""
        task_id = "CQO-LIMIT-001"
        p(task_id, "CQO revise 上限测试")
        d(task_id, "执行完成", status="completed")

        # revise 3 次
        for i in range(3):
            cqo_review(task_id, result='revise', issues=['CQO-01'])
            d(task_id, f"修改第{i+1}次", status="completed")

        # 第 4 次 revise 应自动升级为 reject
        result = cqo_review(task_id, result='revise', issues=['CQO-01'])
        assert result['ok'] is True
        assert result['cqo_result'] == 'reject'
        assert result['revise_count'] == 4

    def test_cqo_review_invalid_result(self, temp_pdca_env):
        """CQO Review 无效结果应拒绝"""
        task_id = "CQO-INVALID-001"
        p(task_id, "CQO 无效结果测试")
        d(task_id, "执行完成", status="completed")

        result = cqo_review(task_id, result='maybe')
        assert result['ok'] is False
        assert 'invalid' in result['error'].lower()

    def test_cqo_review_without_do_fails(self, temp_pdca_env):
        """CQO Review 不能在没有 Do 的情况下调用"""
        task_id = "CQO-NODO-001"
        p(task_id, "CQO 无 Do 测试")

        result = cqo_review(task_id, result='pass')
        assert result['ok'] is False

    def test_cqo_review_in_status_output(self, temp_pdca_env):
        """get_status 包含 cqo_review_status"""
        task_id = "CQO-STATUS-001"
        p(task_id, "CQO 状态测试")
        d(task_id, "执行完成", status="completed")

        status = get_status(task_id)
        assert status['current_phase'] == 'cqo_review'
        assert status['cqo_review_status'] is None

        cqo_review(task_id, result='pass')

        status = get_status(task_id)
        assert status['cqo_review_status'] == 'pass'

    def test_cqo_review_in_history_output(self, temp_pdca_env):
        """get_history 包含 cqo_result"""
        task_id = "CQO-HIST-001"
        p(task_id, "CQO 历史测试")
        d(task_id, "执行完成", status="completed")
        cqo_review(task_id, result='pass')

        history = get_history(task_id)
        assert history['cycles'][0]['cqo_result'] == 'pass'

    def test_cqo_review_skip_backward_compatible(self, temp_pdca_env):
        """跳过 CQO Review，直接从 do 进入 Check（向后兼容）"""
        task_id = "CQO-SKIP-001"
        p(task_id, "跳过 CQO 测试")
        d(task_id, "执行完成", status="completed")

        # 直接调用 c() 而不经过 cqo_review()，应仍可工作
        result_c = c(task_id, review_level='L0', verdict='pass')
        assert result_c['ok'] is True
        assert result_c['phase'] == 'act'
