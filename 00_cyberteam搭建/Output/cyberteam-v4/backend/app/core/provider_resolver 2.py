"""Provider 解析 + 凭证隔离机制"""
import os
from typing import Optional

# 所有被管理的环境变量（切换 Provider 时清理）
MANAGED_ENV_KEYS: set[str] = {
    'ANTHROPIC_API_KEY', 'ANTHROPIC_API_BASE', 'ANTHROPIC_API_VERSION',
    'OPENAI_API_KEY', 'OPENAI_API_BASE', 'OPENAI_ORG_ID',
    'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION',
    'VERTEX_PROJECT', 'VERTEX_LOCATION',
}

# 模型名到 Provider 的映射
MODEL_TO_PROVIDER: dict[str, str] = {
    # Anthropic
    'claude': 'anthropic',
    'claude-': 'anthropic',
    'sonnet': 'anthropic',  # alias for claude-sonnet
    'opus': 'anthropic',    # alias for claude-opus
    # OpenAI
    'gpt-': 'openai',
    'o1-': 'openai',
    'o3-': 'openai',
    # AWS Bedrock (uses anthropic models but via AWS)
    'bedrock/': 'bedrock',
    # Google Vertex
    'vertex/': 'vertex',
    'gemini': 'vertex',
}


class ProviderResolver:
    """Provider 解析器 - 支持多协议"""

    def __init__(self):
        self._provider_priority: list[str] = [
            'anthropic', 'openai', 'bedrock', 'vertex'
        ]

    def resolve(self, model: str, explicit_provider: Optional[str] = None) -> str:
        """解析优先级：
        1. 显式 provider_id（参数）
        2. 从模型名推断
        3. 环境变量
        4. 默认 anthropic
        """
        # 1. 显式 provider
        if explicit_provider:
            return explicit_provider

        # 2. 从模型名推断
        inferred = self._infer_provider_from_model(model)
        if inferred:
            return inferred

        # 3. 从环境变量推断
        env_provider = self._resolve_from_env()
        if env_provider:
            return env_provider

        # 4. 默认值
        return 'anthropic'

    def _infer_provider_from_model(self, model: str) -> Optional[str]:
        """从模型名推断 Provider"""
        model_lower = model.lower()

        # Anthropic 检查
        if any(model_lower.startswith(prefix) for prefix in ['claude-', 'sonnet', 'opus', 'haiku']):
            return 'anthropic'

        # OpenAI 检查
        if any(model_lower.startswith(prefix) for prefix in ['gpt-', 'o1-', 'o3-']):
            return 'openai'

        # Bedrock 检查
        if model_lower.startswith('bedrock/'):
            return 'bedrock'

        # Vertex 检查
        if any(model_lower.startswith(prefix) for prefix in ['vertex/', 'gemini']):
            return 'vertex'

        return None

    def _resolve_from_env(self) -> Optional[str]:
        """从环境变量推断 Provider"""
        # 按优先级检查各 Provider 的凭证
        if os.environ.get('ANTHROPIC_API_KEY'):
            return 'anthropic'
        if os.environ.get('OPENAI_API_KEY'):
            return 'openai'
        if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            return 'bedrock'
        if os.environ.get('VERTEX_PROJECT'):
            return 'vertex'
        return None

    def cleanup_env_for_provider(self, target_provider: str) -> dict:
        """切换 Provider 时清理所有其他 Provider 的凭证

        防止跨 Provider 泄漏 - 只保留目标 Provider 的凭证

        Args:
            target_provider: 目标 Provider (anthropic/openai/bedrock/vertex)

        Returns:
            被清理的环境变量字典（用于恢复）
        """
        original_env = {}

        # 定义各 Provider 关联的环境变量
        provider_env_groups: dict[str, list[str]] = {
            'anthropic': ['ANTHROPIC_API_KEY', 'ANTHROPIC_API_BASE', 'ANTHROPIC_API_VERSION'],
            'openai': ['OPENAI_API_KEY', 'OPENAI_API_BASE', 'OPENAI_ORG_ID'],
            'bedrock': ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION'],
            'vertex': ['VERTEX_PROJECT', 'VERTEX_LOCATION'],
        }

        target_keys = set(provider_env_groups.get(target_provider, []))

        # 遍历所有被管理的环境变量
        for key in MANAGED_ENV_KEYS:
            if key in os.environ:
                original_env[key] = os.environ[key]
                # 只有不在目标 Provider 组内的才清理
                if key not in target_keys:
                    del os.environ[key]

        return original_env

    def restore_env(self, saved_env: dict) -> None:
        """恢复被清理的环境变量

        Args:
            saved_env: cleanup_env_for_provider 返回的字典
        """
        for key, value in saved_env.items():
            os.environ[key] = value

    def get_provider_env_keys(self, provider: str) -> list[str]:
        """获取指定 Provider 的所有环境变量

        Args:
            provider: Provider 名称

        Returns:
            该 Provider 关联的环境变量列表
        """
        provider_env_groups: dict[str, list[str]] = {
            'anthropic': ['ANTHROPIC_API_KEY', 'ANTHROPIC_API_BASE', 'ANTHROPIC_API_VERSION'],
            'openai': ['OPENAI_API_KEY', 'OPENAI_API_BASE', 'OPENAI_ORG_ID'],
            'bedrock': ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION'],
            'vertex': ['VERTEX_PROJECT', 'VERTEX_LOCATION'],
        }
        return provider_env_groups.get(provider, [])


# 全局单例
provider_resolver = ProviderResolver()