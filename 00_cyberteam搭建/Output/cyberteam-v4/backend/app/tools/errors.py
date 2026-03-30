"""苏格拉底式错误提示系统。

本模块提供两类异常：
1. ToolValidationError - 参数验证失败，带苏格拉底式追问
2. ToolExecutionError - 工具执行失败

核心设计理念：
- 当用户传错参数时，不是简单报错，而是追问"你想用的是不是 XXX？"
- 帮助用户发现参数名拼写错误、类型错误等问题
- 类似苏格拉底式提问：通过追问引导用户发现正确答案
"""

from __future__ import annotations

from typing import Optional
from difflib import get_close_matches


class ToolValidationError(Exception):
    """工具参数验证失败 - 带苏格拉底式追问。

    当用户传入的参数不符合 Pydantic 模型定义时，会抛出此异常。
    异常消息包含：
    1. 具体哪些参数错了
    2. 错误的原因
    3. 相似参数推荐（如果找到的话）
    4. 参数签名参考

    使用示例：
        try:
            validated = params_class(**user_input)
        except ValidationError as e:
            raise ToolValidationError(
                tool_name="add",
                errors=e.errors(),
                similar_params=[("a", 0.8), ("b", 0.6)]
            )
    """

    def __init__(
        self,
        tool_name: str,
        errors: list[dict],
        similar_params: Optional[list[tuple[str, float]]] = None,
        expected_signature: Optional[str] = None
    ):
        """
        Args:
            tool_name: 工具名称
            errors: Pydantic ValidationError.errors() 返回的错误列表
            similar_params: 相似参数列表 [(参数名, 相似度), ...]
            expected_signature: 期望的参数签名
        """
        self.tool_name = tool_name
        self.errors = errors
        self.similar_params = similar_params or []
        self.expected_signature = expected_signature

    def get_human_message(self) -> str:
        """生成友好的错误消息 - 苏格拉底式追问风格。

        消息结构：
        1. 错误标题
        2. 具体参数错误（最多3个）
        3. 相似参数推荐
        4. 参数签名参考
        5. 追问式建议

        Returns:
            格式化的错误消息字符串
        """
        lines = [
            f"[工具调用错误] `{self.tool_name}`",
            "",
        ]

        # 第一部分：列出具体的参数错误
        lines.append("[参数错误详情]")
        for err in self.errors[:3]:  # 最多显示3个错误
            loc = " → ".join(str(l) for l in err.get('loc', []))
            msg = err.get('msg', '')
            inp = err.get('input', '')
            input_type = err.get('type', '')

            lines.append(f"  参数 `{loc}`: {msg}")
            if inp is not None and str(inp) not in ('None', ''):
                inp_str = str(inp)
                if len(inp_str) > 50:
                    inp_str = inp_str[:50] + "..."
                lines.append(f"    你传的值: {inp_str}")
            if input_type:
                lines.append(f"    错误类型: {input_type}")

        lines.append("")

        # 第二部分：苏格拉底追问 - 相似参数
        if self.similar_params:
            lines.append("[苏格拉底追问] 你是否想使用以下相似参数？")
            for param, score in self.similar_params[:3]:
                emoji = "🔸" if score > 0.8 else "○"
                lines.append(f"  {emoji} `{param}` (相似度: {score:.0%})")
            lines.append("")
            lines.append("提示: 请检查参数名拼写是否正确。")
            lines.append("")

        # 第三部分：期望的参数签名
        if self.expected_signature:
            lines.append(f"[期望类型] {self.expected_signature}")

        # 第四部分：追问式建议
        lines.append("")
        lines.append("[苏格拉底式追问] 🤔")
        lines.append("  1. 你确定这个参数名是正确的吗？")
        lines.append("  2. 传入的值类型是否匹配？（如：需要 int 却传了 string）")
        lines.append("  3. 是否缺少必需参数？")
        lines.append("")
        lines.append(f"[说明] 工具定义可能已更新，请检查参数签名。")

        return "\n".join(lines)

    def get_short_message(self) -> str:
        """获取简短错误消息（仅参数错误列表）。

        Returns:
            简短错误消息
        """
        lines = [f"[{self.tool_name}] 参数错误:"]
        for err in self.errors[:2]:
            loc = " → ".join(str(l) for l in err.get('loc', []))
            msg = err.get('msg', '')
            lines.append(f"  {loc}: {msg}")
        return "\n".join(lines)

    def __str__(self) -> str:
        """返回完整的人类可读错误消息。"""
        return self.get_human_message()

    def __repr__(self) -> str:
        """返回结构化表示。"""
        return (
            f"ToolValidationError(tool_name={self.tool_name!r}, "
            f"errors={len(self.errors)}, "
            f"similar_params={len(self.similar_params)})"
        )

    def to_dict(self) -> dict:
        """转换为字典格式，便于日志记录。"""
        return {
            'type': 'ToolValidationError',
            'tool_name': self.tool_name,
            'error_count': len(self.errors),
            'errors': self.errors,
            'similar_params': [
                {'param': p, 'score': s}
                for p, s in self.similar_params
            ]
        }


class ToolExecutionError(Exception):
    """工具执行失败。

    当工具本身运行过程中发生错误时抛出。
    与 ToolValidationError（参数错误）不同，这是运行时错误。
    """

    def __init__(self, tool_name: str, reason: str):
        """
        Args:
            tool_name: 工具名称
            reason: 失败原因描述
        """
        self.tool_name = tool_name
        self.reason = reason
        super().__init__(f"[工具执行错误] {tool_name}: {reason}")

    def __repr__(self) -> str:
        """返回结构化表示。"""
        return f"ToolExecutionError(tool_name={self.tool_name!r}, reason={self.reason!r})"

    def to_dict(self) -> dict:
        """转换为字典格式，便于日志记录。"""
        return {
            'type': 'ToolExecutionError',
            'tool_name': self.tool_name,
            'reason': self.reason
        }


class ToolNotFoundError(Exception):
    """工具未找到。"""

    def __init__(self, tool_name: str, available_tools: Optional[list[str]] = None):
        """
        Args:
            tool_name: 尝试调用的工具名称
            available_tools: 可用工具列表（用于提示）
        """
        self.tool_name = tool_name
        self.available_tools = available_tools or []

        # 构建错误消息
        msg = f"[工具未找到] `{tool_name}`"
        if available_tools:
            # 尝试找相似名称
            similar = get_close_matches(tool_name, available_tools, n=3, cutoff=0.3)
            if similar:
                msg += f"\n\n你是否想使用以下工具？"
                for t in similar:
                    msg += f"\n  - `{t}`"
            else:
                msg += f"\n\n可用工具: {', '.join(available_tools[:10])}"
        super().__init__(msg)

    def to_dict(self) -> dict:
        """转换为字典格式。"""
        return {
            'type': 'ToolNotFoundError',
            'tool_name': self.tool_name,
            'available_tools': self.available_tools
        }


class ToolRegistrationError(Exception):
    """工具注册失败。"""

    def __init__(self, tool_name: str, reason: str):
        """
        Args:
            tool_name: 尝试注册的工具名称
            reason: 注册失败原因
        """
        self.tool_name = tool_name
        self.reason = reason
        super().__init__(f"[工具注册失败] {tool_name}: {reason}")