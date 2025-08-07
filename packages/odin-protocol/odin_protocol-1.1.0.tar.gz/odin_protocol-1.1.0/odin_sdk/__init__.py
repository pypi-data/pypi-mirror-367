"""
ODIN Protocol SDK - Revolutionary AI Communication Platform
The definitive Python SDK for AI-to-AI communication with self-healing capabilities.

Installation:
    pip install odin-protocol

Quick Start:
    from odin_sdk import OdinClient, OdinMessage
    
    client = OdinClient(api_key="your-key")
    message = OdinMessage.create("Hello from AI Agent")
    response = client.send(message)

Enterprise Features:
    - Advanced rule engine with 100+ operators
    - Self-healing AI communication
    - Real-time analytics and monitoring
    - Plugin ecosystem for extensibility
"""

from .odin_pb2 import (
    OdinMessage,
    HealingMetadata, 
    ConversationContext,
    PerformanceMetrics,
    OdinMessageBatch,
    OdinReflection
)

from .enhanced import OdinMessageBuilder, OdinSDK

# Import core components (will be created)
try:
    from .client import OdinClient
    from .plugins import PluginManager, BasePlugin
except ImportError:
    # Graceful fallback during development
    OdinClient = None
    PluginManager = None
    BasePlugin = None

__all__ = [
    'OdinMessage', 'HealingMetadata', 'ConversationContext', 
    'PerformanceMetrics', 'OdinMessageBatch', 'OdinReflection',
    'OdinMessageBuilder', 'OdinSDK', 'OdinClient', 'PluginManager', 'BasePlugin'
]

__version__ = "1.0.0"
__author__ = "ODIN Protocol Team"
__description__ = "Revolutionary AI Communication Protocol with Self-Healing Capabilities"
__url__ = "https://odin-protocol.com"
__license__ = "Commercial"
