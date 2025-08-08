import asyncio
from typing import Any, Optional, List, Dict
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from .llm_manger import LLMManager
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, ToolCall
from pydantic import BaseModel
load_dotenv()
from mcp.types import Tool
from logging import Logger

logger = Logger(name='logger')


class MCPClient:
    def __init__(self, llm_manager: LLMManager, server_urls: List[str]):
        self.sessions: Dict[str, ClientSession] = {}  # Map server_url -> session
        self.exit_stack = AsyncExitStack()
        self.llm_manager = llm_manager
        self.server_urls = server_urls

    async def connect_to_servers(self):
        """Connect to multiple MCP servers."""
        for server_url in self.server_urls:
            # Detect protocol (http or stdio)
            if server_url.startswith("http"):
                http_transport = await self.exit_stack.enter_async_context(
                    streamablehttp_client(server_url)
                )
                streamablehttp, write, _ = http_transport
                session = await self.exit_stack.enter_async_context(ClientSession(streamablehttp, write))
            else:
                # Assume stdio (local process)
                params = StdioServerParameters(command=[server_url])
                session = await self.exit_stack.enter_async_context(ClientSession(params))
            await session.initialize()
            self.sessions[server_url] = session
            # List available tools
            response = await session.list_tools()
            tools = response.tools
            print(f"\nConnected to server {server_url} with tools: {[tool.name for tool in tools]}")

    async def register_tools(self):
        # Register tools from all servers
        all_tools = []
        for session in self.sessions.values():
            response = await session.list_tools()
            all_tools.extend(response.tools)
        self.llm_manager.register_tools(all_tools)

    async def call_tool(self, tool_call: ToolCall):
        # Find the session that has the tool
        for session in self.sessions.values():
            response = await session.list_tools()
            if any(tool.name == tool_call["name"] for tool in response.tools):
                result = await session.call_tool(tool_call["name"], tool_call["args"])
                logger.info(f"[Calling tool {tool_call['name']} with args {tool_call['args']}]")
                return ToolMessage(tool_call_id=tool_call["id"], content=result.structuredContent)
        raise Exception(f"Tool {tool_call['name']} not found on any connected server.")

    async def process_query(self, query: str) -> str:
        messages = []
        user_message = HumanMessage(content=query)
        messages.append(user_message)
        tool_call = True
        while tool_call:
            llm_response = self.llm_manager.get_response(messages)
            messages.append(llm_response)
            print(llm_response)
            if len(llm_response.tool_calls):
                for tool_call in llm_response.tool_calls:
                    tool_message = await self.call_tool(tool_call=tool_call)
                    messages.append(tool_message)
            else:
                tool_call = False
        return str(llm_response)

    async def chat_loop(self):
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    llm_manager = LLMManager(provider='gemini')
    # Example: connect to two servers, one HTTP and one local script
    server_urls = [
        "http://127.0.0.1:8000/mcp",
        # "python path/to/other_server.py",  # For stdio, if needed
    ]
    client = MCPClient(llm_manager, server_urls)
    try:
        await client.connect_to_servers()
        await client.register_tools()
        await client.chat_loop()
    except Exception as E:
        print(E)
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())