# MCP SSE Server Fix Summary

## Problem

The Tamil Panchang MCP server was not working properly over SSE transport. The issue was:

- When clients connected to `/sse`, the SSE stream would hang without sending any data
- The server never sent the required `event: endpoint` message that tells clients where to POST messages
- This caused a deadlock: clients couldn't send messages because they didn't know the endpoint, and the server was waiting for messages

## Root Cause

The original implementation used low-level MCP SDK components (`mcp.server.Server` + `mcp.server.sse.SseServerTransport`) with manual Starlette integration. This approach had complex initialization requirements and the SSE endpoint setup wasn't working correctly.

## Solution

Migrated to **FastMCP**, which provides built-in SSE transport support with a simple, high-level API.

### Code Changes

1. **[mcp_server.py](mcp_server.py)** - Complete rewrite:
   - Changed from `mcp.server.Server` to `fastmcp.FastMCP`
   - Removed manual Starlette app creation and route setup
   - Converted from `@server.list_tools()` and `@server.call_tool()` to `@mcp.tool()` decorators
   - Simplified startup to just `mcp.run(transport="sse", host=host, port=port)`

2. **[requirements.txt](requirements.txt)** - Added dependency:
   - Added `fastmcp>=0.2.0`

### Key Differences

**Before (Complex, manual setup):**
```python
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette

app = Server("tamil-panchang")

@app.list_tools()
async def list_tools() -> list[Tool]:
    # ... define tools

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # ... handle tool calls

# Manual Starlette setup
sse = SseServerTransport("/messages/")
async def handle_sse(request):
    async with sse.connect_sse(...) as streams:
        await app.run(...)

starlette_app = Starlette(routes=[...])
uvicorn.run(starlette_app, ...)
```

**After (Simple, automatic):**
```python
from fastmcp import FastMCP

mcp = FastMCP("tamil-panchang")

@mcp.tool()
async def get_panchang(date: str, latitude: float, longitude: float, timezone: float = 5.5) -> str:
    # ... implementation

@mcp.tool()
async def get_today_panchang(latitude: float, longitude: float, timezone: float = 5.5) -> str:
    # ... implementation

mcp.run(transport="sse", host="0.0.0.0", port=8001)
```

## Testing Results

The fixed server now:

1. ✅ Sends the `event: endpoint` message immediately upon SSE connection:
   ```
   event: endpoint
   data: /messages/?session_id=<session_id>
   ```

2. ✅ Lists 2 tools correctly:
   - `get_panchang` - Calculate panchang for specific date
   - `get_today_panchang` - Calculate panchang for today

3. ✅ Successfully processes tool calls and returns complete panchang data

Test output confirmed full functionality - see [test_mcp_client.py](test_mcp_client.py) for the working test client.

## Deployment Instructions

### Local Testing (Already Working)

```bash
# Use the standalone Docker Compose configuration
docker-compose -f docker-compose.standalone.yml up -d

# Check logs
docker-compose -f docker-compose.standalone.yml logs -f

# Test the SSE endpoint
curl http://localhost:8001/sse  # Should see "event: endpoint" message

# Test with MCP client
python test_mcp_client.py
```

### Production Deployment

The production deployment uses Traefik reverse proxy with path-based routing:

1. **Prerequisites:**
   - Traefik must be running
   - The `dokploy-network` Docker network must exist
   - Domain: `panchang.karthikwrites.com`

2. **Deploy:**
   ```bash
   # On the production server
   docker-compose down  # Stop existing container
   docker-compose build --no-cache  # Rebuild with latest code
   docker-compose up -d  # Start updated container
   ```

3. **Verify:**
   ```bash
   # Check SSE endpoint (should see "event: endpoint")
   curl https://panchang.karthikwrites.com/mcp/sse

   # Check FastAPI health
   curl https://panchang.karthikwrites.com/api/health
   ```

4. **Routes (via Traefik):**
   - FastAPI: `https://panchang.karthikwrites.com/api/*` → port 8000
   - MCP SSE: `https://panchang.karthikwrites.com/mcp/*` → port 8001 (with `/mcp` prefix stripped)

### Using in Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tamil-panchang": {
      "url": "https://panchang.karthikwrites.com/mcp/sse"
    }
  }
}
```

Then restart Claude Desktop and ask: *"What's today's panchang in Chennai?"*

## Technical Details

### Why FastMCP?

FastMCP is an official higher-level framework built on top of the MCP Python SDK. It:

- Handles SSE transport setup automatically
- Manages session IDs and message routing internally
- Provides simpler decorator-based tool registration
- Eliminates boilerplate code for common patterns
- Is actively maintained by the MCP team

### SSE Protocol Flow

1. Client connects to `/sse` via GET request
2. Server immediately sends SSE event:
   ```
   event: endpoint
   data: /messages/?session_id=<unique_id>
   ```
3. Client now knows where to POST JSON-RPC messages
4. Client sends `initialize` request to the endpoint
5. Server responds with capabilities
6. Client can now call tools via JSON-RPC

The old implementation failed at step 2 - it never sent the endpoint event.

## Files Changed

- `mcp_server.py` - Completely rewritten to use FastMCP
- `requirements.txt` - Added fastmcp dependency
- `Dockerfile` - No changes needed (requirements.txt handles it)
- `supervisord.conf` - No changes needed
- `docker-compose.yml` - No changes needed
- `docker-compose.standalone.yml` - No changes needed

## Backward Compatibility

The external API remains unchanged:
- Same SSE endpoint: `/sse`
- Same tools exposed: `get_panchang`, `get_today_panchang`
- Same JSON response format

Only the internal implementation changed from low-level Server to high-level FastMCP.

## References

- [FastMCP Documentation](https://gofastmcp.com/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [SSE Transport Spec](https://modelcontextprotocol.io/docs/concepts/transports)
