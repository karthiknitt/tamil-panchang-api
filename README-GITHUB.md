# Tamil Panchang API

> Free, open-source Tamil Panchang API with comprehensive astronomical calculations

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)](https://fastapi.tiangolo.com/)
[![API Status](https://img.shields.io/badge/status-active-success.svg)](https://panchang.karthikwrites.com/health)

🌐 **Live API:** [panchang.karthikwrites.com](https://panchang.karthikwrites.com/docs)

## 🎯 Overview

A self-hosted Tamil Panchang API that provides **highly accurate astronomical calculations** using the Drik Panchanga method with Swiss Ephemeris. Perfect for Tamil community apps, websites, mobile applications, and automation workflows.

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
- 📱 **CORS Enabled** - Use from any website, app, or automation
- 🔓 **No Authentication** - Simple and accessible
- 📍 **Location-aware** - Precise calculations for any latitude/longitude
- 🌅 **Sunrise-based** - Tamil day boundaries (sunrise to sunrise)
- 🌙 **Sidereal Zodiac** - Using Lahiri Ayanamsa for accurate rasi calculations

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

### Self-Hosting with Docker

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/tamil-panchang-api.git
cd tamil-panchang-api
```

2. **Deploy with Docker Compose:**
```bash
docker-compose up -d --build
```

3. **Test:**
```bash
curl http://localhost:8000/health
```

## 📖 API Documentation

### Endpoints Overview

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/health` | Health check | None |
| GET | `/` | API information | None |
| POST | `/api/today` | Get today's panchang | None |
| POST | `/api/panchang` | Get panchang for specific date | None |
| GET | `/docs` | Interactive Swagger UI | None |
| GET | `/redoc` | Alternative ReDoc docs | None |

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

### Option 1: Using Dokploy

1. Create new project in Dokploy
2. Connect this GitHub repository
3. Select `docker-compose.yml`
4. Update domain in docker-compose file
5. Deploy!

### Option 2: Docker Compose (Traefik)

```bash
# Update domain in docker-compose.yml
nano docker-compose.yml

# Deploy with Traefik
docker-compose up -d --build
```

### Option 3: Standalone (No Traefik)

```bash
docker-compose -f docker-compose.standalone.yml up -d --build
```

## 📜 Fair Use Policy

This API is free for everyone:

**✅ Allowed:**
- Personal use
- Educational projects
- Community apps/websites
- Non-commercial mobile apps
- Reasonable automation

**⚠️ Please Avoid:**
- Excessive requests (> 100/min per IP)
- Commercial reselling
- Malicious traffic

**Rate Limits:**
- 100 requests/minute per IP
- 50 burst requests allowed

## 🔧 Configuration

### Environment Variables

- `TZ` - Timezone (default: Asia/Kolkata)

### Traefik Labels

The included `docker-compose.yml` has:
- Automatic HTTPS (Let's Encrypt)
- Rate limiting (100 req/min)
- Health checks

## 📱 Client Examples

### JavaScript
```javascript
const panchang = await fetch('https://panchang.karthikwrites.com/api/today', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ latitude: 13.0827, longitude: 80.2707, timezone: 5.5 })
}).then(r => r.json());
```

### Python
```python
import requests
panchang = requests.post(
    'https://panchang.karthikwrites.com/api/today',
    json={'latitude': 13.0827, 'longitude': 80.2707, 'timezone': 5.5}
).json()
```

### n8n Workflow

Import the included `n8n-workflow-example.json` for:
- Daily panchang notifications
- Google Sheets logging
- Email/Telegram integration

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

- **Language:** Python 3.11
- **Framework:** FastAPI (modern, async web framework)
- **Astronomical Engine:** PySwisseph (Swiss Ephemeris)
  - Compiled from source for maximum accuracy
  - Includes DE431 ephemeris data files
- **Container:** Docker with multi-stage build
- **Method:** Drik Panchanga (observational/precise)
- **Zodiac:** Sidereal (Lahiri Ayanamsa)
- **Calendar:** Amavasyanta (South Indian style)
- **API Docs:** Auto-generated Swagger UI & ReDoc

## 📚 Documentation Files

- `README.md` - Comprehensive API documentation
- `DEPLOYMENT.md` - Deployment guide
- `SECURITY-RECOMMENDATIONS.md` - Public vs private considerations
- `QUICK-REFERENCE.md` - Command cheat sheet

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

MIT License - Free to use and modify

## 🙏 Acknowledgments

- Swiss Ephemeris for astronomical calculations
- Tamil community for inspiration
- Drik Panchang for methodology reference

## 📞 Support

- 📖 [API Documentation](https://panchang.karthikwrites.com/docs)
- 🐛 [Report Issues](https://github.com/YOUR_USERNAME/tamil-panchang-api/issues)
- 💬 [Discussions](https://github.com/YOUR_USERNAME/tamil-panchang-api/discussions)

## ⭐ Show Your Support

If this project helps you, consider:
- ⭐ Star this repository
- 🐛 Report bugs or suggest features
- 📢 Share with the Tamil community
- 🤝 Contribute improvements

---

**Made with ❤️ for the Tamil community**

[Live API](https://panchang.karthikwrites.com) | [Documentation](https://panchang.karthikwrites.com/docs) | [Blog](https://karthikwrites.com)
