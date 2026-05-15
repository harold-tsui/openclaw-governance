#!/bin/bash
# NUCLEUS 4.0 Heartbeat 模拟验证

cd /Users/haroldtsui/Workspaces/openclaw/main/skills/openclaw-governance/skills/openclaw-governance-nucleus

# 设置环境变量
export PROJECT_DIR="/Users/haroldtsui/Workspaces/openclaw/main/10_Projects/ZT-P015_NUCLEUS-4-0"
export AGENT_WORKSPACE="/Users/haroldtsui/Workspaces/openclaw/main/60_Agents/cqo"

# 运行验证脚本
python3 tests/verify_heartbeat_simulation.py