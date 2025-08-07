"""MCP client connectivity for mbro.
"""
import logging
import os
from typing import Any

from fastmcp import Client
from fastmcp.client import BearerAuth
from mcp.types import TextContent, ImageContent, EmbeddedResource, BlobResourceContents, TextResourceContents, Tool, \
    Resource, ResourceTemplate, Prompt, GetPromptResult
from magg.util.transport import get_transport_for_command_string, is_connection_string_url

logger = logging.getLogger(__name__)


class BrowserConnection:
    """Represents a connection to an MCP server."""

    def __init__(self, name: str, connection_type: str, connection_string: str):
        self.name = name
        self.connection_type = connection_type  # 'http' or 'command'
        self.connection_string = connection_string
        self.client: Client | None = None
        self.connected = False
        self._context_manager = None

    async def get_tools(self) -> list[dict[str, Any]]:
        """Get tools list."""
        if not self.client or not self.connected:
            return []

        async with self.client as conn:
            tools_result = await conn.list_tools()
            return self.parse_tools_list(tools_result)

    async def get_resources(self) -> list[dict[str, Any]]:
        """Get resources list."""
        if not self.client or not self.connected:
            return []

        resources_data = []
        async with self.client as conn:
            try:
                resources_result = await conn.list_resources()
                resources_data = self.parse_resources_list(resources_result)
            except Exception as e:
                logger.debug("Server does not support resources: %s", e)

            try:
                resource_templates = await conn.list_resource_templates()
                resources_data.extend(self.parse_resources_list(resource_templates))
            except Exception as e:
                logger.debug("Server does not support resource templates: %s", e)

        return resources_data

    async def get_prompts(self) -> list[dict[str, Any]]:
        """Get prompts list."""
        if not self.client or not self.connected:
            return []

        prompts_data = []
        async with self.client as conn:
            try:
                prompts_result = await conn.list_prompts()
                prompts_data = self.parse_prompts_list(prompts_result)
            except Exception as e:
                logger.debug("Server does not support prompts: %s", e)

        return prompts_data

    async def connect(self, env_pass: bool = False, env_vars: dict[str, str] | None = None) -> bool:
        """Connect to the MCP server using FastMCP Client."""
        jwt = os.getenv("MAGG_JWT", os.getenv("MBRO_JWT", os.getenv("MCP_JWT", None)))
        auth = BearerAuth(jwt) if jwt else None

        if is_connection_string_url(self.connection_string):
            url = self.connection_string
            if not url.endswith("/mcp/"):
                url = url.rstrip("/") + "/mcp/"
            client = Client(url, auth=auth)
        else:
            from ..util.system import get_subprocess_environment
            env = get_subprocess_environment(inherit=env_pass, provided=env_vars)

            transport = get_transport_for_command_string(self.connection_string, env=env)
            client = Client(transport, auth=auth)

        try:
            async with client as conn:
                result = await conn.ping()

                if not result:
                    logger.warning("Connected to %r but ping failed", client)

        except Exception as e:
            logger.error("Failed to connect to MCP server: %s", e)
            return False

        self.client = client
        self.connected = True
        return True

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] = None) -> list[
        TextContent | ImageContent | EmbeddedResource
    ]:
        """Call a tool on the connected MCP server."""
        if not self.client or not self.connected:
            raise RuntimeError("Not connected to server")

        if arguments is None:
            arguments = {}

        try:
            async with self.client as conn:
                result = await conn.call_tool(tool_name, arguments)
                return result.content

        except Exception as e:
            raise RuntimeError(f"Failed to call tool '{tool_name}': {e}")

    async def get_resource(self, uri: str) -> list[TextResourceContents | BlobResourceContents]:
        """Get a resource from the connected MCP server."""
        if not self.client or not self.connected:
            raise RuntimeError("Not connected to server")

        try:
            async with self.client as conn:
                result = await conn.read_resource(uri)
                return result
        except Exception as e:
            raise RuntimeError(f"Failed to get resource '{uri}': {e}")

    async def get_prompt(self, name: str, arguments: dict[str, Any] = None) -> GetPromptResult:
        """Get a prompt from the connected MCP server."""
        if not self.client or not self.connected:
            raise RuntimeError("Not connected to server")

        if arguments is None:
            arguments = {}

        try:
            async with self.client as conn:
                result = await conn.get_prompt(name, arguments)
                return result
        except Exception as e:
            raise RuntimeError(f"Failed to get prompt '{name}': {e}")

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
            except Exception as e:
                logger.debug("Error during disconnect: %s", e)
            self.client = None
        self.connected = False

    @classmethod
    def parse_tool(cls, tool: Tool) -> dict[str, Any]:
        """Parse a single tool into a more usable format."""
        return {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": (
                tool.inputSchema.model_dump(mode="json")
                if hasattr(tool.inputSchema, 'model_dump') and tool.inputSchema
                else (tool.inputSchema if tool.inputSchema else {})
            )
        }

    @classmethod
    def parse_tools_list(cls, tools: list[Tool]) -> list[dict[str, Any]]:
        """Parse tools list into a more usable format."""
        return [
            cls.parse_tool(tool)
            for tool in tools
        ]

    @classmethod
    def parse_resource(cls, resource: Resource | ResourceTemplate) -> dict[str, Any]:
        """Parse a single resource into a more usable format."""
        return resource.model_dump(mode="json", exclude_defaults=True, exclude_none=True, exclude_unset=True)

    @classmethod
    def parse_resources_list(cls, resources: list[Resource | ResourceTemplate]) -> list[dict[str, Any]]:
        """Parse resources list into a more usable format."""
        return [
            cls.parse_resource(resource)
            for resource in resources
        ]

    @classmethod
    def parse_prompt(cls, prompt: Prompt) -> dict[str, Any]:
        """Parse a single prompt into a more usable format."""
        return {
            "name": prompt.name,
            "description": prompt.description,
            "arguments": [
                {
                    "name": arg.name,
                    "description": arg.description,
                    "required": arg.required
                }
                for arg in (prompt.arguments or [])
            ]
        }

    @classmethod
    def parse_prompts_list(cls, prompts: list[Prompt]) -> list[dict[str, Any]]:
        """Parse prompts list into a more usable format."""
        return [
            cls.parse_prompt(prompt)
            for prompt in prompts
        ]


class BrowserClient:
    """Main MCP browser class for managing connections."""
    connections: dict[str, BrowserConnection]
    current_connection: str | None
    env_pass: bool
    env_vars: dict[str, str] | None

    def __init__(self, env_pass: bool = False, env_vars: dict[str, str] | None = None):
        self.connections: dict[str, BrowserConnection] = {}
        self.current_connection: str | None = None
        self.env_pass = env_pass
        self.env_vars = env_vars

    async def add_connection(self, name: str, connection_string: str) -> bool:
        """Add a new MCP connection using FastMCP Client connection string."""
        if name in self.connections:
            return False

        if is_connection_string_url(connection_string):
            connection_type = "http"
        else:
            connection_type = "command"

        connection = BrowserConnection(name, connection_type, connection_string)
        success = await connection.connect(env_pass=self.env_pass, env_vars=self.env_vars)

        if success:
            self.connections[name] = connection
            if not self.current_connection:
                self.current_connection = name
            return True
        else:
            return False

    async def switch_connection(self, name: str) -> bool:
        """Switch to a different connection."""
        if name not in self.connections:
            return False

        if not self.connections[name].connected:
            return False

        self.current_connection = name
        return True

    async def remove_connection(self, name: str) -> bool:
        """Remove a connection."""
        if name not in self.connections:
            return False

        await self.connections[name].disconnect()
        del self.connections[name]

        if self.current_connection == name:
            self.current_connection = None
            if self.connections:
                self.current_connection = next(iter(self.connections.keys()))

        return True

    def get_current_connection(self) -> BrowserConnection | None:
        """Get the current active connection."""
        if not self.current_connection:
            return None
        return self.connections.get(self.current_connection)

    async def list_connections(self, *, extended: bool = False) -> list[dict[str, Any]]:
        """List all connections with their status."""
        result = []
        for name, conn in self.connections.items():
            extend = {}

            if extended:
                try:
                    extend["tools"] = await conn.get_tools()
                except Exception as e:
                    logger.debug("Failed to get tools for %s: %s", name, e)
                    extend["tools"] = None

                try:
                    extend["resources"] = await conn.get_resources()
                except Exception as e:
                    logger.debug("Failed to get resources for %s: %s", name, e)
                    extend["resources"] = None

                try:
                    extend["prompts"] = await conn.get_prompts()
                except Exception as e:
                    logger.debug("Failed to get prompts for %s: %s", name, e)
                    extend["prompts"] = None

            result.append({
                "name": name,
                "type": conn.connection_type,
                "connected": conn.connected,
                "current": name == self.current_connection,
                **extend,
            })
        return result
