# Lackey

Task chain management engine for AI agents with MCP integration.

## Overview

Lackey is a task chain management engine (not a database) that provides intelligent logic for managing complex task dependencies while storing all data directly in your project repository. This design enables AI agents to work within consistent, structured workflows while maintaining full human visibility and control.

## Key Features

- **Your Repository, Your Data**: All task data lives in your project repository
- **AI-First, Human-Friendly**: Designed for AI agents with human-readable formats
- **Zero Global State**: Each project is completely self-contained
- **MCP Integration**: Full Model Context Protocol support for AI agent access

## Installation

```bash
pip install lackey-mcp
```

## Quick Start

```bash
# Initialize a new project
lackey init --domain web-development --name "My Project"

# Start the MCP server
lackey serve

# Connect with your AI agent
q chat --agent manager "Let's plan the first sprint"
```

## Documentation

Full documentation is under devleopment.

## License

Proprietary License
