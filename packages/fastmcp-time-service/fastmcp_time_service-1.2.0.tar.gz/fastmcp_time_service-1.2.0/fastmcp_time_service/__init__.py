"""FastMCP Time Service - 基于SSE传输的MCP时间服务器

提供多时区时间查询功能的MCP服务器实现。
"""

from importlib.metadata import version
from .server import TimeServer

try:
    __version__ = version("fastmcp-time-service")
except Exception:
    __version__ = "1.2.0"  # Fallback version

__all__ = ["TimeServer"]