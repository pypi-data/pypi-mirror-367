#!/usr/bin/env python3

import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def test_mcp():
    # Start the server process
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "sast_fixer_mcp"],
    )
    
    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List tools
            result = await session.list_tools()
            print("Available tools:")
            for tool in result.tools:
                print(f"- {tool.name}: {tool.description}")
            
            # Test a tool call
            print("\nTesting get_pending_vulnerability_json_files...")
            response = await session.call_tool("get_pending_vulnerability_json_files", {})
            print("Response:", response.content[0].text if response.content else "No content")

if __name__ == "__main__":
    asyncio.run(test_mcp())