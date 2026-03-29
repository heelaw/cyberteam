"""Event bus for CyberTeam engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Any, Optional, Union
from asyncio import Queue
import asyncio


class EventType(str, Enum):
    """Predefined event types."""
    # Agent events
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    AGENT_MESSAGE = "agent.message"

    # Chat events
    CHAT_CREATED = "chat.created"
    CHAT_MESSAGE = "chat.message"
    CHAT_CLOSED = "chat.closed"

    # Project events
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_COMPLETED = "project.completed"

    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_INFO = "system.info"

    # Thinking events
    THINKING_STARTED = "thinking.started"
    THINKING_INJECTED = "thinking.injected"
    THINKING_COMPLETED = "thinking.completed"


@dataclass
class Event:
    """Event dataclass."""
    type: EventType
    data: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "system"
    correlation_id: Optional[str] = None


class EventBus:
    """Event bus for publish-subscribe messaging."""

    def __init__(self):
        self._subscribers: dict[EventType, list[Callable]] = {}
        self._middleware: list[Callable[[Event], Optional[Event]]] = []
        self._event_queue: Queue = Queue()

    def on(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def off(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)

    def middleware(self, middleware: Callable[[Event], Event | None]) -> None:
        """Add middleware to process events before handlers."""
        self._middleware.append(middleware)

    def emit(self, event: Event) -> None:
        """Emit an event to all subscribers."""
        # Apply middleware
        processed_event = event
        for mw in self._middleware:
            result = mw(processed_event)
            if result is None:
                return  # Middleware filtered the event
            processed_event = result

        # Dispatch to handlers
        handlers = self._subscribers.get(event.type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(processed_event))
                else:
                    handler(processed_event)
            except Exception as e:
                print(f"Error in event handler: {e}")

    async def emit_async(self, event: Event) -> None:
        """Emit an event asynchronously."""
        # Apply middleware
        processed_event = event
        for mw in self._middleware:
            result = mw(processed_event)
            if result is None:
                return
            processed_event = result

        # Dispatch to handlers
        handlers = self._subscribers.get(event.type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(processed_event)
                else:
                    handler(processed_event)
            except Exception as e:
                print(f"Error in event handler: {e}")

    def clear(self) -> None:
        """Clear all subscribers and middleware."""
        self._subscribers.clear()
        self._middleware.clear()


# Global event bus instance
event_bus = EventBus()
