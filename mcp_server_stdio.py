#!/usr/bin/env python3
"""
Tamil Panchang MCP Server - STDIO Version
For Claude Desktop compatibility, uses standard input/output.
Reuses the server instance from app.py to ensure consistency.
"""

import asyncio
from mcp.server.stdio import stdio_server
from app import mcp_server

async def main():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
