"""
Claude Code CLI Integration — 使用本地 Claude Code CLI 作为 AI 引擎。
参考 CodePilot-0.41.0 的 claude-client.ts 实现。

通过 subprocess 调用 `claude --print --output-format stream-json`
解析 JSON 流并转发为 SSE 事件。

v2: 支持 system_prompt、对话历史（messages）、指定 model、多轮 session。
"""
from __future__ import annotations

import asyncio
import json
import shutil
import os
from typing import AsyncIterator, Sequence


def find_claude_binary() -> str | None:
    """查找 Claude Code CLI 可执行文件路径。"""
    return shutil.which("claude")


def _build_conversation_prompt(
    prompt: str,
    messages: Sequence[dict] | None = None,
) -> str:
    """将对话历史与当前 prompt 组合为 Claude CLI 的 stdin 输入。

    Claude Code CLI 的 -p 模式通过 stdin 接收 prompt 文本。
    为了传递对话历史，我们在 prompt 前拼接历史消息作为上下文。

    Args:
        prompt: 当前用户输入
        messages: 对话历史列表，每条 {"role": "user"|"assistant", "content": "..."}

    Returns:
        组合后的完整 prompt 字符串
    """
    if not messages:
        return prompt

    parts: list[str] = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            parts.append(f"<human>\n{content}\n</human>")
        elif role == "assistant":
            parts.append(f"<assistant>\n{content}\n</assistant>")
        elif role == "system":
            parts.append(f"<system>\n{content}\n</system>")

    # 在历史消息后追加当前 prompt
    parts.append(f"<human>\n{prompt}\n</human>")

    return "\n\n".join(parts)


async def stream_claude_response(
    prompt: str,
    *,
    session_id: str | None = None,
    model: str | None = None,
    system_prompt: str | None = None,
    messages: Sequence[dict] | None = None,
    working_directory: str | None = None,
    max_turns: int = 1,
) -> AsyncIterator[dict]:
    """
    调用 Claude Code CLI 并流式返回 JSON 事件。

    Claude CLI --output-format stream-json 每行输出一个 JSON：
    - {"type":"system","subtype":"init",...}  — 初始化（model, tools, session_id）
    - {"type":"assistant","message":{...}}     — 助手回复（content blocks）
    - {"type":"result",...}                    — 最终结果（usage, cost）

    Args:
        prompt: 当前用户输入
        session_id: Claude Code 会话 ID（用于 --resume 多轮对话）
        model: 模型名称（如 claude-sonnet-4-20250514）
        system_prompt: 系统提示词（传给 --system-prompt 参数）
        messages: 对话历史列表（拼接为上下文传给 stdin）
        working_directory: CLI 工作目录
        max_turns: 最大对话轮次

    Yields:
        dict: 统一格式的事件
    """
    claude_path = find_claude_binary()
    if not claude_path:
        yield {
            "type": "error",
            "data": "Claude Code CLI 未找到。请先安装: npm install -g @anthropic-ai/claude-code",
        }
        yield {"type": "done", "data": ""}
        return

    # 构建命令参数
    cmd = [
        claude_path,
        "-p",                           # --print 非交互模式
        "--output-format", "stream-json",
        "--verbose",                    # stream-json 必须 --verbose
        "--max-turns", str(max_turns),
    ]

    # 指定模型
    if model:
        cmd.extend(["--model", model])

    # 系统提示词
    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])

    # 多轮对话：使用 --resume 续接已有会话
    if session_id:
        cmd.extend(["--resume", session_id])

    # 环境变量 — 清理嵌套检测
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)

    # 组合 prompt（拼接对话历史）
    full_prompt = _build_conversation_prompt(prompt, messages)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_directory or os.getcwd(),
            env=env,
        )

        # 写入完整 prompt 到 stdin
        proc.stdin.write(full_prompt.encode("utf-8"))
        proc.stdin.close()

        # 逐行读取 stdout 的 JSON 流
        buffer = ""
        while True:
            chunk = await proc.stdout.read(4096)
            if not chunk:
                break

            buffer += chunk.decode("utf-8", errors="replace")

            # 按行分割处理 JSON
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                event_type = event.get("type", "")

                # ── init 事件：session_id, model, tools ──
                if event_type == "system" and event.get("subtype") == "init":
                    yield {
                        "type": "status",
                        "session_id": event.get("session_id"),
                        "model": event.get("model", "unknown"),
                        "tools": event.get("tools", []),
                    }

                # ── assistant 事件：content blocks（text / thinking） ──
                elif event_type == "assistant":
                    message = event.get("message", {})
                    content_blocks = message.get("content", [])
                    for block in content_blocks:
                        block_type = block.get("type", "")
                        if block_type == "text":
                            yield {
                                "type": "text",
                                "data": block.get("text", ""),
                            }
                        elif block_type == "thinking":
                            yield {
                                "type": "thinking",
                                "data": block.get("thinking", ""),
                            }
                        elif block_type == "tool_use":
                            yield {
                                "type": "tool_use",
                                "data": json.dumps({
                                    "name": block.get("name"),
                                    "input": block.get("input"),
                                }, ensure_ascii=False),
                            }

                # ── result 事件：最终结果 + usage ──
                elif event_type == "result":
                    usage = event.get("usage", {})
                    model_usage = event.get("modelUsage", {})
                    # 取第一个 model 的数据
                    first_model = next(iter(model_usage.values()), {})
                    yield {
                        "type": "result",
                        "model": event.get("modelUsage", {}),
                        "usage": {
                            "input_tokens": first_model.get("inputTokens", usage.get("input_tokens", 0)),
                            "output_tokens": first_model.get("outputTokens", usage.get("output_tokens", 0)),
                            "cost_usd": first_model.get("costUSD", 0),
                        },
                        "session_id": event.get("session_id"),
                        "duration_ms": event.get("duration_ms"),
                        "is_error": event.get("is_error", False),
                    }

        # 等待进程结束
        await proc.wait()

        # 读取 stderr 用于调试
        if proc.returncode and proc.returncode != 0:
            stderr = await proc.stderr.read()
            stderr_text = stderr.decode("utf-8", errors="replace")[:500]
            yield {
                "type": "error",
                "data": f"Claude Code CLI 错误 (exit {proc.returncode}): {stderr_text}",
            }

    except FileNotFoundError:
        yield {
            "type": "error",
            "data": "Claude Code CLI 可执行文件不存在。请安装: npm install -g @anthropic-ai/claude-code",
        }
    except Exception as e:
        yield {
            "type": "error",
            "data": f"调用 Claude Code 时发生错误: {str(e)}",
        }

    yield {"type": "done", "data": ""}


# Alias for backward compatibility
query_claude_stream = stream_claude_response
