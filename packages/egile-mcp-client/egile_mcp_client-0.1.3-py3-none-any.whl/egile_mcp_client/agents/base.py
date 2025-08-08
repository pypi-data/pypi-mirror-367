"""Base agent interface for AI providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional


@dataclass
class Message:
    """Chat message structure."""

    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


@dataclass
class ToolCall:
    """Tool call structure."""

    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolResult:
    """Tool execution result."""

    tool_call_id: str
    content: str
    is_error: bool = False


class AIAgent(ABC):
    """Abstract base class for AI agents."""

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        self.available_tools: List[Dict[str, Any]] = []

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Message:
        """Generate a chat completion."""
        pass

    @abstractmethod
    async def stream_chat_completion(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming chat completion."""
        pass

    def set_available_tools(self, tools: List[Dict[str, Any]]) -> None:
        """Set the available tools for the agent."""
        self.available_tools = tools

    def format_tool_for_ai(self, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format tool information for the AI provider."""
        return {
            "type": "function",
            "function": {
                "name": tool_info.get("name", ""),
                "description": tool_info.get("description", ""),
                "parameters": tool_info.get("input_schema", {}),
            },
        }

    def format_tools_for_ai(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format multiple tools for the AI provider."""
        return [self.format_tool_for_ai(tool) for tool in tools]
