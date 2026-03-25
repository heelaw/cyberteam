#!/usr/bin/env python3
"""
CyberTeam V4 - Mailbox 消息系统
实现 Agent 间消息传递
"""

import json
import time
import uuid
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import asdict

from .models import TeamMessage, MessageType


# 默认消息存储路径
DEFAULT_MAILBOX_DIR = Path.home() / ".cyberteam" / "teams"


class MailboxManager:
    """消息箱管理器"""

    def __init__(self, team_name: str, mailbox_dir: Optional[Path] = None):
        self.team_name = team_name
        self.mailbox_dir = mailbox_dir or DEFAULT_MAILBOX_DIR / team_name / "inboxes"
        self.mailbox_dir.mkdir(parents=True, exist_ok=True)

    def _inbox_path(self, agent_name: str) -> Path:
        """获取收件箱路径"""
        return self.mailbox_dir / agent_name

    def _ensure_inbox(self, agent_name: str) -> Path:
        """确保收件箱存在"""
        inbox = self._inbox_path(agent_name)
        inbox.mkdir(parents=True, exist_ok=True)
        return inbox

    def send(
        self,
        from_agent: str,
        to: str,
        content: str,
        msg_type: MessageType = MessageType.MESSAGE
    ) -> TeamMessage:
        """
        发送消息

        Args:
            from_agent: 发送者
            to: 接收者 ("*" 表示广播)
            content: 消息内容
            msg_type: 消息类型

        Returns:
            TeamMessage
        """
        msg_id = str(uuid.uuid4())[:12]
        msg = TeamMessage(
            msg_id=msg_id,
            msg_type=msg_type,
            from_agent=from_agent,
            to=to,
            content=content
        )

        if to == "*":
            # 广播 - 发送给所有人
            # 需要知道所有成员，这里简化处理，存到 broadcast 目录
            broadcast_dir = self._ensure_inbox("_broadcast")
            self._write_msg(broadcast_dir, msg)
        else:
            inbox = self._ensure_inbox(to)
            self._write_msg(inbox, msg)

        return msg

    def _write_msg(self, inbox: Path, msg: TeamMessage) -> None:
        """写入消息"""
        msg_file = inbox / f"msg-{int(time.time()*1000)}-{msg.msg_id}.json"
        tmp_file = msg_file.with_suffix(".tmp")

        tmp_file.write_text(json.dumps(msg.to_dict(), indent=2, ensure_ascii=False))
        tmp_file.replace(msg_file)

    def receive(self, agent_name: str, limit: int = 10, consume: bool = True) -> List[TeamMessage]:
        """
        接收消息

        Args:
            agent_name: 接收者名称
            limit: 最大数量
            consume: 是否消费 (删除已读消息)

        Returns:
            List[TeamMessage]
        """
        inbox = self._inbox_path(agent_name)
        if not inbox.exists():
            return []

        messages = []
        msg_files = sorted(inbox.glob("msg-*.json"))[:limit]

        for msg_file in msg_files:
            try:
                data = json.loads(msg_file.read_text())
                msg = TeamMessage.from_dict(data)

                # 检查是否已消费
                if msg_file.suffix == ".consumed":
                    continue

                messages.append(msg)

                # 消费消息
                if consume:
                    consumed_file = msg_file.with_suffix(".consumed")
                    msg_file.rename(consumed_file)

            except (json.JSONDecodeError, KeyError):
                continue

        return messages

    def count(self, agent_name: str) -> int:
        """获取未读消息数量"""
        inbox = self._inbox_path(agent_name)
        if not inbox.exists():
            return 0

        return len([
            f for f in inbox.glob("msg-*.json")
            if f.suffix != ".consumed"
        ])

    def list_inboxes(self) -> List[str]:
        """列出所有收件箱"""
        if not self.mailbox_dir.exists():
            return []

        return [
            d.name for d in self.mailbox_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        ]

    def clear(self, agent_name: str) -> int:
        """清空收件箱"""
        inbox = self._inbox_path(agent_name)
        if not inbox.exists():
            return 0

        count = len(list(inbox.glob("msg-*.json")))
        for f in inbox.glob("msg-*.json"):
            f.unlink()

        return count

    def peek(self, agent_name: str, limit: int = 10) -> List[TeamMessage]:
        """查看消息 (不消费)"""
        return self.receive(agent_name, limit=limit, consume=False)


class Inbox:
    """收件箱便捷类"""

    def __init__(self, team_name: str, agent_name: str):
        self.manager = MailboxManager(team_name)
        self.agent_name = agent_name

    def send_to(self, to: str, content: str) -> TeamMessage:
        """发送消息"""
        return self.manager.send(self.agent_name, to, content)

    def receive(self, limit: int = 10) -> List[TeamMessage]:
        """接收消息"""
        return self.manager.receive(self.agent_name, limit=limit)

    def count(self) -> int:
        """未读数量"""
        return self.manager.count(self.agent_name)

    def peek(self, limit: int = 10) -> List[TeamMessage]:
        """查看消息"""
        return self.manager.peek(self.agent_name, limit=limit)

    def clear(self) -> int:
        """清空"""
        return self.manager.clear(self.agent_name)


def main():
    """测试"""
    print("Mailbox 测试")
    print("=" * 50)

    manager = MailboxManager("test-team")

    # 发送消息
    print("\n发送消息:")
    msg1 = manager.send("leader", "worker-a", "你好 worker-a!")
    print(f"  leader -> worker-a: {msg1.content}")

    msg2 = manager.send("worker-a", "leader", "任务完成!")
    print(f"  worker-a -> leader: {msg2.content}")

    msg3 = manager.send("leader", "*", "广播: 所有人注意!")
    print(f"  leader -> *: {msg3.content}")

    # 接收消息
    print("\n接收消息 (worker-a):")
    messages = manager.receive("worker-a")
    for msg in messages:
        print(f"  from {msg.from_agent}: {msg.content}")

    # 统计
    print(f"\nworker-a 未读: {manager.count('worker-a')}")
    print(f"leader 未读: {manager.count('leader')}")


if __name__ == "__main__":
    main()
