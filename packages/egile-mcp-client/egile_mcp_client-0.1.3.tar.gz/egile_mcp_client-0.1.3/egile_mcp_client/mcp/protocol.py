"""MCP Protocol implementation and message handling."""

import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class MessageType(Enum):
    """MCP message types."""

    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


class MCPMethod(Enum):
    """MCP protocol methods."""

    # Initialization
    INITIALIZE = "initialize"
    INITIALIZED = "initialized"

    # Tools
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"

    # Resources
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    SUBSCRIBE_RESOURCE = "resources/subscribe"
    UNSUBSCRIBE_RESOURCE = "resources/unsubscribe"

    # Prompts
    LIST_PROMPTS = "prompts/list"
    GET_PROMPT = "prompts/get"

    # Logging
    SET_LEVEL = "logging/setLevel"


@dataclass
class MCPMessage:
    """Base MCP message."""

    jsonrpc: str = "2.0"


@dataclass
class MCPRequest:
    """MCP request message."""

    jsonrpc: str
    method: str
    id: Union[str, int]
    params: Optional[Dict[str, Any]] = None


@dataclass
class MCPResponse:
    """MCP response message."""

    jsonrpc: str
    id: Union[str, int]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


@dataclass
class MCPNotification:
    """MCP notification message."""

    jsonrpc: str
    method: str
    params: Optional[Dict[str, Any]] = None


@dataclass
class MCPError:
    """MCP error structure."""

    code: int
    message: str
    data: Optional[Dict[str, Any]] = None


@dataclass
class ToolInfo:
    """Information about an MCP tool."""

    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class ResourceInfo:
    """Information about an MCP resource."""

    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None


@dataclass
class PromptInfo:
    """Information about an MCP prompt."""

    name: str
    description: str
    arguments: Optional[List[Dict[str, Any]]] = None


class MCPProtocol:
    """MCP protocol handler."""

    def __init__(self):
        self.next_id = 1

    def create_request(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> MCPRequest:
        """Create a new MCP request."""
        request = MCPRequest(
            jsonrpc="2.0", method=method, id=self.next_id, params=params
        )
        self.next_id += 1
        return request

    def create_response(
        self,
        request_id: Union[str, int],
        result: Optional[Dict[str, Any]] = None,
        error: Optional[MCPError] = None,
    ) -> MCPResponse:
        """Create an MCP response."""
        error_dict = asdict(error) if error else None
        return MCPResponse(
            jsonrpc="2.0", id=request_id, result=result, error=error_dict
        )

    def create_notification(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> MCPNotification:
        """Create an MCP notification."""
        return MCPNotification(jsonrpc="2.0", method=method, params=params)

    def serialize_message(
        self, message: Union[MCPRequest, MCPResponse, MCPNotification]
    ) -> str:
        """Serialize an MCP message to JSON."""
        return json.dumps(asdict(message))

    def parse_message(
        self, data: str
    ) -> Union[MCPRequest, MCPResponse, MCPNotification]:
        """Parse an MCP message from JSON."""
        try:
            parsed = json.loads(data)

            if "method" in parsed and "id" in parsed:
                return MCPRequest(**parsed)
            elif "method" in parsed:
                return MCPNotification(**parsed)
            elif "id" in parsed:
                return MCPResponse(**parsed)
            else:
                raise ValueError(f"Invalid MCP message: {data}")
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Failed to parse MCP message: {e}")

    def create_initialize_request(self, client_info: Dict[str, Any]) -> MCPRequest:
        """Create an initialization request."""
        return self.create_request(
            MCPMethod.INITIALIZE.value,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                "clientInfo": client_info,
            },
        )

    def create_list_tools_request(self) -> MCPRequest:
        """Create a list tools request."""
        return self.create_request(MCPMethod.LIST_TOOLS.value)

    def create_call_tool_request(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> MCPRequest:
        """Create a call tool request."""
        return self.create_request(
            MCPMethod.CALL_TOOL.value, {"name": tool_name, "arguments": arguments}
        )

    def create_list_resources_request(self) -> MCPRequest:
        """Create a list resources request."""
        return self.create_request(MCPMethod.LIST_RESOURCES.value)

    def create_read_resource_request(self, uri: str) -> MCPRequest:
        """Create a read resource request."""
        return self.create_request(MCPMethod.READ_RESOURCE.value, {"uri": uri})

    def create_list_prompts_request(self) -> MCPRequest:
        """Create a list prompts request."""
        return self.create_request(MCPMethod.LIST_PROMPTS.value)

    def create_get_prompt_request(
        self, name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> MCPRequest:
        """Create a get prompt request."""
        params = {"name": name}
        if arguments:
            params["arguments"] = arguments
        return self.create_request(MCPMethod.GET_PROMPT.value, params)
