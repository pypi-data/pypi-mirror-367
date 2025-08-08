"""Command-line interface for the MCP client."""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .agents.anthropic_agent import AnthropicAgent
from .agents.base import AIAgent, Message
from .agents.openai_agent import OpenAIAgent
from .agents.xai_agent import XAIAgent
from .config import get_ai_provider_config, load_config
from .mcp.client import MCPClient
from .utils.history import HistoryManager
from .utils.logging import get_logger, setup_logging

console = Console()
logger = get_logger(__name__)


def create_agent(provider_name: str, config) -> AIAgent:
    """Create an AI agent based on provider name."""
    provider_config = get_ai_provider_config(config, provider_name)
    if not provider_config:
        raise ValueError(f"AI provider {provider_name} not configured")

    if provider_name == "openai":
        return OpenAIAgent(provider_config.model, provider_config.api_key)
    elif provider_name == "anthropic":
        return AnthropicAgent(provider_config.model, provider_config.api_key)
    elif provider_name == "xai":
        return XAIAgent(provider_config.model, provider_config.api_key)
    else:
        raise ValueError(f"Unsupported AI provider: {provider_name}")


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, config, verbose):
    """Egile MCP Client - Connect to MCP servers directly or through AI agents."""
    ctx.ensure_object(dict)

    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)

    # Load configuration
    try:
        ctx.obj["config"] = load_config(config)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--server", "-s", help="MCP server name to connect to")
@click.pass_context
def direct(ctx, server):
    """Connect directly to an MCP server."""
    config = ctx.obj["config"]

    if not server:
        server = config.default_mcp_server
        if not server:
            available_servers = [s.name for s in config.mcp_servers]
            console.print("[red]No server specified and no default configured.[/red]")
            console.print(f"Available servers: {', '.join(available_servers)}")
            sys.exit(1)

    asyncio.run(_direct_mode(config, server))


async def _direct_mode(config, server_name: str):
    """Run direct mode interaction with MCP server."""
    client = MCPClient(config)

    try:
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            task = progress.add_task(f"Connecting to {server_name}...", total=None)
            await client.connect_to_server(server_name)
            progress.remove_task(task)

        console.print(f"[green]Connected to MCP server: {server_name}[/green]")

        while True:
            console.print("\n[bold]Available commands:[/bold]")
            console.print("1. List tools")
            console.print("2. Call tool")
            console.print("3. List resources")
            console.print("4. Read resource")
            console.print("5. List prompts")
            console.print("6. Get prompt")
            console.print("7. Exit")

            choice = console.input("\nEnter your choice (1-7): ")

            if choice == "1":
                await _list_tools(client, server_name)
            elif choice == "2":
                await _call_tool(client, server_name)
            elif choice == "3":
                await _list_resources(client, server_name)
            elif choice == "4":
                await _read_resource(client, server_name)
            elif choice == "5":
                await _list_prompts(client, server_name)
            elif choice == "6":
                await _get_prompt(client, server_name)
            elif choice == "7":
                break
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        await client.disconnect_all()


async def _list_tools(client: MCPClient, server_name: str):
    """List available tools from the server."""
    try:
        tools = await client.list_tools(server_name)

        if not tools:
            console.print("[yellow]No tools available.[/yellow]")
            return

        table = Table(title="Available Tools")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")

        for tool in tools:
            table.add_row(tool.name, tool.description)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing tools: {e}[/red]")


async def _call_tool(client: MCPClient, server_name: str):
    """Call a tool on the server."""
    try:
        # First list tools
        tools = await client.list_tools(server_name)
        if not tools:
            console.print("[yellow]No tools available.[/yellow]")
            return

        # Show available tools
        console.print("\n[bold]Available tools:[/bold]")
        for i, tool in enumerate(tools, 1):
            console.print(f"{i}. {tool.name} - {tool.description}")

        # Get tool selection
        choice = console.input("\nEnter tool number: ")
        try:
            tool_index = int(choice) - 1
            if tool_index < 0 or tool_index >= len(tools):
                raise ValueError("Invalid tool number")
            selected_tool = tools[tool_index]
        except ValueError:
            console.print("[red]Invalid tool number.[/red]")
            return

        # Get arguments
        console.print(f"\n[bold]Tool: {selected_tool.name}[/bold]")
        console.print(f"Schema: {json.dumps(selected_tool.input_schema, indent=2)}")

        args_input = console.input("Enter arguments (JSON): ")
        try:
            arguments = json.loads(args_input) if args_input.strip() else {}
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON format.[/red]")
            return

        # Call the tool
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            task = progress.add_task(
                f"Calling tool {selected_tool.name}...", total=None
            )
            result = await client.call_tool(server_name, selected_tool.name, arguments)
            progress.remove_task(task)

        console.print(Panel(json.dumps(result, indent=2), title="Tool Result"))

    except Exception as e:
        console.print(f"[red]Error calling tool: {e}[/red]")


async def _list_resources(client: MCPClient, server_name: str):
    """List available resources from the server."""
    try:
        resources = await client.list_resources(server_name)

        if not resources:
            console.print("[yellow]No resources available.[/yellow]")
            return

        table = Table(title="Available Resources")
        table.add_column("URI", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description", style="yellow")
        table.add_column("MIME Type", style="magenta")

        for resource in resources:
            table.add_row(
                resource.uri,
                resource.name,
                resource.description or "",
                resource.mime_type or "",
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing resources: {e}[/red]")


async def _read_resource(client: MCPClient, server_name: str):
    """Read a resource from the server."""
    try:
        # First list resources
        resources = await client.list_resources(server_name)
        if not resources:
            console.print("[yellow]No resources available.[/yellow]")
            return

        # Show available resources
        console.print("\n[bold]Available resources:[/bold]")
        for i, resource in enumerate(resources, 1):
            console.print(f"{i}. {resource.uri} - {resource.name}")

        # Get resource selection
        choice = console.input("\nEnter resource number or URI: ")

        if choice.isdigit():
            resource_index = int(choice) - 1
            if resource_index < 0 or resource_index >= len(resources):
                console.print("[red]Invalid resource number.[/red]")
                return
            uri = resources[resource_index].uri
        else:
            uri = choice

        # Read the resource
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            task = progress.add_task(f"Reading resource {uri}...", total=None)
            result = await client.read_resource(server_name, uri)
            progress.remove_task(task)

        console.print(Panel(json.dumps(result, indent=2), title="Resource Content"))

    except Exception as e:
        console.print(f"[red]Error reading resource: {e}[/red]")


async def _list_prompts(client: MCPClient, server_name: str):
    """List available prompts from the server."""
    try:
        prompts = await client.list_prompts(server_name)

        if not prompts:
            console.print("[yellow]No prompts available.[/yellow]")
            return

        table = Table(title="Available Prompts")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")

        for prompt in prompts:
            table.add_row(prompt.name, prompt.description)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing prompts: {e}[/red]")


async def _get_prompt(client: MCPClient, server_name: str):
    """Get a prompt from the server."""
    try:
        # First list prompts
        prompts = await client.list_prompts(server_name)
        if not prompts:
            console.print("[yellow]No prompts available.[/yellow]")
            return

        # Show available prompts
        console.print("\n[bold]Available prompts:[/bold]")
        for i, prompt in enumerate(prompts, 1):
            console.print(f"{i}. {prompt.name} - {prompt.description}")

        # Get prompt selection
        choice = console.input("\nEnter prompt number: ")
        try:
            prompt_index = int(choice) - 1
            if prompt_index < 0 or prompt_index >= len(prompts):
                raise ValueError("Invalid prompt number")
            selected_prompt = prompts[prompt_index]
        except ValueError:
            console.print("[red]Invalid prompt number.[/red]")
            return

        # Get arguments if needed
        arguments = None
        if selected_prompt.arguments:
            console.print(
                f"\n[bold]Prompt arguments: {selected_prompt.arguments}[/bold]"
            )
            args_input = console.input(
                "Enter arguments (JSON, or press Enter for none): "
            )
            if args_input.strip():
                try:
                    arguments = json.loads(args_input)
                except json.JSONDecodeError:
                    console.print("[red]Invalid JSON format.[/red]")
                    return

        # Get the prompt
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            task = progress.add_task(
                f"Getting prompt {selected_prompt.name}...", total=None
            )
            result = await client.get_prompt(
                server_name, selected_prompt.name, arguments
            )
            progress.remove_task(task)

        console.print(Panel(json.dumps(result, indent=2), title="Prompt Content"))

    except Exception as e:
        console.print(f"[red]Error getting prompt: {e}[/red]")


@cli.command()
@click.option("--provider", "-p", help="AI provider to use (openai, anthropic, xai)")
@click.option("--server", "-s", help="MCP server to connect the agent to")
@click.pass_context
def agent(ctx, provider, server):
    """Use an AI agent that can interact with MCP servers."""
    config = ctx.obj["config"]

    if not provider:
        provider = config.default_ai_provider

    if not server:
        server = config.default_mcp_server

    asyncio.run(_agent_mode(config, provider, server))


async def _setup_mcp_client(config, server_name: str, agent) -> Optional[MCPClient]:
    """Set up MCP client and connect to server."""
    mcp_client = MCPClient(config)
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task(f"Connecting to {server_name}...", total=None)
        await mcp_client.connect_to_server(server_name)
        progress.remove_task(task)

    # Get available tools and set them for the agent
    tools = await mcp_client.list_tools(server_name)
    if tools:
        formatted_tools = []
        for tool in tools:
            formatted_tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
            )
        agent.set_available_tools(formatted_tools)
        console.print(
            f"[green]Connected to MCP server {server_name} with {len(tools)} tools[/green]"
        )

    return mcp_client


async def _handle_tool_calls(
    mcp_client: MCPClient, server_name: str, response, history_manager, conv_id
):
    """Handle tool calls from AI response."""
    if not response.tool_calls or not mcp_client:
        return

    console.print("[yellow]Agent is calling tools...[/yellow]")

    for tool_call in response.tool_calls:
        try:
            tool_result = await mcp_client.call_tool(
                server_name, tool_call["name"], tool_call["arguments"]
            )

            # Add tool result message
            tool_message = Message(
                role="tool",
                content=json.dumps(tool_result),
                tool_call_id=tool_call["id"],
            )
            history_manager.add_message(conv_id, tool_message)

        except Exception as e:
            console.print(f"[red]Tool call error: {e}[/red]")
            tool_message = Message(
                role="tool",
                content=f"Error: {str(e)}",
                tool_call_id=tool_call["id"],
            )
            history_manager.add_message(conv_id, tool_message)


async def _get_ai_response(agent, messages, mcp_client):
    """Get AI response with progress indicator."""
    ai_tools = None
    if mcp_client and agent.available_tools:
        ai_tools = agent.format_tools_for_ai(agent.available_tools)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task("Thinking...", total=None)
        response = await agent.chat_completion(messages, tools=ai_tools)
        progress.remove_task(task)

    return response


async def _agent_mode(config, provider_name: str, server_name: Optional[str]):
    """Run agent mode with AI provider."""
    try:
        # Create AI agent
        agent = create_agent(provider_name, config)
        console.print(
            f"[green]Created {provider_name} agent with model {agent.model}[/green]"
        )

        # Create MCP client and connect if server specified
        mcp_client = None
        if server_name:
            mcp_client = await _setup_mcp_client(config, server_name, agent)

        # Create history manager
        history_manager = HistoryManager(
            storage_type=config.history.storage_type,
            file_path=config.history.file_path,
            max_conversations=config.history.max_conversations,
        )

        # Create new conversation
        conv_id = history_manager.create_conversation(
            title=f"Agent Chat - {provider_name}",
            server_name=server_name,
            agent_provider=provider_name,
        )

        console.print("[bold]Agent mode activated. Type 'exit' to quit.[/bold]")

        while True:
            user_input = console.input("\n[bold blue]You:[/bold blue] ")

            if user_input.lower() in ["exit", "quit"]:
                break

            # Add user message to history
            user_message = Message(role="user", content=user_input)
            history_manager.add_message(conv_id, user_message)

            # Get conversation history
            messages = history_manager.get_conversation_messages(conv_id)

            try:
                # Get AI response
                response = await _get_ai_response(agent, messages, mcp_client)

                # Handle tool calls if any
                await _handle_tool_calls(
                    mcp_client, server_name, response, history_manager, conv_id
                )

                # If there were tool calls, get a final response after tool results
                if response.tool_calls and mcp_client:
                    messages = history_manager.get_conversation_messages(conv_id)
                    response = await _get_ai_response(agent, messages, mcp_client)

                # Add assistant response to history
                history_manager.add_message(conv_id, response)

                # Display response
                console.print(f"[bold green]Agent:[/bold green] {response.content}")

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

    except Exception as e:
        console.print(f"[red]Error in agent mode: {e}[/red]")
    finally:
        if mcp_client:
            await mcp_client.disconnect_all()


@cli.command()
@click.option("--server", "-s", help="MCP server name")
@click.pass_context
def tools(ctx, server):
    """List available tools from MCP servers."""
    config = ctx.obj["config"]

    if server:
        servers = [server]
    else:
        servers = [s.name for s in config.mcp_servers]

    asyncio.run(_list_all_tools(config, servers))


async def _list_all_tools(config, server_names: List[str]):
    """List tools from multiple servers."""
    client = MCPClient(config)

    for server_name in server_names:
        try:
            console.print(f"\n[bold]Server: {server_name}[/bold]")
            await client.connect_to_server(server_name)
            await _list_tools(client, server_name)
        except Exception as e:
            console.print(f"[red]Error with server {server_name}: {e}[/red]")

    await client.disconnect_all()


@cli.command()
@click.pass_context
def web(ctx):
    """Start the web interface."""
    config = ctx.obj["config"]

    try:
        import uvicorn

        from .web.app import create_app

        app = create_app(config)

        console.print(
            f"[green]Starting web interface at http://{config.web_interface.host}:{config.web_interface.port}[/green]"
        )

        uvicorn.run(
            app,
            host=config.web_interface.host,
            port=config.web_interface.port,
            log_level="info",
        )

    except ImportError as e:
        console.print(f"[red]Web interface dependencies not available: {e}[/red]")
        console.print("Install with: pip install fastapi uvicorn")
    except Exception as e:
        console.print(f"[red]Error starting web interface: {e}[/red]")


@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command("show")
@click.pass_context
def config_show(ctx):
    """Show current configuration."""
    try:
        config_data = ctx.parent.parent.obj.get("config")
        if not config_data:
            console.print("[yellow]No configuration loaded[/yellow]")
            return

        # Convert config to JSON for pretty printing
        config_dict = {
            "ai_providers": config_data.ai_providers,
            "mcp_servers": [
                {
                    "name": server.name,
                    "type": server.type,
                    "url": server.url,
                    "command": server.command,
                    "description": server.description,
                }
                for server in config_data.mcp_servers
            ],
            "default_ai_provider": config_data.default_ai_provider,
            "default_mcp_server": config_data.default_mcp_server,
            "web_interface": config_data.web_interface,
            "logging": config_data.logging,
            "history": config_data.history,
        }

        console.print(
            Panel(
                json.dumps(config_dict, indent=2, default=str),
                title="Current Configuration",
                border_style="blue",
            )
        )
    except Exception as e:
        console.print(f"[red]Error showing configuration: {e}[/red]")


@config.command("validate")
@click.pass_context
def config_validate(ctx):
    """Validate configuration syntax and settings."""
    config_data = _get_config_data(ctx)
    if not config_data:
        return

    console.print("[green]✓[/green] Configuration syntax is valid")

    _validate_ai_providers(config_data)
    _validate_mcp_servers(config_data)
    _validate_defaults(config_data)

    console.print("\n[green]Configuration validation complete![/green]")


def _get_config_data(ctx):
    """Get configuration data from context."""
    config_data = ctx.parent.parent.obj.get("config")
    if not config_data:
        console.print("[red]No configuration loaded[/red]")
        return None
    return config_data


def _validate_ai_providers(config_data):
    """Validate AI providers configuration."""
    if config_data.ai_providers:
        console.print("[green]✓[/green] AI providers configuration found")
        for provider_name in config_data.ai_providers.keys():
            console.print(f"  - {provider_name}")
    else:
        console.print("[yellow]⚠[/yellow] No AI providers configured")


def _validate_mcp_servers(config_data):
    """Validate MCP servers configuration."""
    if config_data.mcp_servers:
        console.print(
            f"[green]✓[/green] {len(config_data.mcp_servers)} MCP server(s) configured"
        )
        for server in config_data.mcp_servers:
            console.print(f"  - {server.name} ({server.type})")
    else:
        console.print("[yellow]⚠[/yellow] No MCP servers configured")


def _validate_defaults(config_data):
    """Validate default provider and server settings."""
    _validate_default_ai_provider(config_data)
    _validate_default_mcp_server(config_data)


def _validate_default_ai_provider(config_data):
    """Validate default AI provider setting."""
    if not config_data.default_ai_provider:
        return

    if config_data.default_ai_provider in config_data.ai_providers:
        console.print(
            f"[green]✓[/green] Default AI provider: {config_data.default_ai_provider}"
        )
    else:
        console.print(
            f"[red]✗[/red] Default AI provider '{config_data.default_ai_provider}' not found in configuration"
        )


def _validate_default_mcp_server(config_data):
    """Validate default MCP server setting."""
    if not config_data.default_mcp_server:
        return

    server_names = [s.name for s in config_data.mcp_servers]
    if config_data.default_mcp_server in server_names:
        console.print(
            f"[green]✓[/green] Default MCP server: {config_data.default_mcp_server}"
        )
    else:
        console.print(
            f"[red]✗[/red] Default MCP server '{config_data.default_mcp_server}' not found in configuration"
        )


@config.command("test-servers")
@click.pass_context
def config_test_servers(ctx):
    """Test connections to configured MCP servers."""

    async def _test_servers():
        try:
            config_data = ctx.parent.parent.obj.get("config")
            if not config_data:
                console.print("[red]No configuration loaded[/red]")
                return

            if not config_data.mcp_servers:
                console.print("[yellow]No MCP servers configured to test[/yellow]")
                return

            console.print("Testing MCP server connections...\n")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                for server_config in config_data.mcp_servers:
                    task = progress.add_task(
                        f"Testing {server_config.name}...", total=None
                    )

                    try:
                        client = MCPClient()
                        await client.connect(server_config)
                        await client.disconnect()

                        progress.update(
                            task,
                            description=f"[green]✓[/green] {server_config.name} - Connection successful",
                        )
                        progress.stop_task(task)

                    except Exception as e:
                        progress.update(
                            task,
                            description=f"[red]✗[/red] {server_config.name} - Connection failed: {e}",
                        )
                        progress.stop_task(task)

            console.print("\n[green]Server connection tests complete![/green]")

        except Exception as e:
            console.print(f"[red]Error testing servers: {e}[/red]")

    asyncio.run(_test_servers())


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
