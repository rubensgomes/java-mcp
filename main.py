import argparse
import asyncio
import signal
import sys
from typing import List, Optional
from java_mcp.server import MCPServer, run_stdio_server
import logging
import os

from java_mcp.utility import configure_logging

# At the top of your file, after imports
DEFAULT_SERVER_NAME = "java-mcp-server"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000
DEFAULT_FOLDER_PATH = os.getcwd()
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

# Initialize logger after configuration
logger = logging.getLogger(__name__)

# Global server instance for signal handling
_server_instance: Optional[MCPServer] = None

def stop_server(mcp_server: JavaMCPServer) -> None:
    """
    Stop the running MCP server.

    Gracefully shuts down the provided JavaMCPServer instance, cleaning up
    resources and ensuring a proper shutdown sequence.

    Args:
        mcp_server (JavaMCPServer): The server instance to stop.

    Example:
        mcp_server = start_server('/folder_path', ['https://github.com/rubensgomes/ms-reqresp-lib'])
        # ... server operations ...
        stop_server(mcp_server)
    """
    global _server_instance

    if mcp_server is None:
        logger.warning("Attempted to stop a None server instance")
        return

    try:
        logger.info(f"Stopping MCP GitHub server...")
        logger.debug(f"Stopping server with name: {getattr(mcp_server, 'name', 'unknown')}")

        # Clear global reference
        if _server_instance == mcp_server:
            _server_instance = None

        mcp_server.stop()
        logger.info("MCP GitHub server stopped successfully")

    except Exception as e:
        logger.error(f"Error stopping server: {e}")
        logger.debug("Server stop error details:", exc_info=True)
        raise



def _signal_handler(signum: int, frame) -> None:
    """
    Handle system signals for graceful shutdown.

    Args:
        signum (int): The signal number received.
        frame: The current stack frame.
    """
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    logger.debug(f"Signal handler called with signum={signum}")

    if _server_instance:
        stop_server(_server_instance)

    sys.exit(0)
