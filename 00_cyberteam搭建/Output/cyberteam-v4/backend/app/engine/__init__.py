"""Engine package - CyberTeam core orchestration engines."""

from .agent_compiler import AgentCompiler, AgentProfile
try:
    from .agent_compiler import agent_compiler
except ImportError:
    agent_compiler = None

from .model_gateway import ModelGateway
try:
    from .model_gateway import model_gateway
except ImportError:
    model_gateway = None

from .event_bus import EventBus, Event, EventTypes
try:
    from .event_bus import event_bus
except ImportError:
    event_bus = None

from .swarm_orchestrator import SwarmOrchestrator
from .thinking_injector import ThinkingInjector

__all__ = [
    # Agent compiler
    "AgentCompiler",
    "AgentProfile",
    "agent_compiler",
    # Model gateway
    "ModelGateway",
    "model_gateway",
    # Event bus
    "EventBus",
    "Event",
    "EventTypes",
    "event_bus",
    # Swarm orchestrator
    "SwarmOrchestrator",
    # Thinking injector
    "ThinkingInjector",
]
