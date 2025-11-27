# Tamil Panchang API

> Free, open-source Tamil Panchang API for the community

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![API Status](https://img.shields.io/badge/status-active-success.svg)](https://panchang.karthikwrites.com/health)

🌐 **Live API:** [panchang.karthikwrites.com](https://panchang.karthikwrites.com/docs)

## 🎯 Overview

A self-hosted Tamil Panchang API that provides accurate astronomical calculations using the Drik Panchanga method (Swiss Ephemeris). Perfect for Tamil community apps, websites, and automation workflows.

### ✨ Features

- 🆓 **Free & Open Source** - No API keys, no subscriptions
- 🎯 **Accurate** - Swiss Ephemeris calculations
- 🇮🇳 **Tamil Format** - Authentic South Indian panchang with Tamil names
- ⚡ **Fast** - Instant API responses
- 🐳 **Docker-based** - Easy self-hosting
- 📱 **CORS Enabled** - Use from any website or app
- 🔓 **No Authentication** - Simple and accessible

### 📊 What You Get

- Tamil month (solar calendar)
- Sunrise & sunset timings
- Tithi (lunar day) with Paksha
- Nakshatra (in Tamil)
- Yoga & Karana
- Sun & Moon Rashi (zodiac signs)
- Inauspicious timings: Rahu Kalam, Yamagandam, Gulikai Kalam
- Works for any location (latitude/longitude)

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

### Endpoints

- `GET /health` - Health check
- `POST /api/today` - Get today's panchang
- `POST /api/panchang` - Get panchang for specific date
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### Example Request

**Get Today's Panchang:**
```bash
POST https://panchang.karthikwrites.com/api/today
Content-Type: application/json

{
  "latitude": 13.0827,
  "longitude": 80.2707,
  "timezone": 5.5
}
```

**Response:**
```json
{
  "date": "2024-11-27",
  "tamil_month": "Karthigai",
  "weekday": {"tamil": "Budhan", "english": "Wednesday"},
  "sunrise": "06:13:45",
  "sunset": "17:48:23",
  "tithi": {"name": "Dwadasi", "paksha": "Krishna Paksha"},
  "nakshatra": {"name": "Avittam"},
  "yoga": {"name": "Vajra"},
  "karana": {"name": "Vanija"},
  "sun_sign": {"rasi": "Vrischika"},
  "moon_sign": {"rasi": "Makara"},
  "inauspicious_timings": {
    "rahu_kalam": {"start": "12:01:04", "end": "13:27:34"},
    "yamagandam": {"start": "10:34:34", "end": "12:01:04"},
    "gulikai_kalam": {"start": "09:08:04", "end": "10:34:34"}
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

## 🏗️ Technical Stack

- **Framework:** FastAPI (Python 3.11)
- **Calculations:** PySwisseph (Swiss Ephemeris)
- **Container:** Docker
- **Method:** Drik Panchanga (observational/precise)
- **Calendar:** Amavasyanta (South Indian style)

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
