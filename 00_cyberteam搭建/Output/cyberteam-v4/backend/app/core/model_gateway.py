"""模型网关：统一管理多 Provider"""
import os
import logging
from typing import Optional, Any

from .provider_resolver import ProviderResolver, provider_resolver
from .capability_cache import CapabilityCache, ModelCapability

log = logging.getLogger("cyberteam.model_gateway")


class ModelGateway:
    """
    统一模型网关

    功能：
    - 多 Provider 抽象（Anthropic / OpenAI / Bedrock / Vertex）
    - 凭证隔离：切换 Provider 时清理其他 Provider 的环境变量
    - 能力缓存：避免重复查询模型能力

    用法:
        gateway = ModelGateway()
        capability = await gateway.get_capability("claude-opus-4-6")
        response = await gateway.chat_completion("claude-opus-4-6", messages)
    """

    def __init__(self, resolver: Optional[ProviderResolver] = None):
        """
        初始化模型网关

        Args:
            resolver: 可选的 ProviderResolver 实例，默认使用全局单例
        """
        self._resolver = resolver or provider_resolver
        self._cache = CapabilityCache.get_instance()
        self._providers = {
            'anthropic': self._resolve_anthropic,
            'openai': self._resolve_openai,
            'bedrock': self._resolve_bedrock,
            'vertex': self._resolve_vertex,
        }
        # 保存切换 Provider 前的环境变量（用于恢复）
        self._saved_env: Optional[dict] = None

    async def resolve_provider(
        self, model: str, explicit_provider: Optional[str] = None
    ) -> dict:
        """解析模型对应的 Provider 配置

        解析优先级：
        1. 从缓存读取
        2. 从模型名推断 provider
        3. 从环境变量解析凭证
        4. 凭证隔离：切换时只保留目标 Provider 的变量

        Args:
            model: 模型标识符
            explicit_provider: 显式指定的 provider

        Returns:
            Provider 配置字典，包含凭证和环境信息
        """
        # 使用 resolver 确定 provider
        provider_name = self._resolver.resolve(model, explicit_provider)

        # 执行凭证隔离
        self._saved_env = self._resolver.cleanup_env_for_provider(provider_name)

        # 调用对应 provider 的解析函数
        if provider_name in self._providers:
            config = self._providers[provider_name]()
            config['provider_name'] = provider_name
            return config

        # 默认返回 anthropic 配置
        return self._resolve_anthropic()

    async def get_capability(self, model: str) -> ModelCapability:
        """获取模型能力（含缓存）

        首次调用会查询能力，之后从缓存返回。

        Args:
            model: 模型标识符

        Returns:
            模型能力描述对象
        """
        # 先从缓存读取
        cached = self._cache.get(model)
        if cached:
            log.debug(f"Capability cache hit: {model}")
            return cached

        # 缓存未命中，查询能力
        log.debug(f"Capability cache miss: {model}")
        capability = await self._fetch_capability(model)

        # 存入缓存
        self._cache.set(model, capability)

        return capability

    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """统一调用入口

        根据模型自动选择对应的 Provider 并调用其 chat completion 接口。

        Args:
            model: 模型标识符
            messages: 消息列表
            **kwargs: 额外参数（如 stream, temperature, max_tokens 等）

        Returns:
            API 响应字典
        """
        # 解析 provider 并执行凭证隔离
        provider_config = await self.resolve_provider(model)

        # 根据 provider 调用对应的 chat completion
        provider_name = provider_config.get('provider_name', 'anthropic')

        if provider_name == 'anthropic':
            return await self._anthropic_completion(model, messages, provider_config, **kwargs)
        elif provider_name == 'openai':
            return await self._openai_completion(model, messages, provider_config, **kwargs)
        elif provider_name == 'bedrock':
            return await self._bedrock_completion(model, messages, provider_config, **kwargs)
        elif provider_name == 'vertex':
            return await self._vertex_completion(model, messages, provider_config, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    def _resolve_anthropic(self) -> dict:
        """解析 Anthropic Provider 配置

        从环境变量获取：
        - ANTHROPIC_API_KEY: API 密钥
        - ANTHROPIC_API_BASE: API 基础 URL（可选）
        - ANTHROPIC_API_VERSION: API 版本（可选）
        """
        return {
            'provider_name': 'anthropic',
            'api_key': os.environ.get('ANTHROPIC_API_KEY', ''),
            'base_url': os.environ.get('ANTHROPIC_API_BASE', 'https://api.anthropic.com'),
            'api_version': os.environ.get('ANTHROPIC_API_VERSION', '2023-06-01'),
        }

    def _resolve_openai(self) -> dict:
        """解析 OpenAI Provider 配置

        从环境变量获取：
        - OPENAI_API_KEY: API 密钥
        - OPENAI_API_BASE: API 基础 URL（可选）
        - OPENAI_ORG_ID: 组织 ID（可选）
        """
        return {
            'provider_name': 'openai',
            'api_key': os.environ.get('OPENAI_API_KEY', ''),
            'base_url': os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1'),
            'org_id': os.environ.get('OPENAI_ORG_ID', ''),
        }

    def _resolve_bedrock(self) -> dict:
        """解析 AWS Bedrock Provider 配置

        从环境变量获取：
        - AWS_ACCESS_KEY_ID: AWS 访问密钥
        - AWS_SECRET_ACCESS_KEY: AWS 秘密密钥
        - AWS_REGION: AWS 区域
        """
        return {
            'provider_name': 'bedrock',
            'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID', ''),
            'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
            'aws_region': os.environ.get('AWS_REGION', 'us-east-1'),
        }

    def _resolve_vertex(self) -> dict:
        """解析 Google Vertex Provider 配置

        从环境变量获取：
        - VERTEX_PROJECT: GCP 项目 ID
        - VERTEX_LOCATION: GCP 区域（可选，默认 us-central1）
        """
        return {
            'provider_name': 'vertex',
            'project': os.environ.get('VERTEX_PROJECT', ''),
            'location': os.environ.get('VERTEX_LOCATION', 'us-central1'),
        }

    async def _fetch_capability(self, model: str) -> ModelCapability:
        """查询模型能力（网络请求）

        这里应该调用各 Provider 的 API 获取模型能力。
        当前实现使用默认值，实际使用时应该替换为真实 API 调用。

        Args:
            model: 模型标识符

        Returns:
            模型能力描述对象
        """
        # 确定 provider
        provider_name = self._resolver.resolve(model)

        # 根据模型名设置默认能力
        capability = self._get_default_capability(model, provider_name)

        return capability

    def _get_default_capability(self, model: str, provider: str) -> ModelCapability:
        """获取模型的默认能力

        Args:
            model: 模型标识符
            provider: Provider 名称

        Returns:
            模型能力描述对象
        """
        # Anthropic 模型默认值
        anthropic_defaults = {
            'max_tokens': 4096,
            'supports_streaming': True,
            'supports_vision': True,
            'supports_function_calling': True,
        }

        # OpenAI 模型默认值
        openai_defaults = {
            'max_tokens': 4096,
            'supports_streaming': True,
            'supports_vision': True,
            'supports_function_calling': True,
        }

        # 根据 provider 选择默认值
        if provider == 'anthropic':
            defaults = anthropic_defaults
        elif provider == 'openai':
            defaults = openai_defaults
        else:
            defaults = {
                'max_tokens': 4096,
                'supports_streaming': True,
                'supports_vision': False,
                'supports_function_calling': False,
            }

        return ModelCapability(
            model_id=model,
            provider=provider,
            **defaults,
        )

    async def _anthropic_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        config: dict,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Anthropic Chat Completion 调用

        Args:
            model: 模型标识符
            messages: 消息列表
            config: Provider 配置
            **kwargs: 额外参数

        Returns:
            API 响应字典
        """
        # 这里应该实现真实的 Anthropic API 调用
        # 当前返回模拟响应
        return {
            'provider': 'anthropic',
            'model': model,
            'message': {'role': 'assistant', 'content': 'Mock response'},
            'usage': {'input_tokens': 0, 'output_tokens': 0},
        }

    async def _openai_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        config: dict,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """OpenAI Chat Completion 调用

        Args:
            model: 模型标识符
            messages: 消息列表
            config: Provider 配置
            **kwargs: 额外参数

        Returns:
            API 响应字典
        """
        # 这里应该实现真实的 OpenAI API 调用
        return {
            'provider': 'openai',
            'model': model,
            'message': {'role': 'assistant', 'content': 'Mock response'},
            'usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
        }

    async def _bedrock_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        config: dict,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """AWS Bedrock Chat Completion 调用

        Args:
            model: 模型标识符
            messages: 消息列表
            config: Provider 配置
            **kwargs: 额外参数

        Returns:
            API 响应字典
        """
        # 这里应该实现真实的 Bedrock API 调用
        return {
            'provider': 'bedrock',
            'model': model,
            'message': {'role': 'assistant', 'content': 'Mock response'},
            'usage': {'input_tokens': 0, 'output_tokens': 0},
        }

    async def _vertex_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        config: dict,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Google Vertex Chat Completion 调用

        Args:
            model: 模型标识符
            messages: 消息列表
            config: Provider 配置
            **kwargs: 额外参数

        Returns:
            API 响应字典
        """
        # 这里应该实现真实的 Vertex API 调用
        return {
            'provider': 'vertex',
            'model': model,
            'message': {'role': 'assistant', 'content': 'Mock response'},
            'usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
        }

    def restore_env(self) -> None:
        """恢复切换 Provider 前保存的环境变量"""
        if self._saved_env:
            self._resolver.restore_env(self._saved_env)
            self._saved_env = None

    def clear_cache(self, model: Optional[str] = None) -> None:
        """清除能力缓存

        Args:
            model: 如果指定，只清除该模型；否则清除所有
        """
        self._cache.invalidate(model)


# 全局单例
model_gateway = ModelGateway()