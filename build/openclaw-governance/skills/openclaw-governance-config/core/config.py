#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
governance-config 核心实现

加载与管理系统配置，支持系统级/用户级分层。
基于 ARCH v1.4.3 §4.1 Skills 增强计划。

Author: 张铁 (CQO)
Date: 2026-04-11
"""

import os
import yaml
from typing import Dict, Any, Optional

# 全局配置缓存
_config_cache: Dict[str, Any] = {}


class ConfigError(Exception):
    """配置操作异常基类"""
    pass


class ConfigNotFoundError(ConfigError):
    """配置文件不存在"""
    pass


class ConfigWriteError(ConfigError):
    """配置写入错误"""
    pass


def _get_config_dir() -> str:
    """
    获取配置根目录
    
    Returns:
        配置目录路径
    """
    # 优先从环境变量获取
    env_config_dir = os.environ.get("GOVERNANCE_CONFIG_DIR")
    if env_config_dir:
        return env_config_dir
    
    # 默认路径：工作目录下的 .system/governance/current/config/
    workspace_dir = os.environ.get("OPENCLAW_LOCAL_WORKSPACE", os.getcwd())
    return os.path.join(workspace_dir, ".system", "governance", "current", "config")


def _load_yaml(file_path: str) -> Dict[str, Any]:
    """
    加载YAML文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        YAML解析结果，文件不存在返回空字典
    """
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"YAML parsing error in {file_path}: {e}")


def _save_yaml(file_path: str, data: Dict[str, Any]) -> None:
    """
    原子性保存YAML文件
    
    Args:
        file_path: 文件路径
        data: 要保存的数据
    
    Raises:
        ConfigWriteError: 写入失败
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    tmp_path = file_path + '.tmp'
    
    try:
        # 写入临时文件
        with open(tmp_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, indent=2)
        
        # 原子性重命名
        os.rename(tmp_path, file_path)
        
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def load_config(filename: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        filename: 配置文件名（相对于配置根目录）
        default: 文件不存在时的默认返回值
    
    Returns:
        配置字典
    """
    config_dir = _get_config_dir()
    file_path = os.path.join(config_dir, filename)
    
    if not os.path.exists(file_path) and default is not None:
        return default
    
    return _load_yaml(file_path)


def update_config(filename: str, data: Dict[str, Any]) -> None:
    """
    更新配置文件
    
    Args:
        filename: 配置文件名（相对于配置根目录）
        data: 要更新的数据（全量覆盖）
    """
    config_dir = _get_config_dir()
    file_path = os.path.join(config_dir, filename)
    
    _save_yaml(file_path, data)
    
    # 清除缓存
    cache_key = f"file:{filename}"
    if cache_key in _config_cache:
        del _config_cache[cache_key]


def load_system(subset: Optional[str] = None) -> Dict[str, Any]:
    """
    加载系统级配置
    
    Args:
        subset: 配置子集（agents/skills/projects/tasks/topics），None表示加载全部
    
    Returns:
        系统配置字典
    """
    config_dir = _get_config_dir()
    system_config = {}
    
    if subset == "agents":
        system_config.update(_load_yaml(os.path.join(config_dir, "system", "agents.yaml")))
    elif subset == "skills":
        system_config.update(_load_yaml(os.path.join(config_dir, "system", "skills.yaml")))
    elif subset == "projects":
        system_config.update(_load_yaml(os.path.join(config_dir, "system", "system-projects.yaml")))
    elif subset == "tasks":
        system_config.update(_load_yaml(os.path.join(config_dir, "system", "system-tasks.yaml")))
    elif subset == "topics":
        system_config.update(_load_yaml(os.path.join(config_dir, "system", "system-topics.yaml")))
    else:
        # 加载全部系统配置
        system_config["agents"] = _load_yaml(os.path.join(config_dir, "system", "agents.yaml"))
        system_config["skills"] = _load_yaml(os.path.join(config_dir, "system", "skills.yaml"))
        system_config["projects"] = _load_yaml(os.path.join(config_dir, "system", "system-projects.yaml"))
        system_config["tasks"] = _load_yaml(os.path.join(config_dir, "system", "system-tasks.yaml"))
        system_config["topics"] = _load_yaml(os.path.join(config_dir, "system", "system-topics.yaml"))
    
    return system_config


def load_user(subset: Optional[str] = None) -> Dict[str, Any]:
    """
    加载用户级配置
    
    Args:
        subset: 配置子集（projects/tasks/topics/persons），None表示加载全部
    
    Returns:
        用户配置字典
    """
    config_dir = _get_config_dir()
    user_config = {}
    
    if subset == "projects":
        user_config.update(_load_yaml(os.path.join(config_dir, "user", "user-projects.yaml")))
    elif subset == "tasks":
        user_config.update(_load_yaml(os.path.join(config_dir, "user", "user-tasks.yaml")))
    elif subset == "topics":
        user_config.update(_load_yaml(os.path.join(config_dir, "user", "user-topics.yaml")))
    elif subset == "persons":
        user_config.update(_load_yaml(os.path.join(config_dir, "user", "persons.yaml")))
    else:
        # 加载全部用户配置
        user_config["projects"] = _load_yaml(os.path.join(config_dir, "user", "user-projects.yaml"))
        user_config["tasks"] = _load_yaml(os.path.join(config_dir, "user", "user-tasks.yaml"))
        user_config["topics"] = _load_yaml(os.path.join(config_dir, "user", "user-topics.yaml"))
        user_config["persons"] = _load_yaml(os.path.join(config_dir, "user", "persons.yaml"))

    return user_config


def load_core() -> Dict[str, Any]:
    """
    加载核心配置（会话启动时调用）
    
    Returns:
        核心配置字典
    """
    config_dir = _get_config_dir()
    core_config = {}
    
    core_config["globals"] = _load_yaml(os.path.join(config_dir, "globals.yaml"))
    core_config["duty_mapping"] = _load_yaml(os.path.join(config_dir, "duty-mapping.yaml"))
    
    return core_config


def get_config(key: str) -> Any:
    """
    获取配置项（从已加载的配置中）
    
    Args:
        key: 配置项路径，格式："globals.environment.workspace"
    
    Returns:
        配置项值，不存在返回None
    """
    parts = key.split('.')
    if not parts:
        return None
    
    # 先加载对应配置
    if parts[0] == "globals" or parts[0] == "duty_mapping":
        config = load_core()
    elif parts[0] in ["agents", "skills", "projects", "tasks", "topics"]:
        config = load_system(parts[0])
    else:
        config = load_user(parts[0])

    # Traverse nested keys
    value = config
    for part in parts[1:]:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return None
    return value
