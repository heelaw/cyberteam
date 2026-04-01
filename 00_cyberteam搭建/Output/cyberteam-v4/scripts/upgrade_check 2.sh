#!/bin/bash
# CyberTeam V4 升级检查脚本
# 用法: bash scripts/upgrade_check.sh

set -e

cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         CyberTeam V4 - 升级检查                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. 检查 ClawTeam 版本
echo "[1/7] 检查 ClawTeam 版本..."
if command -v clawteam &> /dev/null; then
    CLAWTEAM_VERSION=$(clawteam --version 2>/dev/null || echo "unknown")
    echo "  ✅ ClawTeam 版本: $CLAWTEAM_VERSION"
else
    echo "  ⚠️ ClawTeam CLI 未安装 (仅检查 CyberTeam 模块)"
fi

# 2. 设置 Python 路径
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 3. 核心模块导入测试
echo ""
echo "[2/7] 核心模块导入测试..."

test_module() {
    local module=$1
    local desc=$2
    if python3 -c "import $module" 2>/dev/null; then
        echo "  ✅ $desc"
        return 0
    else
        echo "  ❌ $desc (导入失败)"
        return 1
    fi
}

test_module "cyberteam.team" "team/"
test_module "cyberteam.spawn" "spawn/"
test_module "cyberteam.workspace" "workspace/"
test_module "cyberteam.transport" "transport/"
test_module "cyberteam.board" "board/"
test_module "cyberteam.adaptors" "adaptors/"

# 4. Swarm 编排器测试
echo ""
echo "[3/7] Swarm 编排器测试..."
test_module "swarm_orchestrator" "swarm_orchestrator.py"
test_module "integration.cyberteam_adapter" "integration/"

# 5. Engine 层测试
echo ""
echo "[4/7] Engine 层测试..."
test_module "engine.ceo" "engine/ceo/"
test_module "engine.department" "engine/department/"
test_module "engine.strategy" "engine/strategy/"

# 6. 适配器健康检查
echo ""
echo "[5/7] 适配器健康检查..."
python3 << 'PYTHON' 2>/dev/null
import sys
sys.path.insert(0, ".")
from integration.cyberteam_adapter import CyberTeamAdapter

adapter = CyberTeamAdapter()
health = adapter.health_check()

print(f"  cyberteam_available: {health['cyberteam_available']}")
print(f"  backend: {health['backend']}")
print(f"  data_dir: {health['data_dir']}")
print(f"  teams_count: {health['teams_count']}")

if health['cyberteam_available']:
    print("  ✅ CyberTeam 底层可用")
else:
    print("  ⚠️ CyberTeam 底层不可用 (模拟模式)")
PYTHON

# 7. CLI 命令检查
echo ""
echo "[6/7] CLI 命令检查..."
if python3 -m cyberteam --version &> /dev/null; then
    VERSION=$(python3 -m cyberteam --version 2>/dev/null | head -1)
    echo "  ✅ cyberteam CLI: $VERSION"
else
    echo "  ❌ cyberteam CLI 不可用"
fi

# 8. Swarm 基本功能测试
echo ""
echo "[7/7] Swarm 基本功能测试..."
python3 << 'PYTHON' 2>/dev/null
import sys
sys.path.insert(0, ".")
from swarm_orchestrator import SwarmOrchestrator, SwarmStatus

swarm = SwarmOrchestrator("upgrade-test", "升级测试")
print(f"  ✅ Swarm 创建成功: {swarm.team_name}")
print(f"  ✅ Swarm 状态: {swarm.status.value}")
PYTHON

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    检查完成                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "如发现问题，请运行完整测试:"
echo "  python3 -c \"from swarm_orchestrator import SwarmOrchestrator\""
echo ""
