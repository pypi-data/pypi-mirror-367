"""
MCP Time Server - 基于SSE传输的MCP时间服务器

这是一个基于FastMCP框架的时间服务器，提供多时区时间查询功能。
支持中文时区别名，默认为中国标准时间。
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "基于SSE传输的MCP时间服务器，提供多时区时间查询功能"

from .time_server import TimeServer, get_current_time

__all__ = ["TimeServer", "get_current_time", "__version__"]