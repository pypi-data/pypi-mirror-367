"""
Main CLI application for Pareng Boyong AI Agent.

This module implements the main command-line interface using Typer,
providing various commands for setup, chat, web interface, and configuration.
"""

import typer
import sys
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..core.config import ParengBoyongConfig
from ..core.agent import ParengBoyong
from ..core.exceptions import ParengBoyongError, ConfigurationError
from .setup import setup_wizard
from .chat import interactive_chat
from .config import config_manager
from .web import launch_web_interface

# Initialize Rich console for beautiful output
console = Console()

# Create main Typer app
app = typer.Typer(
    help="🇵🇭 Pareng Boyong - Your Intelligent Filipino AI Agent and Coding Assistant",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode="rich",
)


def version_callback(value: bool):
    """Show version information."""
    if value:
        from .. import __version__, __author__
        console.print(Panel.fit(
            f"[bold blue]Pareng Boyong[/bold blue] v{__version__}\n"
            f"Your Intelligent Filipino AI Agent\n"
            f"Developed by {__author__}\n\n"
            f"🇵🇭 [italic]\"Bayanihan spirit meets AI excellence\"[/italic]",
            border_style="blue"
        ))
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v", 
        callback=version_callback,
        help="Show version information"
    )
):
    """
    🇵🇭 Pareng Boyong - Your Intelligent Filipino AI Agent and Coding Assistant
    
    A cost-optimized AI agent with Filipino cultural integration, multimodal capabilities,
    and 44+ specialized tools for development and automation.
    
    Key Features:
    • Cost optimization (FREE → paid service prioritization)
    • Filipino cultural integration with Tagalog TTS
    • Multimodal generation (text, images, video, audio)
    • 44+ specialized AI tools
    • Web interface and CLI
    • Multi-agent architecture
    
    Use 'boyong --help' to see available commands.
    """
    pass


@app.command()
def setup(
    force: bool = typer.Option(False, "--force", "-f", help="Force setup even if already configured"),
    minimal: bool = typer.Option(False, "--minimal", help="Minimal setup with essential features only")
):
    """
    🔧 Run the initial setup wizard for Pareng Boyong.
    
    This will guide you through:
    • API key configuration
    • Cultural preferences
    • Tool selection
    • Cost optimization settings
    """
    try:
        console.print(Panel.fit(
            "[bold blue]🇵🇭 Pareng Boyong Setup Wizard[/bold blue]\n"
            "[italic]Let's configure your intelligent Filipino AI assistant![/italic]",
            border_style="blue"
        ))
        
        config = setup_wizard(force=force, minimal=minimal)
        
        console.print("[green]✅ Setup completed successfully![/green]")
        console.print(f"Configuration saved to: {config.config_dir}")
        
        # Offer to start chat
        if typer.confirm("Would you like to start chatting with Pareng Boyong now?"):
            interactive_chat(config)
            
    except Exception as e:
        console.print(f"[red]❌ Setup failed: {e}[/red]")
        raise typer.Exit(1)


@app.command() 
def chat(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Custom config file path"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override default model"),
    cultural: bool = typer.Option(True, "--cultural/--no-cultural", help="Enable/disable cultural mode"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode")
):
    """
    💬 Start interactive chat mode with Pareng Boyong.
    
    This launches an interactive chat session where you can:
    • Ask questions and get help
    • Generate multimedia content
    • Execute code and commands
    • Use all 44+ specialized tools
    
    Examples:
    • boyong chat
    • boyong chat --model "openai/gpt-4"
    • boyong chat --no-cultural
    """
    try:
        # Load configuration
        if config_file and config_file.exists():
            # TODO: Load from custom config file
            config = ParengBoyongConfig()
        else:
            config = ParengBoyongConfig()
        
        # Apply CLI overrides
        if model:
            config.default_llm = model
        config.cultural_mode = cultural
        config.debug = debug
        
        console.print(Panel.fit(
            "[bold blue]🇵🇭 Pareng Boyong Chat Mode[/bold blue]\n"
            "[italic]Kumusta! Ready to help with your AI needs![/italic]\n\n"
            f"Cultural Mode: {'✅ ON' if cultural else '❌ OFF'}\n"
            f"Model: {config.default_llm}\n"
            f"Tools Available: {len(config.enabled_tools)}",
            border_style="blue"
        ))
        
        interactive_chat(config)
        
    except ConfigurationError as e:
        console.print(f"[red]❌ Configuration error: {e}[/red]")
        console.print("\n[yellow]💡 Try running 'boyong setup' first[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Chat failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def web(
    host: str = typer.Option("localhost", help="Host to bind to"),
    port: int = typer.Option(8080, help="Port to bind to"),
    debug: bool = typer.Option(False, help="Enable debug mode"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open browser automatically")
):
    """
    🌐 Launch the Pareng Boyong web interface.
    
    This starts a web server providing:
    • Interactive chat interface
    • Tool management dashboard
    • Configuration settings
    • Real-time monitoring
    • Multimedia gallery
    
    The web interface will be available at http://localhost:8080
    """
    try:
        console.print(Panel.fit(
            "[bold blue]🌐 Pareng Boyong Web Interface[/bold blue]\n"
            f"Starting server at http://{host}:{port}\n"
            "[italic]Your Filipino AI assistant in your browser![/italic]",
            border_style="blue"
        ))
        
        launch_web_interface(host=host, port=port, debug=debug, open_browser=open_browser)
        
    except Exception as e:
        console.print(f"[red]❌ Web interface failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    edit: bool = typer.Option(False, "--edit", help="Edit configuration interactively"),
    key: Optional[str] = typer.Option(None, "--key", help="Get/set specific config key"),
    value: Optional[str] = typer.Option(None, "--value", help="Value to set (used with --key)"),
    reset: bool = typer.Option(False, "--reset", help="Reset to default configuration")
):
    """
    ⚙️ Manage Pareng Boyong configuration.
    
    Examples:
    • boyong config --show
    • boyong config --edit
    • boyong config --key cultural_mode --value true
    • boyong config --reset
    """
    try:
        config_manager(show=show, edit=edit, key=key, value=value, reset=reset)
        
    except Exception as e:
        console.print(f"[red]❌ Config management failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def tools(
    list_all: bool = typer.Option(False, "--list", "-l", help="List all available tools"),
    enabled: bool = typer.Option(False, "--enabled", help="Show only enabled tools"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    enable: Optional[str] = typer.Option(None, "--enable", help="Enable a specific tool"),
    disable: Optional[str] = typer.Option(None, "--disable", help="Disable a specific tool")
):
    """
    🔧 Manage Pareng Boyong tools.
    
    View and manage the 44+ specialized AI tools available in Pareng Boyong.
    
    Examples:
    • boyong tools --list
    • boyong tools --enabled
    • boyong tools --category multimodal
    • boyong tools --enable imagen4_generator
    """
    try:
        # Load configuration to get tool info
        config = ParengBoyongConfig()
        agent = ParengBoyong(config)
        
        if list_all or enabled or category:
            _show_tools(agent, enabled_only=enabled, category=category)
        elif enable:
            _enable_tool(config, enable)
        elif disable:
            _disable_tool(config, disable)
        else:
            # Show tool summary by default
            _show_tools_summary(agent)
            
    except Exception as e:
        console.print(f"[red]❌ Tool management failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status():
    """
    📊 Show Pareng Boyong system status and health.
    
    Displays:
    • System health metrics
    • Available tools and their status
    • Configuration summary
    • Recent usage statistics
    """
    try:
        config = ParengBoyongConfig()
        agent = ParengBoyong(config)
        
        # Get system status
        capabilities = agent.get_capabilities()
        
        # Create status display
        status_table = Table(title="🇵🇭 Pareng Boyong System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Details")
        
        # System health
        health = capabilities.get('system_health', {})
        health_status = "✅ Healthy" if health.get('healthy', True) else "⚠️ Issues"
        status_table.add_row("System Health", health_status, f"Memory: {health.get('memory_percent', 0):.1f}%")
        
        # Cultural features
        cultural_status = "✅ Enabled" if config.cultural_mode else "❌ Disabled"
        status_table.add_row("Cultural Mode", cultural_status, "Filipino integration")
        
        # Tools
        enabled_tools = len(config.enabled_tools)
        total_tools = len(capabilities.get('tools', []))
        status_table.add_row("Tools", f"✅ {enabled_tools}/{total_tools}", "AI tools available")
        
        # Cost optimization
        cost_status = "✅ Enabled" if config.cost_optimization else "❌ Disabled"
        status_table.add_row("Cost Optimization", cost_status, f"Daily limit: ${config.max_daily_cost}")
        
        console.print(status_table)
        
        # Show capabilities summary
        if capabilities:
            console.print("\n[bold blue]🎯 Key Capabilities:[/bold blue]")
            for feature in capabilities.get('cultural_features', {}).get('cultural_elements', []):
                console.print(f"  • {feature}")
        
    except Exception as e:
        console.print(f"[red]❌ Status check failed: {e}[/red]")
        raise typer.Exit(1)


def _show_tools(agent: ParengBoyong, enabled_only: bool = False, category: Optional[str] = None):
    """Show tools in a formatted table."""
    capabilities = agent.get_capabilities()
    tools = capabilities.get('tools', [])
    
    if enabled_only:
        tools = [t for t in tools if t.get('enabled', True)]
    
    if category:
        tools = [t for t in tools if t.get('category', '').lower() == category.lower()]
    
    # Create tools table
    table = Table(title=f"🔧 Pareng Boyong Tools{' (Enabled Only)' if enabled_only else ''}")
    table.add_column("Tool Name", style="cyan")
    table.add_column("Category", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Description")
    
    for tool in tools:
        name = tool.get('name', 'Unknown')
        cat = tool.get('category', 'General')
        status = "✅ Enabled" if tool.get('enabled', True) else "❌ Disabled"
        desc = tool.get('description', 'No description')[:50] + "..."
        
        table.add_row(name, cat, status, desc)
    
    console.print(table)


def _show_tools_summary(agent: ParengBoyong):
    """Show tools summary."""
    capabilities = agent.get_capabilities()
    tools = capabilities.get('tools', [])
    
    # Group by category
    categories = {}
    for tool in tools:
        cat = tool.get('category', 'General')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(tool)
    
    console.print("[bold blue]🔧 Pareng Boyong Tools Summary[/bold blue]\n")
    
    for category, cat_tools in categories.items():
        enabled_count = len([t for t in cat_tools if t.get('enabled', True)])
        total_count = len(cat_tools)
        
        console.print(f"[yellow]{category}[/yellow]: {enabled_count}/{total_count} enabled")
        
        for tool in cat_tools[:3]:  # Show first 3 tools
            status = "✅" if tool.get('enabled', True) else "❌"
            console.print(f"  {status} {tool.get('name', 'Unknown')}")
        
        if len(cat_tools) > 3:
            console.print(f"  ... and {len(cat_tools) - 3} more")
        console.print()


def _enable_tool(config: ParengBoyongConfig, tool_name: str):
    """Enable a specific tool."""
    config.enable_tool(tool_name)
    config.save_config()
    console.print(f"[green]✅ Enabled tool: {tool_name}[/green]")


def _disable_tool(config: ParengBoyongConfig, tool_name: str):
    """Disable a specific tool.""" 
    config.disable_tool(tool_name)
    config.save_config()
    console.print(f"[yellow]❌ Disabled tool: {tool_name}[/yellow]")


if __name__ == "__main__":
    app()