"""
Interactive chat interface for Pareng Boyong CLI.
"""

import asyncio
from typing import Optional
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

from ..core.config import ParengBoyongConfig
from ..core.agent import ParengBoyong

console = Console()


def interactive_chat(config: ParengBoyongConfig):
    """
    Start interactive chat session with Pareng Boyong.
    
    Args:
        config: Pareng Boyong configuration
    """
    try:
        # Initialize agent
        agent = ParengBoyong(config)
        
        # Welcome message
        greeting = agent.filipino_identity.generate_greeting()
        console.print(Panel(greeting, title="Pareng Boyong", border_style="blue"))
        
        # Chat loop
        console.print("\n[dim]Type 'exit', 'quit', or press Ctrl+C to end the chat[/dim]")
        console.print("[dim]Type 'help' for available commands[/dim]\n")
        
        while True:
            try:
                # Get user input
                user_input = console.input("\n[bold blue]You:[/bold blue] ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    farewell = _get_farewell_message(agent)
                    console.print(f"\n[yellow]{farewell}[/yellow]")
                    break
                
                if user_input.lower() == 'help':
                    _show_help()
                    continue
                
                if user_input.lower() == 'status':
                    _show_status(agent)
                    continue
                
                if user_input.lower() == 'reset':
                    agent.reset_session()
                    console.print("[green]Session reset! Starting fresh.[/green]")
                    continue
                
                # Process message with agent
                console.print("\n[bold green]Pareng Boyong:[/bold green]")
                
                # Show thinking indicator and get response
                with Live(
                    Panel(Text("🤔 Thinking...", style="dim"), border_style="green"),
                    refresh_per_second=2
                ) as live:
                    response = agent.chat(user_input)
                    live.update(Panel(Markdown(response), border_style="green"))
                
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Chat interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                console.print("[dim]The conversation continues...[/dim]")
                
    except Exception as e:
        console.print(f"[red]Failed to start chat: {e}[/red]")
        console.print("[yellow]Try running 'boyong setup' first[/yellow]")


def _show_help():
    """Show help information."""
    help_text = """
[bold]Available Commands:[/bold]

[cyan]Chat Commands:[/cyan]
• Just type your message - Pareng Boyong will respond
• Ask for help with coding, content creation, or general questions
• Request images, videos, or audio generation

[cyan]Special Commands:[/cyan]
• [bold]help[/bold]     - Show this help message
• [bold]status[/bold]   - Show system status and capabilities
• [bold]reset[/bold]    - Reset the current chat session
• [bold]exit/quit[/bold] - End the chat session

[cyan]Example Requests:[/cyan]
• "Create an image of Banaue Rice Terraces"
• "Generate a short video of Philippine flag waving" 
• "Help me write Python code for a web scraper"
• "What's the weather like in Manila?"
• "Translate this to Filipino: 'Good morning everyone'"

[cyan]Cultural Features:[/cyan]
• Pareng Boyong understands Filipino/Tagalog
• Uses respectful communication (po/opo)
• Cost-conscious recommendations
• Bayanihan spirit in problem-solving
"""
    console.print(Panel(help_text, title="Help", border_style="cyan"))


def _show_status(agent: ParengBoyong):
    """Show agent status and capabilities."""
    try:
        capabilities = agent.get_capabilities()
        
        status_text = f"""
[bold]System Status:[/bold]
• Session ID: {agent.session_id}
• Cultural Mode: {'✅ Enabled' if agent.config.cultural_mode else '❌ Disabled'}
• Cost Optimization: {'✅ Enabled' if agent.config.cost_optimization else '❌ Disabled'}
• Daily Budget: ${agent.config.max_daily_cost}

[bold]Available Tools:[/bold]
• Total Tools: {len(capabilities.get('tools', []))}
• Enabled Tools: {len(agent.config.enabled_tools)}

[bold]System Health:[/bold]
• Status: {'✅ Healthy' if capabilities.get('system_health', {}).get('healthy', True) else '⚠️ Issues'}

[bold]Session Info:[/bold]
• Conversations: {capabilities.get('session_info', {}).get('conversation_count', 0)}
• Subordinate Agents: {capabilities.get('session_info', {}).get('subordinates', 0)}
"""
        
        console.print(Panel(status_text, title="Status", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[red]Error getting status: {e}[/red]")


def _get_farewell_message(agent: ParengBoyong) -> str:
    """Get culturally appropriate farewell message."""
    if agent.config.cultural_mode:
        farewells = [
            "Salamat sa pag-chat! Ingat po kayo!",
            "Paalam na po! See you again soon!",
            "Thanks sa lahat! Take care po!",
            "Goodbye na! Hanggang sa muli!",
            "Maraming salamat! Keep safe po!",
            "Paalam, kaibigan! Till next time!"
        ]
        import random
        return random.choice(farewells)
    else:
        return "Goodbye! Thanks for chatting with Pareng Boyong!"


async def interactive_chat_async(config: ParengBoyongConfig):
    """
    Async version of interactive chat with streaming responses.
    
    Args:
        config: Pareng Boyong configuration
    """
    # Placeholder for async implementation
    # In a full implementation, this would support streaming responses
    interactive_chat(config)


if __name__ == "__main__":
    # Test the chat interface
    config = ParengBoyongConfig()
    interactive_chat(config)