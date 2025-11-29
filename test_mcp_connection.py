#!/usr/bin/env python3
"""
Test script to verify MCP server connection and functionality.
This simulates what Claude Desktop does when connecting to an MCP server.
"""

import asyncio
import httpx
import json
import sys


async def test_mcp_server():
    """Test the MCP server using SSE transport."""

    base_url = "http://localhost:8001"

    print("[*] Testing Tamil Panchang MCP Server...")
    print(f"[*] URL: {base_url}")
    print()

    # Test 1: Health check
    print("Test 1: Health Check")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            response.raise_for_status()
            health_data = response.json()
            print(f"[PASS] Health check passed: {json.dumps(health_data, indent=2)}")
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return False

    print()

    # Test 2: Initialize MCP connection
    print("Test 2: Initialize MCP Connection (POST to /sse)")
    try:
        async with httpx.AsyncClient() as client:
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }

            # POST to /sse to initiate connection
            print(f"[*] Sending POST with payload: {json.dumps(init_message, indent=2)}")
            response = await client.post(
                f"{base_url}/sse",
                json=init_message,
                headers={"Content-Type": "application/json"},
                timeout=2.0
            )

            if response.status_code == 200:
                print(f"[PASS] POST accepted (Status: {response.status_code})")
                print(f"[*] Response:\n{response.text[:500]}")
            else:
                print(f"[FAIL] POST failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"[FAIL] Initialize failed: {e}")
        return False

    print()

    # Test 3: FastAPI endpoint (to verify MCP can reach it)
    print("Test 3: Verify FastAPI Backend")
    try:
        async with httpx.AsyncClient() as client:
            test_payload = {
                "latitude": 13.0827,
                "longitude": 80.2707,
                "timezone": 5.5
            }
            response = await client.post(
                "http://localhost:8000/api/today",
                json=test_payload,
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            print(f"[PASS] FastAPI working: Got panchang for {data.get('date', 'unknown date')}")
            print(f"   Nakshatra: {data.get('nakshatra', 'N/A')}")
            print(f"   Tithi: {data.get('tithi', 'N/A')}")
    except Exception as e:
        print(f"[FAIL] FastAPI test failed: {e}")
        return False

    print()
    print("=" * 60)
    print("[PASS] All tests passed!")
    print()
    print("[*] Instructions for Claude Desktop:")
    print("Add this to your claude_desktop_config.json:")
    print()
    print(json.dumps({
        "mcpServers": {
            "tamil-panchang": {
                "url": "http://localhost:8001/sse"
            }
        }
    }, indent=2))
    print()
    print("Then restart Claude Desktop and ask:")
    print("  'What is today's panchang in Chennai?'")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
