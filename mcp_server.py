"""
Tamil Panchang MCP Server
Wraps the existing FastAPI REST endpoints to provide MCP (Model Context Protocol) access for AI agents.
Uses low-level MCP SDK with manual Starlette setup for reliable SSE transport.
"""

import httpx
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import argparse
import json

# FastAPI base URL (internal communication)
FASTAPI_BASE = "http://localhost:8000"

# Create MCP server instance
server = Server("tamil-panchang")


def format_panchang_response(data: dict) -> str:
    """
    Format the panchang JSON response into readable text for AI agents.
    This makes it easier for AI to parse and explain to users.
    """
    lines = []

    # Date and location
    if "date" in data:
        lines.append(f"📅 Date: {data['date']}")
    if "location" in data:
        loc = data["location"]
        lines.append(f"📍 Location: {loc.get('latitude')}°N, {loc.get('longitude')}°E (Timezone: UTC+{loc.get('timezone')})")

    lines.append("")

    # Basic panchang elements
    lines.append("🌙 Panchang Elements:")
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

    # Sun times
    lines.append("☀️ Sun Timings:")
    if "sunrise" in data:
        lines.append(f"  Sunrise: {data['sunrise']}")
    if "sunset" in data:
        lines.append(f"  Sunset: {data['sunset']}")

    lines.append("")

    # Inauspicious timings
    lines.append("⚠️ Inauspicious Timings (Avoid for important activities):")
    if "rahu_kalam" in data:
        lines.append(f"  Rahu Kalam: {data['rahu_kalam']}")
    if "yamagandam" in data:
        lines.append(f"  Yamagandam: {data['yamagandam']}")
    if "gulikai_kalam" in data:
        lines.append(f"  Gulikai Kalam: {data['gulikai_kalam']}")

    # Include raw JSON for programmatic access
    lines.append("")
    lines.append("---")
    lines.append("Raw JSON data (for detailed analysis):")
    lines.append(json.dumps(data, indent=2, ensure_ascii=False))

    return "\n".join(lines)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available panchang calculation tools."""
    return [
        Tool(
            name="get_panchang",
            description=(
                "Calculate complete Tamil Panchang (astronomical calendar) for a specific date and location. "
                "Returns tithi, nakshatra, yoga, karana, sunrise/sunset times, inauspicious timings "
                "(Rahu Kalam, Yamagandam, Gulikai Kalam), and solar month information. "
                "All names are in Tamil script."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (e.g., '2024-01-15')"
                    },
                    "latitude": {
                        "type": "number",
                        "description": "Latitude of location (-90 to +90, e.g., 13.0827 for Chennai)"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude of location (-180 to +180, e.g., 80.2707 for Chennai)"
                    },
                    "timezone": {
                        "type": "number",
                        "description": "UTC offset in hours (e.g., 5.5 for IST). Default: 5.5"
                    }
                },
                "required": ["date", "latitude", "longitude"]
            }
        ),
        Tool(
            name="get_today_panchang",
            description=(
                "Get today's Tamil Panchang for a specified location. "
                "Convenience tool that automatically uses the current date. "
                "Returns the same complete panchang data as get_panchang."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude of location (-90 to +90, e.g., 13.0827 for Chennai)"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude of location (-180 to +180, e.g., 80.2707 for Chennai)"
                    },
                    "timezone": {
                        "type": "number",
                        "description": "UTC offset in hours (e.g., 5.5 for IST). Default: 5.5"
                    }
                },
                "required": ["latitude", "longitude"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool invocations by forwarding requests to FastAPI endpoints.
    MCP server acts as a wrapper - no calculation logic here.
    """

    async with httpx.AsyncClient() as client:
        try:
            if name == "get_panchang":
                # Forward to /api/panchang endpoint
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
                # Forward to /api/today endpoint
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
                return [TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{name}'"
                )]

        except httpx.HTTPStatusError as e:
            return [TextContent(
                type="text",
                text=f"Error calling FastAPI: {e.response.status_code} - {e.response.text}"
            )]
        except httpx.RequestError as e:
            return [TextContent(
                type="text",
                text=f"Error connecting to FastAPI: {str(e)}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Unexpected error: {str(e)}"
            )]


def create_sse_server_app(mcp_server: Server) -> Starlette:
    """
    Create a Starlette application that serves the MCP server with SSE.
    Based on the working weather.py example from mcp-sse repository.
    """
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        """Handle SSE connection from MCP clients."""
        from starlette.responses import Response
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )
        return Response()

    return Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET", "OPTIONS"]),
            Mount("/messages/", app=sse.handle_post_message),
        ],
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tamil Panchang MCP Server - Exposes panchang tools via Model Context Protocol"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to listen on (default: 8001)"
    )

    args = parser.parse_args()

    print("🚀 Starting Tamil Panchang MCP Server...")
    print(f"📡 SSE endpoint: http://{args.host}:{args.port}/sse")
    print(f"🔗 Forwarding to FastAPI: {FASTAPI_BASE}")
    print("✨ Exposing 2 tools: get_panchang, get_today_panchang")

    # Create and run the Starlette app with SSE transport
    starlette_app = create_sse_server_app(server)

    uvicorn.run(
        starlette_app,
        host=args.host,
        port=args.port,
        log_level="info"
    )
