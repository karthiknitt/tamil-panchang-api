#!/usr/bin/env python3
"""
Tamil Panchang MCP Server - STDIO Version
For Claude Desktop compatibility, uses standard input/output instead of SSE.
"""

import httpx
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

# FastAPI base URL (internal communication)
FASTAPI_BASE = "http://localhost:8000"

# Create MCP server instance
server = Server("tamil-panchang")


def format_panchang_response(data: dict) -> str:
    """Format the panchang JSON response into readable text."""
    lines = []

    if "date" in data:
        lines.append(f"Date: {data['date']}")
    if "location" in data:
        loc = data["location"]
        lines.append(f"Location: {loc.get('latitude')}N, {loc.get('longitude')}E (UTC+{loc.get('timezone')})")

    lines.append("")
    lines.append("Panchang Elements:")
    if "weekday" in data:
        lines.append(f"  Weekday: {data['weekday']}")
    if "tithi" in data:
        lines.append(f"  Tithi: {data['tithi']}")
    if "nakshatra" in data:
        lines.append(f"  Nakshatra: {data['nakshatra']}")
    if "yoga" in data:
        lines.append(f"  Yoga: {data['yoga']}")
    if "karana" in data:
        lines.append(f"  Karana: {data['karana']}")
    if "tamil_month" in data:
        lines.append(f"  Tamil Month: {data['tamil_month']}")

    lines.append("")
    lines.append("Sun Timings:")
    if "sunrise" in data:
        lines.append(f"  Sunrise: {data['sunrise']}")
    if "sunset" in data:
        lines.append(f"  Sunset: {data['sunset']}")

    lines.append("")
    lines.append("Inauspicious Timings (Avoid for important activities):")
    if "rahu_kalam" in data:
        lines.append(f"  Rahu Kalam: {data['rahu_kalam']}")
    if "yamagandam" in data:
        lines.append(f"  Yamagandam: {data['yamagandam']}")
    if "gulikai_kalam" in data:
        lines.append(f"  Gulikai Kalam: {data['gulikai_kalam']}")

    lines.append("")
    lines.append("---")
    lines.append("Raw JSON data:")
    lines.append(json.dumps(data, indent=2, ensure_ascii=False))

    return "\n".join(lines)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available panchang calculation tools."""
    return [
        Tool(
            name="get_panchang",
            description=(
                "Calculate complete Tamil Panchang for a specific date and location. "
                "Returns tithi, nakshatra, yoga, karana, sunrise/sunset times, "
                "inauspicious timings, and solar month information."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "latitude": {"type": "number", "description": "Latitude (-90 to +90)"},
                    "longitude": {"type": "number", "description": "Longitude (-180 to +180)"},
                    "timezone": {"type": "number", "description": "UTC offset (default: 5.5)"}
                },
                "required": ["date", "latitude", "longitude"]
            }
        ),
        Tool(
            name="get_today_panchang",
            description="Get today's Tamil Panchang for a specified location.",
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {"type": "number", "description": "Latitude (-90 to +90)"},
                    "longitude": {"type": "number", "description": "Longitude (-180 to +180)"},
                    "timezone": {"type": "number", "description": "UTC offset (default: 5.5)"}
                },
                "required": ["latitude", "longitude"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool invocations by forwarding to FastAPI."""
    async with httpx.AsyncClient() as client:
        try:
            if name == "get_panchang":
                response = await client.post(
                    f"{FASTAPI_BASE}/api/panchang",
                    json={
                        "date": arguments.get("date"),
                        "latitude": arguments.get("latitude"),
                        "longitude": arguments.get("longitude"),
                        "timezone": arguments.get("timezone", 5.5)
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=f"Tamil Panchang for {arguments.get('date')}:\n\n{format_panchang_response(result)}"
                )]

            elif name == "get_today_panchang":
                response = await client.post(
                    f"{FASTAPI_BASE}/api/today",
                    json={
                        "latitude": arguments.get("latitude"),
                        "longitude": arguments.get("longitude"),
                        "timezone": arguments.get("timezone", 5.5)
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=f"Today's Tamil Panchang:\n\n{format_panchang_response(result)}"
                )]

            else:
                return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
