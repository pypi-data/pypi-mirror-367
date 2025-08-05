#!/usr/bin/env python3
"""Main CLI entry point for Lackey task chain management engine."""

import asyncio
import sys
from pathlib import Path

import click

from . import __version__


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """Lackey - Task chain management engine for AI agents.

    Lackey provides intelligent task dependency management with MCP server
    integration for AI agent collaboration.
    """
    if version:
        click.echo(f"Lackey {__version__}")
        sys.exit(0)

    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command("serve")
@click.option(
    "--workspace",
    "-w",
    default=".lackey",
    help="Workspace directory for Lackey data (default: .lackey)",
)
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Logging level (default: INFO)",
)
def serve(workspace: str, log_level: str) -> None:
    """Start the Lackey MCP server.

    This starts the MCP (Model Context Protocol) server that enables
    AI agents to interact with Lackey for task management.
    """
    # Create workspace directory if it doesn't exist
    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    click.echo("Starting Lackey MCP server...")
    click.echo(f"Workspace: {workspace_path.resolve()}")
    click.echo(f"Log level: {log_level}")
    click.echo("Server running in stdio mode for MCP compatibility")
    click.echo("Press Ctrl+C to stop")

    # Use the existing MCP server implementation
    import logging

    from .mcp.server import LackeyMCPServer

    # Set up logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    async def run_server() -> None:
        server = LackeyMCPServer(str(workspace_path))
        try:
            await server.run()
        except KeyboardInterrupt:
            logging.info("Received interrupt signal, shutting down...")
            await server.stop()
        except Exception as e:
            logging.error(f"Server error: {e}")
            sys.exit(1)

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")


@main.command("version")
def version() -> None:
    """Show version information."""
    click.echo(f"Lackey {__version__}")


@main.command("doctor")
@click.option("--workspace", "-w", default=".lackey", help="Workspace directory")
def doctor(workspace: str) -> None:
    """Check system requirements and configuration."""
    import platform
    import sys
    from pathlib import Path

    click.echo("🔍 Lackey System Check")
    click.echo("=" * 50)

    # Python version check
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    if sys.version_info >= (3, 10):
        click.echo(f"✅ Python version: {python_version} (compatible)")
    else:
        click.echo(f"❌ Python version: {python_version} (requires 3.10+)")

    # Platform info
    click.echo(f"✅ Platform: {platform.system()} {platform.release()}")

    # Workspace check
    workspace_path = Path(workspace)
    if workspace_path.exists():
        click.echo(f"✅ Workspace exists: {workspace_path.resolve()}")

        # Check workspace structure
        config_file = workspace_path / "config.yaml"
        index_file = workspace_path / "index.yaml"

        if config_file.exists():
            click.echo("✅ Configuration file found")
        else:
            click.echo("⚠️  Configuration file missing (will be created on first use)")

        if index_file.exists():
            click.echo("✅ Project index found")
        else:
            click.echo("⚠️  Project index missing (will be created on first use)")
    else:
        click.echo(f"⚠️  Workspace directory missing: {workspace_path.resolve()}")
        click.echo("   (will be created when running 'lackey serve')")

    # Dependencies check
    try:
        import yaml

        click.echo("✅ PyYAML available")
        del yaml  # Clean up namespace
    except ImportError:
        click.echo("❌ PyYAML missing")

    try:
        import networkx

        click.echo("✅ NetworkX available")
        del networkx  # Clean up namespace
    except ImportError:
        click.echo("❌ NetworkX missing")

    try:
        import mcp

        click.echo("✅ MCP library available")
        del mcp  # Clean up namespace
    except ImportError:
        click.echo("❌ MCP library missing")

    click.echo("\n💡 To start using Lackey:")
    click.echo("   1. Run 'lackey serve' to start the MCP server")
    click.echo(
        "   2. In another terminal, use Q CLI: "
        "'q chat --mcp-server \"lackey serve --workspace .lackey\"'"
    )


@main.command("init")
@click.option("--name", help="Project name")
@click.option("--description", help="Project description")
@click.option("--workspace", "-w", default=".lackey", help="Workspace directory")
def init(name: str, description: str, workspace: str) -> None:
    """Initialize a new Lackey workspace (basic implementation)."""
    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    click.echo(f"🚀 Initializing Lackey workspace at {workspace_path.resolve()}")

    # Create basic config
    config_content = f"""# Lackey Configuration
version: "0.1.0"
workspace_name: "{name or 'Lackey Workspace'}"
description: "{description or 'A Lackey task management workspace'}"
created_at: "{Path().cwd()}"

# Task management settings
task_settings:
  auto_assign_ids: true
  require_success_criteria: true
  default_complexity: "medium"

# Agent settings
agent_settings:
  create_agents: true
  default_roles: ["manager", "developer"]

# Validation settings
validation:
  level: "basic"
  strict_mode: false
"""

    config_file = workspace_path / "config.yaml"
    with open(config_file, "w") as f:
        f.write(config_content)

    # Create basic index
    index_content = """# Project Index
projects: []
"""

    index_file = workspace_path / "index.yaml"
    with open(index_file, "w") as f:
        f.write(index_content)

    click.echo("✅ Created workspace configuration")
    click.echo("✅ Created project index")
    click.echo("\nNext steps:")
    click.echo("1. Run 'lackey serve' to start the MCP server")
    click.echo("2. Use Q CLI to interact with Lackey")


if __name__ == "__main__":
    main()
