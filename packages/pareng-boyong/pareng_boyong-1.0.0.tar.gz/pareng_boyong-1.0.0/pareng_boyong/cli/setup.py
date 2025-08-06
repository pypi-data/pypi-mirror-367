"""
Setup wizard for Pareng Boyong initial configuration.
"""

from typing import Dict, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
import typer

from ..core.config import ParengBoyongConfig

console = Console()


def setup_wizard(force: bool = False, minimal: bool = False) -> ParengBoyongConfig:
    """
    Interactive setup wizard for Pareng Boyong configuration.
    
    Args:
        force: Force setup even if already configured
        minimal: Minimal setup with essential features only
        
    Returns:
        Configured ParengBoyongConfig instance
    """
    console.print(Panel.fit(
        "[bold blue]🇵🇭 Kumusta! Welcome to Pareng Boyong Setup![/bold blue]\n"
        "[italic]Let's configure your intelligent Filipino AI assistant![/italic]",
        border_style="blue"
    ))
    
    # Check existing configuration
    config = ParengBoyongConfig()
    
    if not force and len(config.api_keys) > 0:
        if not Confirm.ask("Configuration already exists. Continue setup?"):
            return config
    
    if minimal:
        return _minimal_setup(config)
    else:
        return _full_setup(config)


def _minimal_setup(config: ParengBoyongConfig) -> ParengBoyongConfig:
    """Minimal setup with essential features only."""
    console.print("[yellow]🔧 Minimal Setup Mode[/yellow]\n")
    
    # Essential API keys
    if not config.get_api_key("openai"):
        openai_key = Prompt.ask("OpenAI API Key (optional, press Enter to skip)", default="")
        if openai_key:
            config.set_api_key("openai", openai_key)
    
    # Cultural mode
    config.cultural_mode = Confirm.ask("Enable Filipino cultural integration?", default=True)
    
    # Cost optimization
    config.cost_optimization = True
    config.prefer_free_services = True
    
    # Save configuration
    config.save_config()
    
    console.print("[green]✅ Minimal setup completed![/green]")
    return config


def _full_setup(config: ParengBoyongConfig) -> ParengBoyongConfig:
    """Full interactive setup."""
    console.print("[cyan]🚀 Full Setup Mode[/cyan]\n")
    
    # API Keys configuration
    _setup_api_keys(config)
    
    # Cultural preferences
    _setup_cultural_preferences(config)
    
    # Cost optimization
    _setup_cost_preferences(config)
    
    # Tool selection
    _setup_tool_preferences(config)
    
    # Save configuration
    config.save_config()
    
    console.print("[green]✅ Full setup completed![/green]")
    console.print(f"Configuration saved to: {config.config_dir}")
    
    return config


def _setup_api_keys(config: ParengBoyongConfig):
    """Setup API keys."""
    console.print("[bold]🔑 API Keys Configuration[/bold]")
    
    api_services = {
        "openai": "OpenAI (for GPT models)",
        "google": "Google (for Imagen 4 Fast)",  
        "replicate": "Replicate (for video generation)",
        "elevenlabs": "ElevenLabs (for TTS)"
    }
    
    for service, description in api_services.items():
        current_key = config.get_api_key(service)
        if current_key:
            if Confirm.ask(f"{description} - Keep existing key?"):
                continue
        
        key = Prompt.ask(f"{description} API Key (optional)", default="")
        if key:
            config.set_api_key(service, key)


def _setup_cultural_preferences(config: ParengBoyongConfig):
    """Setup cultural preferences."""
    console.print("\n[bold]🇵🇭 Cultural Preferences[/bold]")
    
    config.cultural_mode = Confirm.ask("Enable Filipino cultural integration?", default=True)
    
    if config.cultural_mode:
        config.primary_language = Prompt.ask(
            "Primary language mode",
            choices=["english", "filipino", "mixed"],
            default="mixed"
        )
        
        config.cultural_context_level = Prompt.ask(
            "Cultural context level",
            choices=["minimal", "moderate", "full"],
            default="moderate"
        )
        
        config.use_filipino_greetings = Confirm.ask("Use Filipino greetings?", default=True)
        config.use_po_opo = Confirm.ask("Use respectful po/opo patterns?", default=True)


def _setup_cost_preferences(config: ParengBoyongConfig):
    """Setup cost optimization preferences.""" 
    console.print("\n[bold]💰 Cost Optimization[/bold]")
    
    config.cost_optimization = Confirm.ask("Enable cost optimization?", default=True)
    
    if config.cost_optimization:
        config.prefer_free_services = Confirm.ask("Prefer FREE services first?", default=True)
        
        daily_limit = Prompt.ask("Daily cost limit (USD)", default="5.0")
        try:
            config.max_daily_cost = float(daily_limit)
        except ValueError:
            config.max_daily_cost = 5.0
        
        warning_threshold = Prompt.ask("Cost warning threshold (USD)", default="1.0")
        try:
            config.cost_warning_threshold = float(warning_threshold)
        except ValueError:
            config.cost_warning_threshold = 1.0


def _setup_tool_preferences(config: ParengBoyongConfig):
    """Setup tool preferences."""
    console.print("\n[bold]🔧 Tool Configuration[/bold]")
    
    # Essential tools
    essential_tools = [
        "cost_optimized_video_generator",
        "imagen4_generator",
        "system_self_awareness",
        "multimodal_coordinator"
    ]
    
    config.enabled_tools = essential_tools.copy()
    
    # Optional tools
    optional_tools = {
        "enhanced_ui_renderer": "Enhanced UI rendering with React components",
        "filipino_tts": "Filipino text-to-speech",
        "enhanced_code_execution": "Advanced code execution capabilities"
    }
    
    for tool, description in optional_tools.items():
        if Confirm.ask(f"Enable {tool}? ({description})"):
            config.enabled_tools.append(tool)


if __name__ == "__main__":
    setup_wizard()