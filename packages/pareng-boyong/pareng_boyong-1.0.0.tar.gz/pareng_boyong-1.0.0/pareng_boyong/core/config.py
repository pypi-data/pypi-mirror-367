"""
Configuration management for Pareng Boyong AI Agent.

This module handles all configuration settings, API keys, and system preferences
for the Filipino AI agent system.
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml
from dotenv import load_dotenv

from .exceptions import ConfigurationError


@dataclass
class ParengBoyongConfig:
    """
    Configuration class for Pareng Boyong AI Agent.
    
    Handles API keys, system settings, cultural preferences, and tool configurations.
    
    Example:
        >>> config = ParengBoyongConfig(
        ...     api_keys={"openai": "sk-xxx", "google": "xxx"},
        ...     cultural_mode=True,
        ...     cost_optimization=True
        ... )
        >>> agent = ParengBoyong(config)
    """
    
    # Core settings
    cultural_mode: bool = True
    cost_optimization: bool = True
    max_daily_cost: float = 5.0
    max_history_size: int = 100
    
    # API Keys and credentials
    api_keys: Dict[str, str] = field(default_factory=dict)
    
    # Model configurations
    default_llm: str = "openai/gpt-4"
    default_embedding: str = "sentence-transformers/all-MiniLM-L6-v2"
    temperature: float = 0.7
    max_tokens: int = 4000
    
    # Tool preferences
    enabled_tools: List[str] = field(default_factory=lambda: [
        "cost_optimized_video_generator",
        "imagen4_generator", 
        "multimodal_coordinator",
        "system_self_awareness",
        "enhanced_ui_renderer",
        "filipino_tts"
    ])
    disabled_tools: List[str] = field(default_factory=list)
    
    # Cultural settings
    primary_language: str = "mixed"  # "english", "filipino", "mixed"
    cultural_context_level: str = "moderate"  # "minimal", "moderate", "full"
    use_filipino_greetings: bool = True
    use_po_opo: bool = True
    
    # System settings
    subordinate_mode: bool = False
    parent_session: Optional[str] = None
    debug: bool = False
    log_level: str = "INFO"
    
    # File paths
    config_dir: Path = field(default_factory=lambda: Path.home() / ".pareng-boyong")
    data_dir: Path = field(default_factory=lambda: Path.home() / ".pareng-boyong" / "data")
    logs_dir: Path = field(default_factory=lambda: Path.home() / ".pareng-boyong" / "logs")
    
    # Web interface settings
    web_host: str = "localhost"
    web_port: int = 8080
    web_debug: bool = False
    
    # Cost optimization settings
    prefer_free_services: bool = True
    cost_warning_threshold: float = 1.0
    auto_escalate_quality: bool = False
    
    def __post_init__(self):
        """Initialize configuration after creation."""
        # Create necessary directories
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Load environment variables
        self._load_env_vars()
        
        # Load config file if exists
        self._load_config_file()
        
        # Validate configuration
        self._validate_config()
    
    def _load_env_vars(self):
        """Load configuration from environment variables."""
        # Try to load .env file from multiple locations
        env_paths = [
            Path.cwd() / ".env",
            self.config_dir / ".env",
            Path.home() / ".env",
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                break
        
        # Load API keys from environment
        api_key_mapping = {
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY", 
            "anthropic": "ANTHROPIC_API_KEY",
            "elevenlabs": "ELEVENLABS_API_KEY",
            "replicate": "REPLICATE_API_TOKEN",
            "huggingface": "HUGGINGFACE_API_KEY",
        }
        
        for service, env_var in api_key_mapping.items():
            env_value = os.getenv(env_var)
            if env_value and service not in self.api_keys:
                self.api_keys[service] = env_value
        
        # Load other settings from environment
        if os.getenv("PARENG_BOYONG_CULTURAL_MODE"):
            self.cultural_mode = os.getenv("PARENG_BOYONG_CULTURAL_MODE").lower() == "true"
        
        if os.getenv("PARENG_BOYONG_MAX_DAILY_COST"):
            self.max_daily_cost = float(os.getenv("PARENG_BOYONG_MAX_DAILY_COST"))
        
        if os.getenv("PARENG_BOYONG_DEBUG"):
            self.debug = os.getenv("PARENG_BOYONG_DEBUG").lower() == "true"
    
    def _load_config_file(self):
        """Load configuration from file."""
        config_file = self.config_dir / "config.yaml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f)
                
                # Update configuration with file values
                self._update_from_dict(file_config)
                
            except Exception as e:
                raise ConfigurationError(f"Failed to load config file: {e}")
    
    def _update_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self, key):
                # Special handling for nested dictionaries
                if key == "api_keys" and isinstance(value, dict):
                    self.api_keys.update(value)
                elif key in ["enabled_tools", "disabled_tools"] and isinstance(value, list):
                    setattr(self, key, value)
                else:
                    setattr(self, key, value)
    
    def _validate_config(self):
        """Validate configuration settings."""
        # Validate required API keys for enabled tools
        required_keys = self._get_required_api_keys()
        missing_keys = [key for key in required_keys if key not in self.api_keys]
        
        if missing_keys:
            raise ConfigurationError(
                f"Missing required API keys: {missing_keys}. "
                f"Set them in environment variables or config file."
            )
        
        # Validate cost settings
        if self.max_daily_cost <= 0:
            raise ConfigurationError("max_daily_cost must be positive")
        
        # Validate paths
        if not self.config_dir.exists():
            raise ConfigurationError(f"Config directory not accessible: {self.config_dir}")
    
    def _get_required_api_keys(self) -> List[str]:
        """Get required API keys based on enabled tools."""
        key_requirements = {
            "cost_optimized_video_generator": ["replicate", "huggingface"],
            "imagen4_generator": ["google"],
            "filipino_tts": ["elevenlabs"],  # Optional, has fallbacks
            "enhanced_code_execution": [],  # No keys required
        }
        
        required = set()
        for tool in self.enabled_tools:
            if tool in key_requirements:
                # At least one key from the list is required
                tool_keys = key_requirements[tool]
                if tool_keys and not any(key in self.api_keys for key in tool_keys):
                    required.update(tool_keys[:1])  # Require first option
        
        return list(required)
    
    def save_config(self, config_path: Optional[Path] = None):
        """Save current configuration to file."""
        config_path = config_path or (self.config_dir / "config.yaml")
        
        # Prepare config dict (excluding sensitive data)
        config_dict = {
            "cultural_mode": self.cultural_mode,
            "cost_optimization": self.cost_optimization,
            "max_daily_cost": self.max_daily_cost,
            "max_history_size": self.max_history_size,
            "default_llm": self.default_llm,
            "default_embedding": self.default_embedding,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "enabled_tools": self.enabled_tools,
            "disabled_tools": self.disabled_tools,
            "primary_language": self.primary_language,
            "cultural_context_level": self.cultural_context_level,
            "use_filipino_greetings": self.use_filipino_greetings,
            "use_po_opo": self.use_po_opo,
            "debug": self.debug,
            "log_level": self.log_level,
            "web_host": self.web_host,
            "web_port": self.web_port,
            "prefer_free_services": self.prefer_free_services,
            "cost_warning_threshold": self.cost_warning_threshold,
            "auto_escalate_quality": self.auto_escalate_quality,
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise ConfigurationError(f"Failed to save config: {e}")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a service."""
        return self.api_keys.get(service)
    
    def set_api_key(self, service: str, key: str):
        """Set API key for a service."""
        self.api_keys[service] = key
    
    def enable_tool(self, tool_name: str):
        """Enable a specific tool."""
        if tool_name not in self.enabled_tools:
            self.enabled_tools.append(tool_name)
        if tool_name in self.disabled_tools:
            self.disabled_tools.remove(tool_name)
    
    def disable_tool(self, tool_name: str):
        """Disable a specific tool."""
        if tool_name in self.enabled_tools:
            self.enabled_tools.remove(tool_name)
        if tool_name not in self.disabled_tools:
            self.disabled_tools.append(tool_name)
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled."""
        return tool_name in self.enabled_tools and tool_name not in self.disabled_tools
    
    def copy(self) -> 'ParengBoyongConfig':
        """Create a copy of the configuration."""
        return ParengBoyongConfig(
            cultural_mode=self.cultural_mode,
            cost_optimization=self.cost_optimization,
            max_daily_cost=self.max_daily_cost,
            max_history_size=self.max_history_size,
            api_keys=self.api_keys.copy(),
            default_llm=self.default_llm,
            default_embedding=self.default_embedding,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            enabled_tools=self.enabled_tools.copy(),
            disabled_tools=self.disabled_tools.copy(),
            primary_language=self.primary_language,
            cultural_context_level=self.cultural_context_level,
            use_filipino_greetings=self.use_filipino_greetings,
            use_po_opo=self.use_po_opo,
            subordinate_mode=self.subordinate_mode,
            parent_session=self.parent_session,
            debug=self.debug,
            log_level=self.log_level,
            web_host=self.web_host,
            web_port=self.web_port,
            prefer_free_services=self.prefer_free_services,
            cost_warning_threshold=self.cost_warning_threshold,
            auto_escalate_quality=self.auto_escalate_quality,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "cultural_mode": self.cultural_mode,
            "cost_optimization": self.cost_optimization,
            "max_daily_cost": self.max_daily_cost,
            "max_history_size": self.max_history_size,
            "api_keys": self.api_keys,
            "default_llm": self.default_llm,
            "default_embedding": self.default_embedding,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "enabled_tools": self.enabled_tools,
            "disabled_tools": self.disabled_tools,
            "primary_language": self.primary_language,
            "cultural_context_level": self.cultural_context_level,
            "use_filipino_greetings": self.use_filipino_greetings,
            "use_po_opo": self.use_po_opo,
            "subordinate_mode": self.subordinate_mode,
            "parent_session": self.parent_session,
            "debug": self.debug,
            "log_level": self.log_level,
            "web_host": self.web_host,
            "web_port": self.web_port,
            "prefer_free_services": self.prefer_free_services,
            "cost_warning_threshold": self.cost_warning_threshold,
            "auto_escalate_quality": self.auto_escalate_quality,
        }
    
    def __str__(self) -> str:
        return f"ParengBoyongConfig(cultural_mode={self.cultural_mode}, tools={len(self.enabled_tools)})"
    
    def __repr__(self) -> str:
        return (
            f"ParengBoyongConfig("
            f"cultural_mode={self.cultural_mode}, "
            f"cost_optimization={self.cost_optimization}, "
            f"enabled_tools={len(self.enabled_tools)}, "
            f"api_keys={len(self.api_keys)})"
        )