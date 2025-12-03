# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tamil Panchang API is a self-hosted FastAPI service that provides accurate astronomical calculations for Tamil calendar (Panchang) using the Drik Panchanga method with Swiss Ephemeris. The API returns Tamil-formatted panchang data including tithi, nakshatra, yoga, karana, sunrise/sunset, inauspicious timings, and solar month information.

**Tech Stack:**
- Python 3.11 with FastAPI
- PySwisseph (Swiss Ephemeris library)
- MCP (Model Context Protocol) server for AI agent access
- Docker containerized with supervisord managing both servers
- Designed for deployment with Traefik reverse proxy

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI only (requires Swiss Ephemeris data files in /app/ephe/)
python app.py

# Run FastAPI with uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Run MCP server only (requires FastAPI to be running on port 8000)
python mcp_server.py

# Run both servers (for testing the full setup)
# Terminal 1:
python app.py

# Terminal 2:
python mcp_server.py
```

### Testing
```bash
# Run test script (requires API to be running)
python test_api.py
```

### Docker Development
```bash
# Build and run with Docker Compose (standalone)
docker-compose -f docker-compose.standalone.yml up -d --build

# View logs
docker-compose -f docker-compose.standalone.yml logs -f

# Stop and remove containers
docker-compose -f docker-compose.standalone.yml down

# Rebuild without cache
docker-compose -f docker-compose.standalone.yml build --no-cache
```

### Production Deployment
```bash
# Deploy with Traefik (requires dokploy-network)
docker-compose -f docker-compose.standalone.yml up -d --build

# Check health
curl http://localhost:8000/health
```

## Architecture

### Dual Server Architecture

The application now runs two servers in parallel:

1. **FastAPI REST Server** ([app.py](app.py)) - Port 8000
   - Traditional REST API endpoints for n8n workflow and direct HTTP clients
   - Complete panchang calculation logic
   - Swagger/ReDoc documentation

2. **MCP Server** ([mcp_server.py](mcp_server.py)) - Port 8001
   - AI agent access via Model Context Protocol (Anthropic's standard)
   - SSE (Server-Sent Events) transport
   - Wraps FastAPI endpoints - no calculation logic duplication
   - Exposes 2 tools: `get_panchang`, `get_today_panchang`

**Process Management:**

- Both servers run in single Docker container managed by supervisord
- [supervisord.conf](supervisord.conf) ensures both processes auto-restart
- Logs from both servers stream to stdout/stderr

**Routing (Production with Traefik):**

- `http://localhost:8000/api/*` → FastAPI (port 8000)
- `http://localhost:8000/mcp/*` → MCP server (port 8001, `/mcp` prefix stripped)

### Single-File Application Structure (FastAPI)

The entire API logic is contained in [app.py](app.py) (~354 lines). The monolithic design is intentional for simplicity:

**Core Calculation Flow:**
1. Receive location (lat/lon) and date via POST request
2. Convert datetime to Julian Day Number (JD)
3. Calculate sunrise JD (Tamil day starts at sunrise, not midnight)
4. Compute Sun and Moon positions using PySwisseph at sunrise time
5. Calculate panchang elements from celestial positions:
   - **Tithi**: Based on moon-sun longitude difference (12° per tithi)
   - **Nakshatra**: Based on moon longitude (13.33° per nakshatra)
   - **Yoga**: Based on sum of sun and moon longitudes
   - **Karana**: Half of tithi (6° intervals)
6. Calculate inauspicious timings by dividing daylight into 8 parts
7. Return Tamil-formatted response

### Key Functions
- `julian_day()`: Converts Gregorian date to Julian Day Number
- `get_sun_moon_positions()`: Gets celestial positions via PySwisseph
- `get_sunrise_sunset()`: Calculates rise/set times for location
- `get_tithi()`, `get_nakshatra()`, `get_yoga()`, `get_karana()`: Panchang calculations
- `get_rahu_kalam()`, `get_yamagandam()`, `get_gulikai_kalam()`, `get_dhurmuhurtham()`: Inauspicious timing calculations
- `get_special_yoga()`: Calculates Amrita/Siddha/Marana yogas based on weekday-nakshatra combinations
- `get_chandrashtamam()`: Calculates 8th house/nakshatra from Moon position
- `get_nokku_naal()`: Determines nakshatra direction classification (Mel/Keezh/Sama Nokku)
- `get_gowri_panchangam()`, `get_nalla_neram()`, `get_hora()`: Auspicious timing calculations
- `jd_to_datetime()`: Converts Julian Day back to time string with timezone adjustment

### Data Constants
Multiple Tamil name arrays at top of [app.py](app.py):
- `TAMIL_MONTHS`: 12 solar months (Chithirai to Panguni)
- `NAKSHATRAS_TAMIL`: 27 nakshatras
- `TITHIS_TAMIL`: 15 tithi names
- `YOGAS`: 27 yogas
- `KARANAS`: 11 karanas
- `WEEKDAYS_TAMIL`: 7 weekday names

### API Endpoints

**FastAPI REST Endpoints (Port 8000):**

- `POST /api/panchang`: Get panchang for specific date
- `POST /api/today`: Get today's panchang (convenience endpoint)
- `GET /health`: Health check
- `GET /`: Root info
- `GET /docs`: Auto-generated Swagger UI
- `GET /redoc`: Auto-generated ReDoc

**MCP Tools (Port 8001, accessed via `/mcp/sse`):**

- `get_panchang`: Calculate complete panchang for specific date and location
  - Parameters: date (YYYY-MM-DD), latitude, longitude, timezone (default 5.5)
  - Returns: Full panchang JSON with formatted text explanation

- `get_today_panchang`: Get today's panchang for a location
  - Parameters: latitude, longitude, timezone (default 5.5)
  - Returns: Full panchang JSON for current date

### Docker Setup

**[Dockerfile](Dockerfile)** performs critical build steps:

1. Installs build tools and dependencies
2. Installs Python dependencies (including MCP, httpx, supervisor)
3. Downloads Swiss Ephemeris data files (.se1 files) to `/app/ephe/`
4. Copies [app.py](app.py), [mcp_server.py](mcp_server.py), and [supervisord.conf](supervisord.conf)
5. Exposes ports 8000 (FastAPI) and 8001 (MCP)
6. Runs supervisord to manage both servers

**Important:** PySwisseph is built from source and linked against the compiled Swiss Ephemeris library for accurate calculations.

### Deployment Configurations

- **[docker-compose.yml](docker-compose.yml)**: Production deployment with Traefik
  - Exposes both ports 8000 and 8001
  - Path-based routing on same domain:
    - FastAPI: `/api/*`, `/health`, `/docs`, etc. → port 8000
    - MCP: `/mcp/*` → port 8001 (prefix stripped)
  - Includes Let's Encrypt TLS for both routes
  - Rate limiting: 100 req/min per IP, 50 burst (applied to both)
  - Connects to external `dokploy-network`

- **[docker-compose.standalone.yml](docker-compose.standalone.yml)**: Local/testing without Traefik
  - Direct port mapping 8000:8000 and 8001:8001
  - No rate limiting or TLS
  - Access FastAPI at `http://localhost:8000`
  - Access MCP at `http://localhost:8001/sse`

## Calculation Notes

### Tamil Day Boundary
Tamil panchang calculations use **sunrise as the day boundary**, not midnight. This is critical:
- Always calculate sunrise JD first
- Use sunrise JD for all panchang element calculations
- This differs from Western astronomical day (midnight to midnight)

### Timezone Handling
The `timezone` parameter is an offset from UTC (e.g., 5.5 for IST). All time conversions use `jd_to_datetime()` which:
- Converts Julian Day to UTC time
- Applies timezone offset
- Handles day overflow/underflow

### Inauspicious Timing Calculation

**8-Part Division (Rahu Kalam, Yamagandam, Gulikai Kalam):**

1. Divide daylight (sunrise to sunset) into 8 equal parts
2. Select the appropriate part based on weekday
3. Each has a different position sequence for the 7 weekdays

**30-Part Division (Dhurmuhurtham):**

1. Divide daylight into 30 muhurtas (each muhurta ≈ 48 minutes)
2. Position varies by weekday:
   - Sunday: 14th muhurta
   - Monday: 12th muhurta
   - Tuesday: 11th muhurta
   - Wednesday: 10th muhurta
   - Thursday: 9th muhurta
   - Friday: 6th muhurta
   - Saturday: 8th muhurta
3. Dhurmuhurtham is unsuitable for starting new ventures, important work, or auspicious activities

## Common Modifications

### Adding New Panchang Elements
1. Add calculation function following pattern of `get_tithi()`, `get_nakshatra()`, etc.
2. Call from `get_panchang()` endpoint
3. Add to return dictionary
4. Update FastAPI response model if needed

### Supporting New Languages
1. Create new constant arrays (e.g., `NAKSHATRAS_HINDI`)
2. Add language parameter to request models
3. Add conditional logic to select appropriate name arrays

### Adjusting Rate Limits
Edit [docker-compose.yml](docker-compose.yml):
- `traefik.http.middlewares.panchang-ratelimit.ratelimit.average`: requests per period
- `traefik.http.middlewares.panchang-ratelimit.ratelimit.period`: time period
- `traefik.http.middlewares.panchang-ratelimit.ratelimit.burst`: burst allowance

## Testing Locally

### Testing FastAPI

The [test_api.py](test_api.py) script provides basic endpoint validation:

- Health check
- Specific date panchang (Trichy coordinates)
- Today's panchang (Chennai coordinates)

To test manually:

```bash
# Test FastAPI health
curl http://localhost:8000/health

# Test today's panchang
curl -X POST "http://localhost:8000/api/today" \
  -H "Content-Type: application/json" \
  -d '{"latitude":13.0827,"longitude":80.2707,"timezone":5.5}'
```

### Testing MCP Server

**Connect from Claude Desktop (recommended):**

Add to your Claude Desktop MCP configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "tamil-panchang": {
      "url": "http://localhost:8001/sse"
    }
  }
}
```

Then restart Claude Desktop and ask: "What's today's panchang in Chennai?"

**Connect from AI agents programmatically:**

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("http://localhost:8001/sse") as (read, write):
    async with ClientSession(read, write) as session:
        # List available tools
        tools = await session.list_tools()
        print(tools)

        # Call get_today_panchang
        result = await session.call_tool(
            "get_today_panchang",
            {"latitude": 13.0827, "longitude": 80.2707, "timezone": 5.5}
        )
        print(result)
```

**Production URL (after deployment):**

- Replace `http://localhost:8001/sse` with `http://localhost:8000/mcp/sse`

## Using the MCP Server with AI Agents

The MCP server enables AI agents (like Claude) to:

1. **Answer natural language queries**: "What's the nakshatra today in Mumbai?"
2. **Explain panchang concepts**: "Is now a good time to start work?" (checks inauspicious timings)
3. **Multi-step reasoning**: "What are the auspicious timings for tomorrow in Chennai?"
4. **Combine with other tools**: Calendar integration, location services, timezone conversion

**Example AI Agent Interactions:**

- "What's today's panchang in Chennai?" → Calls `get_today_panchang` with Chennai coordinates
- "Is 2pm a good time for an important meeting in Bangalore today?" → Checks Rahu Kalam/Yamagandam
- "What's the tithi on January 15, 2025 in Trichy?" → Calls `get_panchang` with specific date
