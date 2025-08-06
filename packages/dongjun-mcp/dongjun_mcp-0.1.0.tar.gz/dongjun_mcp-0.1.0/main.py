from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo")  # 创建MCP Server并命名为"Demo"


# 装饰器用来给下面的函数增加功能
@mcp.tool()  # 使用该装饰器将此函数注册为MCP Server的工具，工具是MCP Server提供的可执行功能，客户端可以调用这些工具来完成计算或操作
def add(a: int, b: int) -> int:  # 这里的类型修饰符是必须要写的（该函数接收两个int类型的参数并返回int类型的结果）其有助于大模型理解此工具的传参是什么类型的
    """两个数字相加"""
    # 上面的注释是必须要写的，其主要功能是使用自然语言告诉AI大模型此函数的功能是什么
    return a + b


if __name__ == "__main__":
    mcp.run(transport="stdio")  # 使用stdio的方式运行该MCP Server
    # mcp.run(transport="streamable-http")  # 使用Streamable HTTP的方式运行该MCP Server
