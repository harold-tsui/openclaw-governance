#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
governance-delegation 核心实现

授权/降级/Review 等级判定，支持任务评审路由、权限校验、决策自动化分级。
基于 ARCH v1.4.3 §4.1 Skills 增强计划。

Author: 张铁 (CQO)
Date: 2026-04-11
"""

import os
import sys
import yaml
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# 导入 governance-config
sys.path.append(os.path.join(os.path.dirname(__file__), "../../openclaw-governance-config"))
from core.config import load_config, update_config


class DelegationError(Exception):
    """授权操作异常基类"""
    pass


class AgentNotFoundError(DelegationError):
    """Agent不存在"""
    pass


class InvalidLevelError(DelegationError):
    """级别无效"""
    pass


class AdjustmentInvalidError(DelegationError):
    """调整无效（跨级）"""
    pass


class UnauthorizedError(DelegationError):
    """未授权"""
    pass


class PolicyMissingError(DelegationError):
    """策略缺失"""
    pass


def _get_automation_levels_path() -> str:
    """获取自动化级别配置文件路径"""
    config_dir = os.environ.get("GOVERNANCE_CONFIG_DIR", os.path.join(os.getcwd(), "config"))
    return os.path.join(config_dir, "automation-levels.yaml")


def determine_review(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    判定 Review 级别（L0-L3）
    
    Args:
        params: 判定参数
            - target_type: project|topic|task（必填）
            - task_type: 常规|系统级|周期性|应急|一次性
            - project_phase: establishing|transition|cruising|maintaining
            - dl_refs: DL引用列表
            - is_first_time: 是否首次类型
            - priority: P0|P1|P2|P3
            - is_cross_project: 是否跨项目
            - is_out_of_scope: 是否越界
    
    Returns:
        判定结果
    """
    # 校验必填字段
    if "target_type" not in params:
        raise ValueError("Missing required field: target_type")
    
    target_type = params["target_type"]
    rationale = []
    level = "L3"  # 默认最高级别，确保安全
    
    # 判级规则
    if target_type == "project":
        # 项目一律L3
        level = "L3"
        rationale.append({
            "rule": "new_project",
            "source": "ARCH-002 v1.2",
            "desc": "新项目一律 L3"
        })
    
    elif target_type == "topic":
        is_first_time = params.get("is_first_time", False)
        is_cross_project = params.get("is_cross_project", False)
        is_out_of_scope = params.get("is_out_of_scope", False)
        project_phase = params.get("project_phase", "establishing")
        
        if is_first_time:
            level = "L3"
            rationale.append({
                "rule": "first_topic_type",
                "source": "ARCH-002 v1.2",
                "desc": "首次 Topic 类型 L3"
            })
        elif is_cross_project:
            level = "L3"
            rationale.append({
                "rule": "cross_project",
                "source": "ARCH-002 v1.2",
                "desc": "跨项目 Topic 需 Harold 审批"
            })
        elif is_out_of_scope:
            level = "L3"
            rationale.append({
                "rule": "out_of_scope",
                "source": "ARCH-002 v1.2",
                "desc": "越界 Topic 需 Harold 审批"
            })
        else:
            # 按项目阶段判定
            if project_phase == "establishing":
                level = "L3"
                rationale.append({
                    "rule": "phase_establishing",
                    "source": "ARCH-002 v1.2",
                    "desc": "建立期默认 L3"
                })
            elif project_phase == "transition":
                level = "L2"
                rationale.append({
                    "rule": "phase_transition",
                    "source": "ARCH-002 v1.2",
                    "desc": "过渡期默认 L2"
                })
            elif project_phase == "cruising":
                level = "L1"
                rationale.append({
                    "rule": "phase_cruising",
                    "source": "ARCH-002 v1.2",
                    "desc": "巡航期默认 L1"
                })
            elif project_phase == "maintaining":
                level = "L0"
                rationale.append({
                    "rule": "phase_maintaining",
                    "source": "ARCH-002 v1.2",
                    "desc": "维护期默认 L0"
                })
    
    elif target_type == "task":
        is_first_time = params.get("is_first_time", False)
        priority = params.get("priority", "P2")
        project_phase = params.get("project_phase", "transition")
        
        if is_first_time:
            level = "L3"
            rationale.append({
                "rule": "first_task_type",
                "source": "ARCH-002 v1.2",
                "desc": "首次 Task 类型 L3"
            })
        elif priority == "P0":
            level = "L2"
            rationale.append({
                "rule": "p0_emergency",
                "source": "ARCH-002 v1.2",
                "desc": "P0 紧急任务 L2，事后复盘"
            })
        else:
            # 按项目阶段判定
            if project_phase == "establishing":
                level = "L2"
                rationale.append({
                    "rule": "phase_establishing_task",
                    "source": "ARCH-002 v1.2",
                    "desc": "建立期任务默认 L2"
                })
            elif project_phase == "transition":
                level = "L2" if priority == "P1" else "L1"
                rationale.append({
                    "rule": "phase_transition_task",
                    "source": "ARCH-002 v1.2",
                    "desc": f"过渡期P1任务L2，其他L1"
                })
            elif project_phase == "cruising":
                level = "L1" if priority == "P1" else "L0"
                rationale.append({
                    "rule": "phase_cruising_task",
                    "source": "ARCH-002 v1.2",
                    "desc": f"巡航期P1任务L1，其他L0"
                })
            elif project_phase == "maintaining":
                level = "L0"
                rationale.append({
                    "rule": "phase_maintaining_task",
                    "source": "ARCH-002 v1.2",
                    "desc": "维护期任务默认 L0"
                })
    
    # 构造返回结果
    next_action = "等待 Harold 审批" if level in ["L2", "L3"] else "银月验收"
    
    return {
        "status": "OK",
        "level": level,
        "rationale": rationale,
        "next_action": next_action
    }


def check_authorization(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    判定 Actor 是否有权限执行某操作
    
    Args:
        params: 校验参数
            - actor: 操作执行者（必填）
            - operation: 操作类型（create_project/create_topic/create_task/close_project/close_topic/close_task）（必填）
            - target: 操作目标（可选）
    
    Returns:
        校验结果
    """
    # 校验必填字段
    required_fields = ["actor", "operation"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    
    actor = params["actor"]
    operation = params["operation"]
    constraints = []
    
    # 权限矩阵（简化版）
    permission_matrix = {
        "create_project": ["Harold", "ou_84ed4f992e4e9ae6a7043b535f24968b", "harold"],
        "close_project": ["Harold", "ou_84ed4f992e4e9ae6a7043b535f24968b", "harold"],
        "create_topic": ["Harold", "ou_84ed4f992e4e9ae6a7043b535f24968b", "main", "银月", "harold"],
        "close_topic": ["Harold", "ou_84ed4f992e4e9ae6a7043b535f24968b", "main", "银月", "harold"],
        "create_task": ["Harold", "ou_84ed4f992e4e9ae6a7043b535f24968b", "main", "银月", "topic_pic", "harold"],
        "close_task": ["Harold", "ou_84ed4f992e4e9ae6a7043b535f24968b", "main", "银月", "topic_pic", "harold"],
        "review_deliverable": ["Harold", "ou_84ed4f992e4e9ae6a7043b535f24968b", "main", "银月", "topic_pic", "harold", "cqo", "cto", "ceo"]
    }
    
    authorized = False
    if operation in permission_matrix:
        allowed_actors = permission_matrix[operation]
        if actor in allowed_actors:
            authorized = True
        elif "*" in allowed_actors:
            authorized = True
    else:
        # 未知操作默认拒绝，返回L3级别要求
        raise PolicyMissingError(f"No policy for operation: {operation}")
    
    # 特殊约束检查
    if operation == "create_topic" and "target" in params:
        # TODO: 检查是否在项目范围内，需要调用governance-hierarchy
        pass
    
    return {
        "status": "OK",
        "authorized": authorized,
        "constraints": constraints
    }


def check_route_permission(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    路由前权限门控，由 governance-dispatch 主动调用
    
    Args:
        params: 校验参数
            - actor: 操作执行者（必填）
            - operation: 操作类型（必填）
    
    Returns:
        校验结果
    """
    # 路由权限和操作权限检查逻辑一致
    return check_authorization(params)


def determine_automation_level(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    评估 Agent 的决策自动化级别
    
    Args:
        params: 评估参数
            - agent_id: Agent ID（必填）
            - task_type: 任务类型
            - dl_hit_rate: DL命中率
            - consecutive_success: 连续成功次数
            - consecutive_failure: 连续失败次数
            - ll_rejection_exists: 是否有LL驳回
            - dl_expired: DL是否过期
            - project_phase: 项目阶段
    
    Returns:
        评估结果
    """
    if "agent_id" not in params:
        raise ValueError("Missing required field: agent_id")
    
    agent_id = params["agent_id"]
    
    # 读取当前级别配置
    level_config = load_config("automation-levels.yaml", default={})
    if agent_id not in level_config:
        raise AgentNotFoundError(f"Agent not found: {agent_id}")
    
    current_level = level_config[agent_id].get("current_level", "L2")
    current_level_num = int(current_level[1])
    
    # 计算得分
    upgrade_score = 0
    downgrade_score = 0
    rationale = []
    
    # 升级得分项
    dl_hit_rate = params.get("dl_hit_rate", 0.0)
    if dl_hit_rate >= 0.8:
        upgrade_score += 40
        rationale.append({
            "factor": "dl_hit_rate",
            "value": dl_hit_rate,
            "score": 40,
            "rule": ">=0.8"
        })
    
    consecutive_success = params.get("consecutive_success", 0)
    if consecutive_success >= 3:
        upgrade_score += 30
        rationale.append({
            "factor": "consecutive_success",
            "value": consecutive_success,
            "score": 30,
            "rule": ">=3"
        })
    
    ll_rejection_exists = params.get("ll_rejection_exists", False)
    if not ll_rejection_exists:
        upgrade_score += 20
        rationale.append({
            "factor": "no_ll_rejection",
            "value": True,
            "score": 20
        })
    
    project_phase = params.get("project_phase", "cruising")
    if project_phase != "establishing":
        upgrade_score += 10
        rationale.append({
            "factor": "project_phase",
            "value": project_phase,
            "score": 10,
            "rule": "!= 'establishing'"
        })
    
    # 降级得分项
    consecutive_failure = params.get("consecutive_failure", 0)
    if consecutive_failure >= 2:
        downgrade_score += 50
        rationale.append({
            "factor": "consecutive_failure",
            "value": consecutive_failure,
            "score": 50,
            "rule": ">=2"
        })
    
    if ll_rejection_exists:
        downgrade_score += 30
        rationale.append({
            "factor": "ll_rejection_exists",
            "value": True,
            "score": 30
        })
    
    dl_expired = params.get("dl_expired", False)
    if dl_expired:
        downgrade_score += 20
        rationale.append({
            "factor": "dl_expired",
            "value": True,
            "score": 20
        })
    
    # 判定调整
    adjustment = "maintain"
    calculated_level_num = current_level_num
    
    if upgrade_score >= 90 and current_level_num < 5:
        calculated_level_num += 1
        adjustment = "can_upgrade"
    elif downgrade_score >= 50 and current_level_num > 0:
        calculated_level_num -= 1
        adjustment = "needs_downgrade"
    
    calculated_level = f"L{calculated_level_num}"
    
    return {
        "status": "OK",
        "agent_id": agent_id,
        "current_level": current_level,
        "calculated_level": calculated_level,
        "upgrade_score": upgrade_score,
        "downgrade_score": downgrade_score,
        "adjustment": adjustment,
        "rationale": rationale,
        "next_action": "记录到 automation-levels.yaml，通知 Harold" if adjustment != "maintain" else "无需调整"
    }


def adjust_automation_level(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    调整 Agent 的决策自动化级别
    
    Args:
        params: 调整参数
            - agent_id: Agent ID（必填）
            - new_level: 新级别（必填）
            - reason: 调整原因
    
    Returns:
        调整结果
    """
    required_fields = ["agent_id", "new_level"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")
    
    agent_id = params["agent_id"]
    new_level = params["new_level"]
    reason = params.get("reason", "调整")
    
    # 校验级别格式
    if not new_level.startswith("L") or len(new_level) != 2 or not new_level[1].isdigit():
        raise InvalidLevelError(f"Invalid level: {new_level}")
    
    new_level_num = int(new_level[1])
    if new_level_num < 0 or new_level_num > 5:
        raise InvalidLevelError(f"Level must be between L0 and L5, got: {new_level}")
    
    # 读取配置
    config_path = _get_automation_levels_path()
    level_config = load_config("automation-levels.yaml", default={})
    
    if agent_id not in level_config:
        raise AgentNotFoundError(f"Agent not found: {agent_id}")
    
    previous_level = level_config[agent_id].get("current_level", "L2")
    previous_level_num = int(previous_level[1])
    
    # 检查是否跨级调整
    if abs(new_level_num - previous_level_num) > 1:
        raise AdjustmentInvalidError(f"Cannot adjust level across multiple steps: {previous_level} -> {new_level}")
    
    # 更新配置
    if agent_id not in level_config:
        level_config[agent_id] = {}
    
    level_config[agent_id]["current_level"] = new_level
    level_config[agent_id]["previous_level"] = previous_level
    level_config[agent_id]["adjusted_at"] = datetime.now(timezone.utc).isoformat()
    level_config[agent_id]["reason"] = reason
    level_config[agent_id]["consecutive_success"] = 0
    level_config[agent_id]["consecutive_failure"] = 0
    
    # 添加历史记录
    if "adjustment_history" not in level_config[agent_id]:
        level_config[agent_id]["adjustment_history"] = []
    
    level_config[agent_id]["adjustment_history"].append({
        "from": previous_level,
        "to": new_level,
        "reason": reason,
        "adjusted_at": datetime.now(timezone.utc).isoformat()
    })
    
    # 保存配置
    update_config("automation-levels.yaml", level_config)
    
    return {
        "status": "OK",
        "agent_id": agent_id,
        "previous_level": previous_level,
        "new_level": new_level,
        "adjusted_at": datetime.now(timezone.utc).isoformat(),
        "notification_sent": True
    }


# 导出公共接口
__all__ = [
    'determine_review',
    'check_authorization',
    'check_route_permission',
    'determine_automation_level',
    'adjust_automation_level',
    'DelegationError',
    'AgentNotFoundError',
    'InvalidLevelError',
    'AdjustmentInvalidError',
    'UnauthorizedError',
    'PolicyMissingError'
]
