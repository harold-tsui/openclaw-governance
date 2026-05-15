#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
governance-task 单元测试（重构版）
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

from core.task import (
    get_project_config,
    create_task,
    accept_task,
    reject_task,
    create_issue_ticket,
    review_deliverable,
    verify_task_closed,
    close_task,
    archive_task,
    ProjectNotFoundError,
    NotAuthorizedError,
    StateInvalidError,
    CloseDeniedError,
    ReviewIncompleteError,
    KnowledgeCaptureIncompleteError
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

    test_project_id = "ZT-P001"
    test_project_dir = os.path.join(temp_workspace_dir, "10_Projects", f"{test_project_id}_Test_Project")
    os.makedirs(test_project_dir, exist_ok=True)
    os.makedirs(os.path.join(test_project_dir, "T01", "tasks"), exist_ok=True)
    os.makedirs(os.path.join(test_project_dir, "T01", "deliverables"), exist_ok=True)

    user_projects = {
        test_project_id: {
            "id": test_project_id,
            "name": "Test Project",
            "owner": "harold",
            "members": ["cqo", "cto", "ceo"],
            "dir_path": test_project_dir,
            "charter_path": os.path.join(test_project_dir, "PROJECT-CHARTER.md"),
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "topics": ["T01"]
        }
    }

    with open(os.path.join(temp_config_dir, "user", "user-projects.yaml"), 'w', encoding='utf-8') as f:
        yaml.dump(user_projects, f, allow_unicode=True, default_flow_style=False)

    with open(os.path.join(temp_config_dir, "system", "system-projects.yaml"), 'w', encoding='utf-8') as f:
        yaml.dump({}, f, allow_unicode=True, default_flow_style=False)

    agents = {
        "harold": {"name": "Harold", "role": "Owner"},
        "cqo": {"name": "张铁", "role": "CQO"},
        "cto": {"name": "菡云芝", "role": "CTO"},
        "ceo": {"name": "柳玉", "role": "CEO"}
    }
    with open(os.path.join(temp_config_dir, "system", "agents.yaml"), 'w', encoding='utf-8') as f:
        yaml.dump(agents, f, allow_unicode=True, default_flow_style=False)

    automation_levels = {
        "harold": {"current_level": "L3"},
        "cqo": {"current_level": "L3"},
        "cto": {"current_level": "L2"},
        "main": {"current_level": "L2"}
    }
    with open(os.path.join(temp_config_dir, "automation-levels.yaml"), 'w', encoding='utf-8') as f:
        yaml.dump(automation_levels, f, allow_unicode=True, default_flow_style=False)

    yield {
        "test_project_id": test_project_id,
        "test_project_dir": test_project_dir,
        "test_topic_id": "T01",
        "temp_config_dir": temp_config_dir,
        "temp_workspace_dir": temp_workspace_dir
    }

    if os.path.exists(temp_config_dir):
        shutil.rmtree(temp_config_dir)
    if os.path.exists(temp_workspace_dir):
        shutil.rmtree(temp_workspace_dir)


def test_get_project_config(test_config):
    project = get_project_config(test_config["test_project_id"])
    assert project["id"] == test_config["test_project_id"]
    assert project["name"] == "Test Project"
    assert project["dir_path"] == test_config["test_project_dir"]
    print("✅ test_get_project_config passed")


def test_create_task(test_config):
    params = {
        "task_title": "测试任务",
        "task_type": "常规",
        "project_id": test_config["test_project_id"],
        "topic_id": test_config["test_topic_id"],
        "assignee": "harold",
        "task_pic": "cqo",
        "priority": "P2",
        "review_level": "L2",
        "task_goal": "完成测试任务",
        "deliverables": [{
            "name": "测试报告",
            "filename": "TEST-REPORT.md",
            "format": ".md",
            "review_level": "L2",
            "acceptance_criteria": "测试通过"
        }]
    }
    result = create_task(params)
    assert result["status"] == "OK"
    assert result["state"] == "[ ]"
    assert f"{test_config['test_project_id']}-{test_config['test_topic_id']}-T01" in result["task_id"]
    assert os.path.exists(result["task_card_path"])

    with open(result["task_card_path"], 'r', encoding='utf-8') as f:
        content = f.read()
    assert "测试任务" in content
    assert "cqo" in content
    assert "harold" in content
    assert "TEST-REPORT.md" in content
    print("✅ test_create_task passed")


def test_accept_task(test_config):
    create_result = create_task({
        "task_title": "测试任务",
        "task_type": "常规",
        "project_id": test_config["test_project_id"],
        "topic_id": test_config["test_topic_id"],
        "assignee": "harold",
        "task_pic": "cqo",
        "priority": "P2",
        "review_level": "L2",
        "task_goal": "完成测试任务",
        "deliverables": [{
            "name": "测试报告",
            "filename": "TEST-REPORT.md",
            "format": ".md",
            "review_level": "L2",
            "acceptance_criteria": "测试通过"
        }]
    })
    task_id = create_result["task_id"]

    accept_result = accept_task({
        "task_id": task_id,
        "task_pic": "cqo"
    })
    assert accept_result["status"] == "OK"
    assert accept_result["state"] == "[P]"

    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "§七.1 当前状态: [P]" in content
    print("✅ test_accept_task passed")


def test_accept_task_not_authorized(test_config):
    create_result = create_task({
        "task_title": "测试任务",
        "task_type": "常规",
        "project_id": test_config["test_project_id"],
        "topic_id": test_config["test_topic_id"],
        "assignee": "harold",
        "task_pic": "cqo",
        "priority": "P2",
        "review_level": "L2",
        "task_goal": "完成测试任务",
        "deliverables": [{
            "name": "测试报告",
            "filename": "TEST-REPORT.md",
            "format": ".md",
            "review_level": "L2",
            "acceptance_criteria": "测试通过"
        }]
    })
    task_id = create_result["task_id"]

    try:
        accept_task({
            "task_id": task_id,
            "task_pic": "cto"
        })
        assert False, "应该抛出NotAuthorizedError"
    except NotAuthorizedError:
        print("✅ test_accept_task_not_authorized passed")


def test_reject_task(test_config):
    create_result = create_task({
        "task_title": "测试任务",
        "task_type": "常规",
        "project_id": test_config["test_project_id"],
        "topic_id": test_config["test_topic_id"],
        "assignee": "harold",
        "task_pic": "cqo",
        "priority": "P2",
        "review_level": "L2",
        "task_goal": "完成测试任务",
        "deliverables": [{
            "name": "测试报告",
            "filename": "TEST-REPORT.md",
            "format": ".md",
            "review_level": "L2",
            "acceptance_criteria": "测试通过"
        }]
    })
    task_id = create_result["task_id"]

    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace("§七.1 当前状态: [P]", "§七.1 当前状态: [ ]")
    with open(task_card_path, 'w', encoding='utf-8') as f:
        f.write(content)

    result = reject_task({
        "task_id": task_id,
        "task_pic": "cqo",
        "reason": "优先级不够，先处理其他任务"
    })
    assert result["status"] == "OK"
    assert result["state"] == "[ ]"

    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "拒绝原因: 优先级不够" in content
    print("✅ test_reject_task passed")


def test_review_deliverable_pass(test_config):
    create_result = create_task({
        "task_title": "测试任务",
        "task_type": "常规",
        "project_id": test_config["test_project_id"],
        "topic_id": test_config["test_topic_id"],
        "assignee": "harold",
        "task_pic": "cqo",
        "priority": "P2",
        "review_level": "L2",
        "task_goal": "完成测试任务",
        "deliverables": [{
            "name": "测试报告",
            "filename": "TEST-REPORT.md",
            "format": ".md",
            "review_level": "L2",
            "acceptance_criteria": "测试通过"
        }]
    })
    task_id = create_result["task_id"]

    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if "§七.1 当前状态: [P]" in content:
        content = content.replace("§七.1 当前状态: [P]", "§七.1 当前状态: [V]")
    elif "§七.1 当前状态: [ ]" in content:
        content = content.replace("§七.1 当前状态: [ ]", "§七.1 当前状态: [V]")
    with open(task_card_path, 'w', encoding='utf-8') as f:
        f.write(content)

    result = review_deliverable({
        "task_id": task_id,
        "deliverable_name": "测试报告",
        "reviewer": "harold",
        "review_result": "pass",
        "feedback": "测试通过，写的很好"
    })
    assert result["status"] == "OK"
    assert result["review_result"] == "pass"

    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "| 测试报告 | TEST-REPORT.md | .md | L2 | 测试通过 | ✅ |" in content
    assert "评审人: harold" in content
    print("✅ test_review_deliverable_pass passed")


def test_verify_task_closed(test_config):
    create_result = create_task({
        "task_title": "测试任务",
        "task_type": "常规",
        "project_id": test_config["test_project_id"],
        "topic_id": test_config["test_topic_id"],
        "assignee": "harold",
        "task_pic": "cqo",
        "priority": "P2",
        "review_level": "L2",
        "task_goal": "完成测试任务",
        "deliverables": [{
            "name": "测试报告",
            "filename": "TEST-REPORT.md",
            "format": ".md",
            "review_level": "L2",
            "acceptance_criteria": "测试通过"
        }]
    })
    task_id = create_result["task_id"]

    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if "§七.1 当前状态: [P]" in content:
        content = content.replace("§七.1 当前状态: [P]", "§七.1 当前状态: [V]")
    elif "§七.1 当前状态: [ ]" in content:
        content = content.replace("§七.1 当前状态: [ ]", "§七.1 当前状态: [V]")
    with open(task_card_path, 'w', encoding='utf-8') as f:
        f.write(content)

    result = review_deliverable({
        "task_id": task_id,
        "deliverable_name": "测试报告",
        "reviewer": "harold",
        "review_result": "pass",
        "feedback": "测试通过"
    })

    result = verify_task_closed(task_id)
    assert result["verified"] == True
    assert result["deliverables_checked"] == 1
    print("✅ test_verify_task_closed passed")


def test_close_task(test_config):
    create_result = create_task({
        "task_title": "测试任务",
        "task_type": "常规",
        "project_id": test_config["test_project_id"],
        "topic_id": test_config["test_topic_id"],
        "assignee": "harold",
        "task_pic": "cqo",
        "priority": "P2",
        "review_level": "L2",
        "task_goal": "完成测试任务",
        "deliverables": [{
            "name": "测试报告",
            "filename": "TEST-REPORT.md",
            "format": ".md",
            "review_level": "L2",
            "acceptance_criteria": "测试通过"
        }]
    })
    task_id = create_result["task_id"]

    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if "§七.1 当前状态: [P]" in content:
        content = content.replace("§七.1 当前状态: [P]", "§七.1 当前状态: [V]")
    elif "§七.1 当前状态: [ ]" in content:
        content = content.replace("§七.1 当前状态: [ ]", "§七.1 当前状态: [V]")
    with open(task_card_path, 'w', encoding='utf-8') as f:
        f.write(content)

    review_deliverable({
        "task_id": task_id,
        "deliverable_name": "测试报告",
        "reviewer": "harold",
        "review_result": "pass",
        "feedback": "测试通过"
    })

    result = close_task({
        "task_id": task_id,
        "closed_by": "harold"
    })
    assert result["status"] == "OK"
    assert result["state"] == "[x]"
    assert result["zone_c_triggered"] == True

    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "§七.1 当前状态: [x]" in content
    assert "沉淀状态: ⏳ pending" in content
    print("✅ test_close_task passed")


def test_close_task_not_authorized(test_config):
    create_result = create_task({
        "task_title": "测试任务",
        "task_type": "常规",
        "project_id": test_config["test_project_id"],
        "topic_id": test_config["test_topic_id"],
        "assignee": "harold",
        "task_pic": "cqo",
        "priority": "P2",
        "review_level": "L2",
        "task_goal": "完成测试任务",
        "deliverables": [{
            "name": "测试报告",
            "filename": "TEST-REPORT.md",
            "format": ".md",
            "review_level": "L2",
            "acceptance_criteria": "测试通过"
        }]
    })
    task_id = create_result["task_id"]

    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if "§七.1 当前状态: [P]" in content:
        content = content.replace("§七.1 当前状态: [P]", "§七.1 当前状态: [V]")
    elif "§七.1 当前状态: [ ]" in content:
        content = content.replace("§七.1 当前状态: [ ]", "§七.1 当前状态: [V]")
    with open(task_card_path, 'w', encoding='utf-8') as f:
        f.write(content)

    review_deliverable({
        "task_id": task_id,
        "deliverable_name": "测试报告",
        "reviewer": "harold",
        "review_result": "pass",
        "feedback": "测试通过"
    })

    try:
        close_task({
            "task_id": task_id,
            "closed_by": "cto"
        })
        assert False, "应该抛出CloseDeniedError"
    except CloseDeniedError:
        print("✅ test_close_task_not_authorized passed")


def test_archive_task_incomplete_knowledge(test_config):
    create_result = create_task({
        "task_title": "测试任务",
        "task_type": "常规",
        "project_id": test_config["test_project_id"],
        "topic_id": test_config["test_topic_id"],
        "assignee": "harold",
        "task_pic": "cqo",
        "priority": "P2",
        "review_level": "L2",
        "task_goal": "完成测试任务",
        "deliverables": [{
            "name": "测试报告",
            "filename": "TEST-REPORT.md",
            "format": ".md",
            "review_level": "L2",
            "acceptance_criteria": "测试通过"
        }]
    })
    task_id = create_result["task_id"]

    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if "§七.1 当前状态: [P]" in content:
        content = content.replace("§七.1 当前状态: [P]", "§七.1 当前状态: [V]")
    elif "§七.1 当前状态: [ ]" in content:
        content = content.replace("§七.1 当前状态: [ ]", "§七.1 当前状态: [V]")
    with open(task_card_path, 'w', encoding='utf-8') as f:
        f.write(content)

    review_deliverable({
        "task_id": task_id,
        "deliverable_name": "测试报告",
        "reviewer": "harold",
        "review_result": "pass",
        "feedback": "测试通过"
    })

    close_task({
        "task_id": task_id,
        "closed_by": "harold"
    })

    try:
        archive_task({
            "task_id": task_id,
            "archived_by": "harold"
        })
        assert False, "应该抛出KnowledgeCaptureIncompleteError"
    except KnowledgeCaptureIncompleteError:
        print("✅ test_archive_task_incomplete_knowledge passed")


def test_archive_task(test_config):
    create_result = create_task({
        "task_title": "测试任务",
        "task_type": "常规",
        "project_id": test_config["test_project_id"],
        "topic_id": test_config["test_topic_id"],
        "assignee": "harold",
        "task_pic": "cqo",
        "priority": "P2",
        "review_level": "L2",
        "task_goal": "完成测试任务",
        "deliverables": [{
            "name": "测试报告",
            "filename": "TEST-REPORT.md",
            "format": ".md",
            "review_level": "L2",
            "acceptance_criteria": "测试通过"
        }]
    })
    task_id = create_result["task_id"]

    parts = task_id.split("-")
    project_id = "-".join(parts[:2])
    topic_id = parts[2]
    project = get_project_config(project_id)
    task_card_path = os.path.join(project["dir_path"], topic_id, "tasks", f"TASK-CARD-{task_id}.md")
    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if "§七.1 当前状态: [P]" in content:
        content = content.replace("§七.1 当前状态: [P]", "§七.1 当前状态: [V]")
    elif "§七.1 当前状态: [ ]" in content:
        content = content.replace("§七.1 当前状态: [ ]", "§七.1 当前状态: [V]")
    with open(task_card_path, 'w', encoding='utf-8') as f:
        f.write(content)

    review_deliverable({
        "task_id": task_id,
        "deliverable_name": "测试报告",
        "reviewer": "harold",
        "review_result": "pass",
        "feedback": "测试通过"
    })

    close_task({
        "task_id": task_id,
        "closed_by": "harold"
    })

    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace("沉淀状态: ⏳ pending", "沉淀状态: ✅ completed")
    with open(task_card_path, 'w', encoding='utf-8') as f:
        f.write(content)

    result = archive_task({
        "task_id": task_id,
        "archived_by": "harold"
    })
    assert result["status"] == "OK"
    assert result["state"] == "[archived]"
    assert os.path.exists(result["archive_path"])

    with open(task_card_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "§七.1 当前状态: [archived]" in content
    with open(result["archive_path"], 'r', encoding='utf-8') as f:
        archive_content = f.read()
    assert "归档记录" in archive_content
    print("✅ test_archive_task passed")


def test_create_issue_ticket(test_config):
    os.makedirs(os.path.join(test_config["test_project_dir"], "T00", "tasks"), exist_ok=True)

    result = create_issue_ticket({
        "issue_title": "测试问题",
        "issue_description": "这是一个测试问题",
        "issue_severity": "P2",
        "issue_reporter": "cto",
        "task_pic": "cqo",
        "project_id": test_config["test_project_id"],
        "topic_id": "T00",
        "source_task_id": f"{test_config['test_project_id']}-{test_config['test_topic_id']}-T01"
    })
    assert result["status"] == "OK"
    assert result["state"] == "[ ]"
    assert result["source_task_state"] == "[?]"
    assert "T00" in result["task_id"]
    print("✅ test_create_issue_ticket passed")
