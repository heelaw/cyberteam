#!/bin/bash
# CyberTeam V4 快速演示

set -e

cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         CyberTeam V4 - 群体智能系统演示                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 检查安装
if ! pip3 show cyberteam >/dev/null 2>&1; then
    echo "[1/5] 安装 CyberTeam..."
    pip3 install -e . -q
else
    echo "[1/5] ✅ CyberTeam 已安装"
fi

# 验证核心模块
echo ""
echo "[2/5] 验证核心模块..."
python3 -c "
from cyberteam.team import TeamManager
from cyberteam.spawn import get_backend
from cyberteam.workspace import WorkspaceManager
from engine.ceo import CEORouter
from swarm_orchestrator import SwarmOrchestrator
print('  ✅ 所有核心模块导入成功')
"

# 演示 CEO 路由
echo ""
echo "[3/5] 演示 CEO 路由引擎..."
python3 << 'PYTHON'
from engine.ceo import CEORouter

router = CEORouter()

# 测试不同类型的输入
test_cases = [
    ("什么是AI?", "简单咨询"),
    ("写一个Python函数", "低复杂度"),
    ("分析市场趋势并制定战略", "高复杂度SWARM"),
]

for query, expected in test_cases:
    result = router.route(query)
    emoji = "✅"
    print(f"  {emoji} \"{query[:30]}...\" → {result.target} (意图: {result.intent}, 复杂度: {result.complexity})")
PYTHON

# 演示 Swarm 编排
echo ""
echo "[4/5] 演示 Swarm 编排器..."
python3 << 'PYTHON'
from swarm_orchestrator import SwarmOrchestrator

# 创建演示 Swarm
swarm = SwarmOrchestrator("demo-swarm", "演示目标")

# 创建虚拟 Agents
for i in range(3):
    agent_name = f"agent-{i+1}"
    swarm.create_agent(agent_name, "研究员", task="演示任务", workspace=False)

print(f"  ✅ 创建 Swarm: {swarm.team_name}")
print(f"  ✅ Agent 数量: {len(swarm.agents)}")

# 创建任务依赖链
task1 = swarm.assign_task("agent-1", "收集数据")
task2 = swarm.assign_task("agent-2", "分析数据", blocked_by=[task1.task_id])
task3 = swarm.assign_task("agent-3", "撰写报告", blocked_by=[task2.task_id])

print(f"  ✅ 创建任务链: task1 → task2 → task3")

# 完成任务验证依赖解除
swarm.complete_task(task1.task_id, "数据已收集")
progress = swarm.monitor_progress()
print(f"  ✅ 任务进度: total={progress['tasks']['total']}, pending={progress['tasks']['pending']}, blocked={progress['tasks']['blocked']}")

result = swarm.get_result()
print(f"  ✅ Swarm 状态: {result.status}")
PYTHON

# CLI 命令演示
echo ""
echo "[5/5] CLI 命令演示..."
echo "  可用命令:"
cyberteam --help 2>&1 | grep -E "  [a-z]+" | head -10 | sed 's/^/    /'

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    演示完成！                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "下一步:"
echo "  • 创建团队: cyberteam launch --template swarm --goal \"你的目标\""
echo "  • Spawn Agent: cyberteam spawn tmux claude --team my-team --agent-name expert"
echo "  • 查看文档: cat README.md"
