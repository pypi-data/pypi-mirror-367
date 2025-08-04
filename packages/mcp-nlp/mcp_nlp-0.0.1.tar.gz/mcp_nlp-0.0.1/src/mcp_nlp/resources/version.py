from fastmcp.resources import TextResource
from pydantic import AnyUrl


class VersionResource(TextResource):
    """A resource that provides the version of the application."""

    name: str = "version"

    def __init__(self, version: str) -> None:
        super().__init__(uri=AnyUrl("config://version"), text=version)
