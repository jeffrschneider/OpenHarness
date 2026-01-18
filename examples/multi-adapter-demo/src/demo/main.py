#!/usr/bin/env python3
"""Open Harness Multi-Adapter Demo CLI.

This demo showcases the unified Open Harness API across multiple
AI agent harnesses: Anthropic Agent SDK, Letta, Goose, and Deep Agent.
"""

from __future__ import annotations

import asyncio
import sys
from typing import TYPE_CHECKING

import click
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from demo.adapters import ADAPTER_INFO, create_adapter, get_available_adapters

if TYPE_CHECKING:
    from openharness import HarnessAdapter

console = Console()


def print_header():
    """Print the demo header."""
    console.print()
    console.print(
        Panel.fit(
            "[bold blue]Open Harness[/bold blue] Multi-Adapter Demo\n"
            "[dim]One API, Many Harnesses[/dim]",
            border_style="blue",
        )
    )
    console.print()


def print_adapters_table(available: list[str]):
    """Print table of available adapters."""
    table = Table(title="Available Adapters", show_header=True, header_style="bold cyan")
    table.add_column("Adapter", style="bold")
    table.add_column("Package")
    table.add_column("Description")
    table.add_column("Status", justify="center")

    for key, info in ADAPTER_INFO.items():
        status = "[green]Ready[/green]" if key in available else "[dim]Not installed[/dim]"
        table.add_row(
            info["name"],
            info["package"],
            info["description"],
            status,
        )

    console.print(table)
    console.print()


def print_capabilities(adapter: HarnessAdapter):
    """Print adapter capabilities."""
    caps = adapter.capabilities

    table = Table(title="Adapter Capabilities", show_header=True, header_style="bold cyan")
    table.add_column("Capability")
    table.add_column("Supported", justify="center")

    for field in [
        "execution", "streaming", "sessions", "memory", "mcp",
        "files", "skills", "agents", "subagents", "planning",
    ]:
        value = getattr(caps, field, False)
        status = "[green]✓[/green]" if value else "[dim]—[/dim]"
        table.add_row(field.capitalize(), status)

    console.print(table)
    console.print()


async def run_streaming_demo(adapter: HarnessAdapter, message: str):
    """Run a streaming execution demo."""
    from openharness import ExecuteRequest

    console.print(f"[bold]User:[/bold] {message}")
    console.print()
    console.print("[bold]Assistant:[/bold] ", end="")

    response_text = ""

    try:
        async for event in adapter.execute_stream(ExecuteRequest(message=message)):
            if event.type == "text":
                content = event.content
                console.print(content, end="")
                response_text += content
            elif event.type == "tool_call_start":
                console.print(f"\n[dim]→ Calling tool: {event.name}[/dim]")
            elif event.type == "tool_call_end":
                console.print(f"[dim]→ Tool completed[/dim]")
            elif event.type == "error":
                console.print(f"\n[red]Error: {event.message}[/red]")

        console.print()
        console.print()

    except Exception as e:
        console.print(f"\n[red]Error during streaming: {e}[/red]")
        raise


async def run_sync_demo(adapter: HarnessAdapter, message: str):
    """Run a synchronous execution demo."""
    from openharness import ExecuteRequest

    console.print(f"[bold]User:[/bold] {message}")
    console.print()

    with console.status("[bold blue]Thinking...[/bold blue]"):
        result = await adapter.execute(ExecuteRequest(message=message))

    console.print("[bold]Assistant:[/bold]")
    console.print(Markdown(result.content))
    console.print()

    if result.tool_calls:
        console.print(f"[dim]Tools called: {len(result.tool_calls)}[/dim]")
        for tc in result.tool_calls:
            console.print(f"[dim]  • {tc.name}[/dim]")
        console.print()


async def interactive_mode(adapter: HarnessAdapter, adapter_name: str):
    """Run interactive chat mode."""
    info = ADAPTER_INFO.get(adapter_name, {})
    console.print(
        Panel(
            f"[bold]{info.get('name', adapter_name)}[/bold]\n"
            f"[dim]{info.get('description', '')}[/dim]\n\n"
            "Type your message and press Enter. Type 'quit' to exit.",
            title="Interactive Mode",
            border_style="green",
        )
    )
    console.print()

    while True:
        try:
            message = console.input("[bold cyan]You:[/bold cyan] ")

            if message.lower() in ("quit", "exit", "q"):
                console.print("[dim]Goodbye![/dim]")
                break

            if not message.strip():
                continue

            console.print()
            console.print("[bold green]Assistant:[/bold green] ", end="")

            from openharness import ExecuteRequest

            async for event in adapter.execute_stream(ExecuteRequest(message=message)):
                if event.type == "text":
                    console.print(event.content, end="")
                elif event.type == "tool_call_start":
                    console.print(f"\n[dim]→ {event.name}[/dim]", end="")

            console.print("\n")

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Goodbye![/dim]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")


async def compare_adapters(message: str, adapters: list[str]):
    """Compare responses across multiple adapters."""
    from openharness import ExecuteRequest

    console.print(f"[bold]Prompt:[/bold] {message}")
    console.print()

    results = {}

    for adapter_name in adapters:
        try:
            adapter = create_adapter(adapter_name)
            info = ADAPTER_INFO.get(adapter_name, {})

            console.print(f"[bold blue]{info.get('name', adapter_name)}[/bold blue]")
            console.print("[dim]" + "─" * 40 + "[/dim]")

            response = ""
            async for event in adapter.execute_stream(ExecuteRequest(message=message)):
                if event.type == "text":
                    console.print(event.content, end="")
                    response += event.content

            console.print("\n")
            results[adapter_name] = response

        except ImportError:
            console.print(f"[yellow]Skipped (not installed)[/yellow]\n")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")

    return results


@click.group()
def cli():
    """Open Harness Multi-Adapter Demo.

    Demonstrates the unified Open Harness API across multiple AI agent harnesses.
    """
    pass


@cli.command()
def list():
    """List available adapters and their status."""
    print_header()
    available = get_available_adapters()
    print_adapters_table(available)

    if not available:
        console.print("[yellow]No adapters installed. Install with:[/yellow]")
        console.print("  pip install openharness-letta openharness-goose openharness-deepagent")
    else:
        console.print(f"[green]{len(available)} adapter(s) ready to use[/green]")


@cli.command()
@click.argument("adapter_type", type=click.Choice(["anthropic", "letta", "goose", "deepagent"]))
def capabilities(adapter_type: str):
    """Show capabilities for a specific adapter."""
    print_header()

    try:
        adapter = create_adapter(adapter_type)
        info = ADAPTER_INFO.get(adapter_type, {})

        console.print(f"[bold]{info.get('name', adapter_type)}[/bold]")
        console.print(f"[dim]{info.get('description', '')}[/dim]")
        console.print()

        print_capabilities(adapter)

        strengths = info.get("strengths", [])
        if strengths:
            console.print("[bold]Key Strengths:[/bold]")
            for s in strengths:
                console.print(f"  • {s}")

    except ImportError:
        console.print(f"[red]Adapter '{adapter_type}' is not installed[/red]")
        console.print(f"Install with: pip install {ADAPTER_INFO[adapter_type]['package']}")


@cli.command()
@click.argument("adapter_type", type=click.Choice(["anthropic", "letta", "goose", "deepagent"]))
@click.option("--message", "-m", default="Hello! What can you help me with today?")
@click.option("--stream/--no-stream", default=True, help="Use streaming output")
def run(adapter_type: str, message: str, stream: bool):
    """Run a single message through an adapter."""
    print_header()

    try:
        adapter = create_adapter(adapter_type)
        info = ADAPTER_INFO.get(adapter_type, {})

        console.print(f"[dim]Using {info.get('name', adapter_type)}[/dim]")
        console.print()

        if stream:
            asyncio.run(run_streaming_demo(adapter, message))
        else:
            asyncio.run(run_sync_demo(adapter, message))

    except ImportError:
        console.print(f"[red]Adapter '{adapter_type}' is not installed[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("adapter_type", type=click.Choice(["anthropic", "letta", "goose", "deepagent"]))
def chat(adapter_type: str):
    """Start an interactive chat session."""
    print_header()

    try:
        adapter = create_adapter(adapter_type)
        asyncio.run(interactive_mode(adapter, adapter_type))

    except ImportError:
        console.print(f"[red]Adapter '{adapter_type}' is not installed[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def _run_single_adapter(adapter_name: str, message: str) -> str:
    """Run a single adapter in isolation. Called via subprocess."""
    import os

    # Reset argv to prevent langgraph from parsing it
    sys.argv = [sys.argv[0]]

    try:
        from openharness import ExecuteRequest
        adapter = create_adapter(adapter_name)

        response_parts = []

        async def _execute():
            async for event in adapter.execute_stream(ExecuteRequest(message=message)):
                if event.type == "text":
                    response_parts.append(event.content)

        asyncio.run(_execute())
        return "".join(response_parts)
    except Exception as e:
        return f"[ERROR] {e}"


@cli.command()
@click.option("--message", "-m", default="Explain the concept of recursion in one sentence.")
@click.option("--adapters", "-a", multiple=True, type=click.Choice(["anthropic", "letta", "goose", "deepagent"]))
def compare(message: str, adapters: tuple[str, ...]):
    """Compare responses across multiple adapters."""
    import subprocess
    import json

    print_header()

    available = get_available_adapters()

    if not adapters:
        adapters = tuple(available)

    if not adapters:
        console.print("[yellow]No adapters available for comparison[/yellow]")
        sys.exit(1)

    console.print(f"[dim]Comparing {len(adapters)} adapter(s)...[/dim]")
    console.print()
    console.print(f"[bold]Prompt:[/bold] {message}")
    console.print()

    for adapter_name in adapters:
        info = ADAPTER_INFO.get(adapter_name, {})
        console.print(f"[bold blue]{info.get('name', adapter_name)}[/bold blue]")
        console.print("[dim]" + "─" * 40 + "[/dim]")

        # Run each adapter in a subprocess to isolate click context
        script = f'''
import sys
sys.argv = [sys.argv[0]]  # Clear argv before imports
import asyncio
from demo.adapters import create_adapter
from openharness import ExecuteRequest

adapter = create_adapter("{adapter_name}")

async def run():
    async for event in adapter.execute_stream(ExecuteRequest(message="""{message.replace('"', '\\"')}""")):
        if event.type == "text":
            print(event.content, end="", flush=True)

asyncio.run(run())
'''
        try:
            result = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=False,
                text=True,
                cwd="/Users/jeffschneider/Desktop/OpenHarness/examples/multi-adapter-demo",
                env={**dict(__import__('os').environ), "PYTHONPATH": "src"},
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            console.print("[red]Timeout[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

        console.print("\n")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
