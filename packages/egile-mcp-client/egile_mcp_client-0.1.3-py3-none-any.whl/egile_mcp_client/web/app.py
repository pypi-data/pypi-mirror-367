"""FastAPI web application for the MCP client."""

import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from pydantic import BaseModel
except ImportError:
    FastAPI = None
    HTTPException = None
    Request = None
    StaticFiles = None
    Jinja2Templates = None
    HTMLResponse = None
    BaseModel = None

from ..agents.anthropic_agent import AnthropicAgent
from ..agents.base import AIAgent, Message
from ..agents.openai_agent import OpenAIAgent
from ..config import Config
from ..mcp.client import MCPClient
from ..utils.history import HistoryManager
from .routes import create_api_routes

logger = logging.getLogger(__name__)


class AppState:
    """Application state container."""

    def __init__(self, config: Config):
        self.config = config
        self.mcp_client = MCPClient(config)
        self.history_manager = HistoryManager(
            storage_type=config.history.storage_type,
            file_path=config.history.file_path,
            max_conversations=config.history.max_conversations,
        )
        self.agents: Dict[str, AIAgent] = {}
        self.connected_servers: Dict[str, bool] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting MCP Client web application")
    yield
    # Shutdown
    logger.info("Shutting down MCP Client web application")
    if hasattr(app.state, "app_state"):
        await app.state.app_state.mcp_client.disconnect_all()


def create_app(config: Config) -> FastAPI:
    """Create and configure the FastAPI application."""
    if FastAPI is None:
        raise ImportError(
            "FastAPI dependencies not available. Install with: pip install fastapi uvicorn jinja2 aiofiles"
        )

    app = FastAPI(
        title="Egile MCP Client",
        description="Web interface for interacting with MCP servers",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Store app state
    app.state.app_state = AppState(config)

    # Setup static files and templates
    try:
        from pathlib import Path

        web_dir = Path(__file__).parent
        static_dir = web_dir / "static"
        templates_dir = web_dir / "templates"

        if static_dir.exists():
            app.mount("/static", StaticFiles(directory=static_dir), name="static")

        if templates_dir.exists():
            templates = Jinja2Templates(directory=templates_dir)
        else:
            templates = None
    except Exception as e:
        logger.warning(f"Could not setup static files/templates: {e}")
        templates = None

    # Add API routes
    create_api_routes(app)

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        """Home page."""
        if templates:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "title": config.web_interface.title,
                    "servers": [s.name for s in config.mcp_servers],
                    "ai_providers": list(config.ai_providers.keys()),
                },
            )
        else:
            return HTMLResponse(
                """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Egile MCP Client</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 20px; margin: 20px 0; }
                    .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
                    .user-message { background: #e3f2fd; text-align: right; }
                    .assistant-message { background: #f1f8e9; }
                    .input-container { display: flex; gap: 10px; }
                    .input-container input { flex: 1; padding: 10px; }
                    .input-container button { padding: 10px 20px; }
                    .controls { margin: 20px 0; }
                    .controls select, .controls button { margin: 5px; padding: 5px 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Egile MCP Client</h1>
                    <div class="controls">
                        <label>Mode:</label>
                        <select id="mode">
                            <option value="agent">Agent Mode</option>
                            <option value="direct">Direct Mode</option>
                        </select>
                        
                        <label>AI Provider:</label>
                        <select id="provider">
                            <option value="openai">OpenAI</option>
                            <option value="anthropic">Anthropic</option>
                        </select>
                        
                        <label>MCP Server:</label>
                        <select id="server">
                            <option value="">None</option>
                        </select>
                        
                        <button onclick="startSession()">Start Session</button>
                        <button onclick="clearChat()">Clear Chat</button>
                    </div>
                    
                    <div id="chat-container" class="chat-container">
                        <div class="message assistant-message">
                            Welcome to Egile MCP Client! Select your settings and start a session.
                        </div>
                    </div>
                    
                    <div class="input-container">
                        <input type="text" id="message-input" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
                        <button onclick="sendMessage()">Send</button>
                    </div>
                </div>
                
                <script>
                    let sessionId = null;
                    
                    async function startSession() {
                        const mode = document.getElementById('mode').value;
                        const provider = document.getElementById('provider').value;
                        const server = document.getElementById('server').value;
                        
                        try {
                            const response = await fetch('/api/sessions', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ mode, provider, server })
                            });
                            
                            if (response.ok) {
                                const data = await response.json();
                                sessionId = data.session_id;
                                addMessage('assistant', 'Session started! You can now start chatting.');
                            } else {
                                addMessage('assistant', 'Error starting session. Please check your configuration.');
                            }
                        } catch (error) {
                            addMessage('assistant', 'Error: ' + error.message);
                        }
                    }
                    
                    async function sendMessage() {
                        const input = document.getElementById('message-input');
                        const message = input.value.trim();
                        
                        if (!message || !sessionId) return;
                        
                        addMessage('user', message);
                        input.value = '';
                        
                        try {
                            const response = await fetch('/api/chat', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ session_id: sessionId, message })
                            });
                            
                            if (response.ok) {
                                const data = await response.json();
                                addMessage('assistant', data.response);
                            } else {
                                addMessage('assistant', 'Error processing message.');
                            }
                        } catch (error) {
                            addMessage('assistant', 'Error: ' + error.message);
                        }
                    }
                    
                    function addMessage(role, content) {
                        const container = document.getElementById('chat-container');
                        const message = document.createElement('div');
                        message.className = `message ${role}-message`;
                        message.textContent = content;
                        container.appendChild(message);
                        container.scrollTop = container.scrollHeight;
                    }
                    
                    function clearChat() {
                        const container = document.getElementById('chat-container');
                        container.innerHTML = '<div class="message assistant-message">Chat cleared. Start a new session when ready.</div>';
                        sessionId = null;
                    }
                    
                    function handleKeyPress(event) {
                        if (event.key === 'Enter') {
                            sendMessage();
                        }
                    }
                    
                    // Load available servers
                    fetch('/api/servers')
                        .then(response => response.json())
                        .then(data => {
                            const select = document.getElementById('server');
                            data.servers.forEach(server => {
                                const option = document.createElement('option');
                                option.value = server;
                                option.textContent = server;
                                select.appendChild(option);
                            });
                        })
                        .catch(error => console.error('Error loading servers:', error));
                </script>
            </body>
            </html>
            """
            )

    return app


def main():
    """Main entry point for the web application."""
    import uvicorn

    from ..config import load_config

    # Explicitly load .env file before loading config
    try:
        from pathlib import Path

        from dotenv import load_dotenv

        env_path = Path.cwd() / ".env"
        if env_path.exists():
            print(f"Manually loading .env from: {env_path}")
            load_dotenv(env_path, override=True)
        else:
            print(f".env not found at: {env_path}")
    except ImportError:
        print("dotenv not available")

    config = load_config()

    # Debug: Print the configuration being used
    print("=== WEB SERVER STARTUP DEBUG ===")
    print(f"xAI API Key: {config.ai_providers['xai'].api_key[:15]}...")
    print(f"xAI Model: {config.ai_providers['xai'].model}")
    print("=== END DEBUG ===")

    app = create_app(config)

    uvicorn.run(
        app,
        host=config.web_interface.host,
        port=config.web_interface.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
