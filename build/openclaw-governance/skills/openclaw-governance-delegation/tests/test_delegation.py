#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
governance-delegation 单元测试（重构版）
使用 pytest fixture 机制确保测试独立性
"""
import os
import sys
import tempfile
import shutil
import yaml
import pytest
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.delegation import (
    determine_review,
    check_authorization,
    check_route_permission,
    determine_automation_level,
    adjust_automation_level,
    AgentNotFoundError,
    InvalidLevelError,
    AdjustmentInvalidError,
    PolicyMissingError
)


@pytest.fixture(scope="function")
def test_config():
    """测试配置fixture，每个测试有独立的配置"""
    temp_config_dir = tempfile.mkdtemp()
    temp_workspace_dir = tempfile.mkdtemp()

    os.environ["GOVERNANCE_CONFIG_DIR"] = temp_config_dir
    os.environ["WORKSPACE_DIR"] = temp_workspace_dir

    os.makedirs(os.path.join(temp_config_dir, "system"), exist_ok=True)
    os.makedirs(os.path.join(temp_config_dir, "user"), exist_ok=True)

    # 创建测试automation-levels.yaml
    levels_config = {
        "harold": {"current_level": "L3"},
        "cqo": {"current_level": "L3", "consecutive_success": 0, "consecutive_failure": 0},
        "cto": {"current_level": "L2", "consecutive_success": 0, "consecutive_failure": 0},
        "main": {"current_level": "L2"}
    }
    with open(os.path.join(temp_config_dir, "automation-levels.yaml"), 'w', encoding='utf-8') as f:
        yaml.dump(levels_config, f, allow_unicode=True, default_flow_style=False)

    yield {
        "temp_config_dir": temp_config_dir,
        "temp_workspace_dir": temp_workspace_dir
    }

    if os.path.exists(temp_config_dir):
        shutil.rmtree(temp_config_dir)
    if os.path.exists(temp_workspace_dir):
        shutil.rmtree(temp_workspace_dir)


def test_determine_review_project(test_config):
    """测试项目级别判定（一律L3）"""
    params = {
        "target_type": "project",
        "task_type": "new"
    }
    
    result = determine_review(params)
    assert result["status"] == "OK"
    assert result["level"] == "L3"
    assert len(result["rationale"]) == 1
    assert result["rationale"][0]["rule"] == "new_project"
    print("✅ test_determine_review_project passed")


def test_determine_review_topic_first_time(test_config):
    """测试首次Topic类型判定（L3）"""
    params = {
        "target_type": "topic",
        "is_first_time": True,
        "project_phase": "transition"
    }
    
    result = determine_review(params)
    assert result["status"] == "OK"
    assert result["level"] == "L3"
    assert result["rationale"][0]["rule"] == "first_topic_type"
    print("✅ test_determine_review_topic_first_time passed")


def test_determine_review_topic_cross_project(test_config):
    """测试跨项目Topic判定（L3）"""
    params = {
        "target_type": "topic",
        "is_cross_project": True,
        "project_phase": "cruising"
    }
    
    result = determine_review(params)
    assert result["status"] == "OK"
    assert result["level"] == "L3"
    assert result["rationale"][0]["rule"] == "cross_project"
    print("✅ test_determine_review_topic_cross_project passed")


def test_determine_review_topic_phase(test_config):
    """测试Topic按阶段判定"""
    # 建立期
    params = {
        "target_type": "topic",
        "project_phase": "establishing"
    }
    result = determine_review(params)
    assert result["level"] == "L3"
    
    # 过渡期
    params["project_phase"] = "transition"
    result = determine_review(params)
    assert result["level"] == "L2"
    
    # 巡航期
    params["project_phase"] = "cruising"
    result = determine_review(params)
    assert result["level"] == "L1"
    
    # 维护期
    params["project_phase"] = "maintaining"
    result = determine_review(params)
    assert result["level"] == "L0"
    
    print("✅ test_determine_review_topic_phase passed")


def test_determine_review_task_p0(test_config):
    """测试P0紧急任务判定（L2）"""
    params = {
        "target_type": "task",
        "priority": "P0",
        "project_phase": "cruising"
    }
    
    result = determine_review(params)
    assert result["status"] == "OK"
    assert result["level"] == "L2"
    assert result["rationale"][0]["rule"] == "p0_emergency"
    print("✅ test_determine_review_task_p0 passed")


def test_determine_review_task_phase(test_config):
    """测试Task按阶段判定"""
    # 建立期
    params = {
        "target_type": "task",
        "priority": "P1",
        "project_phase": "establishing"
    }
    result = determine_review(params)
    assert result["level"] == "L2"
    
    # 过渡期 P1
    params["project_phase"] = "transition"
    result = determine_review(params)
    assert result["level"] == "L2"
    
    # 过渡期 P2
    params["priority"] = "P2"
    result = determine_review(params)
    assert result["level"] == "L1"
    
    # 巡航期 P1
    params["priority"] = "P1"
    params["project_phase"] = "cruising"
    result = determine_review(params)
    assert result["level"] == "L1"
    
    # 巡航期 P2
    params["priority"] = "P2"
    result = determine_review(params)
    assert result["level"] == "L0"
    
    # 维护期
    params["project_phase"] = "maintaining"
    result = determine_review(params)
    assert result["level"] == "L0"
    
    print("✅ test_determine_review_task_phase passed")


def test_check_authorization_create_project(test_config):
    """测试创建项目权限"""
    # Harold有权限
    params = {
        "actor": "ou_84ed4f992e4e9ae6a7043b535f24968b",
        "operation": "create_project"
    }
    result = check_authorization(params)
    assert result["authorized"] == True
    
    # 银月无权限
    params["actor"] = "银月"
    result = check_authorization(params)
    assert result["authorized"] == False
    
    print("✅ test_check_authorization_create_project passed")


def test_check_authorization_create_topic(test_config):
    """测试创建主题权限"""
    # 银月有权限
    params = {
        "actor": "银月",
        "operation": "create_topic"
    }
    result = check_authorization(params)
    assert result["authorized"] == True
    
    # 普通Agent无权限
    params["actor"] = "cqo"
    result = check_authorization(params)
    assert result["authorized"] == False
    
    print("✅ test_check_authorization_create_topic passed")


def test_check_route_permission(test_config):
    """测试路由权限检查"""
    # 银月创建Topic有权限
    params = {
        "actor": "银月",
        "operation": "create_topic"
    }
    result = check_route_permission(params)
    assert result["authorized"] == True
    
    # CQO创建项目无权限
    params["actor"] = "cqo"
    params["operation"] = "create_project"
    result = check_route_permission(params)
    assert result["authorized"] == False
    
    print("✅ test_check_route_permission passed")


def test_determine_automation_level_upgrade(test_config):
    """测试自动化级别升级判定"""
    params = {
        "agent_id": "cqo",
        "dl_hit_rate": 0.9,
        "consecutive_success": 4,
        "ll_rejection_exists": False,
        "project_phase": "cruising"
    }
    
    result = determine_automation_level(params)
    assert result["status"] == "OK"
    assert result["current_level"] == "L3"
    assert result["calculated_level"] == "L4"
    assert result["adjustment"] == "can_upgrade"
    assert result["upgrade_score"] == 100  # 40+30+20+10
    assert result["downgrade_score"] == 0
    
    print("✅ test_determine_automation_level_upgrade passed")


def test_determine_automation_level_downgrade(test_config):
    """测试自动化级别降级判定"""
    params = {
        "agent_id": "cto",
        "consecutive_failure": 2,
        "ll_rejection_exists": True
    }
    
    result = determine_automation_level(params)
    assert result["status"] == "OK"
    assert result["current_level"] == "L2"
    assert result["calculated_level"] == "L1"
    assert result["adjustment"] == "needs_downgrade"
    assert result["downgrade_score"] == 80  # 50+30
    
    print("✅ test_determine_automation_level_downgrade passed")


def test_adjust_automation_level_success(test_config):
    """测试调整自动化级别成功"""
    params = {
        "agent_id": "cqo",
        "new_level": "L4",
        "reason": "连续成功，符合升级条件"
    }
    
    result = adjust_automation_level(params)
    assert result["status"] == "OK"
    assert result["previous_level"] == "L3"
    assert result["new_level"] == "L4"
    
    config_path = os.path.join(test_config["temp_config_dir"], "automation-levels.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    assert config["cqo"]["current_level"] == "L4"
    assert len(config["cqo"]["adjustment_history"]) == 1
    assert config["cqo"]["adjustment_history"][0]["to"] == "L4"
    
    print("✅ test_adjust_automation_level_success passed")


def test_adjust_automation_level_invalid_level(test_config):
    """测试调整无效级别"""
    params = {
        "agent_id": "cqo",
        "new_level": "L6",  # 超过上限
        "reason": "测试"
    }
    
    try:
        adjust_automation_level(params)
        assert False, "应该抛出InvalidLevelError"
    except InvalidLevelError:
        print("✅ test_adjust_automation_level_invalid_level passed")


def test_adjust_automation_level_cross_step(test_config):
    """测试跨级调整"""
    # 先升级到L4
    upgrade_params = {
        "agent_id": "cqo",
        "new_level": "L4",
        "reason": "先升级到L4以测试跨级调整"
    }
    adjust_automation_level(upgrade_params)
    
    # 然后测试跨级调整（从L4到L2，降级2级）
    params = {
        "agent_id": "cqo",
        "new_level": "L2",
        "reason": "测试跨级调整"
    }
    
    try:
        adjust_automation_level(params)
        assert False, "应该抛出AdjustmentInvalidError"
    except AdjustmentInvalidError:
        print("✅ test_adjust_automation_level_cross_step passed")


def test_adjust_automation_level_agent_not_found(test_config):
    """测试调整不存在的Agent"""
    params = {
        "agent_id": "nonexistent",
        "new_level": "L3",
        "reason": "测试"
    }
    
    try:
        adjust_automation_level(params)
        assert False, "应该抛出AgentNotFoundError"
    except AgentNotFoundError:
        print("✅ test_adjust_automation_level_agent_not_found passed")
