"""Multi-model gateway for routing to different LLM providers."""
from typing import Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import httpx


class ModelType(str, Enum):
    """Model types."""
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo"
    GPT35 = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    GEMINI_PRO = "gemini-pro"
    GEMINI_ULTRA = "gemini-ultra"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    LOCAL = "local"


@dataclass
class ModelConfig:
    """Configuration for a model."""
    name: str
    provider: str
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7


class ModelGateway:
    """Gateway for routing tasks to appropriate LLM models.

    Model selection strategy based on Magic framework:
    - Complex reasoning -> Claude 3 Opus / GPT-4
    - Fast responses -> GPT-3.5 / Claude 3 Haiku
    - Code generation -> Claude 3 / GPT-4
    - Chinese content -> Qwen / DeepSeek
    """

    # Model map following Magic's routing strategy
    MODEL_MAP: dict[str, ModelConfig] = {
        "gpt-4": ModelConfig(
            name="gpt-4",
            provider="openai",
            endpoint="https://api.openai.com/v1/chat/completions",
            max_tokens=8192,
            temperature=0.7,
        ),
        "gpt-4-turbo": ModelConfig(
            name="gpt-4-turbo",
            provider="openai",
            endpoint="https://api.openai.com/v1/chat/completions",
            max_tokens=128000,
            temperature=0.7,
        ),
        "gpt-3.5-turbo": ModelConfig(
            name="gpt-3.5-turbo",
            provider="openai",
            endpoint="https://api.openai.com/v1/chat/completions",
            max_tokens=16384,
            temperature=0.7,
        ),
        "claude-3-opus": ModelConfig(
            name="claude-3-opus",
            provider="anthropic",
            endpoint="https://api.anthropic.com/v1/messages",
            max_tokens=200000,
            temperature=0.7,
        ),
        "claude-3-sonnet": ModelConfig(
            name="claude-3-sonnet",
            provider="anthropic",
            endpoint="https://api.anthropic.com/v1/messages",
            max_tokens=200000,
            temperature=0.7,
        ),
        "claude-3-haiku": ModelConfig(
            name="claude-3-haiku",
            provider="anthropic",
            endpoint="https://api.anthropic.com/v1/messages",
            max_tokens=200000,
            temperature=0.7,
        ),
        "deepseek": ModelConfig(
            name="deepseek-chat",
            provider="deepseek",
            endpoint="https://api.deepseek.com/v1/chat/completions",
            max_tokens=16384,
            temperature=0.7,
        ),
        "qwen": ModelConfig(
            name="qwen-plus",
            provider="ali",
            endpoint="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            max_tokens=8192,
            temperature=0.7,
        ),
        "gemini-pro": ModelConfig(
            name="gemini-pro",
            provider="google",
            endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            max_tokens=32768,
            temperature=0.7,
        ),
    }

    # Task type to model mapping
    TASK_MODEL_ROUTING: dict[str, list[str]] = {
        "reasoning": ["claude-3-opus", "gpt-4-turbo"],
        "coding": ["claude-3-sonnet", "gpt-4"],
        "writing": ["gpt-4-turbo", "claude-3-sonnet"],
        "fast": ["claude-3-haiku", "gpt-3.5-turbo"],
        "chinese": ["qwen", "deepseek"],
        "analysis": ["claude-3-opus", "gpt-4"],
        "creative": ["gpt-4-turbo", "claude-3-sonnet"],
        "default": ["gpt-4-turbo", "claude-3-sonnet"],
    }

    def resolve(self, task_type: str = "default", context: Optional[dict] = None) -> ModelConfig:
        """Resolve the best model for a task type.

        Args:
            task_type: Type of task (reasoning/coding/writing/fast/chinese/analysis/creative)
            context: Optional context for model selection

        Returns:
            ModelConfig for the selected model
        """
        model_list = self.TASK_MODEL_ROUTING.get(task_type, self.TASK_MODEL_ROUTING["default"])

        # Check context for preferences
        if context:
            if context.get("prefer_chinese"):
                model_list = ["qwen", "deepseek"] + model_list
            if context.get("high_quality"):
                model_list = [model_list[0]] + model_list  # Prioritize best model

        # Return first available model
        primary_model = model_list[0]
        return self.MODEL_MAP.get(primary_model, self.MODEL_MAP["gpt-4-turbo"])

    def get_model(self, model_name: str) -> Optional[ModelConfig]:
        """Get a specific model by name."""
        return self.MODEL_MAP.get(model_name)

    def list_models(self) -> list[str]:
        """List all available model names."""
        return list(self.MODEL_MAP.keys())


# Global instance
model_gateway = ModelGateway()
