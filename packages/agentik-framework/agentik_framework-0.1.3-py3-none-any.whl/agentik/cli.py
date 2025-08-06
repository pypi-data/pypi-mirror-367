# agentik/cli.py

"""
CLI for the Agentik Framework.

Provides commands to:
- Run an agent from config
- List available tools
- Create new agent YAML configurations
- Explain memory backends
"""

import typer
from pathlib import Path
from typing import Optional
import pkgutil
import importlib

import agentik.tools
from agentik.config import load_agent_config
from agentik.tools import Tool

# Initialize Typer CLI application
app = typer.Typer(help="Agentik – Modular Agent Framework CLI")


@app.command()
def run(config: str, verbose: bool = False, dry_run: bool = False):
    """
    Run an agent using the specified YAML/JSON configuration file.

    Args:
        config (str): Path to the agent configuration file.
        verbose (bool): If set, prints detailed logs.
        dry_run (bool): If set, does not execute the agent loop.
    """
    config_path = Path(config)
    if not config_path.exists():
        typer.echo(f"[Error] Config file not found: {config}")
        raise typer.Exit(code=1)

    agent = load_agent_config(config)

    typer.echo(f"Starting Agent '{agent.name}' with goal: {agent.goal}")
    if verbose:
        typer.echo("[Verbose Mode Enabled]")

    if dry_run:
        typer.echo("[Dry Run] Exiting without execution.")
        return

    # Prompt user for initial input
    prompt = typer.prompt("Enter your initial prompt")
    agent.run(prompt)


@app.command("list-tools")
def list_tools():
    """
    List all available tool classes in the agentik.tools module.
    """
    typer.echo("Available Tools:")

    tool_classes = []

    # Dynamically load tool classes from agentik.tools.*
    for _, modname, _ in pkgutil.iter_modules(agentik.tools.__path__):
        try:
            module = importlib.import_module(f"agentik.tools.{modname}")
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, Tool) and obj is not Tool:
                    tool_classes.append(obj)
        except Exception as e:
            typer.echo(f"[Warning] Failed to load tool '{modname}': {e}")

    if not tool_classes:
        typer.echo("No tools found.")
    else:
        for tool in tool_classes:
            typer.echo(f"- {tool.name}: {tool.description}")


@app.command("create-agent")
def create_agent():
    """
    Create a new agent YAML configuration file interactively.
    """
    name = typer.prompt("Agent name")
    goal = typer.prompt("Agent goal")
    llm_type = typer.prompt("LLM type (openai/claude/mistral/deepseek/local)")
    api_key = typer.prompt("API Key (leave blank for local)", default="", show_default=False)
    tools = typer.prompt("Tools (comma-separated, e.g., calculator,websearch)")
    memory_type = typer.prompt("Memory type (dict/json/none)", default="json")

    # Format tools as YAML list
    tool_list = ''.join([f'  - {t.strip()}\n' for t in tools.split(",") if t.strip()])

    # Build config string
    config_data = (
        f'name: "{name}"\n'
        f'goal: "{goal}"\n'
        f'llm:\n'
        f'  type: {llm_type}\n'
        f'  api_key: "{api_key}"\n'
        f'  model: gpt-3.5-turbo\n'
        f'tools:\n'
        f'{tool_list}'
        f'memory:\n'
        f'  type: {memory_type}\n'
        f'  path: "memory.json"\n'
    )

    # Write to file
    out_file = Path(f"configs/{name.lower()}_agent.yaml")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(config_data)
    typer.echo(f"Created new agent config: {out_file}")


@app.command("explain-memory")
def explain_memory():
    """
    Display a summary of supported memory backends.
    """
    typer.echo(
        "\nMemory Backends in Agentik:\n\n"
        "1. DictMemory   – In-memory (temporary, resets each run)\n"
        "2. JSONMemory   – Persistent JSON file storage\n"
        "3. CustomMemory – Extend MemoryBase in memory.py for your own implementation\n"
    )


def main():
    """
    Entry point for CLI execution.
    """
    app()


if __name__ == "__main__":
    main()
