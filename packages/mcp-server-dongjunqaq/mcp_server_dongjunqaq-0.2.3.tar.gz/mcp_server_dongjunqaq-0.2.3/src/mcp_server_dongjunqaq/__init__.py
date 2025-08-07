from mcp.server.fastmcp import FastMCP

from .tools import get_platform_info

mcp = FastMCP("mcp-server-DongJunQAQ")  # 创建MCP Server并命名
mcp.add_tool(get_platform_info)  # 注册工具


def main() -> None:
    mcp.run(transport="stdio")  # 使用stdio的方式运行该MCP Server
