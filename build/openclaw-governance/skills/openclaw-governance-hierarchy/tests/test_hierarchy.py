#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
governance-hierarchy 单元测试
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 把当前目录加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.hierarchy import create_project, create_topic, NameDuplicateError, ProjectNotFoundError, OwnerInvalidError

# 模拟配置目录
os.environ["GOVERNANCE_CONFIG_DIR"] = tempfile.mkdtemp()
os.environ["WORKSPACE_DIR"] = tempfile.mkdtemp()

# 创建测试配置
config_dir = os.environ["GOVERNANCE_CONFIG_DIR"]
workspace_dir = os.environ["WORKSPACE_DIR"]
os.makedirs(os.path.join(workspace_dir, "10_Projects"), exist_ok=True)
os.makedirs(os.path.join(config_dir, "system"), exist_ok=True)
os.makedirs(os.path.join(config_dir, "user"), exist_ok=True)

# 创建测试agents.yaml
agents = {
    "cqo": {"name": "张铁", "role": "首席质量官"},
    "ceo": {"name": "柳玉", "role": "首席执行官"},
    "cto": {"name": "菡云芝", "role": "首席技术官"}
}
with open(os.path.join(config_dir, "system", "agents.yaml"), 'w', encoding='utf-8') as f:
    import yaml
    yaml.dump(agents, f, allow_unicode=True, default_flow_style=False)

# 创建空配置文件
with open(os.path.join(config_dir, "system", "system-projects.yaml"), 'w', encoding='utf-8') as f:
    yaml.dump({}, f, default_flow_style=False)
with open(os.path.join(config_dir, "user", "user-projects.yaml"), 'w', encoding='utf-8') as f:
    yaml.dump({}, f, default_flow_style=False)

# 切换工作目录到workspace
os.chdir(workspace_dir)


def test_create_project_success():
    """测试创建项目成功"""
    params = {
        "name": "测试项目",
        "description": "这是一个测试项目",
        "owner": "cqo",
        "members": ["ceo", "cto"],
        "tags": ["测试", "MVP"],
        "privacy_level": "P2"
    }
    
    result = create_project(params)
    
    assert result["status"] == "OK"
    assert result["project_id"] == "ZT-P1"
    assert "10_Projects/ZT-P1_测试项目/" in result["dir_path"]
    assert result["review_level"] == "L3"
    assert "cycle_unit_id" in result
    assert "cycle_unit" in result
    assert result["cycle_unit"]["scope"] == "project"
    assert result["cycle_unit"]["task_card_id"] == "ZT-P1"
    assert result["cycle_unit"]["phase"] == "plan"
    
    # 验证目录和文件是否存在
    assert os.path.exists(result["dir_path"])
    assert os.path.exists(result["charter_path"])
    
    # 验证配置是否保存
    with open(os.path.join(config_dir, "user", "user-projects.yaml"), 'r', encoding='utf-8') as f:
        projects = yaml.safe_load(f)
        assert "ZT-P1" in projects
        assert projects["ZT-P1"]["name"] == "测试项目"
        assert projects["ZT-P1"]["owner"] == "cqo"
    
    print("✅ test_create_project_success passed")


def test_create_project_duplicate_name():
    """测试创建项目名称重复"""
    params = {
        "name": "测试项目",
        "owner": "cqo"
    }
    
    try:
        create_project(params)
        assert False, "应该抛出NameDuplicateError"
    except NameDuplicateError:
        print("✅ test_create_project_duplicate_name passed")


def test_create_project_invalid_owner():
    """测试创建项目负责人无效"""
    params = {
        "name": "测试项目2",
        "owner": "invalid_agent"
    }
    
    try:
        create_project(params)
        assert False, "应该抛出OwnerInvalidError"
    except OwnerInvalidError:
        print("✅ test_create_project_invalid_owner passed")


def test_create_topic_success():
    """测试创建主题成功"""
    # 先创建一个项目
    project_params = {
        "name": "父项目",
        "owner": "cqo"
    }
    project_result = create_project(project_params)
    project_id = project_result["project_id"]
    
    # 创建主题
    topic_params = {
        "project_id": project_id,
        "name": "测试主题",
        "description": "这是一个测试主题",
        "topic_pm": "cto"
    }
    
    result = create_topic(topic_params)
    
    assert result["status"] == "OK"
    assert result["topic_id"] == "T01-测试主题"
    assert project_result["dir_path"] in result["dir_path"]
    assert result["review_level"] == "L2"
    assert "cycle_unit_id" in result
    assert "cycle_unit" in result
    assert result["cycle_unit"]["scope"] == "topic"
    assert result["cycle_unit"]["task_card_id"] == "T01-测试主题"
    assert result["cycle_unit"]["phase"] == "plan"
    
    # 验证目录和文件是否存在
    assert os.path.exists(result["dir_path"])
    assert os.path.exists(result["brief_path"])
    
    # 验证项目topics_count是否更新
    with open(os.path.join(config_dir, "user", "user-projects.yaml"), 'r', encoding='utf-8') as f:
        projects = yaml.safe_load(f)
        assert projects[project_id]["topics_count"] == 1
    
    print("✅ test_create_topic_success passed")


def test_create_topic_invalid_project():
    """测试创建主题项目不存在"""
    params = {
        "project_id": "ZT-P999",
        "name": "测试主题",
        "topic_pm": "cto"
    }
    
    try:
        create_topic(params)
        assert False, "应该抛出ProjectNotFoundError"
    except ProjectNotFoundError:
        print("✅ test_create_topic_invalid_project passed")


def test_create_topic_invalid_pm():
    """测试创建主题PM无效"""
    # 先创建一个项目
    project_params = {
        "name": "父项目2",
        "owner": "cqo"
    }
    project_result = create_project(project_params)
    
    params = {
        "project_id": project_result["project_id"],
        "name": "测试主题2",
        "topic_pm": "invalid_agent"
    }
    
    try:
        create_topic(params)
        assert False, "应该抛出OwnerInvalidError"
    except OwnerInvalidError:
        print("✅ test_create_topic_invalid_pm passed")


if __name__ == "__main__":
    print("=" * 60)
    print("governance-hierarchy 单元测试")
    print("=" * 60)
    
    try:
        test_create_project_success()
        test_create_project_duplicate_name()
        test_create_project_invalid_owner()
        test_create_topic_success()
        test_create_topic_invalid_project()
        test_create_topic_invalid_pm()
        
        print("\n🎉 所有测试通过!")
        
    finally:
        # 清理临时目录
        shutil.rmtree(config_dir)
        shutil.rmtree(workspace_dir)
