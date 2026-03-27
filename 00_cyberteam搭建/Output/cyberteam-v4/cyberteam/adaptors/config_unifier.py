"""配置统一管理器

统一管理 CyberTeam V4 与外部 ClawTeam v0.2.0 的配置。

核心功能：
1. 统一配置路径（~/.cyberteam/config.json）
2. 环境变量兼容（CLAWTEAM_* 和 CYBERTEAM_*）
3. 配置文件迁移（从 ClawTeam 迁移到 CyberTeam）
4. 配置验证和默认值管理
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from cyberteam.config import (
    CyberTeamConfig,
    load_config as cyberteam_load,
    save_config as cyberteam_save,
)

logger = logging.getLogger(__name__)


class ConfigUnifier:
    """配置统一管理器

    确保 CyberTeam 和 ClawTeam 配置的互操作性。
    """

    # 统一配置目录
    CYBERTEAM_DIR = Path.home() / ".cyberteam"
    CLAWTEAM_DIR = Path.home() / ".clawteam"

    # 配置文件
    CYBERTEAM_CONFIG = CYBERTEAM_DIR / "config.json"
    CLAWTEAM_CONFIG = CLAWTEAM_DIR / "config.json"

    # 环境变量映射（ClawTeam -> CyberTeam）
    ENV_VAR_MAP = {
        # ClawTeam 环境变量 -> CyberTeam 环境变量
        "CLAWTEAM_DATA_DIR": "CYBERTEAM_DATA_DIR",
        "CLAWTEAM_USER": "CYBERTEAM_USER",
        "CLAWTEAM_TEAM_NAME": "CYBERTEAM_TEAM_NAME",
        "CLAWTEAM_TRANSPORT": "CYBERTEAM_TRANSPORT",
        "CLAWTEAM_WORKSPACE": "CYBERTEAM_WORKSPACE",
        "CLAWTEAM_DEFAULT_BACKEND": "CYBERTEAM_DEFAULT_BACKEND",
        "CLAWTEAM_SKIP_PERMISSIONS": "CYBERTEAM_SKIP_PERMISSIONS",
        "CLAWTEAM_TIMEZONE": "CYBERTEAM_TIMEZONE",
        "CLAWTEAM_GOURCE_PATH": "CYBERTEAM_GOURCE_PATH",
        "CLAWTEAM_GOURCE_RESOLUTION": "CYBERTEAM_GOURCE_RESOLUTION",
        "CLAWTEAM_GOURCE_SECONDS_PER_DAY": "CYBERTEAM_GOURCE_SECONDS_PER_DAY",
        "CLAWTEAM_SPAWN_PROMPT_DELAY": "CYBERTEAM_SPAWN_PROMPT_DELAY",
        "CLAWTEAM_SPAWN_READY_TIMEOUT": "CYBERTEAM_SPAWN_READY_TIMEOUT",
    }

    def __init__(self, auto_migrate: bool = True):
        """初始化配置统一管理器

        Args:
            auto_migrate: 是否自动迁移 ClawTeam 配置
        """
        self._ensure_dirs()
        if auto_migrate:
            self._setup_compat_env()
            self._migrate_if_needed()

    def _ensure_dirs(self) -> None:
        """确保必要目录存在"""
        self.CYBERTEAM_DIR.mkdir(parents=True, exist_ok=True)

    def _setup_compat_env(self) -> None:
        """设置兼容环境变量（将 CLAWTEAM_* 映射到 CYBERTEAM_*）"""
        for claw_key, cyber_key in self.ENV_VAR_MAP.items():
            claw_val = os.environ.get(claw_key)
            cyber_val = os.environ.get(cyber_key)

            # 如果 CyberTeam 环境变量未设置，但 ClawTeam 环境变量已设置，则复制
            if claw_val and not cyber_val:
                os.environ[cyber_key] = claw_val
                logger.info(f"环境变量兼容: {claw_key} -> {cyber_key}")

    def _migrate_if_needed(self) -> None:
        """迁移 ClawTeam 配置到 CyberTeam（如果需要）"""
        # 如果 CyberTeam 配置已存在，无需迁移
        if self.CYBERTEAM_CONFIG.exists():
            logger.debug("CyberTeam 配置已存在，跳过迁移")
            return

        # 如果 ClawTeam 配置存在，迁移它
        if self.CLAWTEAM_CONFIG.exists():
            logger.info("检测到 ClawTeam 配置，开始迁移...")
            self.migrate_from_clawteam()
        else:
            # 创建默认配置
            cfg = CyberTeamConfig()
            cyberteam_save(cfg)
            logger.info("已创建默认 CyberTeam 配置")

    # -------------------------------------------------------------------------
    # 配置迁移
    # -------------------------------------------------------------------------

    def migrate_from_clawteam(self) -> bool:
        """从 ClawTeam 迁移配置和数据

        Returns:
            True 如果迁移成功，False 如果失败
        """
        try:
            # 迁移配置文件
            self._migrate_config()

            # 迁移数据目录（使用软链接）
            self._migrate_data_dirs()

            logger.info("ClawTeam 配置迁移完成")
            return True

        except Exception as e:
            logger.error(f"配置迁移失败: {e}")
            return False

    def _migrate_config(self) -> None:
        """迁移配置文件"""
        if not self.CLAWTEAM_CONFIG.exists():
            logger.warning("ClawTeam 配置文件不存在")
            return

        # 读取 ClawTeam 配置
        data = json.loads(self.CLAWTEAM_CONFIG.read_text(encoding="utf-8"))

        # 备份原配置
        backup = self.CLAWTEAM_CONFIG.with_suffix(".json.migrated")
        shutil.copy2(self.CLAWTEAM_CONFIG, backup)
        logger.info(f"ClawTeam 配置已备份: {backup}")

        # 转换为 CyberTeam 配置并保存
        cfg = CyberTeamConfig.model_validate(data)
        cyberteam_save(cfg)
        logger.info(f"配置已迁移到: {self.CYBERTEAM_CONFIG}")

    def _migrate_data_dirs(self) -> None:
        """迁移数据目录（使用软链接节省空间）"""
        subdirs = ["teams", "tasks", "workspaces", "mailboxes", "sessions", "costs", "templates"]

        for subdir in subdirs:
            clawteam_subdir = self.CLAWTEAM_DIR / subdir
            cyberteam_subdir = self.CYBERTEAM_DIR / subdir

            if clawteam_subdir.exists() and not cyberteam_subdir.exists():
                try:
                    # 使用软链接
                    cyberteam_subdir.symlink_to(clawteam_subdir.resolve())
                    logger.info(f"数据目录已链接: {subdir} -> {clawteam_subdir}")
                except FileExistsError:
                    # 如果已经存在，跳过
                    pass
                except OSError as e:
                    logger.warning(f"无法创建符号链接 {subdir}: {e}")
                    # 如果软链接失败，尝试复制
                    self._copy_dir(clawteam_subdir, cyberteam_subdir)

    def _copy_dir(self, src: Path, dst: Path) -> None:
        """复制目录"""
        import shutil

        try:
            shutil.copytree(src, dst, dirs_exist_ok=True)
            logger.info(f"数据目录已复制: {src} -> {dst}")
        except Exception as e:
            logger.error(f"复制目录失败: {e}")

    # -------------------------------------------------------------------------
    # 配置访问
    # -------------------------------------------------------------------------

    def load(self) -> CyberTeamConfig:
        """加载 CyberTeam 配置"""
        return cyberteam_load()

    def save(self, config: CyberTeamConfig) -> None:
        """保存 CyberTeam 配置"""
        cyberteam_save(config)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取配置项（兼容环境变量）

        优先级：CYBERTEAM_* > CLAWTEAM_* > 配置文件 > 默认值
        """
        # 先检查环境变量
        cyber_env = f"CYBERTEAM_{key}"
        if cyber_env in os.environ:
            return os.environ[cyber_env]

        claw_env = f"CLAWTEAM_{key}"
        if claw_env in os.environ:
            return os.environ[claw_env]

        # 检查配置文件
        cfg = self.load()
        value = getattr(cfg, key, None)
        if value is not None and value != "":
            return str(value)

        return default

    def set(self, key: str, value: str) -> None:
        """设置配置项"""
        cfg = self.load()
        if hasattr(cfg, key):
            # 根据类型转换
            field_type = type(getattr(cfg, key))
            if field_type == bool:
                setattr(cfg, key, value.lower() in ("true", "1", "yes"))
            elif field_type == int:
                setattr(cfg, key, int(value))
            elif field_type == float:
                setattr(cfg, key, float(value))
            else:
                setattr(cfg, key, value)
            self.save(cfg)

        # 同时设置环境变量
        os.environ[f"CYBERTEAM_{key}"] = value

    # -------------------------------------------------------------------------
    # 配置验证
    # -------------------------------------------------------------------------

    def validate(self, config: CyberTeamConfig) -> list[str]:
        """验证配置有效性

        Returns:
            错误列表，如果为空则配置有效
        """
        errors = []

        # 验证 profiles
        for name, profile in config.profiles.items():
            if not profile.agent:
                errors.append(f"Profile '{name}' 缺少 agent 字段")

        # 验证 workspace 配置
        if config.workspace not in ("auto", "always", "never", ""):
            errors.append(f"workspace 配置无效: {config.workspace}")

        # 验证 backend 配置
        if config.default_backend not in ("tmux", "subprocess"):
            errors.append(f"default_backend 配置无效: {config.default_backend}")

        return errors

    # -------------------------------------------------------------------------
    # 工具方法
    # -------------------------------------------------------------------------

    def backup(self, path: Optional[Path] = None) -> Path:
        """备份当前配置

        Args:
            path: 备份路径，默认备份到 ~/.cyberteam/config.json.backup

        Returns:
            备份文件路径
        """
        if path is None:
            path = self.CYBERTEAM_CONFIG.with_suffix(".json.backup")

        if self.CYBERTEAM_CONFIG.exists():
            shutil.copy2(self.CYBERTEAM_CONFIG, path)
            logger.info(f"配置已备份: {path}")

        return path

    def restore(self, path: Path) -> bool:
        """恢复配置

        Args:
            path: 备份文件路径

        Returns:
            True 如果恢复成功
        """
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cfg = CyberTeamConfig.model_validate(data)
            self.save(cfg)
            logger.info(f"配置已恢复: {path}")
            return True
        except Exception as e:
            logger.error(f"配置恢复失败: {e}")
            return False

    def reset(self) -> None:
        """重置为默认配置"""
        cfg = CyberTeamConfig()
        self.save(cfg)
        logger.info("配置已重置为默认")


# 全局实例
_unifier: Optional[ConfigUnifier] = None


def get_unifier() -> ConfigUnifier:
    """获取全局配置统一管理器实例（单例模式）"""
    global _unifier
    if _unifier is None:
        _unifier = ConfigUnifier()
    return _unifier
