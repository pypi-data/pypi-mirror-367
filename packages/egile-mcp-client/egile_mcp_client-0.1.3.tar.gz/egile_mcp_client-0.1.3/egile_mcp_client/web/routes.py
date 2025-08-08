"""API routes for the web interface."""

import asyncio
import json
import logging
import uuid
from typing import Dict, Optional

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:
    FastAPI = None
    HTTPException = None
    BaseModel = None

from ..agents.anthropic_agent import AnthropicAgent
from ..agents.base import Message
from ..agents.openai_agent import OpenAIAgent
from ..agents.xai_agent import XAIAgent

logger = logging.getLogger(__name__)


class SessionRequest(BaseModel):
    """Request to start a new session."""

    mode: str  # "agent" or "direct"
    provider: Optional[str] = None  # AI provider for agent mode
    server: Optional[str] = None  # MCP server name


class ChatRequest(BaseModel):
    """Request to send a chat message."""

    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Response from chat."""

    response: str
    tool_calls: Optional[list] = None


# Global sessions storage (in production, use Redis or database)
sessions: Dict[str, dict] = {}


def create_agent(provider_name: str, config) -> object:
    """Create an AI agent based on provider name."""
    provider_config = config.ai_providers.get(provider_name)
    if not provider_config:
        raise ValueError(f"AI provider {provider_name} not configured")

    # Debug: Log the API key being used
    logger.info(
        f"Creating {provider_name} agent with API key: {provider_config.api_key[:10]}..."
    )

    if provider_name == "openai":
        return OpenAIAgent(provider_config.model, provider_config.api_key)
    elif provider_name == "anthropic":
        return AnthropicAgent(provider_config.model, provider_config.api_key)
    elif provider_name == "xai":
        return XAIAgent(provider_config.model, provider_config.api_key)
    else:
        raise ValueError(f"Unsupported AI provider: {provider_name}")


def create_api_routes(app):
    """Create API routes for the web interface."""
    if FastAPI is None:
        return

    @app.get("/api/servers")
    async def get_servers():
        """Get available MCP servers."""
        config = app.state.app_state.config
        return {"servers": [s.name for s in config.mcp_servers]}

    @app.get("/api/providers")
    async def get_providers():
        """Get available AI providers."""
        config = app.state.app_state.config
        return {"providers": list(config.ai_providers.keys())}

    @app.post("/api/sessions")
    async def create_session(request: SessionRequest):
        """Create a new chat session."""
        try:
            session_id = str(uuid.uuid4())
            app_state = app.state.app_state
            config = app_state.config

            session_data = {
                "id": session_id,
                "mode": request.mode,
                "provider": request.provider,
                "server": request.server,
                "conversation_id": None,
                "agent": None,
                "mcp_connected": False,
            }

            # Create conversation in history
            title = f"{request.mode.title()} Chat"
            if request.provider:
                title += f" - {request.provider}"
            if request.server:
                title += f" - {request.server}"

            conv_id = app_state.history_manager.create_conversation(
                title=title, server_name=request.server, agent_provider=request.provider
            )
            session_data["conversation_id"] = conv_id

            # Setup agent if in agent mode
            if request.mode == "agent" and request.provider:
                try:
                    agent = create_agent(request.provider, config)
                    session_data["agent"] = agent
                except Exception as e:
                    logger.error(f"Failed to create agent: {e}")
                    raise HTTPException(
                        status_code=400, detail=f"Failed to create agent: {e}"
                    )

            # Connect to MCP server if specified
            if request.server:
                try:
                    await app_state.mcp_client.connect_to_server(request.server)
                    session_data["mcp_connected"] = True

                    # If agent mode, get tools and set them for the agent
                    if request.mode == "agent" and session_data["agent"]:
                        tools = await app_state.mcp_client.list_tools(request.server)
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
                            session_data["agent"].set_available_tools(formatted_tools)

                except Exception as e:
                    logger.error(f"Failed to connect to MCP server: {e}")
                    # Continue without MCP connection
                    session_data["mcp_connected"] = False

            sessions[session_id] = session_data

            return {"session_id": session_id, "status": "created"}

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/chat")
    async def chat(request: ChatRequest):
        """Handle chat message."""
        try:
            session = sessions.get(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")

            app_state = app.state.app_state
            conv_id = session["conversation_id"]

            # Add user message to history
            user_message = Message(role="user", content=request.message)
            app_state.history_manager.add_message(conv_id, user_message)

            if session["mode"] == "agent" and session["agent"]:
                # Agent mode
                return await _handle_agent_chat(session, app_state, conv_id)
            else:
                # Direct mode - for now, just echo
                response_content = f"Direct mode response to: {request.message}"
                response_message = Message(role="assistant", content=response_content)
                app_state.history_manager.add_message(conv_id, response_message)

                return ChatResponse(response=response_content)

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/sessions/{session_id}")
    async def delete_session(session_id: str):
        """Delete a chat session."""
        if session_id in sessions:
            del sessions[session_id]
            return {"status": "deleted"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")

    @app.get("/api/sessions/{session_id}/history")
    async def get_session_history(session_id: str):
        """Get chat history for a session."""
        session = sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        app_state = app.state.app_state
        conv_id = session["conversation_id"]
        messages = app_state.history_manager.get_conversation_messages(conv_id)

        return {
            "messages": [
                {"role": msg.role, "content": msg.content, "tool_calls": msg.tool_calls}
                for msg in messages
            ]
        }

    @app.delete("/api/sessions/{session_id}/history")
    async def clear_session_history(session_id: str):
        """Clear chat history for a session."""
        session = sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        app_state = app.state.app_state
        conv_id = session["conversation_id"]

        # Clear the conversation history
        app_state.history_manager.clear_conversation(conv_id)

        return {"status": "history cleared"}


async def _handle_agent_chat(session: dict, app_state, conv_id: str) -> ChatResponse:
    """Handle chat in agent mode."""
    agent = session["agent"]
    server_name = session["server"]

    # Get conversation history
    messages = app_state.history_manager.get_conversation_messages(conv_id)

    # Prepare tools for AI if MCP server is connected
    ai_tools = None
    if session["mcp_connected"] and agent.available_tools:
        ai_tools = agent.format_tools_for_ai(agent.available_tools)

    # Get AI response
    response = await agent.chat_completion(messages, tools=ai_tools)
    logger.info(f"Agent response content: '{response.content}'")
    logger.info(f"Agent response tool_calls: {response.tool_calls}")

    # Handle tool calls if any
    if response.tool_calls and session["mcp_connected"]:
        # First, add the assistant's response with tool calls to history
        app_state.history_manager.add_message(conv_id, response)

        for tool_call in response.tool_calls:
            try:
                tool_result = await app_state.mcp_client.call_tool(
                    server_name, tool_call["name"], tool_call["arguments"]
                )
                logger.info(f"Tool '{tool_call['name']}' result: {tool_result}")

                # Add tool result message
                tool_message = Message(
                    role="tool",
                    content=json.dumps(tool_result),
                    tool_call_id=tool_call["id"],
                )
                logger.info(f"Tool message content: {tool_message.content}")
                app_state.history_manager.add_message(conv_id, tool_message)

            except Exception as e:
                logger.error(f"Tool call error: {e}")
                tool_message = Message(
                    role="tool", content=f"Error: {e}", tool_call_id=tool_call["id"]
                )
                app_state.history_manager.add_message(conv_id, tool_message)

        # Get final response after tool calls
        messages = app_state.history_manager.get_conversation_messages(conv_id)
        response = await agent.chat_completion(messages, tools=ai_tools)
        logger.info(f"Final agent response content: '{response.content}'")
        logger.info(f"Final agent response tool_calls: {response.tool_calls}")

    # Add assistant response to history
    app_state.history_manager.add_message(conv_id, response)

    return ChatResponse(response=response.content, tool_calls=response.tool_calls)
