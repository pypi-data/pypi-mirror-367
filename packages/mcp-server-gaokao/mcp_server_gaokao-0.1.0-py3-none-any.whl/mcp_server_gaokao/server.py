import logging

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from mcp_server_gaokao.tools import QueryMajorInfo

query_major_info_tool = QueryMajorInfo()
tools_map = {query_major_info_tool.name: query_major_info_tool}


async def serve(return_format: str) -> None:
    server = Server(name="gaokao-server")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name=query_major_info_tool.name,
                description=query_major_info_tool.description,
                inputSchema=query_major_info_tool.parameters,
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        try:
            tool = tools_map[name]
        except Exception as e:
            text = str(e)
        else:
            result = tool.execute(**arguments, return_format=return_format)
            if result.success:
                text = f"{result.name}工具调用成功！返回内容如下：\n{result.content}"
            else:
                text = f"{result.name}工具调用失败！错误信息如下：\n{result.content}"
        return [types.TextContent(type="text", text=text)]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)


def main():
    import argparse
    import asyncio

    # 配置日志记录器
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    #     handlers=[logging.StreamHandler()],  # 输出到控制台
    # )

    parser = argparse.ArgumentParser(description="Query major information")
    parser.add_argument(
        "--return_format",
        type=str,
        choices=["json", "markdown"],
        default="json",
        help="The value is 'json' or 'markdown', default is 'json'",
    )
    args = parser.parse_args()
    # logging.info("Starting mcp-server-gaokao with return format: %s", args.return_format)
    asyncio.run(serve(return_format=args.return_format))
