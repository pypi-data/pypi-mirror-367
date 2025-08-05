"""
DoorDash MCP Server

An MCP server that provides DoorDash food ordering functionality.
"""

__version__ = "0.1.0"

from .server import main, mcp

__all__ = ["main", "mcp"]