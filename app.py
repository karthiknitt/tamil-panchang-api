from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
import swisseph as swe
import math

app = FastAPI(
    title="Tamil Panchang API",
    description="Self-hosted Tamil Panchang API using Drik Panchanga calculations",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the ephemeris path
swe.set_ephe_path('/app/ephe')

class PanchangRequest(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    latitude: float = Field(..., description="Latitude of location")
    longitude: float = Field(..., description="Longitude of location")
    timezone: float = Field(5.5, description="Timezone offset (default: IST 5.5)")

class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    timezone: float = 5.5

# Tamil month names
TAMIL_MONTHS = [
    "Chithirai", "Vaikasi", "Aani", "Aadi", "Aavani", "Purattasi",
    "Aippasi", "Karthigai", "Margazhi", "Thai", "Maasi", "Panguni"
]

# Nakshatra names (Tamil)
NAKSHATRAS_TAMIL = [
    "Aswini", "Bharani", "Karthigai", "Rohini", "Mirugasiridam",
    "Thiruvathirai", "Punarpoosam", "Poosam", "Ayilyam", "Makam",
    "Puram", "Uthiram", "Hastham", "Chithirai", "Swathi",
    "Visakam", "Anusham", "Kettai", "Moolam", "Pooradam",
    "Uthiradam", "Thiruvonam", "Avittam", "Sadayam", "Poorattathi",
    "Uthirattathi", "Revathi"
]

# Tithi names (Tamil)
TITHIS_TAMIL = [
    "Prathama", "Dwithiya", "Thrithiya", "Chathurthi", "Panchami",
    "Shashthi", "Sapthami", "Ashtami", "Navami", "Dasami",
    "Ekadasi", "Dwadasi", "Trayodasi", "Chaturdasi", "Pournami/Amavasya"
]

# Yoga names
YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarman", "Dhriti", "Shoola", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

# Karana names
KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garaja",
    "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kimstughna"
]

# Weekday names (Tamil)
WEEKDAYS_TAMIL = [
    "Gnayiru", "Thingal", "Sevvai", "Budhan", "Viyazhan", "Velli", "Sani"
]

def julian_day(year, month, day, hour=0, minute=0, second=0):
    """Calculate Julian Day Number"""
    decimal_time = hour + minute/60.0 + second/3600.0
    return swe.julday(year, month, day, decimal_time)

def get_sun_moon_positions(jd):
    """Get Sun and Moon positions"""
    sun = swe.calc_ut(jd, swe.SUN)[0][0]
    moon = swe.calc_ut(jd, swe.MOON)[0][0]
    return sun, moon

def get_tithi(sun_long, moon_long):
    """Calculate Tithi"""
    diff = (moon_long - sun_long) % 360
    tithi_num = int(diff / 12)
    tithi_remaining = (diff % 12) / 12
    
    paksha = "Shukla Paksha" if tithi_num < 15 else "Krishna Paksha"
    tithi_name = TITHIS_TAMIL[tithi_num % 15]
    
    return {
        "number": tithi_num + 1,
        "name": tithi_name,
        "paksha": paksha,
        "remaining": round((1 - tithi_remaining) * 100, 2)
    }

def get_nakshatra(moon_long):
    """Calculate Nakshatra"""
    nak_num = int(moon_long * 27 / 360)
    nak_remaining = (moon_long * 27 / 360) % 1
    
    return {
        "number": nak_num + 1,
        "name": NAKSHATRAS_TAMIL[nak_num],
        "remaining": round((1 - nak_remaining) * 100, 2)
    }

def get_yoga(sun_long, moon_long):
    """Calculate Yoga"""
    yoga_val = (sun_long + moon_long) % 360
    yoga_num = int(yoga_val * 27 / 360)
    yoga_remaining = (yoga_val * 27 / 360) % 1
    
    return {
        "number": yoga_num + 1,
        "name": YOGAS[yoga_num],
        "remaining": round((1 - yoga_remaining) * 100, 2)
    }

def get_karana(sun_long, moon_long):
    """Calculate Karana"""
    diff = (moon_long - sun_long) % 360
    karana_num = int(diff / 6)
    
    # Fixed Karanas (last 4)
    if karana_num >= 57:
        karana_idx = 7 + (karana_num - 57)
    else:
        karana_idx = karana_num % 7
    
    return {
        "number": karana_num + 1,
        "name": KARANAS[min(karana_idx, 10)]
    }

def get_sunrise_sunset(jd, lat, lon):
    """Calculate sunrise and sunset times"""
    geopos = (lon, lat, 0)  # longitude, latitude, altitude

    # Sunrise (rsmi=1 for rise) - search from previous day
    sunrise_jd = swe.rise_trans(
        jd - 1, swe.SUN, 1, geopos, 0, 0
    )[1][0]

    # Sunset (rsmi=2 for set) - search from sunrise to get NEXT sunset
    sunset_jd = swe.rise_trans(
        sunrise_jd, swe.SUN, 2, geopos, 0, 0
    )[1][0]

    return sunrise_jd, sunset_jd

def jd_to_datetime(jd, timezone):
    """Convert Julian Day to datetime"""
    result = swe.revjul(jd)
    year, month, day, hour = result[0], result[1], result[2], result[3]
    
    # Adjust for timezone
    hour_adjusted = hour + timezone
    
    # Handle day overflow
    if hour_adjusted >= 24:
        hour_adjusted -= 24
        day += 1
    elif hour_adjusted < 0:
        hour_adjusted += 24
        day -= 1
    
    hours = int(hour_adjusted)
    minutes = int((hour_adjusted - hours) * 60)
    seconds = int(((hour_adjusted - hours) * 60 - minutes) * 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_rahu_kalam(sunrise_jd, sunset_jd, weekday, timezone):
    """Calculate Rahu Kalam timing"""
    day_duration = (sunset_jd - sunrise_jd) * 24  # in hours
    part_duration = day_duration / 8

    # Rahu Kalam position based on weekday (0=Sunday)
    # Sun=8, Mon=2, Tue=7, Wed=5, Thu=6, Fri=4, Sat=3
    rahu_positions = [8, 2, 7, 5, 6, 4, 3]  # Position in the day (1-8)
    position = rahu_positions[weekday]

    start_jd = sunrise_jd + ((position - 1) * part_duration / 24)
    end_jd = sunrise_jd + (position * part_duration / 24)

    return {
        "start": jd_to_datetime(start_jd, timezone),
        "end": jd_to_datetime(end_jd, timezone)
    }

def get_yamagandam(sunrise_jd, sunset_jd, weekday, timezone):
    """Calculate Yamagandam timing"""
    day_duration = (sunset_jd - sunrise_jd) * 24
    part_duration = day_duration / 8

    # Yamagandam position based on weekday (0=Sunday)
    # Sun=5, Mon=4, Tue=3, Wed=2, Thu=1, Fri=7, Sat=6
    yama_positions = [5, 4, 3, 2, 1, 7, 6]
    position = yama_positions[weekday]

    start_jd = sunrise_jd + ((position - 1) * part_duration / 24)
    end_jd = sunrise_jd + (position * part_duration / 24)

    return {
        "start": jd_to_datetime(start_jd, timezone),
        "end": jd_to_datetime(end_jd, timezone)
    }

def get_gulikai_kalam(sunrise_jd, sunset_jd, weekday, timezone):
    """Calculate Gulikai Kalam timing"""
    day_duration = (sunset_jd - sunrise_jd) * 24
    part_duration = day_duration / 8

    # Gulikai position based on weekday (0=Sunday)
    # Sun=7, Mon=6, Tue=5, Wed=4, Thu=3, Fri=2, Sat=1
    gulikai_positions = [7, 6, 5, 4, 3, 2, 1]
    position = gulikai_positions[weekday]

    start_jd = sunrise_jd + ((position - 1) * part_duration / 24)
    end_jd = sunrise_jd + (position * part_duration / 24)

    return {
        "start": jd_to_datetime(start_jd, timezone),
        "end": jd_to_datetime(end_jd, timezone)
    }

def get_tamil_month(sun_long):
    """Get Tamil month based on Sun's position"""
    # Tamil months are solar-based, starting with Chithirai when Sun enters Mesha
    month_num = int(sun_long / 30)
    return TAMIL_MONTHS[month_num]

@app.get("/")
def read_root():
    return {
        "message": "Tamil Panchang API",
        "version": "1.0.0",
        "endpoints": {
            "panchang": "/api/panchang",
            "today": "/api/today",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/panchang")
def get_panchang(request: PanchangRequest):
    """Get complete Tamil Panchang for a given date and location"""
    try:
        # Parse date
        dt = datetime.strptime(request.date, "%Y-%m-%d")
        
        # Calculate Julian Day
        jd = julian_day(dt.year, dt.month, dt.day, 6, 0, 0)  # 6 AM local time
        
        # Get sunrise and sunset
        sunrise_jd, sunset_jd = get_sunrise_sunset(
            jd, request.latitude, request.longitude
        )
        
        # Use sunrise JD for calculations (Tamil day starts at sunrise)
        sun_long, moon_long = get_sun_moon_positions(sunrise_jd)
        
        # Calculate panchang elements
        tithi = get_tithi(sun_long, moon_long)
        nakshatra = get_nakshatra(moon_long)
        yoga = get_yoga(sun_long, moon_long)
        karana = get_karana(sun_long, moon_long)
        
        # Get weekday
        weekday = dt.weekday()
        weekday_sunday_start = (weekday + 1) % 7  # Convert to Sunday=0
        
        # Calculate inauspicious timings
        rahu_kalam = get_rahu_kalam(
            sunrise_jd, sunset_jd, weekday_sunday_start, request.timezone
        )
        yamagandam = get_yamagandam(
            sunrise_jd, sunset_jd, weekday_sunday_start, request.timezone
        )
        gulikai = get_gulikai_kalam(
            sunrise_jd, sunset_jd, weekday_sunday_start, request.timezone
        )
        
        # Get Tamil month
        tamil_month = get_tamil_month(sun_long)
        
        return {
            "date": request.date,
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude,
                "timezone": request.timezone
            },
            "tamil_month": tamil_month,
            "weekday": {
                "english": dt.strftime("%A"),
                "tamil": WEEKDAYS_TAMIL[weekday_sunday_start]
            },
            "sunrise": jd_to_datetime(sunrise_jd, request.timezone),
            "sunset": jd_to_datetime(sunset_jd, request.timezone),
            "tithi": tithi,
            "nakshatra": nakshatra,
            "yoga": yoga,
            "karana": karana,
            "sun_sign": {
                "longitude": round(sun_long, 2),
                "rasi": ["Mesha", "Vrishabha", "Mithuna", "Kataka", "Simha", "Kanya", 
                        "Tula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"][int(sun_long/30)]
            },
            "moon_sign": {
                "longitude": round(moon_long, 2),
                "rasi": ["Mesha", "Vrishabha", "Mithuna", "Kataka", "Simha", "Kanya", 
                        "Tula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"][int(moon_long/30)]
            },
            "inauspicious_timings": {
                "rahu_kalam": rahu_kalam,
                "yamagandam": yamagandam,
                "gulikai_kalam": gulikai
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating panchang: {str(e)}")

@app.post("/api/today")
def get_today_panchang(location: LocationRequest):
    """Get Tamil Panchang for today"""
    today = date.today().strftime("%Y-%m-%d")
    request = PanchangRequest(
        date=today,
        latitude=location.latitude,
        longitude=location.longitude,
        timezone=location.timezone
    )
    return get_panchang(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
