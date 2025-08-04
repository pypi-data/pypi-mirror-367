from unittest.mock import patch

import pytest

from src.mcp_nlp.app import create_application

# Create the application instance
mcp_app, http_app = create_application()


@pytest.mark.asyncio
async def test_run_server_stdio() -> None:
    with patch.object(mcp_app, "run_async") as mock_run_async:
        mock_run_async.return_value = None
        await mcp_app.run_async(transport="stdio")
        mock_run_async.assert_called_once_with(transport="stdio")


@pytest.mark.asyncio
async def test_run_server_sse() -> None:
    with patch.object(mcp_app, "run_async") as mock_run_async:
        mock_run_async.return_value = None
        test_port = 9000
        await mcp_app.run_async(transport="sse", port=test_port)
        mock_run_async.assert_called_once_with(transport="sse", port=test_port)


@pytest.mark.asyncio
async def test_run_server_streamable_http() -> None:
    with patch.object(mcp_app, "run_async") as mock_run_async:
        mock_run_async.return_value = None
        test_port = 9001
        test_host = "127.0.0.1"
        test_path = "/custom_mcp"
        await mcp_app.run_async(
            transport="streamable-http", port=test_port, host=test_host, path=test_path
        )
        mock_run_async.assert_called_once_with(
            transport="streamable-http", port=test_port, host=test_host, path=test_path
        )


@pytest.mark.asyncio
async def test_run_server_invalid_transport() -> None:
    transport = "invalid_transport"
    with pytest.raises(ValueError) as exc:
        await mcp_app.run_async(transport=transport)  # type: ignore

    assert f"Unknown transport: {transport}" in str(exc.value)
