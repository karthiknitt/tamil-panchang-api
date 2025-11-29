#!/usr/bin/env python3
"""
Test production MCP server to verify it works correctly.
"""

import asyncio
import os
from mcp import ClientSession
from mcp.client.sse import sse_client


async def test_production_mcp_server():
    """Test the production MCP server."""

    server_url = "https://panchang.karthikwrites.com/mcp/sse"

    print(f"Connecting to production MCP server at {server_url}...")

    try:
        async with sse_client(
            url=server_url,
        ) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                print("✓ Connected successfully!")
                print("\nInitializing session...")
                await session.initialize()
                print("✓ Session initialized!")

                # List available tools
                print("\nListing tools...")
                tools_response = await session.list_tools()
                print(f"✓ Found {len(tools_response.tools)} tools:")
                for tool in tools_response.tools:
                    print(f"  - {tool.name}: {tool.description[:60]}...")

                # Call get_today_panchang
                print("\n" + "="*60)
                print("Calling get_today_panchang for Chennai (13.0827°N, 80.2707°E)...")
                print("="*60)
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
                        # Show first 500 characters only
                        text = content.text[:500]
                        # Remove emojis for Windows console compatibility
                        text = text.encode('ascii', 'ignore').decode('ascii')
                        print(text)
                        print("\n... (truncated for brevity)")
                    else:
                        print(content)
                print("=============\n")

                print("SUCCESS: Production MCP server is working correctly!")
                return True

    except Exception as e:
        print(f"\nError testing production server: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_production_mcp_server())
    exit(0 if success else 1)
