import os
import json
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

client = OpenAI(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

def mcp_tools_to_openai(tools):
    """Convert MCP tool definitions to OpenAI function-calling format."""
    converted = []
    for tool in tools.tools:
        converted.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            },
        })
    return converted

async def run_agent(user_message: str) -> str:
    """Full agentic loop: user message -> Qwen decides -> MCP tools -> answer."""
    params = StdioServerParameters(command="python", args=["mcp_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            openai_tools = mcp_tools_to_openai(tools)

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are LeadFlow Agent, a lead management assistant for a small "
                        "appointment-based business, living inside Slack. You have tools to "
                        "add, list, update and assign leads. Use them when needed. "
                        "Keep replies short, friendly and formatted for Slack (use *bold* and bullet points). "
                        "Never invent leads - always check the database via tools."
                    ),
                },
                {"role": "user", "content": user_message},
            ]

            # Agent loop: let the model call tools until it has an answer
            for _ in range(5):
                response = client.chat.completions.create(
                    model="qwen-plus",
                    messages=messages,
                    tools=openai_tools,
                )
                msg = response.choices[0].message

                if not msg.tool_calls:
                    return msg.content or "Done!"

                messages.append(msg)
                for tool_call in msg.tool_calls:
                    args = json.loads(tool_call.function.arguments or "{}")
                    result = await session.call_tool(tool_call.function.name, args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result.content[0].text,
                    })

            return "I got a bit lost — try rephrasing that?"

def ask_agent(user_message: str) -> str:
    """Synchronous wrapper for use inside the Slack bot."""
    return asyncio.run(run_agent(user_message))