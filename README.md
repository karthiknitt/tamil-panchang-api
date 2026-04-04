# Tamil Panchang API

> Free, open-source Tamil Panchang API with comprehensive astronomical calculations and AI agent integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Enabled-purple)](https://modelcontextprotocol.io)
[![API Status](https://img.shields.io/badge/status-active-success.svg)](http://localhost:8000/health)

🌐 **Live API:** [panchang.karthikwrites.com](https://panchang.karthikwrites.com/docs)

## 🎯 Overview

A self-hosted Tamil Panchang API that provides **highly accurate astronomical calculations** using the Drik Panchanga method with Swiss Ephemeris. Perfect for Tamil community apps, websites, mobile applications, automation workflows, and **AI agent integration via MCP (Model Context Protocol)**.

### What is Panchang?

Panchang (meaning "five limbs") is the Hindu astronomical calendar system combining five key elements:
1. **Tithi** (Lunar day) - 30 phases of the Moon
2. **Nakshatra** (Lunar mansion) - 27 divisions of the zodiac
3. **Yoga** (Auspicious combination) - 27 types
4. **Karana** (Half-tithi) - 11 types
5. **Var** (Weekday) - 7 days

This API calculates all these elements **plus extensive additional information** crucial for Tamil calendar users.

### ✨ Key Features

- 🆓 **Free & Open Source** - No API keys, no subscriptions, MIT licensed
- 🎯 **Highly Accurate** - Swiss Ephemeris calculations with Drik Panchanga method
- 🇮🇳 **Tamil Format** - Authentic South Indian panchang with Tamil names
- ⚡ **Fast** - 100-300ms average response time
- 🐳 **Docker-based** - Easy self-hosting with one command
- 🤖 **AI Agent Ready** - Built-in MCP server for Claude and other AI assistants
- 📱 **CORS Enabled** - Use from any website, app, or automation
- 🔓 **No Authentication** - Simple and accessible
- 📍 **Location-aware** - Precise calculations for any latitude/longitude
- 🌅 **Sunrise-based** - Tamil day boundaries (sunrise to sunrise)
- 🌙 **Sidereal Zodiac** - Using Lahiri Ayanamsa for accurate rasi calculations
- 🔄 **Dual Server Architecture** - REST API + MCP server in one container

### 📊 Complete Data Provided

#### Core Panchang Elements

- ✅ **Tithi** - Lunar day with paksha (waxing/waning) and percentage remaining
- ✅ **Nakshatra** - Lunar mansion (27 divisions) with Tamil names
- ✅ **Yoga** - Auspicious/inauspicious combinations (27 types)
- ✅ **Karana** - Half-tithi calculations (11 types)
- ✅ **Tamil Month** - Solar month (Chithirai to Panguni)
- ✅ **Weekday** - In both English and Tamil

#### Astronomical Data

- 🌅 **Sunrise & Sunset** - Precise timings for location
- 🌙 **Moon Sign (Rasi)** - Sidereal zodiac position
- ☀️ **Sun Sign (Rasi)** - Sidereal zodiac position
- 🔄 **Transition Times** - All tithi, nakshatra, yoga changes during the Tamil day

#### Inauspicious Timings (Avoid These)

- ⏰ **Rahu Kalam** - Period ruled by Rahu (~90 minutes daily)
- ⏰ **Yamagandam** - Period ruled by Yama (~90 minutes daily)
- ⏰ **Gulikai Kalam** - Period ruled by Saturn's son (~90 minutes daily)
- ⏰ **Dhurmuhurtham** - Inauspicious muhurtam (~48 minutes daily)

#### Auspicious Timings (Good Times)

- 🌟 **Gowri Panchangam** - 8-part division of day and night
- 🌟 **Nalla Neram** - Auspicious times extracted from Gowri
- 🌟 **Hora** - Planetary hours (24 per day)

#### Special Features

- 🎯 **Special Yoga** - Amrita/Siddha/Marana yogas (weekday-nakshatra based)
- 👁️ **Nokku Naal** - Nakshatra direction (Mel/Keezh/Sama Nokku)
- 🌙 **Chandrashtamam** - 8th house from Moon (birth star specific)
- 📅 **Multi-day Transitions** - Tracks panchang changes across calendar days

## 🚀 Quick Start

### Using Public API (Easiest)

No setup needed! Just use the public endpoint:

```bash
curl -X POST "https://panchang.karthikwrites.com/api/today" \
  -H "Content-Type: application/json" \
  -d '{"latitude":13.0827,"longitude":80.2707,"timezone":5.5}'
```

### Using with AI Agents (Claude, etc.)

Connect the MCP server to Claude Desktop or any MCP-compatible AI assistant:

**Production API (Recommended):**

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tamil-panchang": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://panchang.karthikwrites.com/mcp/sse"]
    }
  }
}
```

**Local Docker (For Testing):**

If you're running the API locally with Docker, use:

```json
{
  "mcpServers": {
    "tamil-panchang": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:8001/sse"]
    }
  }
}
```

Then restart Claude Desktop and ask: *"What's today's panchang in Chennai?"*

### Self-Hosting with Docker

1. **Clone the repository:**

```bash
git clone https://github.com/karthiknitt/tamil-panchang-api.git
cd tamil-panchang-api
```

2. **Deploy with Docker Compose:**

```bash
docker-compose -f docker-compose.standalone.yml up -d --build
```

3. **Test the REST API:**

```bash
curl http://localhost:8000/health
```

4. **Test the MCP Server (SSE endpoint):**

```bash
curl http://localhost:8001/sse
```

## 📖 API Documentation

### Dual Server Architecture

This application runs **two servers in parallel** within a single Docker container:

1. **FastAPI REST Server (Port 8000)** - Traditional HTTP REST API
   - Direct HTTP access for web apps, mobile apps, n8n workflows
   - Auto-generated OpenAPI/Swagger documentation
   - Fast response times (100-300ms)

2. **MCP Server (Port 8001)** - AI Agent Integration
   - Model Context Protocol (SSE transport)
   - Enables natural language queries via Claude and other AI assistants
   - Wraps REST API endpoints for AI-friendly access

### REST API Endpoints (Port 8000)

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/health` | Health check | None |
| GET | `/` | API information | None |
| POST | `/api/today` | Get today's panchang | None |
| POST | `/api/panchang` | Get panchang for specific date | None |
| GET | `/docs` | Interactive Swagger UI | None |
| GET | `/redoc` | Alternative ReDoc docs | None |

### MCP Server Tools (Port 8001)

Access via SSE endpoint: `/sse` (or `/mcp/sse` in production with Traefik)

| Tool | Parameters | Description |
|------|------------|-------------|
| `get_panchang` | `date`, `latitude`, `longitude`, `timezone` | Get panchang for specific date and location |
| `get_today_panchang` | `latitude`, `longitude`, `timezone` | Get today's panchang for a location |

**MCP Client Example:**

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("http://localhost:8001/sse") as (read, write):
    async with ClientSession(read, write) as session:
        result = await session.call_tool(
            "get_today_panchang",
            {"latitude": 13.0827, "longitude": 80.2707, "timezone": 5.5}
        )
        print(result)
```

### Detailed Endpoint Documentation

#### 1. POST `/api/panchang` - Get Panchang for Specific Date

Get complete panchang information for any date and location.

**Request Body:**

```json
{
  "date": "2025-11-28",
  "latitude": 13.0827,
  "longitude": 80.2707,
  "timezone": 5.5
}
```

**Parameters:**

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `date` | string | Yes | Date in YYYY-MM-DD format | "2025-11-28" |
| `latitude` | float | Yes | Latitude (-90 to +90) | 13.0827 |
| `longitude` | float | Yes | Longitude (-180 to +180) | 80.2707 |
| `timezone` | float | No | UTC offset (default: 5.5) | 5.5 |

#### 2. POST `/api/today` - Get Today's Panchang

Convenience endpoint for today's date.

**Request Body:**

```json
{
  "latitude": 13.0827,
  "longitude": 80.2707,
  "timezone": 5.5
}
```

### Response Structure

The API returns a comprehensive JSON response with all panchang data:

**Example Response (Simplified):**

```json
{
  "date": "2025-11-28",
  "location": {
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": 5.5
  },
  "tamil_month": "Karthigai",
  "weekday": {
    "tamil": "Velli",
    "english": "Friday"
  },
  "sunrise": "06:13:45",
  "sunset": "17:48:23",
  "tithi": {
    "number": 12,
    "name": "Dwadasi",
    "paksha": "Shukla Paksha",
    "remaining": 45.67
  },
  "tithi_list": [
    {
      "number": 12,
      "name": "Dwadasi",
      "paksha": "Shukla Paksha",
      "start": "06:13:45",
      "end": "08:23:12"
    }
  ],
  "nakshatra": {
    "number": 15,
    "name": "Swathi",
    "remaining": 23.45
  },
  "nakshatra_list": [
    {
      "number": 15,
      "name": "Swathi",
      "start": "06:13:45",
      "end": "04:23:12 (2025-11-29)"
    }
  ],
  "yoga": {
    "number": 8,
    "name": "Dhriti",
    "remaining": 67.89
  },
  "karana": {
    "number": 23,
    "name": "Balava"
  },
  "sun_sign": {
    "longitude": 245.67,
    "sidereal_longitude": 221.45,
    "rasi": "Vrischika"
  },
  "moon_sign": {
    "longitude": 195.34,
    "sidereal_longitude": 171.12,
    "rasi": "Kanya"
  },
  "inauspicious_timings": {
    "rahu_kalam": {"start": "10:30:00", "end": "12:00:00"},
    "yamagandam": {"start": "15:15:00", "end": "16:45:00"},
    "gulikai_kalam": {"start": "07:45:00", "end": "09:15:00"},
    "dhurmuhurtham": {
      "start": "08:30:00",
      "end": "09:18:00",
      "muhurta_number": 6,
      "duration_minutes": 48
    }
  },
  "gowri_panchangam": {
    "day": [
      {"name": "Sugam", "type": "auspicious", "start": "06:13:45", "end": "07:39:00"}
    ],
    "night": [
      {"name": "Rogam", "type": "inauspicious", "start": "17:48:23", "end": "19:15:00"}
    ]
  },
  "nalla_neram": {
    "day": [
      {"name": "Amridha", "type": "auspicious", "start": "12:30:00", "end": "14:00:00"}
    ]
  },
  "hora": {
    "day": [
      {"hora_number": 1, "planet": "Venus", "start": "06:13:45", "end": "07:10:00"}
    ]
  },
  "nokku_naal": {
    "classification": "Sama Nokku Naal",
    "tamil": "சம நோக்கு நாள்",
    "direction": "Forward/Side Looking",
    "suitable_for": "Travel, starting journeys, buying vehicles"
  },
  "special_yoga": {
    "name": "Amrita",
    "tamil": "அமிர்தம்",
    "type": "Highly Auspicious",
    "description": "Nectar-like yoga, excellent for all auspicious activities"
  },
  "chandrashtamam": {
    "current_moon": {
      "rasi": {"name": "Kanya", "tamil": "கன்னி", "number": 6}
    },
    "chandrashtamam": {
      "rasi": {"name": "Mesha", "tamil": "மேஷம்", "number": 1}
    },
    "advice": "If your birth Moon (Janma Rasi) is Mesha..."
  }
}
```

### Common Locations

| City | Latitude | Longitude |
|------|----------|-----------|
| Chennai | 13.0827 | 80.2707 |
| Trichy | 10.7905 | 78.7047 |
| Madurai | 9.9252 | 78.1198 |
| Bangalore | 12.9716 | 77.5946 |
| Hyderabad | 17.3850 | 78.4867 |

## 🛠️ Deployment Options

### Pre-built Docker Images

This repository is available as a pre-built Docker image on Docker Hub:

**Docker Hub:**

```bash
docker pull karthiknitt/tamil-panchang-api:latest
```

**Quick Run:**

```bash
# Run with Docker Hub image
docker run -d -p 8000:8000 -p 8001:8001 karthiknitt/tamil-panchang-api:latest

# Test the API
curl http://localhost:8000/health
```

The image is automatically built and published to Docker Hub on every push to the main branch via GitHub Actions.

### Option 1: Standalone (Local Development/Testing)

**Best for:** Local development, testing, or simple deployments without reverse proxy

```bash
# Uses docker-compose.standalone.yml
docker-compose -f docker-compose.standalone.yml up -d --build

# Access endpoints:
# - REST API: http://localhost:8000
# - MCP Server: http://localhost:8001/sse
# - Swagger Docs: http://localhost:8000/docs
```

**Configuration:**
- Direct port mapping: `8000:8000` and `8001:8001`
- No TLS/HTTPS (use reverse proxy if needed)
- No rate limiting (add nginx/caddy if needed)

### Option 2: Production with Traefik

**Best for:** Production deployments with automatic HTTPS and rate limiting

```bash
# Requires external dokploy-network and Traefik running
docker-compose up -d --build

# Access endpoints:
# - REST API: https://your-domain.com/api/*
# - MCP Server: https://your-domain.com/mcp/*
# - Swagger Docs: https://your-domain.com/docs
```

**Configuration:**
- Update domain in [docker-compose.yml](docker-compose.yml):
  ```yaml
  - "traefik.http.routers.panchang.rule=Host(`your-domain.com`)"
  ```
- Automatic Let's Encrypt TLS certificates
- Path-based routing:
  - `/api/*`, `/docs`, `/redoc`, `/health` → FastAPI (port 8000)
  - `/mcp/*` → MCP server (port 8001, prefix stripped)
- Rate limiting: 100 req/min per IP (50 burst)
- Connects to `dokploy-network` for Traefik integration

### Option 3: Using Dokploy (Managed Platform)

**Best for:** Easiest production deployment with GUI management

1. Create new service in Dokploy
2. Connect this GitHub repository
3. Select `docker-compose.yml`
4. Update domain in compose file
5. Deploy!

Dokploy automatically handles:
- Network creation (`dokploy-network`)
- Traefik configuration
- SSL certificates
- Container orchestration

### Port Reference

| Server | Port | Endpoint | Purpose |
|--------|------|----------|---------|
| FastAPI | 8000 | `/api/*`, `/docs`, `/health` | REST API |
| MCP | 8001 | `/sse` (standalone) or `/mcp/sse` (Traefik) | AI Agent Integration |

### Environment Variables

Optional configuration via environment variables:

```yaml
environment:
  - TZ=Asia/Kolkata  # Timezone for logging (default: Asia/Kolkata)
```

**Note:** Swiss Ephemeris data files are automatically downloaded during Docker build.

### CI/CD Pipeline

This repository includes automated Docker image building and publishing via GitHub Actions.

#### Automated Deployment

The CI/CD pipeline automatically:

1. **Triggers** on pushes to the `main` branch
2. **Builds** the Docker image using the optimized Dockerfile
3. **Pushes** to Docker Hub
4. **Tests** the deployed image to ensure functionality

#### Required Secrets

To enable automated publishing, configure these repository secrets in GitHub:

| Secret Name | Description | Where to Get It |
|-------------|-------------|-----------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | Docker Hub account settings |
| `DOCKERHUB_TOKEN` | Docker Hub access token | Docker Hub → Account Settings → Security → Access Tokens |

**Setting up Docker Hub Token:**

1. Go to [Docker Hub](https://hub.docker.com/)
2. Login and go to Account Settings → Security
3. Generate a new Access Token
4. Copy the token and add it as `DOCKERHUB_TOKEN` in repository secrets

#### Image Name

The image is published as:

- **Docker Hub:** `karthiknitt/tamil-panchang-api`

#### Tags

The following tags are automatically applied:

- `latest` - Latest build from main branch
- `main` - Current main branch commit
- `main-<sha>` - Specific commit SHA (first 7 characters)

## 📜 Fair Use Policy

This API is free for everyone:

**✅ Allowed:**

- Personal use
- Educational projects
- Community apps/websites
- Non-commercial mobile apps
- AI agent integration
- Reasonable automation

**⚠️ Please Avoid:**

- Excessive requests (> 100/min per IP)
- Commercial reselling
- Malicious traffic

**Rate Limits (Production with Traefik):**

- 100 requests/minute per IP
- 50 burst requests allowed
- Applied to both FastAPI and MCP endpoints

## 📱 Client Examples

### REST API Usage

#### JavaScript/TypeScript

```javascript
const panchang = await fetch('https://panchang.karthikwrites.com/api/today', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ latitude: 13.0827, longitude: 80.2707, timezone: 5.5 })
}).then(r => r.json());

console.log(`Today's Nakshatra: ${panchang.nakshatra.name}`);
```

#### Python

```python
import requests

panchang = requests.post(
    'https://panchang.karthikwrites.com/api/today',
    json={'latitude': 13.0827, 'longitude': 80.2707, 'timezone': 5.5}
).json()

print(f"Today's Tithi: {panchang['tithi']['name']}")
```

#### cURL

```bash
curl -X POST "https://panchang.karthikwrites.com/api/panchang" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-25",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": 5.5
  }'
```

### AI Agent Usage (MCP)

#### Claude Desktop Configuration

**Production API (Recommended):**

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tamil-panchang": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://panchang.karthikwrites.com/mcp/sse"]
    }
  }
}
```

**Local Docker (For Testing):**

If running the API locally, use:

```json
{
  "mcpServers": {
    "tamil-panchang": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:8001/sse"]
    }
  }
}
```

**Example AI queries:**

- *"What's today's panchang in Chennai?"*
- *"Is 2pm a good time for a meeting in Bangalore today?"*
- *"What's the nakshatra on December 25, 2025 in Trichy?"*

#### Python MCP Client

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("https://panchang.karthikwrites.com/mcp/sse") as (read, write):
    async with ClientSession(read, write) as session:
        # Get today's panchang
        result = await session.call_tool(
            "get_today_panchang",
            {"latitude": 13.0827, "longitude": 80.2707, "timezone": 5.5}
        )
        print(result)
```

### n8n Workflow Integration

Create automated workflows with n8n:

**Example workflow:**

1. **Schedule Trigger** - Daily at 6 AM
2. **HTTP Request** - POST to `/api/today`
3. **Process Data** - Extract important timings
4. **Send Notification** - Telegram/Email/SMS

**Sample n8n HTTP Request Node:**

```json
{
  "method": "POST",
  "url": "https://panchang.karthikwrites.com/api/today",
  "body": {
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": 5.5
  },
  "headers": {
    "Content-Type": "application/json"
  }
}
```

## 📐 Understanding the Calculations

### Tamil Day Boundary (CRITICAL)

**Tamil panchang uses sunrise as the day boundary, not midnight:**

- **Tamil Day:** Sunrise to next sunrise (≈24 hours)
- **Western Day:** Midnight to midnight

This is why the API provides `tithi_list`, `nakshatra_list`, and `yoga_list` - to show all transitions during the Tamil day, which may span two calendar dates.

**Example:**

```json
{
  "date": "2025-11-28",
  "nakshatra_list": [
    {
      "name": "Swathi",
      "start": "06:15:23",              // Sunrise on 2025-11-28
      "end": "04:23:12 (2025-11-29)"    // Before sunrise on next day
    }
  ]
}
```

### Sidereal vs Tropical Zodiac

Tamil calendar uses **sidereal (Nirayana)** zodiac, not tropical:

| Type | Based On | Used In | Difference |
|------|----------|---------|------------|
| **Tropical** | Seasons | Western astrology | Moves with precession |
| **Sidereal** | Fixed stars | Vedic/Tamil astrology | Fixed to constellation positions |

The API uses **Lahiri Ayanamsa** to convert tropical to sidereal longitudes. Current ayanamsa ≈ 24° (as of 2025).

### Calculation Methods

#### Tithi Calculation

- **Formula:** `(Moon longitude - Sun longitude) mod 360 / 12`
- **Each tithi:** 12° of lunar elongation
- **30 tithis:** 15 in Shukla Paksha (waxing), 15 in Krishna Paksha (waning)

#### Nakshatra Calculation

- **Formula:** `Moon longitude × 27 / 360`
- **Each nakshatra:** 13.33° (360° / 27)
- **27 nakshatras:** Moon spends ≈1 day in each

#### Yoga Calculation

- **Formula:** `(Sun longitude + Moon longitude) mod 360 × 27 / 360`
- **Each yoga:** 13.33° (same as nakshatra span)
- **27 yogas:** Based on combined Sun-Moon position

#### Karana Calculation

- **Formula:** `(Moon longitude - Sun longitude) mod 360 / 6`
- **Each karana:** 6° (half of tithi)
- **11 karanas:** 7 movable (repeating) + 4 fixed

### Inauspicious Timings

#### Rahu Kalam, Yamagandam, Gulikai (8-Part Division)

1. Calculate daylight: `sunset - sunrise`
2. Divide by 8: each part ≈ 90 minutes
3. Select position based on weekday

**Positions by weekday:**

| Day | Rahu Kalam | Yamagandam | Gulikai |
|-----|------------|------------|---------|
| Sun | 8th (16:30-18:00) | 5th (12:00-13:30) | 7th (15:00-16:30) |
| Mon | 2nd (07:45-09:15) | 4th (10:30-12:00) | 6th (13:30-15:00) |
| Tue | 7th (15:00-16:30) | 3rd (09:15-10:45) | 5th (12:00-13:30) |
| Wed | 5th (12:00-13:30) | 2nd (07:45-09:15) | 4th (10:30-12:00) |
| Thu | 6th (13:30-15:00) | 1st (06:15-07:45) | 3rd (09:15-10:45) |
| Fri | 4th (10:30-12:00) | 7th (15:00-16:30) | 2nd (07:45-09:15) |
| Sat | 3rd (09:15-10:45) | 6th (13:30-15:00) | 1st (06:15-07:45) |

*Times shown are approximate for a typical sunrise at 06:15 and sunset at 18:00*

#### Dhurmuhurtham (30-Part Division)

1. Divide daylight into 30 muhurtas
2. Each muhurta ≈ 48 minutes
3. Select muhurta based on weekday

**Muhurta positions:** Sunday=14th, Monday=12th, Tuesday=11th, Wednesday=10th, Thursday=9th, Friday=6th, Saturday=8th

### Special Yogas

**Amrita, Siddha, Marana** are based on **fixed weekday-nakshatra combinations:**

- **Amrita (அமிர்தம்):** Highly auspicious - "Nectar-like"
  - Best for: Marriages, housewarming, starting ventures

- **Siddha (சித்தம்):** Auspicious - "Success"
  - Good for: Business deals, important work, spiritual practices

- **Marana (மரணம்):** Inauspicious - "Death-like"
  - Avoid: New ventures, marriages, major decisions

Example: Sunday + Karthigai = Amrita, Sunday + Aswini = Marana

### Nokku Naal (Direction Classification)

Based on nakshatra, determines suitable activities:

- **Mel Nokku (மேல் நோக்கு):** Upward - Construction, planting trees
- **Keezh Nokku (கீழ் நோக்கு):** Downward - Digging, foundations
- **Sama Nokku (சம நோக்கு):** Forward - Travel, vehicles

### Gowri Panchangam & Hora

**Gowri:** Divides day and night into 8 parts each
- 5 Auspicious: Amridha, Uthi, Labam, Sugam, Dhanam
- 3 Inauspicious: Visham, Rogam, Soram
- Sequence changes daily based on weekday

**Hora:** Divides day and night into 12 parts each (planetary hours)
- Follows Chaldean order: Sun, Venus, Mercury, Moon, Saturn, Jupiter, Mars
- Each day starts with its ruling planet

## 🏗️ Technical Stack

### Core Technologies

- **Language:** Python 3.11
- **REST API Framework:** FastAPI (modern, async web framework)
- **AI Integration:** MCP (Model Context Protocol) with SSE transport
- **Process Manager:** Supervisord (manages both servers)
- **Container:** Docker with optimized multi-stage build
- **Astronomical Engine:** PySwisseph (Swiss Ephemeris)
  - Compiled from source for maximum accuracy
  - Includes DE431 ephemeris data files (.se1 files)

### Calculation Methods

- **Method:** Drik Panchanga (observational/precise)
- **Zodiac:** Sidereal (Nirayana) using Lahiri Ayanamsa
- **Calendar:** Amavasyanta (South Indian style)
- **Day Boundary:** Sunrise-based (Tamil tradition)

### API Features

- **REST API:** Auto-generated OpenAPI/Swagger UI & ReDoc
- **MCP Server:** SSE-based tool server for AI agents
- **CORS:** Enabled for cross-origin requests
- **Health Checks:** Built-in endpoints for monitoring
- **Rate Limiting:** Configurable via Traefik (production)

### System Architecture

```text
┌─────────────────────────────────────────┐
│   Docker Container (tamil-panchang)    │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │      Supervisord (PID 1)         │ │
│  └───────────────────────────────────┘ │
│           │                │            │
│           ▼                ▼            │
│  ┌─────────────┐  ┌────────────────┐  │
│  │   FastAPI   │  │   MCP Server   │  │
│  │  (Port 8000)│  │  (Port 8001)   │  │
│  │             │  │                │  │
│  │  REST API   │  │  AI Tools via  │  │
│  │  Swagger UI │  │  SSE Transport │  │
│  └─────────────┘  └────────────────┘  │
│           │                │            │
│           └────────┬───────┘            │
│                    ▼                    │
│         ┌────────────────────┐         │
│         │  PySwisseph Engine │         │
│         │  Swiss Ephemeris   │         │
│         │  (DE431 Data)      │         │
│         └────────────────────┘         │
└─────────────────────────────────────────┘
              │              │
              ▼              ▼
        HTTP Clients    AI Agents
        (Web/Mobile)    (Claude, etc.)
```

## 📚 Project Files

- **[README.md](README.md)** - Comprehensive API documentation (this file)
- **[CLAUDE.md](.claude/CLAUDE.md)** - Developer guide for Claude Code
- **[app.py](app.py)** - Main FastAPI application (354 lines)
- **[mcp_server.py](mcp_server.py)** - MCP server for AI integration
- **[supervisord.conf](supervisord.conf)** - Process manager configuration
- **[Dockerfile](Dockerfile)** - Container build instructions
- **[docker-compose.yml](docker-compose.yml)** - Production deployment with Traefik
- **[docker-compose.standalone.yml](docker-compose.standalone.yml)** - Local/testing deployment
- **[test_api.py](test_api.py)** - API testing script


## 🤝 Contributing

Contributions are welcome! Ways to contribute:

- 🐛 Report bugs or issues
- 💡 Suggest new features or improvements
- 📝 Improve documentation
- 🔧 Submit pull requests
- 🌍 Add support for other languages/formats
- 🧪 Add more test cases

**Development Setup:**

```bash
# Clone and install dependencies (requires uv: https://docs.astral.sh/uv/)
git clone https://github.com/karthiknitt/tamil-panchang-api.git
cd tamil-panchang-api
uv sync

# Run lint + format checks
uv run ruff check .
uv run ruff format --check .

# Start API server and run tests
uv run uvicorn app:app --host 0.0.0.0 --port 8000 &
sleep 5
uv run python test_api.py
```

Or test the full stack with Docker Compose:

```bash
docker-compose -f docker-compose.standalone.yml up -d --build
```

## 📄 License

MIT License - Free to use, modify, and distribute

**Copyright (c) 2025 Karthik**

See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Swiss Ephemeris** - Accurate astronomical calculations
- **Tamil Community** - Inspiration and cultural knowledge
- **Drik Panchang** - Methodology reference
- **Anthropic** - MCP (Model Context Protocol) specification
- **FastAPI Team** - Excellent web framework

## 📞 Support & Contact

- 📖 [Live API Documentation](https://panchang.karthikwrites.com/docs)
- 🐛 [Report Issues](https://github.com/karthiknitt/tamil-panchang-api/issues)
- 💬 [GitHub Discussions](https://github.com/karthiknitt/tamil-panchang-api/discussions)
- 📧 [Contact](https://karthikwrites.com)

## ⭐ Show Your Support

If this project helps you:

- ⭐ Star this repository on GitHub
- 🐛 Report bugs or suggest features
- 📢 Share with the Tamil community
- 🤝 Contribute improvements
- ☕ [Buy me a coffee](https://karthikwrites.com)

---

**Made with ❤️ for the Tamil community**

[Live API](https://panchang.karthikwrites.com) | [Documentation](https://panchang.karthikwrites.com/docs) | [Blog](https://karthikwrites.com)
