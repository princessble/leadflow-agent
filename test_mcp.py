import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command="python", args=["mcp_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("✅ MCP server is up! Available tools:")
            for tool in tools.tools:
                print(f"  • {tool.name}: {tool.description.strip().splitlines()[0]}")

            print("\n🧪 Calling get_open_leads via MCP...")
            result = await session.call_tool("get_open_leads", {})
            print(result.content[0].text)

asyncio.run(main())