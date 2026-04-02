"""ModelGateway 测试套件"""
import os
import pytest
import time

# 测试用的 imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.model_gateway import ModelGateway
from app.core.provider_resolver import ProviderResolver, MANAGED_ENV_KEYS
from app.core.capability_cache import CapabilityCache, ModelCapability


class TestProviderResolver:
    """ProviderResolver 测试"""

    def setup_method(self):
        """每个测试方法前重置环境变量"""
        # 保存原始环境变量
        self._orig_env = {}
        for key in MANAGED_ENV_KEYS:
            if key in os.environ:
                self._orig_env[key] = os.environ[key]
                del os.environ[key]

    def teardown_method(self):
        """每个测试方法后恢复环境变量"""
        for key in MANAGED_ENV_KEYS:
            if key in os.environ:
                del os.environ[key]
        for key, value in self._orig_env.items():
            os.environ[key] = value

    def test_resolve_explicit_provider(self):
        """测试显式 provider 参数"""
        resolver = ProviderResolver()
        result = resolver.resolve('claude-opus-4-6', explicit_provider='openai')
        assert result == 'openai'

    def test_resolve_anthropic_model(self):
        """测试 Anthropic 模型推断"""
        resolver = ProviderResolver()

        assert resolver.resolve('claude-opus-4-6') == 'anthropic'
        assert resolver.resolve('claude-sonnet-4-6') == 'anthropic'
        assert resolver.resolve('claude-haiku-4-5') == 'anthropic'
        assert resolver.resolve('sonnet-4-6') == 'anthropic'
        assert resolver.resolve('opus-4-6') == 'anthropic'

    def test_resolve_openai_model(self):
        """测试 OpenAI 模型推断"""
        resolver = ProviderResolver()

        assert resolver.resolve('gpt-4o') == 'openai'
        assert resolver.resolve('gpt-4-turbo') == 'openai'
        assert resolver.resolve('o1-preview') == 'openai'
        assert resolver.resolve('o3-mini') == 'openai'

    def test_resolve_bedrock_model(self):
        """测试 Bedrock 模型推断"""
        resolver = ProviderResolver()

        assert resolver.resolve('bedrock/anthropic/claude-v3') == 'bedrock'

    def test_resolve_vertex_model(self):
        """测试 Vertex 模型推断"""
        resolver = ProviderResolver()

        assert resolver.resolve('vertex/gemini-2.0-flash') == 'vertex'
        assert resolver.resolve('gemini-1.5-pro') == 'vertex'

    def test_resolve_from_env(self):
        """测试从环境变量推断 Provider"""
        resolver = ProviderResolver()

        # 设置 Anthropic 凭证
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        assert resolver.resolve('unknown-model') == 'anthropic'

    def test_resolve_default(self):
        """测试默认 Provider"""
        resolver = ProviderResolver()
        # 无任何信息时返回默认
        result = resolver.resolve('completely-unknown-model')
        assert result == 'anthropic'

    def test_cleanup_env_for_provider(self):
        """测试凭证隔离"""
        resolver = ProviderResolver()

        # 设置多 Provider 凭证
        os.environ['ANTHROPIC_API_KEY'] = 'anthropic-key'
        os.environ['OPENAI_API_KEY'] = 'openai-key'
        os.environ['VERTEX_PROJECT'] = 'vertex-project'

        # 切换到 OpenAI，验证 Anthropic 和 Vertex 凭证被清理
        saved = resolver.cleanup_env_for_provider('openai')

        assert 'ANTHROPIC_API_KEY' not in os.environ
        assert 'VERTEX_PROJECT' not in os.environ
        assert os.environ.get('OPENAI_API_KEY') == 'openai-key'

        # 验证保存的内容包含被清理的变量
        assert 'ANTHROPIC_API_KEY' in saved
        assert 'VERTEX_PROJECT' in saved

    def test_restore_env(self):
        """测试环境变量恢复"""
        resolver = ProviderResolver()

        # 设置多 Provider 凭证
        os.environ['ANTHROPIC_API_KEY'] = 'anthropic-key'
        os.environ['OPENAI_API_KEY'] = 'openai-key'

        # 切换到 OpenAI
        saved = resolver.cleanup_env_for_provider('openai')

        # 恢复
        resolver.restore_env(saved)

        assert os.environ.get('ANTHROPIC_API_KEY') == 'anthropic-key'
        assert os.environ.get('OPENAI_API_KEY') == 'openai-key'


class TestCapabilityCache:
    """CapabilityCache 测试"""

    def setup_method(self):
        """每个测试前重置单例"""
        CapabilityCache.reset_instance()

    def teardown_method(self):
        """每个测试后重置单例"""
        CapabilityCache.reset_instance()

    def test_singleton(self):
        """测试单例模式"""
        cache1 = CapabilityCache.get_instance()
        cache2 = CapabilityCache.get_instance()
        assert cache1 is cache2

    def test_set_and_get(self):
        """测试设置和获取缓存"""
        cache = CapabilityCache.get_instance()
        cap = ModelCapability(
            model_id='claude-opus-4-6',
            provider='anthropic',
            max_tokens=4096,
            supports_streaming=True,
        )

        cache.set('claude-opus-4-6', cap)
        result = cache.get('claude-opus-4-6')

        assert result is not None
        assert result.model_id == 'claude-opus-4-6'
        assert result.provider == 'anthropic'
        assert result.supports_streaming is True

    def test_cache_miss(self):
        """测试缓存未命中"""
        cache = CapabilityCache.get_instance()
        result = cache.get('non-existent-model')
        assert result is None

    def test_cache_expiry(self):
        """测试缓存过期"""
        # 创建 TTL 为 1 秒的缓存
        cache = CapabilityCache(ttl_seconds=1)
        CapabilityCache._instance = cache

        cap = ModelCapability(
            model_id='test-model',
            provider='test',
            max_tokens=100,
        )
        cache.set('test-model', cap)

        # 立即获取应该命中
        assert cache.get('test-model') is not None

        # 等待过期
        time.sleep(1.1)

        # 过期后获取应该返回 None
        assert cache.get('test-model') is None

    def test_invalidate_single(self):
        """测试清除单个缓存"""
        cache = CapabilityCache.get_instance()

        cache.set('model-1', ModelCapability('model-1', 'test', 100))
        cache.set('model-2', ModelCapability('model-2', 'test', 100))

        cache.invalidate('model-1')

        assert cache.get('model-1') is None
        assert cache.get('model-2') is not None

    def test_invalidate_all(self):
        """测试清除所有缓存"""
        cache = CapabilityCache.get_instance()

        cache.set('model-1', ModelCapability('model-1', 'test', 100))
        cache.set('model-2', ModelCapability('model-2', 'test', 100))

        cache.invalidate()

        assert cache.get('model-1') is None
        assert cache.get('model-2') is None

    def test_ttl_remaining(self):
        """测试剩余 TTL"""
        cache = CapabilityCache(ttl_seconds=10)
        CapabilityCache._instance = cache

        cap = ModelCapability('test', 'test', 100)
        cache.set('test', cap)

        remaining = cache.get_ttl_remaining('test')
        assert remaining is not None
        assert 0 < remaining <= 10

    def test_size(self):
        """测试缓存大小"""
        cache = CapabilityCache.get_instance()

        assert cache.size() == 0

        cache.set('model-1', ModelCapability('model-1', 'test', 100))
        assert cache.size() == 1

        cache.set('model-2', ModelCapability('model-2', 'test', 100))
        assert cache.size() == 2

    def test_list_cached_models(self):
        """测试列出所有缓存的模型"""
        cache = CapabilityCache.get_instance()

        cache.set('model-a', ModelCapability('model-a', 'test', 100))
        cache.set('model-b', ModelCapability('model-b', 'test', 100))

        models = cache.list_cached_models()
        assert 'model-a' in models
        assert 'model-b' in models


class TestModelGateway:
    """ModelGateway 测试"""

    def setup_method(self):
        """每个测试前重置缓存和设置环境变量"""
        CapabilityCache.reset_instance()
        self._orig_env = {}
        for key in MANAGED_ENV_KEYS:
            if key in os.environ:
                self._orig_env[key] = os.environ[key]
                del os.environ[key]
        # 设置测试用的凭证
        os.environ['ANTHROPIC_API_KEY'] = 'test-anthropic-key'
        os.environ['OPENAI_API_KEY'] = 'test-openai-key'

    def teardown_method(self):
        """每个测试后恢复环境变量"""
        CapabilityCache.reset_instance()
        for key in MANAGED_ENV_KEYS:
            if key in os.environ:
                del os.environ[key]
        for key, value in self._orig_env.items():
            os.environ[key] = value

    @pytest.mark.asyncio
    async def test_resolve_provider_anthropic(self):
        """测试解析 Anthropic Provider"""
        gateway = ModelGateway()
        config = await gateway.resolve_provider('claude-opus-4-6')

        assert config['provider_name'] == 'anthropic'
        assert config['api_key'] == 'test-anthropic-key'

    @pytest.mark.asyncio
    async def test_resolve_provider_openai(self):
        """测试解析 OpenAI Provider"""
        gateway = ModelGateway()
        config = await gateway.resolve_provider('gpt-4o')

        assert config['provider_name'] == 'openai'
        assert config['api_key'] == 'test-openai-key'

    @pytest.mark.asyncio
    async def test_resolve_provider_explicit(self):
        """测试显式指定 Provider"""
        gateway = ModelGateway()
        config = await gateway.resolve_provider('claude-opus-4-6', explicit_provider='openai')

        assert config['provider_name'] == 'openai'

    @pytest.mark.asyncio
    async def test_get_capability_cached(self):
        """测试获取模型能力（缓存命中）"""
        gateway = ModelGateway()

        # 第一次获取
        cap1 = await gateway.get_capability('claude-opus-4-6')
        assert cap1.model_id == 'claude-opus-4-6'
        assert cap1.provider == 'anthropic'

        # 第二次获取应该从缓存返回
        cap2 = await gateway.get_capability('claude-opus-4-6')
        assert cap2 is cap1  # 同一个对象

    @pytest.mark.asyncio
    async def test_get_capability_cache_miss(self):
        """测试获取模型能力（缓存未命中）"""
        gateway = ModelGateway()

        cap = await gateway.get_capability('claude-opus-4-6')

        assert isinstance(cap, ModelCapability)
        assert cap.model_id == 'claude-opus-4-6'
        assert cap.provider == 'anthropic'
        assert cap.max_tokens == 4096
        assert cap.supports_streaming is True

    @pytest.mark.asyncio
    async def test_chat_completion_anthropic(self):
        """测试 Anthropic Chat Completion"""
        gateway = ModelGateway()

        messages = [{'role': 'user', 'content': 'Hello'}]
        response = await gateway.chat_completion('claude-opus-4-6', messages)

        assert response['provider'] == 'anthropic'
        assert response['model'] == 'claude-opus-4-6'

    @pytest.mark.asyncio
    async def test_chat_completion_openai(self):
        """测试 OpenAI Chat Completion"""
        gateway = ModelGateway()

        messages = [{'role': 'user', 'content': 'Hello'}]
        response = await gateway.chat_completion('gpt-4o', messages)

        assert response['provider'] == 'openai'
        assert response['model'] == 'gpt-4o'

    def test_clear_cache(self):
        """测试清除缓存"""
        gateway = ModelGateway()

        # 设置缓存
        gateway._cache.set('test', ModelCapability('test', 'test', 100))
        assert gateway._cache.get('test') is not None

        # 清除单个
        gateway.clear_cache('test')
        assert gateway._cache.get('test') is None

    def test_clear_cache_all(self):
        """测试清除所有缓存"""
        gateway = ModelGateway()

        gateway._cache.set('model-1', ModelCapability('model-1', 'test', 100))
        gateway._cache.set('model-2', ModelCapability('model-2', 'test', 100))

        gateway.clear_cache()

        assert gateway._cache.get('model-1') is None
        assert gateway._cache.get('model-2') is None

    def test_provider_env_keys(self):
        """测试获取 Provider 环境变量"""
        resolver = ProviderResolver()

        anthropic_keys = resolver.get_provider_env_keys('anthropic')
        assert 'ANTHROPIC_API_KEY' in anthropic_keys
        assert 'ANTHROPIC_API_BASE' in anthropic_keys

        openai_keys = resolver.get_provider_env_keys('openai')
        assert 'OPENAI_API_KEY' in openai_keys
        assert 'OPENAI_ORG_ID' in openai_keys


if __name__ == '__main__':
    pytest.main([__file__, '-v'])