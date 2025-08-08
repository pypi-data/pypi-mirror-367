"""Anthropic Claude agent implementation."""

import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

from .base import AIAgent, Message

logger = logging.getLogger(__name__)


class AnthropicAgent(AIAgent):
    """Anthropic Claude-based AI agent."""

    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)
        if AsyncAnthropic is None:
            raise ImportError(
                "Anthropic library not installed. Install with: pip install anthropic"
            )
        self.client = AsyncAnthropic(api_key=api_key)

    def _convert_messages_to_anthropic(
        self, messages: List[Message]
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Convert internal message format to Anthropic format."""
        system_message = ""
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_msg = {
                    "role": "user" if msg.role == "user" else "assistant",
                    "content": msg.content,
                }
                anthropic_messages.append(anthropic_msg)

        return system_message, anthropic_messages

    def _convert_anthropic_message(self, anthropic_msg: Dict[str, Any]) -> Message:
        """Convert Anthropic message to internal format."""
        return Message(
            role="assistant",
            content=anthropic_msg.get("content", [{}])[0].get("text", ""),
        )

    async def chat_completion(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Message:
        """Generate a chat completion using Anthropic Claude."""
        try:
            system_message, anthropic_messages = self._convert_messages_to_anthropic(
                messages
            )

            kwargs = {
                "model": self.model,
                "messages": anthropic_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            if system_message:
                kwargs["system"] = system_message

            if tools:
                # Convert tools to Anthropic format
                anthropic_tools = []
                for tool in tools:
                    if tool.get("type") == "function":
                        func = tool.get("function", {})
                        anthropic_tools.append(
                            {
                                "name": func.get("name", ""),
                                "description": func.get("description", ""),
                                "input_schema": func.get("parameters", {}),
                            }
                        )
                kwargs["tools"] = anthropic_tools

            response = await self.client.messages.create(**kwargs)

            # Handle tool calls if present
            tool_calls = None
            content = ""

            for content_block in response.content:
                if content_block.type == "text":
                    content += content_block.text
                elif content_block.type == "tool_use":
                    if tool_calls is None:
                        tool_calls = []
                    tool_calls.append(
                        {
                            "id": content_block.id,
                            "name": content_block.name,
                            "arguments": content_block.input,
                        }
                    )

            return Message(role="assistant", content=content, tool_calls=tool_calls)

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def stream_chat_completion(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming chat completion using Anthropic Claude."""
        try:
            system_message, anthropic_messages = self._convert_messages_to_anthropic(
                messages
            )

            kwargs = {
                "model": self.model,
                "messages": anthropic_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
            }

            if system_message:
                kwargs["system"] = system_message

            if tools:
                # Convert tools to Anthropic format
                anthropic_tools = []
                for tool in tools:
                    if tool.get("type") == "function":
                        func = tool.get("function", {})
                        anthropic_tools.append(
                            {
                                "name": func.get("name", ""),
                                "description": func.get("description", ""),
                                "input_schema": func.get("parameters", {}),
                            }
                        )
                kwargs["tools"] = anthropic_tools

            stream = await self.client.messages.create(**kwargs)

            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    if hasattr(chunk.delta, "text"):
                        yield chunk.delta.text

        except Exception as e:
            logger.error(f"Anthropic streaming API error: {e}")
            raise
