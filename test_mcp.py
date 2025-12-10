#!/usr/bin/env python3
"""
Simple test script to verify MCP server tools are working correctly.
Tests the MCP server running on localhost:8001
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

async def test_mcp_sse():
    """Test MCP server via SSE transport"""
    print("🔍 Testing MCP Server via SSE transport...")
    print(f"📡 Connecting to http://localhost:8001/sse")

    try:
        # Connect to SSE server
        async with sse_client("http://localhost:8001/sse") as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                print("\n✅ Connected to MCP server")
                await session.initialize()
                print("✅ Session initialized")

                # List available tools
                print("\n📋 Listing available tools...")
                tools_result = await session.list_tools()
                print(f"✅ Found {len(tools_result.tools)} tools:")
                for tool in tools_result.tools:
                    print(f"   - {tool.name}: {tool.description[:80]}...")

                # Test get_today_panchang tool
                print("\n🧪 Testing 'tamil_panchang_get_today' tool...")
                result = await session.call_tool(
                    "tamil_panchang_get_today",
                    arguments={
                        "params": {
                            "latitude": 13.0827,
                            "longitude": 80.2707,
                            "timezone": 5.5,
                            "response_format": "json"
                        }
                    }
                )
                print(f"✅ Tool execution successful!")

                # Parse and display result
                if result.content:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        result_text = content.text
                        try:
                            # Try to parse as JSON
                            data = json.loads(result_text)
                            print(f"\n📅 Date: {data.get('date', 'N/A')}")
                            print(f"📍 Location: {data.get('location', {}).get('name', 'N/A')}")
                            print(f"🌙 Tithi: {data.get('tithi', {}).get('name', 'N/A')}")
                            print(f"⭐ Nakshatra: {data.get('nakshatra', {}).get('name', 'N/A')}")
                            print(f"☀️ Sunrise: {data.get('sunrise', 'N/A')}")
                            print(f"🌅 Sunset: {data.get('sunset', 'N/A')}")
                        except json.JSONDecodeError:
                            # Not JSON, display as text (probably markdown)
                            print(f"\n📄 Result (first 500 chars):\n{result_text[:500]}...")

                print("\n✅ All MCP tests passed!")
                return True

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_sse())
    exit(0 if success else 1)
