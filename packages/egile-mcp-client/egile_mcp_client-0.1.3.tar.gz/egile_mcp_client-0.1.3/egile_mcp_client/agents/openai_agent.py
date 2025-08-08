"""OpenAI agent implementation."""

import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from .base import AIAgent, Message, ToolCall

logger = logging.getLogger(__name__)


class OpenAIAgent(AIAgent):
    """OpenAI-based AI agent."""

    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)
        if AsyncOpenAI is None:
            raise ImportError(
                "OpenAI library not installed. Install with: pip install openai"
            )
        self.client = AsyncOpenAI(api_key=api_key)

    def _convert_messages_to_openai(
        self, messages: List[Message]
    ) -> List[Dict[str, Any]]:
        """Convert internal message format to OpenAI format."""
        openai_messages = []

        for msg in messages:
            openai_msg = {"role": msg.role, "content": msg.content}

            if msg.tool_calls:
                openai_msg["tool_calls"] = []
                for tool_call in msg.tool_calls:
                    openai_msg["tool_calls"].append(
                        {
                            "id": tool_call.get("id", ""),
                            "type": "function",
                            "function": {
                                "name": tool_call.get("name", ""),
                                "arguments": json.dumps(tool_call.get("arguments", {})),
                            },
                        }
                    )

            if msg.tool_call_id:
                openai_msg["tool_call_id"] = msg.tool_call_id

            openai_messages.append(openai_msg)

        return openai_messages

    def _convert_openai_message(self, openai_msg: Dict[str, Any]) -> Message:
        """Convert OpenAI message to internal format."""
        tool_calls = None
        if openai_msg.get("tool_calls"):
            tool_calls = []
            for tool_call in openai_msg["tool_calls"]:
                tool_calls.append(
                    {
                        "id": tool_call["id"],
                        "name": tool_call["function"]["name"],
                        "arguments": json.loads(tool_call["function"]["arguments"]),
                    }
                )

        return Message(
            role=openai_msg["role"],
            content=openai_msg.get("content", "") or "",
            tool_calls=tool_calls,
        )

    async def chat_completion(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Message:
        """Generate a chat completion using OpenAI."""
        try:
            openai_messages = self._convert_messages_to_openai(messages)

            kwargs = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = await self.client.chat.completions.create(**kwargs)

            choice = response.choices[0]
            return self._convert_openai_message(choice.message.model_dump())

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def stream_chat_completion(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming chat completion using OpenAI."""
        try:
            openai_messages = self._convert_messages_to_openai(messages)

            kwargs = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            stream = await self.client.chat.completions.create(**kwargs)

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming API error: {e}")
            raise
