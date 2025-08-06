"""
GoGather Agent SDK

A Python SDK for building agents that integrate with GoGather WebSocket system.
"""

from .agent import (
    BaseAgent,
    AgentContext,
    UserContext,
    ChatContext,
    MessageContext,
    AgentResponse,
    AgentError
)
from .client import AgentClient, run_agent
from .auth import SimpleAuth

__version__ = "0.0.6.7"

__all__ = [
    # Core classes
    "BaseAgent",
    "AgentClient",
    "SimpleAuth",
    
    # Context models
    "AgentContext",
    "UserContext", 
    "ChatContext",
    "MessageContext",
    
    # Helper classes
    "AgentResponse",
    "AgentError",
    
    # Convenience functions
    "run_agent"
]