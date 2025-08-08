from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext
from mcp import McpError, ErrorData


class StaticAuthenticationMiddleware(Middleware):
    def __init__(
        self,
        value: str,
        header_key: str,
        error_code: int = -40001,
        error_message: str = "Authentication failed",
    ):
        self.value = value
        self.header_key = header_key
        self.error_code = error_code
        self.error_message = error_message

    async def on_message(self, context: MiddlewareContext, call_next):
        """Called for all MCP messages."""
        headers = get_http_headers()
        if headers.get(self.header_key) != self.value:
            raise McpError(ErrorData(code=self.error_code, message=self.error_message))

        result = await call_next(context)
        return result
