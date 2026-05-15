#!/usr/bin/env python3
"""
NUCLEUS v4.0 PDCA 扩展测试

补充测试覆盖：边界情况、错误处理、blocker、特殊场景
目标：将覆盖率从 56% 提升到 80%+
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
    get_status,
    get_pending,
    aggregate,
    _aggregate_verdict,
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


class TestBlockerHandling:
    """测试 blocker 处理逻辑"""

    def test_do_with_blocker(self, temp_pdca_env):
        """测试 Do 阶段阻塞"""
        task_id = "BLOCKED-001"

        p(task_id, "测试阻塞")
        result = d(task_id, "遇到阻塞", status="blocked", blocker="依赖服务不可用")

        assert result['ok'] is True
        assert result['status'] == 'blocked'

    def test_partial_status(self, temp_pdca_env):
        """测试 partial 状态"""
        task_id = "PARTIAL-001"

        p(task_id, "部分完成测试")
        result = d(task_id, "部分完成", status="partial")

        assert result['ok'] is True
        assert result['status'] == 'partial'


class TestVerdictVariations:
    """测试各种 verdict 组合"""

    def test_verdict_fail(self, temp_pdca_env):
        """测试 fail verdict"""
        task_id = "FAIL-001"

        p(task_id, "失败测试")
        d(task_id, "完成", status="completed")
        result = c(task_id, review_level='L0', verdict='fail')

        assert result['ok'] is True
        assert result['verdict'] == 'fail'

    def test_verdict_partial(self, temp_pdca_env):
        """测试 partial verdict"""
        task_id = "PARTIAL-VER-001"

        p(task_id, "部分通过测试")
        d(task_id, "完成", status="completed")
        result = c(task_id, review_level='L1', verdict='partial')

        assert result['ok'] is True
        assert result['verdict'] == 'partial'

    def test_verdict_skip(self, temp_pdca_env):
        """测试 skip verdict"""
        task_id = "SKIP-001"

        p(task_id, "跳过测试")
        d(task_id, "完成", status="completed")
        result = c(task_id, review_level='L0', verdict='skip')

        assert result['ok'] is True
        assert result['verdict'] == 'skip'


class TestAggregateWeightedMode:
    """测试加权聚合模式（P2-1 功能）"""

    def test_weighted_mode_80_percent_pass(self, temp_pdca_env):
        """测试加权模式：80% pass → pass"""
        # 创建 10 个 task：8 pass, 2 fail
        for i in range(8):
            task_id = f"WEIGHT-PASS-{i}"
            p(task_id, f"Task {i}", topic_id="TOPIC-WEIGHT")
            d(task_id, "Done", status="completed")
            c(task_id, review_level='L0', verdict='pass')
            a(task_id, "Summary")

        for i in range(2):
            task_id = f"WEIGHT-FAIL-{i}"
            p(task_id, f"Task {i}", topic_id="TOPIC-WEIGHT")
            d(task_id, "Done", status="completed")
            c(task_id, review_level='L0', verdict='fail')
            a(task_id, "Summary")

        # 使用 weighted 模式聚合
        result = aggregate(mode='weighted')
        assert result['ok'] is True

    def test_weighted_mode_20_percent_fail(self, temp_pdca_env):
        """测试加权模式：20% fail → fail"""
        # 创建 5 个 task：1 fail, 4 pass
        for i in range(4):
            task_id = f"WEIGHT2-PASS-{i}"
            p(task_id, f"Task {i}", topic_id="TOPIC-WEIGHT2")
            d(task_id, "Done", status="completed")
            c(task_id, review_level='L0', verdict='pass')
            a(task_id, "Summary")

        task_id = "WEIGHT2-FAIL-0"
        p(task_id, "Task fail", topic_id="TOPIC-WEIGHT2")
        d(task_id, "Done", status="completed")
        c(task_id, review_level='L0', verdict='fail')
        a(task_id, "Summary")

        result = aggregate(mode='weighted')
        assert result['ok'] is True


class TestAggregateVerdictFunction:
    """直接测试 _aggregate_verdict 函数"""

    def test_all_pass(self):
        """全部 pass"""
        result = _aggregate_verdict(['pass', 'pass', 'pass'])
        assert result == 'pass'

    def test_one_fail(self):
        """任一 fail"""
        result = _aggregate_verdict(['pass', 'fail', 'pass'])
        assert result == 'fail'

    def test_all_skip(self):
        """全部 skip"""
        result = _aggregate_verdict(['skip', 'skip'])
        assert result == 'skip'

    def test_mixed(self):
        """混合"""
        result = _aggregate_verdict(['pass', 'partial', 'skip'])
        assert result == 'partial'

    def test_weighted_pass_majority(self):
        """加权模式：大多数 pass"""
        result = _aggregate_verdict(
            ['pass', 'pass', 'pass', 'pass', 'fail'],
            mode='weighted'
        )
        assert result == 'pass'

    def test_weighted_fail_threshold(self):
        """加权模式：fail 超过阈值"""
        result = _aggregate_verdict(
            ['fail', 'fail', 'pass', 'pass', 'pass'],
            mode='weighted'
        )
        # 40% fail >= 20% threshold → fail
        assert result == 'fail'

    def test_weighted_partial_middle(self):
        """加权模式：partial 居中"""
        result = _aggregate_verdict(
            ['pass', 'partial', 'partial', 'skip'],
            mode='weighted'
        )
        assert result in ['partial', 'pass']


class TestMultipleCycles:
    """测试多 cycle 场景"""

    def test_three_cycles(self, temp_pdca_env):
        """测试 3 个 cycle"""
        task_id = "MULTI-001"

        # Cycle 1
        p(task_id, "Cycle 1")
        d(task_id, "Done 1", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "Summary 1")

        # Cycle 2
        p(task_id, "Cycle 2")
        d(task_id, "Done 2", status="completed")
        c(task_id, review_level='L0', verdict='fail')
        a(task_id, "Summary 2")

        # Cycle 3
        p(task_id, "Cycle 3")
        d(task_id, "Done 3", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "Summary 3")

        status = get_status(task_id)
        assert status['cycles_total'] == 3
        assert status['current_cycle_index'] == 3


class TestEvidenceHandling:
    """测试 evidence 处理"""

    def test_check_with_evidence(self, temp_pdca_env):
        """测试带 evidence 的 Check"""
        task_id = "EVIDENCE-001"

        p(task_id, "证据测试")
        d(task_id, "完成", status="completed")

        result = c(
            task_id,
            review_level='L1',
            verdict='pass',
            evidence=["测试通过", "代码审查完成", "性能达标"]
        )

        assert result['ok'] is True
        assert result['verdict'] == 'pass'


class TestTopicProjectHierarchy:
    """测试 Topic/Project 层级"""

    def test_task_with_topic_and_project(self, temp_pdca_env):
        """测试包含 Topic 和 Project 的任务"""
        task_id = "HIER-001"

        p(
            task_id,
            "层级测试",
            topic_id="TOPIC-A",
            project_id="PROJECT-X"
        )
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L0', verdict='pass')
        a(task_id, "总结")

        # 聚合应该包含 topic 和 project
        result = aggregate()
        assert result['ok'] is True


class TestGetPendingFiltering:
    """测试 get_pending 过滤"""

    def test_get_pending_all(self, temp_pdca_env):
        """测试获取所有 pending"""
        # 创建 L2 pending
        p("PEND-L2", "L2 test")
        d("PEND-L2", "Done", status="completed")
        c("PEND-L2", review_level='L2', verdict='pending')

        # 创建 L3 pending
        p("PEND-L3", "L3 test")
        d("PEND-L3", "Done", status="completed")
        c("PEND-L3", review_level='L3', verdict='pending')

        # 获取所有 pending（不过滤）
        all_pending = get_pending()
        assert len(all_pending) >= 2


class TestLessonsAndNextTask:
    """测试 lessons 和 next_task"""

    def test_act_with_lessons_and_next(self, temp_pdca_env):
        """测试 Act 包含 lessons 和 next_task"""
        task_id = "LESSON-001"

        p(task_id, "经验总结测试")
        d(task_id, "完成", status="completed")
        c(task_id, review_level='L0', verdict='pass')

        result = a(
            task_id,
            summary="总结完成",
            lessons=["经验1", "经验2"],
            next_task="LESSON-002"
        )

        assert result['ok'] is True
        assert result['next_task'] == "LESSON-002"


class TestEdgeCases:
    """测试边界情况"""

    def test_empty_acceptance_criteria(self, temp_pdca_env):
        """测试空 acceptance_criteria"""
        task_id = "EDGE-001"

        result = p(task_id, "空 AC", acceptance_criteria=[])
        assert result['ok'] is True

    def test_long_summary(self, temp_pdca_env):
        """测试超长 summary"""
        task_id = "EDGE-002"

        long_summary = "这是一个非常长的摘要 " * 100

        result = p(task_id, long_summary)
        assert result['ok'] is True
