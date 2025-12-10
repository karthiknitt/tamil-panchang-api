"""
Tamil Panchang MCP Server

Modern MCP server using FastMCP framework that provides AI agents with access to
Tamil Panchang astronomical calculations. Wraps existing FastAPI endpoints.

Key Features:
- FastMCP framework with automatic schema generation
- Pydantic v2 input validation
- Proper error handling with actionable messages
- Support for both JSON and Markdown response formats
- Comprehensive tool annotations for AI understanding
"""

import httpx
import json
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

# FastAPI base URL for internal communication
FASTAPI_BASE = "http://localhost:8000"

# Initialize FastMCP server
mcp = FastMCP("tamil_panchang_mcp")


class ResponseFormat(str, Enum):
    """Output format options for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class PanchangInput(BaseModel):
    """Input model for specific date panchang calculation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    date: str = Field(
        ...,
        description="Date in YYYY-MM-DD format (e.g., '2024-01-15', '2025-12-25')",
        pattern=r'^\d{4}-\d{2}-\d{2}$',
        examples=["2024-01-15", "2025-12-25"]
    )
    latitude: float = Field(
        ...,
        description="Latitude of location in decimal degrees (-90 to +90). Examples: Chennai=13.0827, Mumbai=19.0760, Delhi=28.7041",
        ge=-90.0,
        le=90.0
    )
    longitude: float = Field(
        ...,
        description="Longitude of location in decimal degrees (-180 to +180). Examples: Chennai=80.2707, Mumbai=72.8777, Delhi=77.1025",
        ge=-180.0,
        le=180.0
    )
    timezone: float = Field(
        default=5.5,
        description="UTC offset in hours (e.g., 5.5 for IST, 8.0 for SGT). Default: 5.5 (India Standard Time)",
        ge=-12.0,
        le=14.0
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable formatted text or 'json' for raw structured data"
    )

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate date format and range."""
        import datetime
        try:
            date_obj = datetime.datetime.strptime(v, '%Y-%m-%d')
            # Reasonable range check (Swiss Ephemeris supports 13000 BCE to 17000 CE)
            if date_obj.year < 1900 or date_obj.year > 2100:
                raise ValueError("Date must be between 1900 and 2100")
            return v
        except ValueError as e:
            raise ValueError(f"Invalid date format or range: {e}")


class TodayPanchangInput(BaseModel):
    """Input model for today's panchang calculation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    latitude: float = Field(
        ...,
        description="Latitude of location in decimal degrees (-90 to +90). Examples: Chennai=13.0827, Mumbai=19.0760, Delhi=28.7041",
        ge=-90.0,
        le=90.0
    )
    longitude: float = Field(
        ...,
        description="Longitude of location in decimal degrees (-180 to +180). Examples: Chennai=80.2707, Mumbai=72.8777, Delhi=77.1025",
        ge=-180.0,
        le=180.0
    )
    timezone: float = Field(
        default=5.5,
        description="UTC offset in hours (e.g., 5.5 for IST, 8.0 for SGT). Default: 5.5 (India Standard Time)",
        ge=-12.0,
        le=14.0
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable formatted text or 'json' for raw structured data"
    )


def format_panchang_markdown(data: dict) -> str:
    """
    Format panchang data as human-readable Markdown.

    Args:
        data: Raw panchang JSON data from FastAPI

    Returns:
        Formatted markdown string with emojis and structure
    """
    lines = []

    # Header with date and location
    if "date" in data:
        lines.append(f"# Tamil Panchang for {data['date']}")
        lines.append("")

    if "location" in data:
        loc = data["location"]
        lines.append(f"**Location:** {loc.get('latitude', 'N/A')}°N, {loc.get('longitude', 'N/A')}°E")
        lines.append(f"**Timezone:** UTC+{loc.get('timezone', 5.5)}")
        lines.append("")

    # Basic panchang elements
    lines.append("## 🌙 Panchang Elements")
    lines.append("")
    if "weekday" in data:
        lines.append(f"- **Weekday:** {data['weekday']}")
    if "tithi" in data:
        lines.append(f"- **Tithi:** {data['tithi']}")
    if "nakshatra" in data:
        lines.append(f"- **Nakshatra:** {data['nakshatra']}")
    if "yoga" in data:
        lines.append(f"- **Yoga:** {data['yoga']}")
    if "karana" in data:
        lines.append(f"- **Karana:** {data['karana']}")
    if "tamil_month" in data:
        lines.append(f"- **Tamil Month:** {data['tamil_month']}")
    lines.append("")

    # Sun timings
    lines.append("## ☀️ Sun Timings")
    lines.append("")
    if "sunrise" in data:
        lines.append(f"- **Sunrise:** {data['sunrise']}")
    if "sunset" in data:
        lines.append(f"- **Sunset:** {data['sunset']}")
    lines.append("")

    # Inauspicious timings
    lines.append("## ⚠️ Inauspicious Timings")
    lines.append("")
    lines.append("*Avoid these periods for important activities, new ventures, or auspicious events:*")
    lines.append("")
    if "rahu_kalam" in data:
        lines.append(f"- **Rahu Kalam:** {data['rahu_kalam']}")
    if "yamagandam" in data:
        lines.append(f"- **Yamagandam:** {data['yamagandam']}")
    if "gulikai_kalam" in data:
        lines.append(f"- **Gulikai Kalam:** {data['gulikai_kalam']}")
    if "dhurmuhurtham" in data:
        lines.append(f"- **Dhurmuhurtham:** {data['dhurmuhurtham']}")
    lines.append("")

    # Additional elements if present
    if "special_yoga" in data and data["special_yoga"]:
        lines.append("## ✨ Special Yoga")
        lines.append("")
        lines.append(f"- {data['special_yoga']}")
        lines.append("")

    if "chandrashtamam" in data:
        lines.append("## 🌒 Chandrashtamam")
        lines.append("")
        lines.append(f"- {data['chandrashtamam']}")
        lines.append("")

    return "\n".join(lines)


def _handle_api_error(e: Exception) -> str:
    """
    Convert API errors into actionable error messages.

    Args:
        e: Exception from httpx or other sources

    Returns:
        User-friendly error message with suggested actions
    """
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 404:
            return "Error: Panchang API endpoint not found. Please ensure FastAPI server is running on port 8000."
        elif status == 422:
            return f"Error: Invalid input parameters. {e.response.text}"
        elif status == 500:
            return f"Error: Panchang calculation failed. This may be due to invalid astronomical parameters. Details: {e.response.text}"
        else:
            return f"Error: API request failed with status {status}. Details: {e.response.text}"
    elif isinstance(e, httpx.ConnectError):
        return "Error: Cannot connect to FastAPI server at http://localhost:8000. Please ensure the FastAPI server is running."
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. The panchang calculation took too long. Please try again."
    else:
        return f"Error: Unexpected error occurred: {type(e).__name__} - {str(e)}"


@mcp.tool(name="tamil_panchang_get_panchang")
async def get_panchang(params: PanchangInput) -> str:
    """
    Calculate complete Tamil Panchang for a specific date and location.

    Returns comprehensive panchang data including:
    - Tithi (lunar day, 1-15 in each lunar fortnight)
    - Nakshatra (lunar mansion, 27 divisions of the zodiac)
    - Yoga (sun-moon angle combination, 27 yogas)
    - Karana (half of tithi, 11 karanas)
    - Sunrise and sunset times (Tamil day starts at sunrise)
    - Inauspicious timings: Rahu Kalam, Yamagandam, Gulikai Kalam, Dhurmuhurtham
    - Tamil solar month (12 months: Chithirai to Panguni)
    - Special yogas and Chandrashtamam information

    All calculations use the Drik Panchanga method with Swiss Ephemeris for
    high astronomical accuracy. Tamil day boundary is sunrise (not midnight).

    Args:
        params (PanchangInput): Validated input containing:
            - date (str): Date in YYYY-MM-DD format
            - latitude (float): Location latitude (-90 to +90)
            - longitude (float): Location longitude (-180 to +180)
            - timezone (float): UTC offset (default 5.5 for IST)
            - response_format (str): 'markdown' or 'json'

    Returns:
        str: Formatted panchang data in requested format (markdown or JSON)

    Examples:
        Get panchang for Chennai on January 15, 2024:
        - date: "2024-01-15"
        - latitude: 13.0827
        - longitude: 80.2707
        - timezone: 5.5
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{FASTAPI_BASE}/api/panchang",
                json={
                    "date": params.date,
                    "latitude": params.latitude,
                    "longitude": params.longitude,
                    "timezone": params.timezone
                },
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()

            if params.response_format == ResponseFormat.JSON:
                return json.dumps(result, indent=2, ensure_ascii=False)
            else:
                return format_panchang_markdown(result)

        except Exception as e:
            return _handle_api_error(e)


@mcp.tool(name="tamil_panchang_get_today")
async def get_today_panchang(params: TodayPanchangInput) -> str:
    """
    Get today's Tamil Panchang for a specified location.

    Convenience tool that automatically uses the current date. Returns the same
    comprehensive panchang data as get_panchang but without requiring a date parameter.

    Useful for:
    - Checking today's auspicious/inauspicious timings
    - Planning daily activities based on panchang
    - Finding current tithi, nakshatra, and yoga
    - Determining sunrise/sunset for the current day

    Args:
        params (TodayPanchangInput): Validated input containing:
            - latitude (float): Location latitude (-90 to +90)
            - longitude (float): Location longitude (-180 to +180)
            - timezone (float): UTC offset (default 5.5 for IST)
            - response_format (str): 'markdown' or 'json'

    Returns:
        str: Formatted panchang data for today in requested format

    Examples:
        Get today's panchang for Mumbai:
        - latitude: 19.0760
        - longitude: 72.8777
        - timezone: 5.5
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{FASTAPI_BASE}/api/today",
                json={
                    "latitude": params.latitude,
                    "longitude": params.longitude,
                    "timezone": params.timezone
                },
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()

            if params.response_format == ResponseFormat.JSON:
                return json.dumps(result, indent=2, ensure_ascii=False)
            else:
                return format_panchang_markdown(result)

        except Exception as e:
            return _handle_api_error(e)


# Entry point - use as ASGI app with uvicorn
# Run with: uvicorn mcp_server:app --host 0.0.0.0 --port 8001
# This exposes the FastMCP SSE app for external serving

# Get the ASGI app from FastMCP for SSE transport
app = mcp.sse_app()
