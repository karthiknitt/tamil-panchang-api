#!/usr/bin/env python3
"""
Test MCP client to verify the server works correctly.
"""

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client


async def test_mcp_server():
    """Test the MCP server by calling the get_today_panchang tool."""

    print("Connecting to MCP server at http://localhost:8001/sse...")

    async with sse_client("http://localhost:8001/sse") as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            print("Initializing session...")
            await session.initialize()

            # List available tools
            print("\nListing tools...")
            tools_response = await session.list_tools()
            print(f"Found {len(tools_response.tools)} tools:")
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description[:80]}...")

            # Call get_today_panchang
            print("\nCalling get_today_panchang for Chennai (13.0827°N, 80.2707°E)...")
            result = await session.call_tool(
                "get_today_panchang",
                {
                    "latitude": 13.0827,
                    "longitude": 80.2707,
                    "timezone": 5.5
                }
            )

            print("\n=== RESULT ===")
            for content in result.content:
                if hasattr(content, 'text'):
                    # Remove emojis for Windows console compatibility
                    text = content.text.encode('ascii', 'ignore').decode('ascii')
                    print(text)
                else:
                    print(content)
            print("=============\n")

            print("✅ Test successful!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
