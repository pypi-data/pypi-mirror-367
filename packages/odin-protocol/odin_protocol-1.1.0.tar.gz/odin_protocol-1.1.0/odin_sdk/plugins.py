"""
ODIN Protocol Plugin System
Extensible plugin architecture for custom functionality.
"""

import abc
import importlib
import json
import logging
from typing import Dict, List, Optional, Any, Type
from pathlib import Path


class BasePlugin(abc.ABC):
    """
    Base class for all ODIN Protocol plugins.
    
    Plugins can extend functionality for:
    - Custom message processing
    - Rule evaluation logic
    - Analytics and monitoring
    - Integration with external services
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"odin.plugin.{self.__class__.__name__}")
        self.enabled = True
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
    
    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @property
    def description(self) -> str:
        """Plugin description."""
        return "ODIN Protocol Plugin"
    
    @abc.abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass
    
    @abc.abstractmethod
    async def process_message(self, message: Any, context: Dict[str, Any]) -> Any:
        """Process an ODIN message. Return modified message or None."""
        pass
    
    async def shutdown(self):
        """Clean shutdown of the plugin."""
        pass


class RulePlugin(BasePlugin):
    """Base class for rule-based plugins."""
    
    @abc.abstractmethod
    async def evaluate_rule(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate custom rules. Return rule result."""
        pass


class AnalyticsPlugin(BasePlugin):
    """Base class for analytics plugins."""
    
    @abc.abstractmethod
    async def track_event(self, event: str, data: Dict[str, Any]):
        """Track an analytics event."""
        pass


class PluginManager:
    """
    Plugin manager for ODIN Protocol.
    
    Features:
    - Dynamic plugin loading/unloading
    - Plugin dependency management
    - Configuration management
    - Plugin marketplace integration
    """
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, BasePlugin] = {}
        self.enabled_plugins: Dict[str, BasePlugin] = {}
        self.logger = logging.getLogger("odin.plugin_manager")
        
        # Create plugin directory if it doesn't exist
        self.plugin_dir.mkdir(exist_ok=True)
    
    async def load_plugin(self, plugin_path: str, config: Dict[str, Any] = None) -> bool:
        """Load a plugin from file path."""
        try:
            # Import the plugin module
            spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                self.logger.error(f"No plugin class found in {plugin_path}")
                return False
            
            # Instantiate and initialize plugin
            plugin = plugin_class(config)
            if await plugin.initialize():
                self.plugins[plugin.name] = plugin
                if plugin.enabled:
                    self.enabled_plugins[plugin.name] = plugin
                self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
                return True
            else:
                self.logger.error(f"Failed to initialize plugin: {plugin.name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_path}: {e}")
            return False
    
    async def load_plugins_from_directory(self, directory: str = None):
        """Load all plugins from a directory."""
        plugin_dir = Path(directory) if directory else self.plugin_dir
        
        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            # Load plugin config if it exists
            config_file = plugin_file.with_suffix(".json")
            config = {}
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
            
            await self.load_plugin(str(plugin_file), config)
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            await plugin.shutdown()
            del self.plugins[plugin_name]
            if plugin_name in self.enabled_plugins:
                del self.enabled_plugins[plugin_name]
            self.logger.info(f"Unloaded plugin: {plugin_name}")
            return True
        return False
    
    async def process_message(self, message: Any, context: Dict[str, Any] = None) -> Any:
        """Process message through all enabled plugins."""
        context = context or {}
        
        for plugin in self.enabled_plugins.values():
            try:
                result = await plugin.process_message(message, context)
                if result is not None:
                    message = result
            except Exception as e:
                self.logger.error(f"Error in plugin {plugin.name}: {e}")
        
        return message
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a specific plugin by name."""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins."""
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "enabled": plugin.enabled
            }
            for plugin in self.plugins.values()
        ]
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.enabled = True
            self.enabled_plugins[plugin_name] = plugin
            return True
        return False
    
    async def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        if plugin_name in self.enabled_plugins:
            plugin = self.enabled_plugins[plugin_name]
            plugin.enabled = False
            del self.enabled_plugins[plugin_name]
            return True
        return False


# Example plugins for demonstration
class LoggingPlugin(BasePlugin):
    """Example plugin that logs all messages."""
    
    @property
    def name(self) -> str:
        return "logging"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Logs all ODIN messages for debugging"
    
    async def initialize(self) -> bool:
        self.logger.info("Logging plugin initialized")
        return True
    
    async def process_message(self, message: Any, context: Dict[str, Any]) -> Any:
        self.logger.info(f"Processing message: {type(message).__name__}")
        return message


class ValidationPlugin(RulePlugin):
    """Example plugin that validates message content."""
    
    @property
    def name(self) -> str:
        return "validation"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Validates ODIN message content and structure"
    
    async def initialize(self) -> bool:
        self.min_length = self.config.get("min_length", 10)
        self.max_length = self.config.get("max_length", 10000)
        return True
    
    async def process_message(self, message: Any, context: Dict[str, Any]) -> Any:
        if hasattr(message, 'raw_output'):
            content_length = len(message.raw_output)
            if content_length < self.min_length:
                self.logger.warning(f"Message too short: {content_length} chars")
            elif content_length > self.max_length:
                self.logger.warning(f"Message too long: {content_length} chars")
        return message
    
    async def evaluate_rule(self, context: Dict[str, Any]) -> Dict[str, Any]:
        message = context.get("message")
        if message and hasattr(message, 'raw_output'):
            content_length = len(message.raw_output)
            is_valid = self.min_length <= content_length <= self.max_length
            return {
                "rule_name": "content_length_validation",
                "passed": is_valid,
                "score": 1.0 if is_valid else 0.0,
                "details": f"Content length: {content_length}"
            }
        return {"rule_name": "content_length_validation", "passed": True, "score": 1.0}
