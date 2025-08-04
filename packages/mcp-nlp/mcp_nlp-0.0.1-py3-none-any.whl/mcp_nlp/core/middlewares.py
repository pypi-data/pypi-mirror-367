import json
import logging
from typing import Any

from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

logger = logging.getLogger("mcp-nlp")


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check for API key in the request headers.

    If the API key is missing or invalid, a 401 Unauthorized response is returned.
    """

    def __init__(self, app: ASGIApp, api_key: str, api_key_name: str = "X-API-Key") -> None:
        super().__init__(app)
        self.api_key = api_key
        self.api_key_name = api_key_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check for API key in header
        api_key = request.headers.get(self.api_key_name)
        if api_key != self.api_key:
            logger.error(f"Invalid API key provided: {api_key}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or missing API key"},
            )

        return await call_next(request)


class LoggingMiddleware(Middleware):
    """
    Middleware to log incoming requests and outgoing responses.

    This middleware logs the method, source, and message of incoming requests,
    and the result of outgoing responses. It also logs any exceptions that occur
    during the request processing.
    """

    def __init__(
        self,
        *,
        include_payloads: bool = False,
        methods: list[str] | None = None,
    ) -> None:
        """Initialize structured logging middleware.

        Args:
            include_payloads: Whether to include message payloads in logs
            methods: List of methods to log. If None, logs all methods.
        """
        self.include_payloads = include_payloads
        self.methods = methods

    def _create_log_entry(
        self, context: MiddlewareContext, event: str, **extra_fields: Any
    ) -> dict:
        """Create a structured log entry."""
        entry = {
            "event": event,
            "timestamp": context.timestamp.isoformat(),
            "source": context.source,
            "type": context.type,
            "method": context.method,
            **extra_fields,
        }

        if self.include_payloads and hasattr(context.message, "__dict__"):
            try:
                entry["payload"] = context.message.__dict__
            except (TypeError, ValueError):
                entry["payload"] = "<non-serializable>"

        return entry

    async def on_message(self, context: MiddlewareContext, call_next: CallNext) -> Any:
        """Log structured message information."""

        start_entry = self._create_log_entry(context, "request_start")
        if self.methods and context.method not in self.methods:
            return await call_next(context)

        logger.info(json.dumps(start_entry))

        try:
            result = await call_next(context)

            success_entry = self._create_log_entry(
                context,
                "request_success",
                result_type=type(result).__name__ if result else None,
            )
            logger.info(json.dumps(success_entry))

            return result
        except Exception as e:
            error_entry = self._create_log_entry(
                context,
                "request_error",
                error_type=type(e).__name__,
                error_message=str(e),
            )
            logger.error(json.dumps(error_entry))
            raise
