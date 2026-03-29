#!/bin/bash
# CyberTeam V4 安装和测试脚本

set -e

cd "$(dirname "$0")"

echo "=== CyberTeam V4 安装测试 ==="

# 1. 安装
echo "[1/4] 安装 CyberTeam..."
pip3 install -e . -q

# 2. 验证 CLI
echo "[2/4] 验证 CLI 命令..."
cyberteam --help > /dev/null && echo "  ✅ cyberteam --help"
cyberteam team --help > /dev/null && echo "  ✅ cyberteam team"
cyberteam spawn --help > /dev/null && echo "  ✅ cyberteam spawn"
cyberteam task --help > /dev/null && echo "  ✅ cyberteam task"

# 3. 验证 Python 导入
echo "[3/4] 验证 Python 模块..."
python3 -c "from cyberteam.team import TeamManager; print('  ✅ cyberteam.team.TeamManager')"
python3 -c "from cyberteam.spawn import get_backend; print('  ✅ cyberteam.spawn.get_backend')"
python3 -c "from cyberteam.workspace import WorkspaceManager; print('  ✅ cyberteam.workspace.WorkspaceManager')"
python3 -c "from engine.ceo import CEORouter; print('  ✅ engine.ceo.CEORouter')"
python3 -c "from swarm_orchestrator import SwarmOrchestrator; print('  ✅ swarm_orchestrator.SwarmOrchestrator')"

# 4. 运行测试
echo "[4/4] 运行单元测试..."
python3 -m pytest tests/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== 安装测试完成 ==="
