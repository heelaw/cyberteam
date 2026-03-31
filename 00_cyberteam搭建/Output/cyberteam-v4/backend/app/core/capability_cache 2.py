"""per-model 能力缓存"""
import time
from typing import Optional, Any


class ModelCapability:
    """模型能力描述"""

    def __init__(
        self,
        model_id: str,
        provider: str,
        max_tokens: int,
        supports_streaming: bool = False,
        supports_vision: bool = False,
        supports_function_calling: bool = False,
    ):
        self.model_id = model_id
        self.provider = provider
        self.max_tokens = max_tokens
        self.supports_streaming = supports_streaming
        self.supports_vision = supports_vision
        self.supports_function_calling = supports_function_calling

    def to_dict(self) -> dict[str, Any]:
        return {
            'model_id': self.model_id,
            'provider': self.provider,
            'max_tokens': self.max_tokens,
            'supports_streaming': self.supports_streaming,
            'supports_vision': self.supports_vision,
            'supports_function_calling': self.supports_function_calling,
        }


class CapabilityCache:
    """能力缓存 - globalThis 等效于进程级单例

    使用单例模式确保整个进程共享同一个缓存实例。

    用法:
        cache = CapabilityCache.get_instance()
        cache.set('claude-opus-4-6', capability)
        cap = cache.get('claude-opus-4-6')
    """

    _instance: Optional['CapabilityCache'] = None

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: dict[str, tuple[ModelCapability, float]] = {}
        self._ttl = ttl_seconds

    @classmethod
    def get_instance(cls, ttl_seconds: int = 3600) -> 'CapabilityCache':
        """获取单例实例

        Args:
            ttl_seconds: 缓存过期时间（秒），默认3600（1小时）
        """
        if cls._instance is None:
            cls._instance = cls(ttl_seconds)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（主要用于测试）"""
        cls._instance = None

    def get(self, model: str) -> Optional[ModelCapability]:
        """获取缓存的模型能力

        Args:
            model: 模型标识符

        Returns:
            缓存的能力对象，如果不存在或已过期返回 None
        """
        if model not in self._cache:
            return None

        capability, timestamp = self._cache[model]

        # 检查是否过期
        if time.time() - timestamp > self._ttl:
            del self._cache[model]
            return None

        return capability

    def set(self, model: str, capability: ModelCapability) -> None:
        """设置缓存

        Args:
            model: 模型标识符
            capability: 模型能力对象
        """
        self._cache[model] = (capability, time.time())

    def invalidate(self, model: Optional[str] = None) -> None:
        """清除缓存

        Args:
            model: 如果指定，只清除该模型的缓存；否则清除所有
        """
        if model:
            self._cache.pop(model, None)
        else:
            self._cache.clear()

    def get_ttl_remaining(self, model: str) -> Optional[int]:
        """获取缓存剩余TTL

        Args:
            model: 模型标识符

        Returns:
            剩余秒数，如果不存在返回 None
        """
        if model not in self._cache:
            return None

        _, timestamp = self._cache[model]
        remaining = self._ttl - (time.time() - timestamp)

        if remaining <= 0:
            del self._cache[model]
            return None

        return int(remaining)

    def size(self) -> int:
        """返回缓存的模型数量"""
        return len(self._cache)

    def list_cached_models(self) -> list[str]:
        """返回所有缓存的模型ID列表"""
        return list(self._cache.keys())