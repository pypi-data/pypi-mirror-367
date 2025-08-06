"""
Pareng Boyong - Your Intelligent Filipino AI Agent and Coding Assistant

A cost-optimized AI agent system with Filipino cultural integration, multimodal 
capabilities, and extensive tool ecosystem built on Agent Zero framework.

Key Features:
- 44+ specialized AI tools with cost optimization
- Filipino cultural integration and Tagalog TTS
- Multimodal generation (text, images, video, audio)
- Web interface and CLI tools
- Multi-agent architecture
- Self-healing and monitoring systems

Example usage:
    >>> from pareng_boyong import ParengBoyong
    >>> agent = ParengBoyong()
    >>> response = agent.chat("Kumusta! Create a video of Manila sunset")
    >>> print(response)

CLI usage:
    $ boyong setup  # Initial setup wizard
    $ boyong chat   # Interactive chat mode
    $ boyong web    # Launch web interface
"""

__version__ = "1.0.0"
__author__ = "InnovateHub PH"
__email__ = "info@innovatehub.ph"
__license__ = "MIT"

# Core imports
from .core.agent import ParengBoyong
from .core.config import ParengBoyongConfig
from .core.exceptions import ParengBoyongError, ConfigurationError, ToolError

# Cultural integration
from .cultural.identity import FilipinoIdentity
from .cultural.language import LanguageProcessor

# Quick setup function
def setup_pareng_boyong(
    api_keys: dict = None,
    cultural_mode: bool = True,
    cost_optimization: bool = True,
    **kwargs
) -> ParengBoyong:
    """
    Quick setup function for Pareng Boyong agent.
    
    Args:
        api_keys: Dictionary of API keys for various services
        cultural_mode: Enable Filipino cultural integration
        cost_optimization: Enable cost optimization features
        **kwargs: Additional configuration options
        
    Returns:
        Configured ParengBoyong instance
        
    Example:
        >>> agent = setup_pareng_boyong(
        ...     api_keys={"openai": "sk-xxx", "google": "xxx"},
        ...     cultural_mode=True
        ... )
        >>> response = agent.chat("Hello, Pareng Boyong!")
    """
    config = ParengBoyongConfig(
        api_keys=api_keys or {},
        cultural_mode=cultural_mode,
        cost_optimization=cost_optimization,
        **kwargs
    )
    return ParengBoyong(config)

# Package exports
__all__ = [
    # Core classes
    "ParengBoyong",
    "ParengBoyongConfig", 
    "ParengBoyongError",
    "ConfigurationError",
    "ToolError",
    
    # Cultural features
    "FilipinoIdentity",
    "LanguageProcessor",
    
    # Convenience functions
    "setup_pareng_boyong",
    
    # Package metadata
    "__version__",
    "__author__", 
    "__email__",
    "__license__",
]

# Package information for tooling
PACKAGE_INFO = {
    "name": "pareng-boyong",
    "version": __version__,
    "description": "Your Intelligent Filipino AI Agent and Coding Assistant",
    "cultural_features": [
        "Filipino/Tagalog language support",
        "Cultural context awareness", 
        "Bayanihan collaborative approach",
        "Cost-conscious recommendations",
        "Local business practices understanding"
    ],
    "core_capabilities": [
        "44+ specialized AI tools",
        "Multimodal generation (text, images, video, audio)",
        "Cost optimization (FREE → paid service prioritization)",
        "Multi-agent architecture",
        "Self-healing and monitoring",
        "Web interface and CLI"
    ],
    "supported_languages": ["English", "Filipino", "Tagalog"],
    "platforms": ["Windows", "macOS", "Linux"],
    "python_versions": ["3.8+", "3.9", "3.10", "3.11", "3.12"]
}

# Version check and compatibility warnings
import sys
import warnings

if sys.version_info < (3, 8):
    warnings.warn(
        "Pareng Boyong requires Python 3.8 or higher. "
        f"You are using Python {sys.version_info.major}.{sys.version_info.minor}. "
        "Some features may not work correctly.",
        UserWarning,
        stacklevel=2
    )

# Cultural greeting when package is imported
if __name__ != "__main__":
    try:
        from .cultural.greetings import get_random_greeting
        import random
        
        # Show greeting 10% of the time when imported
        if random.random() < 0.1:
            greeting = get_random_greeting()
            print(f"🇵🇭 {greeting} - Pareng Boyong v{__version__} loaded!")
    except ImportError:
        # Graceful fallback if cultural module not available
        pass