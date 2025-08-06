from mcp.server.fastmcp import FastMCP
from datetime import datetime
import os
import pytz
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 服务器配置从环境变量获取，提供默认值
MCP_HOST = os.getenv("MCP_TIME_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_TIME_PORT", "8005"))

# Initialize FastMCP server with configuration
mcp = FastMCP(
    "TimeService",  # Name of the MCP server
    instructions="""你是一个专业的时间查询助手。当用户询问任何与时间相关的问题时，你应该主动使用get_current_time工具来获取准确的时间信息。

触发场景包括但不限于：
- 用户问"现在几点了？"、"什么时间了？"
- 询问特定时区时间："北京时间几点？"、"纽约现在几点？"
- 时间查询："查询东京时间"、"告诉我伦敦时间"
- 任何包含"时间"、"几点"、"时区"等关键词的问题

你支持全球所有时区查询，包括中文时区别名（如：北京、上海、中国）和标准时区格式（如：Asia/Shanghai、America/New_York）。

请主动识别时间查询请求并调用相应工具。""",
    host=MCP_HOST,  # Host address from environment variable
    port=MCP_PORT,  # Port number from environment variable
)


@mcp.tool()
async def get_current_time(timezone: Optional[str] = "Asia/Shanghai") -> str:
    """
    获取指定时区的当前时间信息 - Get current time information for any timezone
    
    当用户询问时间、当前时间、几点、什么时候、时间查询、时区时间时，请使用此工具。
    支持全球所有时区查询，包括中文时区别名。
    
    适用场景：
    - "现在几点了？"
    - "北京时间是几点？" 
    - "东京现在是什么时间？"
    - "美国纽约的当前时间"
    - "查询上海时间"
    - "GMT时间是多少？"
    - "中国标准时间"
    - 任何关于时间查询的问题
    
    支持的时区格式：
    - 标准时区名：Asia/Shanghai, America/New_York, Europe/London
    - 中文别名：北京, 上海, 中国
    - 英文别名：Beijing, China, GMT, UTC
    
    Use this tool when users ask about time, current time, timezone queries, or any time-related questions.
    
    Args:
        timezone (str, optional): 时区名称，支持标准时区格式和中文别名。默认为"Asia/Shanghai"（中国标准时间）
    
    Returns:
        str: 包含指定时区当前时间信息的字符串
    """
    try:
        # 支持中文时区别名
        timezone_mapping = {
            "中国": "Asia/Shanghai",
            "北京": "Asia/Shanghai", 
            "上海": "Asia/Shanghai",
            "China": "Asia/Shanghai",
            "Beijing": "Asia/Shanghai",
            "CST": "Asia/Shanghai"
        }
        
        # 如果是别名，转换为标准时区名
        actual_timezone = timezone_mapping.get(timezone, timezone)
        
        # Get the timezone object
        tz = pytz.timezone(actual_timezone)

        # Get current time in the specified timezone
        current_time = datetime.now(tz)

        # Format the time as a string
        formatted_time = current_time.strftime("%Y年%m月%d日 %H:%M:%S %Z")

        return f"{timezone} 的当前时间是: {formatted_time}"
    except pytz.exceptions.UnknownTimeZoneError:
        return f"错误: 未知的时区 '{timezone}'。请提供有效的时区名称。"
    except Exception as e:
        return f"获取时间时出错: {str(e)}"


class TimeServer:
    """时间服务器类，封装MCP时间服务器功能"""
    
    def __init__(self, host=None, port=None):
        self.host = host or MCP_HOST
        self.port = port or MCP_PORT
        self.mcp = mcp
    
    def run_stdio(self):
        """使用stdio传输运行服务器"""
        self.mcp.run(transport="stdio")
    
    def run_sse(self):
        """使用SSE传输运行服务器"""
        self.mcp.run(transport="sse", host=self.host, port=self.port)


def main():
    """主入口函数"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        # SSE模式
        server = TimeServer()
        print(f"启动MCP时间服务器 (SSE模式) 在 {server.host}:{server.port}")
        server.run_sse()
    else:
        # 默认stdio模式
        server = TimeServer()
        print("启动MCP时间服务器 (stdio模式)")
        server.run_stdio()


if __name__ == "__main__":
    main()
