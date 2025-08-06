import asyncio
from typing import Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from llm_manger import LLMManager
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, ToolCall
from pydantic import BaseModel
load_dotenv()  # load environment variables from .env
from mcp.types import Tool
from logging import Logger

logger= Logger(name='logger')





class MCPClient:
    def __init__(self, llm_manager: LLMManager):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm_manager = llm_manager
        # No anthropic here

    async def connect_to_server(self):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
       
        server_url = "http://127.0.0.1:8000/mcp" 
        
        http_transport = await self.exit_stack.enter_async_context(streamablehttp_client(server_url))

        streamablehttp, write, _ = http_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(streamablehttp, write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
    
    async def register_tools(self):
        response = await self.session.list_tools() # type: ignore
        self.llm_manager.register_tools(response.tools)

    async def call_tool(self, tool_call: ToolCall):
            # Execute tool call
            result = await self.session.call_tool(tool_call["name"], tool_call["args"]) # type: ignore
            logger.info(f"[Calling tool {tool_call["name"]} with args {tool_call["args"]}]")
            return ToolMessage(tool_call_id= tool_call["id"],content = result.structuredContent) # type: ignore



    async def process_query(self, query: str) -> str:
        """Process a query using the selected LLM and available tools"""
        messages= []
        user_message = HumanMessage(content=query)
        messages.append(user_message)
        # Get available tools from the server
        # Use llm_manager to get the LLM response
        tool_call=True
        while tool_call:
            llm_response = self.llm_manager.get_response(messages)
            messages.append(llm_response)
            print(llm_response)
            if len(llm_response.tool_calls):
                for tool_call in llm_response.tool_calls: 
                    tool_message = await self.call_tool(tool_call= tool_call)
                    messages.append(tool_message)
            else: 
                tool_call=False


    


        # If the LLM response suggests a tool call, handle it here
        # (This is a placeholder; you may need to parse the response for tool triggers)
        # For now, just return the LLM response as text
        return str(llm_response)
    

    async def chat_loop(self):
        """Run an interactive chat loop"""
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
        """Clean up resources"""
        await self.exit_stack.aclose()




async def main():
    llm_manager = LLMManager(provider='gemini')
    client = MCPClient(llm_manager)

    try:
        await client.connect_to_server()
        await client.register_tools()
        await client.chat_loop()
    except Exception as E: 
        print(E)
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())