"""MCP client implementation providing high-level interface to MCP servers."""

import logging
from typing import Any, Dict, List, Optional

from ..config import Config, MCPServerConfig
from .connection import (
    HTTPMCPConnection,
    MCPConnection,
    StdioMCPConnection,
    WebSocketMCPConnection,
)
from .protocol import MCPProtocol, PromptInfo, ResourceInfo, ToolInfo

logger = logging.getLogger(__name__)


class MCPClient:
    """High-level MCP client for interacting with MCP servers."""

    def __init__(self, config: Config):
        self.config = config
        self.protocol = MCPProtocol()
        self.connections: Dict[str, MCPConnection] = {}
        self.initialized_servers: set = set()

    def _create_connection(self, server_config: MCPServerConfig) -> MCPConnection:
        """Create appropriate connection type based on server configuration."""
        connection_map = {
            "http": self._create_http_connection,
            "websocket": self._create_websocket_connection,
            "stdio": self._create_stdio_connection,
        }

        connection_factory = connection_map.get(server_config.type)
        if not connection_factory:
            raise ValueError(f"Unsupported server type: {server_config.type}")

        return connection_factory(server_config)

    def _create_http_connection(
        self, server_config: MCPServerConfig
    ) -> HTTPMCPConnection:
        """Create HTTP connection."""
        if not server_config.url:
            raise ValueError(f"HTTP server {server_config.name} requires URL")
        return HTTPMCPConnection(server_config.url)

    def _create_websocket_connection(
        self, server_config: MCPServerConfig
    ) -> WebSocketMCPConnection:
        """Create WebSocket connection."""
        if not server_config.url:
            raise ValueError(f"WebSocket server {server_config.name} requires URL")
        return WebSocketMCPConnection(server_config.url)

    def _create_stdio_connection(
        self, server_config: MCPServerConfig
    ) -> StdioMCPConnection:
        """Create stdio connection."""
        if not server_config.command:
            raise ValueError(f"Stdio server {server_config.name} requires command")
        return StdioMCPConnection(server_config.command)

    async def connect_to_server(self, server_name: str) -> None:
        """Connect to a specific MCP server."""
        server_config = self._find_server_config(server_name)

        if self._is_already_connected(server_name):
            return

        try:
            await self._establish_connection(server_name, server_config)
            logger.info(f"Successfully connected to MCP server: {server_name}")
        except Exception as e:
            logger.error(f"Failed to connect to server {server_name}: {e}")
            raise

    def _find_server_config(self, server_name: str) -> MCPServerConfig:
        """Find server configuration by name."""
        for config in self.config.mcp_servers:
            if config.name == server_name:
                return config
        raise ValueError(f"Server {server_name} not found in configuration")

    def _is_already_connected(self, server_name: str) -> bool:
        """Check if already connected to server."""
        if server_name in self.connections:
            logger.warning(f"Already connected to server {server_name}")
            return True
        return False

    async def _establish_connection(
        self, server_name: str, server_config: MCPServerConfig
    ) -> None:
        """Establish connection and initialize server."""
        connection = self._create_connection(server_config)
        await connection.connect()
        self.connections[server_name] = connection
        await self._initialize_server(server_name)

    async def disconnect_from_server(self, server_name: str) -> None:
        """Disconnect from a specific MCP server."""
        if server_name not in self.connections:
            logger.warning(f"Not connected to server {server_name}")
            return

        try:
            await self.connections[server_name].disconnect()
            del self.connections[server_name]
            self.initialized_servers.discard(server_name)
            logger.info(f"Disconnected from MCP server: {server_name}")
        except Exception as e:
            logger.error(f"Error disconnecting from server {server_name}: {e}")

    async def disconnect_all(self) -> None:
        """Disconnect from all MCP servers."""
        for server_name in list(self.connections.keys()):
            await self.disconnect_from_server(server_name)

    async def _initialize_server(self, server_name: str) -> None:
        """Initialize connection with an MCP server."""
        if server_name not in self.connections:
            raise ValueError(f"Not connected to server {server_name}")

        connection = self.connections[server_name]

        # Send initialization request
        init_request = self.protocol.create_initialize_request(
            {"name": "egile-mcp-client", "version": "0.1.0"}
        )

        try:
            response = await connection.send_request(init_request)

            if response.error:
                raise RuntimeError(f"Initialization failed: {response.error}")

            # Send initialized notification
            initialized_notification = self.protocol.create_notification("initialized")
            await connection.send_notification(initialized_notification)

            self.initialized_servers.add(server_name)
            logger.info(f"Initialized server {server_name}")

        except Exception as e:
            logger.error(f"Failed to initialize server {server_name}: {e}")
            raise

    async def list_tools(self, server_name: str) -> List[ToolInfo]:
        """List available tools from an MCP server."""
        if server_name not in self.connections:
            await self.connect_to_server(server_name)

        connection = self.connections[server_name]
        request = self.protocol.create_list_tools_request()

        try:
            response = await connection.send_request(request)
            self._validate_response(response, "Failed to list tools")
            return self._parse_tools_response(response)
        except Exception as e:
            logger.error(f"Error listing tools from {server_name}: {e}")
            raise

    def _validate_response(self, response, error_message: str) -> None:
        """Validate MCP response for errors."""
        if response.error:
            raise RuntimeError(f"{error_message}: {response.error}")

    def _parse_tools_response(self, response) -> List[ToolInfo]:
        """Parse tools from MCP response."""
        tools = []
        if response.result and "tools" in response.result:
            for tool_data in response.result["tools"]:
                tools.append(
                    ToolInfo(
                        name=tool_data.get("name", ""),
                        description=tool_data.get("description", ""),
                        input_schema=tool_data.get("inputSchema", {}),
                    )
                )
        return tools

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a tool on an MCP server."""
        if server_name not in self.connections:
            await self.connect_to_server(server_name)

        connection = self.connections[server_name]
        request = self.protocol.create_call_tool_request(tool_name, arguments)

        try:
            response = await connection.send_request(request)
            self._validate_response(response, "Tool call failed")
            return response.result or {}
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on {server_name}: {e}")
            raise

    async def list_resources(self, server_name: str) -> List[ResourceInfo]:
        """List available resources from an MCP server."""
        if server_name not in self.connections:
            await self.connect_to_server(server_name)

        connection = self.connections[server_name]
        request = self.protocol.create_list_resources_request()

        try:
            response = await connection.send_request(request)
            self._validate_response(response, "Failed to list resources")
            return self._parse_resources_response(response)
        except Exception as e:
            logger.error(f"Error listing resources from {server_name}: {e}")
            raise

    def _parse_resources_response(self, response) -> List[ResourceInfo]:
        """Parse resources from MCP response."""
        resources = []
        if response.result and "resources" in response.result:
            for resource_data in response.result["resources"]:
                resources.append(
                    ResourceInfo(
                        uri=resource_data.get("uri", ""),
                        name=resource_data.get("name", ""),
                        description=resource_data.get("description"),
                        mime_type=resource_data.get("mimeType"),
                    )
                )
        return resources

    async def read_resource(self, server_name: str, uri: str) -> Dict[str, Any]:
        """Read a resource from an MCP server."""
        if server_name not in self.connections:
            await self.connect_to_server(server_name)

        connection = self.connections[server_name]
        request = self.protocol.create_read_resource_request(uri)

        try:
            response = await connection.send_request(request)
            self._validate_response(response, "Failed to read resource")
            return response.result or {}
        except Exception as e:
            logger.error(f"Error reading resource {uri} from {server_name}: {e}")
            raise

    async def list_prompts(self, server_name: str) -> List[PromptInfo]:
        """List available prompts from an MCP server."""
        if server_name not in self.connections:
            await self.connect_to_server(server_name)

        connection = self.connections[server_name]
        request = self.protocol.create_list_prompts_request()

        try:
            response = await connection.send_request(request)
            self._validate_response(response, "Failed to list prompts")
            return self._parse_prompts_response(response)
        except Exception as e:
            logger.error(f"Error listing prompts from {server_name}: {e}")
            raise

    def _parse_prompts_response(self, response) -> List[PromptInfo]:
        """Parse prompts from MCP response."""
        prompts = []
        if response.result and "prompts" in response.result:
            for prompt_data in response.result["prompts"]:
                prompts.append(
                    PromptInfo(
                        name=prompt_data.get("name", ""),
                        description=prompt_data.get("description", ""),
                        arguments=prompt_data.get("arguments"),
                    )
                )
        return prompts

    async def get_prompt(
        self, server_name: str, name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get a prompt from an MCP server."""
        if server_name not in self.connections:
            await self.connect_to_server(server_name)

        connection = self.connections[server_name]
        request = self.protocol.create_get_prompt_request(name, arguments)

        try:
            response = await connection.send_request(request)
            self._validate_response(response, "Failed to get prompt")
            return response.result or {}
        except Exception as e:
            logger.error(f"Error getting prompt {name} from {server_name}: {e}")
            raise

    def get_connected_servers(self) -> List[str]:
        """Get list of currently connected server names."""
        return list(self.connections.keys())

    def is_connected(self, server_name: str) -> bool:
        """Check if connected to a specific server."""
        return (
            server_name in self.connections
            and self.connections[server_name].is_connected
        )
