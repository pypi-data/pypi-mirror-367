# Egile MCP Client

A comprehensive Model Context Protocol (MCP) client that provides two operational modes and a web interface for interacting with MCP servers.

## Features

- **Two Operation Modes**:
  - **Direct Mode**: Connect directly to MCP server tools and resources
  - **Agent Mode**: Use a generic AI agent that works with any MCP server
- **Multiple Interfaces**:
  - **Terminal CLI**: Command-line interface for both modes
  - **Web Chat Interface**: Browser-based chatbot with conversation history
- **AI Provider Support**: OpenAI, Anthropic Claude, xAI Grok, and extensible for other providers
- **Conversation History**: Persistent chat history across sessions
- **Real-time Communication**: WebSocket support for live interactions

## Quick Start

### Installation

```bash
# Install dependencies
pip install -e .

# Or using poetry
poetry install
```

### Configuration

Create a `config.yaml` file:

```yaml
# AI Providers (for agent mode)
ai_providers:
  openai:
    api_key: "your-openai-api-key"
    model: "gpt-4"
  anthropic:
    api_key: "your-anthropic-api-key"
    model: "claude-3-sonnet-20240229"
  xai:
    api_key: "your-xai-api-key"
    model: "grok-3"

# MCP Servers
mcp_servers:
  - name: "example_server"
    url: "http://localhost:8000"
    type: "http"
  - name: "local_server"
    command: ["python", "/path/to/server/main.py"]
    type: "stdio"

# Default settings
default_ai_provider: "openai"
web_interface:
  host: "localhost"
  port: 8080
```

### Usage

#### Terminal Interface

```bash
# Direct mode - connect directly to MCP server
egile-mcp-client direct --server example_server

# Agent mode - use AI agent with MCP tools
egile-mcp-client agent --provider openai

# List available tools from a server
egile-mcp-client tools --server example_server

# Interactive chat in terminal
egile-mcp-client chat --mode agent --provider openai
```

#### Web Interface

```bash
# Start the web server
egile-mcp-client web

# Then open http://localhost:8080 in your browser
```

## Architecture

```
egile-mcp-client/
├── egile_mcp_client/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration management
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── client.py       # MCP client implementation
│   │   ├── connection.py   # Connection management
│   │   └── protocol.py     # MCP protocol handling
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py         # Base agent interface
│   │   ├── openai_agent.py # OpenAI implementation
│   │   └── anthropic_agent.py # Anthropic implementation
│   ├── web/
│   │   ├── __init__.py
│   │   ├── app.py          # FastAPI web application
│   │   ├── routes.py       # API routes
│   │   ├── static/         # Static files (CSS, JS)
│   │   └── templates/      # HTML templates
│   └── utils/
│       ├── __init__.py
│       ├── history.py      # Conversation history
│       └── logging.py      # Logging utilities
├── tests/
├── config.example.yaml
└── README.md
```

## License

MIT License
