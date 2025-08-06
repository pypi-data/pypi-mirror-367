"""
Configuration management CLI for Pareng Boyong.
"""

from typing import Optional
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from ..core.config import ParengBoyongConfig

console = Console()


def config_manager(
    show: bool = False,
    edit: bool = False, 
    key: Optional[str] = None,
    value: Optional[str] = None,
    reset: bool = False
):
    """
    Manage Pareng Boyong configuration.
    
    Args:
        show: Show current configuration
        edit: Edit configuration interactively
        key: Specific config key to get/set
        value: Value to set (used with key)
        reset: Reset to default configuration
    """
    try:
        config = ParengBoyongConfig()
        
        if reset:
            _reset_config(config)
        elif show:
            _show_config(config)
        elif edit:
            _edit_config(config)
        elif key:
            if value is not None:
                _set_config_value(config, key, value)
            else:
                _get_config_value(config, key)
        else:
            _show_config_summary(config)
            
    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")


def _show_config(config: ParengBoyongConfig):
    """Show complete configuration."""
    console.print(Panel.fit(
        "[bold blue]🇵🇭 Pareng Boyong Configuration[/bold blue]",
        border_style="blue"
    ))
    
    # Core settings
    core_table = Table(title="Core Settings")
    core_table.add_column("Setting", style="cyan")
    core_table.add_column("Value", style="green")
    core_table.add_column("Description")
    
    core_settings = [
        ("Cultural Mode", config.cultural_mode, "Filipino cultural integration"),
        ("Cost Optimization", config.cost_optimization, "Cost-conscious tool selection"),
        ("Max Daily Cost", f"${config.max_daily_cost}", "Daily spending limit"),
        ("Primary Language", config.primary_language, "Language preference"),
        ("Default LLM", config.default_llm, "Default language model"),
    ]
    
    for setting, value, desc in core_settings:
        core_table.add_row(setting, str(value), desc)
    
    console.print(core_table)
    
    # API Keys
    api_table = Table(title="API Keys")
    api_table.add_column("Service", style="cyan") 
    api_table.add_column("Status", style="green")
    
    for service in ["openai", "google", "replicate", "elevenlabs"]:
        key = config.get_api_key(service)
        status = "✅ Configured" if key else "❌ Not set"
        api_table.add_row(service.title(), status)
    
    console.print(api_table)
    
    # Tools
    tools_info = f"Enabled: {len(config.enabled_tools)} | Disabled: {len(config.disabled_tools)}"
    console.print(Panel(f"[bold]Tools:[/bold] {tools_info}", border_style="yellow"))


def _show_config_summary(config: ParengBoyongConfig):
    """Show configuration summary."""
    summary = f"""
[bold blue]🇵🇭 Pareng Boyong Configuration Summary[/bold blue]

[bold]Cultural Settings:[/bold]
• Mode: {'✅ Enabled' if config.cultural_mode else '❌ Disabled'}
• Language: {config.primary_language}
• Po/Opo: {'✅ Yes' if config.use_po_opo else '❌ No'}

[bold]Cost Settings:[/bold]
• Optimization: {'✅ Enabled' if config.cost_optimization else '❌ Disabled'}
• Daily Limit: ${config.max_daily_cost}
• Prefer FREE: {'✅ Yes' if config.prefer_free_services else '❌ No'}

[bold]Tools:[/bold]
• Enabled: {len(config.enabled_tools)}
• API Keys: {len([k for k in config.api_keys.values() if k])} configured

[bold]Directories:[/bold]
• Config: {config.config_dir}  
• Data: {config.data_dir}
• Logs: {config.logs_dir}
"""
    
    console.print(Panel(summary, border_style="blue"))


def _edit_config(config: ParengBoyongConfig):
    """Edit configuration interactively."""
    console.print("[bold]🔧 Interactive Configuration Editor[/bold]\n")
    
    sections = {
        "Cultural Settings": _edit_cultural_settings,
        "Cost Settings": _edit_cost_settings, 
        "API Keys": _edit_api_keys,
        "Tool Settings": _edit_tool_settings,
    }
    
    for section_name, edit_func in sections.items():
        if Confirm.ask(f"Edit {section_name}?"):
            edit_func(config)
            console.print()
    
    # Save changes
    if Confirm.ask("Save changes?"):
        config.save_config()
        console.print("[green]✅ Configuration saved![/green]")
    else:
        console.print("[yellow]Changes discarded[/yellow]")


def _edit_cultural_settings(config: ParengBoyongConfig):
    """Edit cultural settings."""
    config.cultural_mode = Confirm.ask("Enable cultural mode?", default=config.cultural_mode)
    
    if config.cultural_mode:
        config.primary_language = Prompt.ask(
            "Primary language",
            choices=["english", "filipino", "mixed"],
            default=config.primary_language
        )
        
        config.cultural_context_level = Prompt.ask(
            "Cultural context level",
            choices=["minimal", "moderate", "full"], 
            default=config.cultural_context_level
        )
        
        config.use_filipino_greetings = Confirm.ask(
            "Use Filipino greetings?",
            default=config.use_filipino_greetings
        )
        
        config.use_po_opo = Confirm.ask(
            "Use po/opo patterns?",
            default=config.use_po_opo
        )


def _edit_cost_settings(config: ParengBoyongConfig):
    """Edit cost optimization settings."""
    config.cost_optimization = Confirm.ask(
        "Enable cost optimization?",
        default=config.cost_optimization
    )
    
    if config.cost_optimization:
        daily_cost = Prompt.ask(
            "Daily cost limit (USD)",
            default=str(config.max_daily_cost)
        )
        try:
            config.max_daily_cost = float(daily_cost)
        except ValueError:
            console.print("[red]Invalid number, keeping current value[/red]")
        
        config.prefer_free_services = Confirm.ask(
            "Prefer FREE services first?",
            default=config.prefer_free_services
        )
        
        warning_threshold = Prompt.ask(
            "Cost warning threshold (USD)",
            default=str(config.cost_warning_threshold)
        )
        try:
            config.cost_warning_threshold = float(warning_threshold)
        except ValueError:
            console.print("[red]Invalid number, keeping current value[/red]")


def _edit_api_keys(config: ParengBoyongConfig):
    """Edit API keys."""
    services = ["openai", "google", "replicate", "elevenlabs"]
    
    for service in services:
        current_key = config.get_api_key(service)
        status = "configured" if current_key else "not set"
        
        if Confirm.ask(f"Update {service} API key? (currently {status})"):
            new_key = Prompt.ask(f"{service.title()} API key", password=True)
            if new_key:
                config.set_api_key(service, new_key)
                console.print(f"[green]✅ {service} API key updated[/green]")


def _edit_tool_settings(config: ParengBoyongConfig):
    """Edit tool settings."""
    console.print(f"Currently enabled tools: {len(config.enabled_tools)}")
    console.print(f"Currently disabled tools: {len(config.disabled_tools)}")
    
    if Confirm.ask("Modify tool settings?"):
        # This would show tool management interface
        # For now, just show current status
        console.print("\n[bold]Current enabled tools:[/bold]")
        for tool in config.enabled_tools:
            console.print(f"  • {tool}")


def _get_config_value(config: ParengBoyongConfig, key: str):
    """Get specific configuration value."""
    try:
        if hasattr(config, key):
            value = getattr(config, key)
            console.print(f"[cyan]{key}[/cyan]: [green]{value}[/green]")
        else:
            console.print(f"[red]Configuration key '{key}' not found[/red]")
    except Exception as e:
        console.print(f"[red]Error getting config value: {e}[/red]")


def _set_config_value(config: ParengBoyongConfig, key: str, value: str):
    """Set specific configuration value."""
    try:
        if not hasattr(config, key):
            console.print(f"[red]Configuration key '{key}' not found[/red]")
            return
        
        # Type conversion based on current value type
        current_value = getattr(config, key)
        
        if isinstance(current_value, bool):
            new_value = value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(current_value, (int, float)):
            new_value = type(current_value)(value)
        else:
            new_value = value
        
        setattr(config, key, new_value)
        config.save_config()
        
        console.print(f"[green]✅ Set {key} = {new_value}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error setting config value: {e}[/red]")


def _reset_config(config: ParengBoyongConfig):
    """Reset configuration to defaults."""
    if Confirm.ask("⚠️  Reset all configuration to defaults? This cannot be undone."):
        # Create new default config
        new_config = ParengBoyongConfig()
        
        # Keep existing API keys if user wants
        if config.api_keys and Confirm.ask("Keep existing API keys?"):
            new_config.api_keys = config.api_keys
        
        new_config.save_config()
        console.print("[green]✅ Configuration reset to defaults[/green]")
    else:
        console.print("Reset cancelled")


if __name__ == "__main__":
    config_manager(show=True)