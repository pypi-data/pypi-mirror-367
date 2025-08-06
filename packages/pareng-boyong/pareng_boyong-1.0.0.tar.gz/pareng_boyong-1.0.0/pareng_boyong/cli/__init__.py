"""
Command Line Interface for Pareng Boyong AI Agent.

This module provides the CLI commands and interfaces for interacting
with Pareng Boyong from the command line.

Available commands:
- boyong setup     # Initial setup wizard
- boyong chat      # Interactive chat mode
- boyong web       # Launch web interface
- boyong config    # Manage configuration
- boyong tools     # List and manage tools
- boyong --help    # Show help information
"""

from .main import app
from .setup import setup_wizard
from .chat import interactive_chat
from .config import config_manager

__all__ = [
    "app",
    "setup_wizard", 
    "interactive_chat",
    "config_manager",
]