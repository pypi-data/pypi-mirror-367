"""MCP connection management for different transport types."""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import httpx
import websockets
from websockets.exceptions import ConnectionClosed

from .protocol import MCPNotification, MCPProtocol, MCPRequest, MCPResponse

logger = logging.getLogger(__name__)


class MCPConnection(ABC):
    """Abstract base class for MCP connections."""

    def __init__(self):
        self.protocol = MCPProtocol()
        self.is_connected = False

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the MCP server."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection to the MCP server."""
        pass

    @abstractmethod
    async def send_request(self, request: MCPRequest) -> MCPResponse:
        """Send a request and wait for response."""
        pass

    @abstractmethod
    async def send_notification(self, notification: MCPNotification) -> None:
        """Send a notification (no response expected)."""
        pass


class HTTPMCPConnection(MCPConnection):
    """HTTP-based MCP connection."""

    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.client: Optional[httpx.AsyncClient] = None

    async def connect(self) -> None:
        """Establish HTTP client."""
        self.client = httpx.AsyncClient(timeout=30.0)
        self.is_connected = True
        logger.info(f"Connected to HTTP MCP server at {self.base_url}")

    async def disconnect(self) -> None:
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
        self.is_connected = False
        logger.info("Disconnected from HTTP MCP server")

    async def send_request(self, request: MCPRequest) -> MCPResponse:
        """Send HTTP request to MCP server."""
        if not self.client or not self.is_connected:
            raise RuntimeError("Not connected to MCP server")

        try:
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json=request.__dict__,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            data = response.json()
            return MCPResponse(**data)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending request: {e}")
            raise
        except Exception as e:
            logger.error(f"Error sending HTTP request: {e}")
            raise

    async def send_notification(self, notification: MCPNotification) -> None:
        """Send HTTP notification."""
        if not self.client or not self.is_connected:
            raise RuntimeError("Not connected to MCP server")

        try:
            await self.client.post(
                f"{self.base_url}/mcp",
                json=notification.__dict__,
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            logger.error(f"Error sending HTTP notification: {e}")
            raise


class WebSocketMCPConnection(MCPConnection):
    """WebSocket-based MCP connection."""

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.pending_requests: Dict[str, asyncio.Future] = {}

    async def connect(self) -> None:
        """Establish WebSocket connection."""
        try:
            self.websocket = await websockets.connect(self.url)
            self.is_connected = True

            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())
            logger.info(f"Connected to WebSocket MCP server at {self.url}")

        except Exception as e:
            logger.error(f"Failed to connect to WebSocket server: {e}")
            raise

    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.is_connected = False
        logger.info("Disconnected from WebSocket MCP server")

    async def _listen_for_messages(self) -> None:
        """Listen for incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    if "id" in data and data["id"] in self.pending_requests:
                        # This is a response to a pending request
                        future = self.pending_requests.pop(data["id"])
                        response = MCPResponse(**data)
                        future.set_result(response)
                    else:
                        # This is a notification
                        logger.info(f"Received notification: {data}")

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
            self.is_connected = False

    async def send_request(self, request: MCPRequest) -> MCPResponse:
        """Send WebSocket request and wait for response."""
        if not self.websocket or not self.is_connected:
            raise RuntimeError("Not connected to MCP server")

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request.id] = future

        try:
            # Send request
            message = self.protocol.serialize_message(request)
            await self.websocket.send(message)

            # Wait for response
            response = await asyncio.wait_for(future, timeout=30.0)
            return response

        except asyncio.TimeoutError:
            self.pending_requests.pop(request.id, None)
            raise RuntimeError("Request timeout")
        except Exception as e:
            self.pending_requests.pop(request.id, None)
            logger.error(f"Error sending WebSocket request: {e}")
            raise

    async def send_notification(self, notification: MCPNotification) -> None:
        """Send WebSocket notification."""
        if not self.websocket or not self.is_connected:
            raise RuntimeError("Not connected to MCP server")

        try:
            message = self.protocol.serialize_message(notification)
            await self.websocket.send(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {e}")
            raise


class StdioMCPConnection(MCPConnection):
    """Stdio-based MCP connection for local processes."""

    def __init__(self, command: List[str]):
        super().__init__()
        self.command = command
        self.process: Optional[asyncio.subprocess.Process] = None
        self.pending_requests: Dict[str, asyncio.Future] = {}

    async def connect(self) -> None:
        """Start the MCP server process."""
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self.is_connected = True

            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())
            logger.info(f"Started MCP server process: {' '.join(self.command)}")

        except Exception as e:
            logger.error(f"Failed to start MCP server process: {e}")
            raise

    async def disconnect(self) -> None:
        """Terminate the MCP server process."""
        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
            self.process = None
        self.is_connected = False
        logger.info("Terminated MCP server process")

    async def _listen_for_messages(self) -> None:
        """Listen for stdout messages from the process."""
        if not self._can_listen():
            return

        try:
            await self._message_loop()
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
        finally:
            self.is_connected = False

    def _can_listen(self) -> bool:
        """Check if we can listen for messages."""
        return self.process is not None and self.process.stdout is not None

    async def _message_loop(self) -> None:
        """Main message listening loop."""
        while True:
            line = await self._read_message_line()
            if not line:
                break

            if line.strip():
                await self._process_message_line(line.strip())

    async def _read_message_line(self) -> str:
        """Read a single line from the process stdout."""
        if not self.process or not self.process.stdout:
            return ""

        line_bytes = await self.process.stdout.readline()
        return line_bytes.decode() if line_bytes else ""

    async def _process_message_line(self, line: str) -> None:
        """Process a single message line."""
        try:
            data = json.loads(line)
            await self._handle_message_data(data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def _handle_message_data(self, data: dict) -> None:
        """Handle parsed message data."""
        if self._is_response(data):
            self._handle_response(data)
        else:
            self._handle_notification(data)

    def _is_response(self, data: dict) -> bool:
        """Check if data is a response to a pending request."""
        return "id" in data and data["id"] in self.pending_requests

    def _handle_response(self, data: dict) -> None:
        """Handle response to a pending request."""
        future = self.pending_requests.pop(data["id"])
        response = MCPResponse(**data)
        future.set_result(response)

    def _handle_notification(self, data: dict) -> None:
        """Handle notification message."""
        logger.info(f"Received notification: {data}")

    async def send_request(self, request: MCPRequest) -> MCPResponse:
        """Send request via stdin and wait for response."""
        if not self.process or not self.is_connected or not self.process.stdin:
            raise RuntimeError("Not connected to MCP server")

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request.id] = future

        try:
            # Send request
            message = self.protocol.serialize_message(request)
            self.process.stdin.write((message + "\n").encode())
            await self.process.stdin.drain()

            # Wait for response
            response = await asyncio.wait_for(future, timeout=30.0)
            return response

        except asyncio.TimeoutError:
            self.pending_requests.pop(request.id, None)
            raise RuntimeError("Request timeout")
        except Exception as e:
            self.pending_requests.pop(request.id, None)
            logger.error(f"Error sending stdio request: {e}")
            raise

    async def send_notification(self, notification: MCPNotification) -> None:
        """Send notification via stdin."""
        if not self.process or not self.is_connected or not self.process.stdin:
            raise RuntimeError("Not connected to MCP server")

        try:
            message = self.protocol.serialize_message(notification)
            self.process.stdin.write((message + "\n").encode())
            await self.process.stdin.drain()
        except Exception as e:
            logger.error(f"Error sending stdio notification: {e}")
            raise
