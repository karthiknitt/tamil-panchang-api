"""
Tamil Panchang MCP Server
Wraps the existing FastAPI REST endpoints to provide MCP (Model Context Protocol) access for AI agents.
Uses FastMCP for built-in SSE transport support.
"""

import httpx
from fastmcp import FastMCP

# FastAPI base URL (internal communication)
FASTAPI_BASE = "http://localhost:8000"

# Create FastMCP server instance
mcp = FastMCP("tamil-panchang")


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
    import json
    lines.append(json.dumps(data, indent=2, ensure_ascii=False))

    return "\n".join(lines)


@mcp.tool()
async def get_panchang(date: str, latitude: float, longitude: float, timezone: float = 5.5) -> str:
    """
    Calculate complete Tamil Panchang (astronomical calendar) for a specific date and location.

    Returns tithi, nakshatra, yoga, karana, sunrise/sunset times, inauspicious timings
    (Rahu Kalam, Yamagandam, Gulikai Kalam), and solar month information.
    All names are in Tamil script.

    Args:
        date: Date in YYYY-MM-DD format (e.g., '2024-01-15')
        latitude: Latitude of location (-90 to +90, e.g., 13.0827 for Chennai)
        longitude: Longitude of location (-180 to +180, e.g., 80.2707 for Chennai)
        timezone: UTC offset in hours (e.g., 5.5 for IST). Default: 5.5

    Returns:
        Formatted panchang data as text
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FASTAPI_BASE}/api/panchang",
            json={
                "date": date,
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone
            },
            timeout=10.0
        )
        response.raise_for_status()
        result = response.json()

    return f"Tamil Panchang for {date}:\n\n{format_panchang_response(result)}"


@mcp.tool()
async def get_today_panchang(latitude: float, longitude: float, timezone: float = 5.5) -> str:
    """
    Get today's Tamil Panchang for a specified location.

    Convenience tool that automatically uses the current date.
    Returns the same complete panchang data as get_panchang.

    Args:
        latitude: Latitude of location (-90 to +90, e.g., 13.0827 for Chennai)
        longitude: Longitude of location (-180 to +180, e.g., 80.2707 for Chennai)
        timezone: UTC offset in hours (e.g., 5.5 for IST). Default: 5.5

    Returns:
        Formatted panchang data as text
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FASTAPI_BASE}/api/today",
            json={
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone
            },
            timeout=10.0
        )
        response.raise_for_status()
        result = response.json()

    return f"Today's Tamil Panchang:\n\n{format_panchang_response(result)}"


if __name__ == "__main__":
    import argparse

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

    # Run with FastMCP's built-in SSE transport
    mcp.run(transport="sse", host=args.host, port=args.port)
