#!/usr/bin/env python3
"""
Test script to verify the MCP SSE endpoint is working correctly.
An SSE endpoint should immediately send an 'event: endpoint' message.
"""

import requests
import sys
import time

def test_sse_endpoint(url):
    """
    Test the SSE endpoint by making a GET request and reading the initial event.
    """
    print(f"🔍 Testing SSE endpoint: {url}")
    print("=" * 60)

    try:
        # Make a GET request with streaming enabled
        response = requests.get(
            url,
            stream=True,
            headers={
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            },
            timeout=10
        )

        print(f"✅ Connection Status: {response.status_code}")
        print(f"📋 Response Headers:")
        for header, value in response.headers.items():
            print(f"   {header}: {value}")
        print()

        # Check if Content-Type is correct
        content_type = response.headers.get('Content-Type', '')
        if 'text/event-stream' in content_type:
            print("✅ Correct Content-Type: text/event-stream")
        else:
            print(f"⚠️  Warning: Expected 'text/event-stream' but got '{content_type}'")
        print()

        # Read the first few lines (the initial event)
        print("📡 Receiving SSE events (first 10 lines):")
        print("-" * 60)

        line_count = 0
        for line in response.iter_lines(decode_unicode=True):
            if line:
                print(f"   {line}")
                line_count += 1
            if line_count >= 10:  # Read first 10 lines
                break

        print("-" * 60)

        if line_count == 0:
            print("\n❌ ERROR: No data received from SSE endpoint!")
            print("   The endpoint should immediately send an 'event: endpoint' message.")
            return False
        else:
            print(f"\n✅ Received {line_count} lines from SSE stream")
            print("   (Connection interrupted after reading first 10 lines)")
            return True

    except requests.exceptions.Timeout:
        print(f"\n❌ ERROR: Connection timed out after 10 seconds")
        print("   The endpoint should respond immediately with SSE events.")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ ERROR: Connection failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Default to production URL, but allow override
    url = sys.argv[1] if len(sys.argv) > 1 else "https://panchang.karthikwrites.com/mcp/sse"

    print("🚀 MCP SSE Endpoint Test")
    print()

    success = test_sse_endpoint(url)

    print()
    print("=" * 60)
    if success:
        print("✅ SSE endpoint is working correctly!")
        print()
        print("💡 NOTE: When accessed via a web browser, SSE endpoints may")
        print("   appear to 'hang' or show raw event data. This is normal.")
        print("   Use an MCP client (like Claude Desktop) to interact with it.")
    else:
        print("❌ SSE endpoint test failed!")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Check if the container is running: docker ps")
        print("   2. Check container logs: docker-compose logs mcp")
        print("   3. Verify the endpoint URL is correct")
        print("   4. Test locally first: python test_sse_endpoint.py http://localhost:8001/sse")

    print("=" * 60)
    sys.exit(0 if success else 1)
