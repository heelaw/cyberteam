"""ClawTeam 接口兼容层

提供与外部 ClawTeam v0.2.0 的接口兼容性，使 CyberTeam V4 可以：
1. 读取外部 ClawTeam 的配置文件
2. 访问外部 ClawTeam 的数据目录
3. 复用外部 ClawTeam 的成熟功能

融合原则：CyberTeam 逻辑不变，仅做接口适配
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Optional, List

from cyberteam.config import CyberTeamConfig, load_config, save_config

logger = logging.getLogger(__name__)


class ClawTeamCompat:
    """ClawTeam 接口兼容层

    提供与外部 ClawTeam v0.2.0 的无缝兼容能力。
    """

    # ClawTeam 旧数据目录
    CLAWTEAM_DIR = Path.home() / ".clawteam"
    # CyberTeam 新数据目录
    CYBERTEAM_DIR = Path.home() / ".cyberteam"

    # ClawTeam 配置文件
    CLAWTEAM_CONFIG = CLAWTEAM_DIR / "config.json"
    # CyberTeam 配置文件
    CYBERTEAM_CONFIG = CYBERTEAM_DIR / "config.json"

    def __init__(self):
        self._ensure_dirs()
        self._migrate_if_needed()

    def _ensure_dirs(self) -> None:
        """确保 CyberTeam 目录存在"""
        self.CYBERTEAM_DIR.mkdir(parents=True, exist_ok=True)

    def _migrate_if_needed(self) -> None:
        """迁移 ClawTeam 配置到 CyberTeam（如果需要）"""
        # 如果 CyberTeam 配置已存在，无需迁移
        if self.CYBERTEAM_CONFIG.exists():
            return

        # 如果 ClawTeam 配置存在，迁移它
        if self.CLAWTEAM_CONFIG.exists():
            logger.info("检测到 ClawTeam 配置，开始迁移到 CyberTeam...")
            self._migrate_config()
            self._migrate_data()
            logger.info("迁移完成！")
        else:
            # 创建默认配置
            cfg = CyberTeamConfig()
            save_config(cfg)
            logger.info("已创建默认 CyberTeam 配置")

    def _migrate_config(self) -> None:
        """迁移 ClawTeam 配置文件"""
        try:
            # 读取 ClawTeam 配置
            data = json.loads(self.CLAWTEAM_CONFIG.read_text(encoding="utf-8"))

            # 转换为 CyberTeam 配置（字段名相同，可以直接使用）
            cfg = CyberTeamConfig.model_validate(data)
            save_config(cfg)

            # 备份原配置
            backup = self.CLAWTEAM_CONFIG.with_suffix(".json.bak")
            shutil.copy2(self.CLAWTEAM_CONFIG, backup)
            logger.info(f"配置已迁移，备份至: {backup}")

        except Exception as e:
            logger.error(f"配置迁移失败: {e}")
            raise

    def _migrate_data(self) -> None:
        """迁移 ClawTeam 数据目录到 CyberTeam"""
        for subdir in ["teams", "tasks", "workspaces", "mailboxes", "sessions", "costs"]:
            clawteam_subdir = self.CLAWTEAM_DIR / subdir
            cyberteam_subdir = self.CYBERTEAM_DIR / subdir

            if clawteam_subdir.exists() and not cyberteam_subdir.exists():
                # 使用软链接而不是复制，节省空间
                try:
                    cyberteam_subdir.symlink_to(clawteam_subdir.resolve())
                    logger.info(f"数据目录已链接: {subdir}")
                except FileExistsError:
                    pass

    # -------------------------------------------------------------------------
    # 配置兼容
    # -------------------------------------------------------------------------

    @staticmethod
    def load_compat_config() -> CyberTeamConfig:
        """加载配置（优先 CyberTeam，兼容 ClawTeam）"""
        return load_config()

    @staticmethod
    def save_compat_config(config: CyberTeamConfig) -> None:
        """保存配置到 CyberTeam 目录"""
        save_config(config)

    # -------------------------------------------------------------------------
    # 环境变量兼容
    # -------------------------------------------------------------------------

    @staticmethod
    def get_compat_env(key: str) -> Optional[str]:
        """获取环境变量（兼容 CLAWTEAM_* 和 CYBERTEAM_* 前缀）

        优先级：
        1. CYBERTEAM_* 环境变量
        2. CLAWTEAM_* 环境变量（向后兼容）
        3. None
        """
        # 先检查 CYBERTEAM_* 前缀
        cyber_key = f"CYBERTEAM_{key}"
        value = os.environ.get(cyber_key)
        if value is not None:
            return value

        # 再检查 CLAWTEAM_* 前缀（向后兼容）
        claw_key = f"CLAWTEAM_{key}"
        return os.environ.get(claw_key)

    @staticmethod
    def set_compat_env(key: str, value: str) -> None:
        """设置环境变量（同时设置两个前缀以保持兼容）"""
        os.environ[f"CYBERTEAM_{key}"] = value
        os.environ[f"CLAWTEAM_{key}"] = value

    # -------------------------------------------------------------------------
    # 数据目录兼容
    # -------------------------------------------------------------------------

    @staticmethod
    def get_compat_data_dir() -> Path:
        """获取数据目录（兼容 CLAWTEAM_DATA_DIR 和 CYBERTEAM_DATA_DIR）

        优先级：
        1. CYBERTEAM_DATA_DIR 环境变量
        2. CLAWTEAM_DATA_DIR 环境变量
        3. CyberTeam 配置中的 data_dir
        4. ~/.cyberteam/
        """
        # 先检查 CYBERTEAM_DATA_DIR
        cyber_dir = os.environ.get("CYBERTEAM_DATA_DIR")
        if cyber_dir:
            return Path(cyber_dir)

        # 再检查 CLAWTEAM_DATA_DIR（向后兼容）
        claw_dir = os.environ.get("CLAWTEAM_DATA_DIR")
        if claw_dir:
            return Path(claw_dir)

        # 检查配置文件
        cfg = load_config()
        if cfg.data_dir:
            return Path(cfg.data_dir)

        # 默认使用 ~/.cyberteam/
        return Path.home() / ".cyberteam"

    # -------------------------------------------------------------------------
    # ClawTeam 底层功能桥接
    # -------------------------------------------------------------------------

    def import_clawteam_module(self, module_name: str) -> Any:
        """动态导入外部 ClawTeam 模块（如果可用）

        用于在 CyberTeam 缺少某些功能时，回退到外部 ClawTeam 的实现。
        """
        try:
            import importlib
            return importlib.import_module(f"clawteam.{module_name}")
        except ImportError:
            logger.warning(f"外部 ClawTeam 模块不可用: clawteam.{module_name}")
            return None

    def can_use_clawteam_backend(self) -> bool:
        """检查是否可以使用外部 ClawTeam 作为后端"""
        return self.import_clawteam_module("spawn") is not None

    # -------------------------------------------------------------------------
    # 团队数据兼容
    # -------------------------------------------------------------------------

    def list_clawteam_teams(self) -> List[str]:
        """列出外部 ClawTeam 中的团队（可用于数据迁移）"""
        teams_dir = self.CLAWTEAM_DIR / "teams"
        if not teams_dir.exists():
            return []
        return [d.name for d in teams_dir.iterdir() if d.is_dir()]

    def list_cyberteam_teams(self) -> List[str]:
        """列出 CyberTeam 中的团队"""
        teams_dir = self.CYBERTEAM_DIR / "teams"
        if not teams_dir.exists():
            return []
        return [d.name for d in teams_dir.iterdir() if d.is_dir()]

    def get_all_teams(self) -> dict[str, List[str]]:
        """获取所有团队（包括迁移的和新的）"""
        return {
            "cyberteam": self.list_cyberteam_teams(),
            "clawteam": self.list_clawteam_teams(),
        }


# 全局兼容层实例
_compat: Optional[ClawTeamCompat] = None


def get_compat() -> ClawTeamCompat:
    """获取全局兼容层实例（单例模式）"""
    global _compat
    if _compat is None:
        _compat = ClawTeamCompat()
    return _compat
