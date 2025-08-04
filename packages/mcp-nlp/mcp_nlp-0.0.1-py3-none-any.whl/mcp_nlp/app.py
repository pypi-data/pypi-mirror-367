from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from . import __version__
from .core.middlewares import ApiKeyAuthMiddleware, LoggingMiddleware
from .core.settings import get_app_settings
from .resources.version import VersionResource
from .tools.text_distance import textdistance_mcp


def create_application() -> tuple[FastMCP, Starlette]:
    """Create a FastMCP app"""
    settings = get_app_settings()

    # Starlette middlewares
    custom_middlewares = [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_hosts,
            allow_credentials=settings.allow_credentials,
            allow_methods=settings.allowed_methods,
            allow_headers=settings.allowed_headers,
        ),
    ]
    if settings.api_key_enabled and settings.api_key is not None:
        custom_middlewares.append(
            # API Key Authentication Middleware
            Middleware(
                ApiKeyAuthMiddleware,
                api_key=settings.api_key,
                api_key_name=settings.api_key_name,
            )
        )

    # Create the FastMCP application
    mcp_app: FastMCP = FastMCP(**settings.fastmcp_kwargs)

    # Extract the Starlette application for use with ASGI servers, like uvicorn
    starlette_app = mcp_app.http_app(
        middleware=custom_middlewares,
        transport=settings.transport,
    )

    # Tools
    mcp_app.mount(textdistance_mcp, "textdistance")
    # Resources
    mcp_app.add_resource(VersionResource(__version__))

    # FastMCP Middlewares
    mcp_app.add_middleware(LoggingMiddleware(include_payloads=True))

    return mcp_app, starlette_app
