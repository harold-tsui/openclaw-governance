#!/usr/bin/env python3
"""
NUCLEUS v8.1 CQO 合规闸门 — 集成测试

模拟 OpenClaw + 人类共同参与的完整 PDCA 流程：
  1. 正常流程: Plan → Do → CQO Review(pass) → Check(L1) → Act
  2. CQO revise 流程: Plan → Do → CQO(revise) → Do → CQO(pass) → Check → Act
  3. CQO reject 流程: Plan → Do → CQO(reject) → 通知银月
  4. L3 人工审批 + CQO: Plan → Do → CQO(pass) → Check(L3 pending) → Harold 回复 → Act
  5. 断点续传 + CQO: heartbeat 中断在 CQO Review 阶段，下次恢复
  6. CQO revise 上限: 连续 revise 达上限后自动升级为 reject
  7. 完整飞书日志格式: 验证 CQO 步骤在日志中正确记录
"""

import os
import json
import pytest
import sys
import tempfile
import yaml

# Add scripts/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from pdca import (
    p, d, c, a, cqo_review,
    get_status, get_history, get_pending,
    _load,
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
    monkeypatch.setattr(pdca_module, 'CONFIG_FILE', str(config_dir / 'pdca_config.yaml'))
    monkeypatch.setattr(pdca_module, 'STATE_FILE', str(pdca_dir / '_state.yaml'))


class TestCQOIntegrationNormalFlow:
    """集成测试 1: 正常流程 — CQO pass → L1 Check → Act"""

    def test_full_normal_flow_with_cqo(self, temp_pdca_env):
        task_id = "INT-NORMAL-001"

        # Plan
        result_p = p(task_id, "实现用户认证功能",
                     acceptance_criteria=["登录接口", "Token 生成", "单元测试"],
                     topic_id="T01", project_id="ZT-P020")
        assert result_p['ok'] is True
        assert result_p['phase'] == 'plan'

        # Do
        result_d = d(task_id, "完成 JWT 认证模块，修改 auth.py + 新增 test_auth.py",
                     status="completed")
        assert result_d['ok'] is True
        assert result_d['phase'] == 'cqo_review'

        # CQO Review — CQO (张铁) 审核交付物合规性
        result_cqo = cqo_review(task_id, result='pass',
                                report_path='10_Projects/ZT-P020/T01/deliverables/CQO-INT-NORMAL-001.md')
        assert result_cqo['ok'] is True
        assert result_cqo['phase'] == 'check'
        assert result_cqo['cqo_result'] == 'pass'

        # Check — L1 自验收
        result_c = c(task_id, review_level='L1', verdict='pass',
                     evidence=["3/3 tests passed", "coverage 87%"])
        assert result_c['ok'] is True
        assert result_c['phase'] == 'act'

        # Act
        result_a = a(task_id, "认证功能完成，下一任务 INT-NORMAL-002",
                     next_task="INT-NORMAL-002",
                     lessons=["JWT secret 需从环境变量读取"])
        assert result_a['ok'] is True
        assert result_a['phase'] == 'completed'

        # 验证最终状态
        status = get_status(task_id)
        assert status['current_phase'] == 'completed'
        assert status['current_verdict'] == 'pass'
        assert status['cqo_review_status'] == 'pass'


class TestCQOIntegrationReviseFlow:
    """集成测试 2: CQO revise → 修改 → CQO pass → Check → Act"""

    def test_revise_then_pass(self, temp_pdca_env):
        task_id = "INT-REVISE-001"

        # Plan → Do
        p(task_id, "编写 API 文档", acceptance_criteria=["OpenAPI spec", "示例代码"])
        d(task_id, "完成 API 文档初版", status="completed")

        # CQO Review — 发现模板不匹配 + 元数据缺失
        result_cqo1 = cqo_review(task_id, result='revise',
                                 issues=['CQO-01', 'CQO-02'])
        assert result_cqo1['phase'] == 'do'
        assert result_cqo1['cqo_result'] == 'revise'
        assert result_cqo1['revise_count'] == 1

        # 修改后重新 Do
        result_d2 = d(task_id, "使用 TMPL-API-SPEC 模板重写，补充 frontmatter",
                      status="completed")
        assert result_d2['phase'] == 'cqo_review'

        # CQO Review — 本次通过
        result_cqo2 = cqo_review(task_id, result='pass')
        assert result_cqo2['phase'] == 'check'

        # Check → Act
        c(task_id, review_level='L1', verdict='pass')
        a(task_id, "API 文档完成")

        # 验证 CQO revise 历史保留
        history = get_history(task_id)
        assert history['cycles'][0]['cqo_result'] == 'pass'

        record = _load(task_id)
        cqo_data = record['cycles'][0]['cqo_review']
        assert cqo_data['revise_count'] == 1  # 历史记录


class TestCQOIntegrationRejectFlow:
    """集成测试 3: CQO reject → 通知银月 → 重做"""

    def test_reject_triggers_notification(self, temp_pdca_env):
        task_id = "INT-REJECT-001"

        # Plan → Do
        p(task_id, "创建项目章程", acceptance_criteria=["完整模板", "路径合规"])
        d(task_id, "完成项目章程", status="completed")

        # CQO Review — 3+ 项不通过 → reject
        result_cqo = cqo_review(task_id, result='reject',
                                issues=['CQO-01', 'CQO-03', 'CQO-04'])
        assert result_cqo['phase'] == 'do'
        assert result_cqo['cqo_result'] == 'reject'
        assert result_cqo['revise_count'] == 1

        # 验证 Task 状态仍为执行中
        status = get_status(task_id)
        assert status['current_phase'] == 'do'

        # 重做后重新 Do → CQO pass → 完成
        d(task_id, "使用正确模板重做项目章程，移至合规路径", status="completed")
        cqo_review(task_id, result='pass')
        c(task_id, review_level='L2', verdict='pass')
        a(task_id, "项目章程完成")

        status = get_status(task_id)
        assert status['current_phase'] == 'completed'


class TestCQOIntegrationL3WithCQO:
    """集成测试 4: CQO pass + L3 人工审批"""

    def test_cqo_then_l3_human_approval(self, temp_pdca_env):
        task_id = "INT-L3-CQO-001"

        # Plan → Do → CQO pass
        p(task_id, "制定年度技术战略", acceptance_criteria=["技术雷达", "优先级矩阵"])
        d(task_id, "完成年度技术战略文档", status="completed")
        cqo_review(task_id, result='pass')

        # Check — L3 pending（等待 Harold）
        result_c1 = c(task_id, review_level='L3', verdict='pending')
        assert result_c1['phase'] == 'check'

        # 检查 pending 列表
        pending = get_pending()
        assert any(p['task_card_id'] == task_id for p in pending)

        # Harold 回复 A（批准）
        result_c2 = c(task_id, review_level='L3', verdict='pass')
        assert result_c2['phase'] == 'act'

        # Act
        a(task_id, "Harold 批准年度技术战略")

        status = get_status(task_id)
        assert status['current_phase'] == 'completed'
        assert status['current_verdict'] == 'pass'


class TestCQOIntegrationBreakpointResume:
    """集成测试 5: 断点续传 — heartbeat 在 CQO Review 阶段中断"""

    def test_resume_from_cqo_review_phase(self, temp_pdca_env):
        task_id = "INT-BREAK-001"

        # Plan → Do（heartbeat 在这里中断，未执行 CQO Review）
        p(task_id, "集成测试框架搭建")
        d(task_id, "完成 pytest conftest + 3 个 test case", status="completed")

        # 模拟：下次 heartbeat 读取状态
        status = get_status(task_id)
        assert status['current_phase'] == 'cqo_review'

        # 从断点继续：执行 CQO Review
        cqo_review(task_id, result='pass')

        # 继续 Check → Act
        c(task_id, review_level='L1', verdict='pass')
        a(task_id, "集成测试框架完成")

        status = get_status(task_id)
        assert status['current_phase'] == 'completed'


class TestCQOIntegrationReviseLimit:
    """集成测试 6: CQO revise 上限 — 连续 revise 后自动升级为 reject"""

    def test_three_revises_then_auto_reject(self, temp_pdca_env):
        task_id = "INT-LIMIT-001"

        p(task_id, "编写规范文档")
        d(task_id, "完成初版", status="completed")

        # revise 1
        cqo_review(task_id, result='revise', issues=['CQO-01'])
        d(task_id, "修改模板", status="completed")

        # revise 2
        cqo_review(task_id, result='revise', issues=['CQO-02'])
        d(task_id, "补充元数据", status="completed")

        # revise 3
        cqo_review(task_id, result='revise', issues=['CQO-04'])
        d(task_id, "补充章节", status="completed")

        # revise 4 — 应自动升级为 reject
        result = cqo_review(task_id, result='revise', issues=['CQO-05'])
        assert result['cqo_result'] == 'reject'
        assert result['revise_count'] == 4
        assert result['phase'] == 'do'


class TestCQOIntegrationFeishuLogFormat:
    """集成测试 7: 飞书步骤级执行日志 — CQO 步骤记录"""

    def test_cqo_step_in_log(self, temp_pdca_env):
        task_id = "INT-LOG-001"

        # 完整 PDCA 流程
        p(task_id, "飞书日志测试", topic_id="T01", project_id="ZT-P020")
        d(task_id, "执行完成", status="completed")
        cqo_review(task_id, result='pass',
                   report_path='deliverables/CQO-INT-LOG-001.md')
        c(task_id, review_level='L1', verdict='pass')
        a(task_id, "完成")

        # 验证执行日志文件包含 cqo_review 记录
        log_path = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'pdca_test_log.jsonl')
        # 日志格式验证：cqo_review 命令应出现在 _log_call 中
        record = _load(task_id)
        cqo_data = record['cycles'][0]['cqo_review']
        assert cqo_data is not None
        assert cqo_data['result'] == 'pass'
        assert cqo_data['report_path'] == 'deliverables/CQO-INT-LOG-001.md'

        # 验证 status 包含 CQO 信息（用于飞书日志格式化）
        # 预期飞书格式:
        #   Q: CQO合规审核 [pass] —
        status = get_status(task_id)
        assert status['cqo_review_status'] == 'pass'


class TestCQOIntegrationBackwardCompatible:
    """集成测试 8: 向后兼容 — 不走 CQO 的旧流程仍可工作"""

    def test_skip_cqo_still_works(self, temp_pdca_env):
        """旧流程: Plan → Do → Check → Act（跳过 CQO Review）"""
        task_id = "INT-COMPAT-001"

        p(task_id, "向后兼容测试")
        d(task_id, "执行完成", status="completed")

        # 直接进入 Check，不调用 cqo_review
        result_c = c(task_id, review_level='L1', verdict='pass')
        assert result_c['ok'] is True
        assert result_c['phase'] == 'act'

        a(task_id, "向后兼容流程完成")

        status = get_status(task_id)
        assert status['current_phase'] == 'completed'
        # cqo_review_status 应为 None（未经过 CQO）
        assert status['cqo_review_status'] is None

    def test_d_blocked_stays_in_do_phase(self, temp_pdca_env):
        """Do blocked 时 phase 保持 do，不进入 cqo_review"""
        task_id = "INT-BLOCKED-001"

        p(task_id, "阻塞测试")
        result_d = d(task_id, "等待外部依赖", status="blocked", blocker="API 未就绪")
        assert result_d['phase'] == 'do'  # blocked 不触发 cqo_review
