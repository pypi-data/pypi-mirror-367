"""
ScreenMonitorMCP v2 - Streamable HTTP/SSE Architecture

Revolutionary AI Vision Server with modern HTTP/SSE/WebSocket transport.
"""

__version__ = "2.0.0"
__author__ = "inkbytefo"
__email__ = "inkbytefo@example.com"
__license__ = "MIT"

from .server.app import create_app

__all__ = ["create_app"]
