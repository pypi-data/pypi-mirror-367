"""
Main Jarvis Engine - Core functionality for the Shaheen-Jarvis framework.
Handles function registration, dispatch, plugin loading, and configuration management.
"""

import logging
import re
from typing import Dict, Callable, Any, Optional, List, Union
from functools import wraps

from .config_manager import ConfigManager
from .plugin_loader import PluginLoader
from .voice_io import VoiceIO


class Jarvis:
    """
    Main Jarvis class with register, dispatch, plugin loading, and config management.
    """
    
    def __init__(self, config_path: Optional[str] = None, enable_voice: bool = False):
        """
        Initialize Jarvis with configuration and optional voice support.
        
        Args:
            config_path: Path to configuration file
            enable_voice: Whether to enable voice I/O
        """
        self.functions: Dict[str, Callable] = {}
        self.aliases: Dict[str, str] = {}
        self.function_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Initialize components
        self.config = ConfigManager(config_path)
        self.plugin_loader = PluginLoader(self)
        self.voice_io = VoiceIO(self.config) if enable_voice else None
        
        # Setup logging
        self._setup_logging()
        
        # Load predefined functions
        self._load_predefined_functions()
        
        self.logger.info("Jarvis initialized successfully")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('logging.level', 'INFO')
        log_to_file = self.config.get('logging.log_to_file', True)
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        self.logger = logging.getLogger(__name__)
        
        if log_to_file:
            handler = logging.FileHandler('jarvis.log')
            handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(handler)
    
    def _load_predefined_functions(self):
        """Load all predefined functions from modules."""
        modules_to_load = [
            ('basic_functions', 'basic'),
            ('web_functions', 'web'),
            ('system_functions', 'system'),
            ('utility_functions', 'utility'),
            ('productivity_functions', 'productivity'),
            ('ai_functions', 'ai')
        ]
        
        for module_name, category in modules_to_load:
            try:
                module = __import__(f'jarvis.modules.{module_name}', fromlist=[module_name])
                
                # Get all functions from the module
                for name in dir(module):
                    if name.startswith('_') or name in ['os', 'sys', 'json', 'requests', 'datetime', 'random', 'string', 'hashlib', 'smtplib', 'subprocess', 'platform', 'psutil', 'webbrowser', 'wikipedia', 'MIMEMultipart', 'MIMEText', 'MIMEApplication', 'Timer', 'time', 'BeautifulSoup', 'timedelta', 'List', 'Dict', 'Any', 'Optional', 'Callable', 'Union']:
                        continue
                    
                    func = getattr(module, name)
                    if callable(func):
                        description = func.__doc__ or f"{name} function from {category} module"
                        self.register(name, func, description=description, category=category)
                        
            except ImportError as e:
                self.logger.warning(f"Could not load {module_name}: {e}")
            except Exception as e:
                self.logger.error(f"Error loading {module_name}: {e}")
    
    def register(self, name: str, func: Callable, 
                 aliases: Optional[List[str]] = None,
                 description: str = "",
                 category: str = "general") -> None:
        """
        Register a function with the Jarvis system.
        
        Args:
            name: Function name
            func: The callable function
            aliases: List of alternative names for the function
            description: Description of what the function does
            category: Category for organizing functions
        """
        if not callable(func):
            raise ValueError(f"'{name}' is not callable")
        
        self.functions[name] = func
        self.function_metadata[name] = {
            'description': description or func.__doc__ or "",
            'category': category,
            'aliases': aliases or []
        }
        
        # Register aliases
        if aliases:
            for alias in aliases:
                self.aliases[alias] = name
        
        self.logger.debug(f"Registered function: {name}")
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a function.
        
        Args:
            name: Function name to unregister
            
        Returns:
            True if function was unregistered, False if not found
        """
        if name in self.functions:
            # Remove aliases
            aliases = self.function_metadata.get(name, {}).get('aliases', [])
            for alias in aliases:
                self.aliases.pop(alias, None)
            
            # Remove function and metadata
            del self.functions[name]
            del self.function_metadata[name]
            
            self.logger.debug(f"Unregistered function: {name}")
            return True
        return False
    
    def call(self, name: str, *args, **kwargs) -> Any:
        """
        Call a registered function by name.
        
        Args:
            name: Function name or alias
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            ValueError: If function is not found
        """
        # Resolve alias to actual function name
        actual_name = self.aliases.get(name, name)
        
        if actual_name not in self.functions:
            available = list(self.functions.keys()) + list(self.aliases.keys())
            raise ValueError(f"Function '{name}' not found. Available: {available}")
        
        try:
            self.logger.info(f"Calling function: {actual_name}")
            result = self.functions[actual_name](*args, **kwargs)
            self.logger.debug(f"Function {actual_name} completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error calling function {actual_name}: {e}")
            raise
    
    def dispatch(self, text: str) -> Any:
        """
        Dispatch natural language text to appropriate function.
        
        Args:
            text: Natural language command
            
        Returns:
            Result of the function call or error message
        """
        text = text.strip().lower()
        
        # Simple pattern matching for common commands
        patterns = {
            r'what.*time': 'tell_time',
            r'what.*date': 'tell_date',
            r'tell.*joke': 'tell_joke',
            r'weather': 'get_weather',
            r'search.*web': 'search_web',
            r'open.*url': 'open_url',
            r'send.*email': 'send_email',
            r'system.*info': 'system_info',
            r'ip.*address': 'get_ip_address',
            r'generate.*password': 'generate_password',
            r'translate': 'translate_text',
            r'currency': 'convert_currency',
            r'play.*music': 'play_music',
            r'set.*alarm': 'set_alarm',
            r'news': 'news_headlines',
            r'wikipedia': 'wikipedia_summary',
            r'note.*something': 'note_something',
            r'recall.*note': 'recall_note',
            r'random.*quote': 'get_random_quote',
            r'calculate': 'calculate_expression',
            r'track.*package': 'track_package',
            r'create.*todo': 'create_todo',
            r'show.*todo': 'show_todos',
        }
        
        for pattern, func_name in patterns.items():
            if re.search(pattern, text):
                try:
                    return self.call(func_name)
                except ValueError:
                    continue
        
        return f"Sorry, I couldn't understand the command: '{text}'"
    
    def list_functions(self, category: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all registered functions, optionally filtered by category.
        
        Args:
            category: Filter by category (optional)
            
        Returns:
            Dictionary of function names and their metadata
        """
        if category:
            return {
                name: metadata for name, metadata in self.function_metadata.items()
                if metadata.get('category') == category
            }
        return self.function_metadata.copy()
    
    def get_help(self, function_name: Optional[str] = None) -> str:
        """
        Get help information for a function or all functions.
        
        Args:
            function_name: Specific function to get help for (optional)
            
        Returns:
            Help information as string
        """
        if function_name:
            actual_name = self.aliases.get(function_name, function_name)
            if actual_name in self.function_metadata:
                metadata = self.function_metadata[actual_name]
                return f"{actual_name}: {metadata['description']}"
            return f"Function '{function_name}' not found"
        
        # Return help for all functions
        help_text = "Available functions:\n"
        for name, metadata in self.function_metadata.items():
            help_text += f"  {name}: {metadata['description']}\n"
        return help_text
    
    def load_plugin(self, plugin_path: str) -> bool:
        """
        Load a plugin from file or package.
        
        Args:
            plugin_path: Path to plugin file or package name
            
        Returns:
            True if plugin loaded successfully, False otherwise
        """
        return self.plugin_loader.load_plugin(plugin_path)
    
    def speak(self, text: str) -> None:
        """
        Speak text using TTS if voice is enabled.
        
        Args:
            text: Text to speak
        """
        if self.voice_io:
            self.voice_io.speak(text)
    
    def listen(self) -> Optional[str]:
        """
        Listen for voice input if voice is enabled.
        
        Returns:
            Recognized text or None if voice not enabled
        """
        if self.voice_io:
            return self.voice_io.listen()
        return None
