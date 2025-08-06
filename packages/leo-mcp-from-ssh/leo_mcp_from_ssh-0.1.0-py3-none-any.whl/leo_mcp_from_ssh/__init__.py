"""
FastMCP 快速启动示例 - SSH部署的MCP服务器

这是一个基于FastMCP框架的MCP（Model Context Protocol）服务器示例。
该服务器提供了多个工具函数，可以通过MCP协议与客户端进行交互。

使用方法：
1. 在 `examples/snippets/clients` 目录下运行：
   uv run server fastmcp_quickstart stdio
2. 或者直接运行：python -m leo_mcp_from_ssh
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime


# 创建MCP服务器实例
# FastMCP是MCP框架的快速实现，简化了服务器创建过程
# "Demo" 是服务器的名称，会在客户端连接时显示
mcp = FastMCP("Demo")


# ==================== 工具函数定义 ====================
# 这些函数可以通过MCP协议被客户端调用

@mcp.tool()
def add(a: int, b: int) -> int:
    """
    加法工具函数
    
    参数:
        a (int): 第一个数字
        b (int): 第二个数字
    
    返回:
        int: 两个数字的和
    """
    return a + b

@mcp.tool()
def reverse_string(s: str) -> str:
    """
    字符串反转工具函数
    
    参数:
        s (str): 要反转的字符串
    
    返回:
        str: 反转后的字符串
    """
    return s[::-1]

@mcp.tool()
def get_current_time() -> str:
    """
    获取当前时间工具函数
    
    返回:
        str: 格式化的当前时间字符串 (YYYY-MM-DD HH:MM:SS)
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def to_upper(s: str) -> str:
    """
    字符串转大写工具函数
    
    参数:
        s (str): 要转换的字符串
    
    返回:
        str: 转换为大写的字符串
    """
    return s.upper()

@mcp.tool()
def to_lower(s: str) -> str:
    """
    字符串转小写工具函数
    
    参数:
        s (str): 要转换的字符串
    
    返回:
        str: 转换为小写的字符串
    """
    return s.lower()

@mcp.tool()
def sum_list(numbers: list[int]) -> int:
    """
    列表求和工具函数
    
    参数:
        numbers (list[int]): 要求和的数字列表
    
    返回:
        int: 列表中所有数字的和
    """
    return sum(numbers)

@mcp.tool()
def max_in_list(numbers: list[int]) -> int:
    """
    查找列表最大值工具函数
    
    参数:
        numbers (list[int]): 要查找的数字列表
    
    返回:
        int: 列表中的最大值
    """
    return max(numbers)

@mcp.tool()
def min_in_list(numbers: list[int]) -> int:
    """
    查找列表最小值工具函数
    
    参数:
        numbers (list[int]): 要查找的数字列表
    
    返回:
        int: 列表中的最小值
    """
    return min(numbers)

@mcp.tool()
def average_list(numbers: list[int]) -> float:
    """
    计算列表平均值工具函数
    
    参数:
        numbers (list[int]): 要计算平均值的数字列表
    
    返回:
        float: 列表中所有数字的平均值
    """
    return sum(numbers) / len(numbers)

    
# ==================== 资源函数定义 ====================
# 这些函数提供动态资源访问功能

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """
    个性化问候资源函数
    
    这个函数定义了一个动态资源，客户端可以通过 "greeting://{name}" 格式访问
    例如：greeting://Alice 会返回 "Hello, Alice!"
    
    参数:
        name (str): 问候的对象名称
    
    返回:
        str: 个性化的问候语
    """
    return f"Hello, {name}!"


# ==================== 主函数 ====================
def main() -> None:
    """
    主函数 - 启动MCP服务器
    
    这个函数是服务器的入口点，当模块被直接运行时会被调用。
    它启动MCP服务器并监听标准输入输出（stdio）连接。
    
    服务器启动后，客户端可以通过MCP协议连接到服务器并调用上面定义的工具函数。
    """
    
    # 启动MCP服务器，使用stdio传输协议
    # stdio协议通过标准输入输出进行通信，适合本地或SSH连接
    mcp.run(transports='stdio')
