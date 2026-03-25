#!/usr/bin/env python3
"""
CyberTeam V4 - 核心模块测试
覆盖: team/, spawn/, workspace/, transport/
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到 path
_project_root = Path(__file__).parent.parent
sys.path.insert(0, str(_project_root))


class TestCyberTeamImports:
    """测试 CyberTeam 核心模块导入"""

    def test_import_team_manager(self):
        """测试 team.manager 导入"""
        from cyberteam.team.manager import TeamManager
        assert TeamManager is not None

    def test_import_team_models(self):
        """测试 team.models 导入"""
        from cyberteam.team.models import TeamConfig, TeamMember, TaskItem
        assert TeamConfig is not None
        assert TeamMember is not None
        assert TaskItem is not None

    def test_import_task_store(self):
        """测试 team.tasks 导入"""
        from cyberteam.team.tasks import TaskStore
        assert TaskStore is not None

    def test_import_mailbox(self):
        """测试 team.mailbox 导入"""
        from cyberteam.team.mailbox import MailboxManager
        assert MailboxManager is not None

    def test_import_spawn_registry(self):
        """测试 spawn.registry 导入"""
        from cyberteam.spawn.registry import register_agent, get_registry
        assert register_agent is not None
        assert get_registry is not None

    def test_import_workspace_manager(self):
        """测试 workspace.manager 导入"""
        from cyberteam.workspace.manager import WorkspaceManager
        assert WorkspaceManager is not None

    def test_import_transport_file(self):
        """测试 transport.file 导入"""
        from cyberteam.transport.file import FileTransport
        assert FileTransport is not None

    def test_import_board_renderer(self):
        """测试 board.renderer 导入"""
        from cyberteam.board.renderer import BoardRenderer
        assert BoardRenderer is not None


class TestIntegration:
    """测试集成功能"""

    def test_cyberteam_adapter(self):
        """测试 CyberTeamAdapter 导入"""
        from integration.cyberteam_adapter import CyberTeamAdapter
        adapter = CyberTeamAdapter()
        assert adapter is not None
        assert hasattr(adapter, 'TEMPLATES')

    def test_swarm_orchestrator(self):
        """测试 SwarmOrchestrator 导入"""
        from swarm_orchestrator import SwarmOrchestrator
        # 基本功能测试
        swarm = SwarmOrchestrator(
            team_name="test-swarm",
            goal="测试目标",
            repo_root=Path.cwd()
        )
        assert swarm.team_name == "test-swarm"
        assert swarm.goal == "测试目标"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
