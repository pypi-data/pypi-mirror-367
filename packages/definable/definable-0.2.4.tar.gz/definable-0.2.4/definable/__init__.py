"""
Definable - Infrastructure for building and deploying AI agents
"""

# Core agent framework
from .base.agent import AgentBox
from .base.models import (
    AgentInput, 
    AgentOutput, 
    AgentInfo, 
    AgentConfig, 
    BuildConfig, 
    UserConfig,
    PlatformConfig,
    ConcurrencyConfig
)

# Server components (commonly used)
from .server.app import AgentServer
from .server.main import create_app

# Version
__version__ = "0.2.4"

# Main public API
__all__ = [
    # Core classes
    "AgentBox",
    "AgentInput", 
    "AgentOutput", 
    "AgentInfo",
    
    # Configuration models
    "AgentConfig",
    "BuildConfig", 
    "UserConfig",
    "PlatformConfig",
    "ConcurrencyConfig",
    
    # Server components
    "AgentServer",
    "create_app",
]