from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
import swisseph as swe
import math
from fastapi import Request
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
import json

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

# Amirthathi Yoga names (27 yogas based on weekday + nakshatra)
AMIRTHATHI_YOGAS = [
    "Amirtha", "Siddha", "Marana", "Kana", "Uttama", "Arishta", "Sobhana",
    "Dhana", "Vradhi", "Sowmya", "Atiganda", "Kalana", "Mudgara",
    "Kala", "Bava", "Huthasana", "Varuna", "Vishkamba", "Vajra",
    "Siddhi", "Vyatipata", "Parigha", "Siva", "Sadhya", "Brahma",
    "Indra", "Vaidhriti"
]

# Amirthathi Yoga lookup table based on weekday and nakshatra
# Formula: (weekday + nakshatra - 1) % 27
# This gives the yoga index (0-26)

# Rutu (Season) names based on Tamil solar months
RUTU_NAMES = {
    "Chithirai": "Vasantha Rutu (Spring)",
    "Vaikasi": "Vasantha Rutu (Spring)",
    "Aani": "Greeshma Rutu (Summer)",
    "Aadi": "Greeshma Rutu (Summer)",
    "Aavani": "Varsha Rutu (Monsoon)",
    "Purattasi": "Varsha Rutu (Monsoon)",
    "Aippasi": "Sharad Rutu (Autumn)",
    "Karthigai": "Sharad Rutu (Autumn)",
    "Margazhi": "Hemantha Rutu (Pre-Winter)",
    "Thai": "Hemantha Rutu (Pre-Winter)",
    "Maasi": "Shishira Rutu (Winter)",
    "Panguni": "Shishira Rutu (Winter)"
}

# Gowri Panchangam names
GOWRI_NAMES = [
    "Uthi", "Amridha", "Rogam", "Labam", "Dhanam", "Sugam", "Visham", "Soram"
]

# Gowri Panchangam sequence for each weekday (Day - Sunrise to Sunset)
# Each day starts with a different sequence based on weekday
# Sunday=0, Monday=1, ..., Saturday=6
GOWRI_DAY_SEQUENCE = [
    ["Uthi", "Amridha", "Rogam", "Labam", "Dhanam", "Sugam", "Visham", "Soram"],      # Sunday
    ["Labam", "Dhanam", "Sugam", "Visham", "Soram", "Amridha", "Uthi", "Rogam"],      # Monday
    ["Visham", "Soram", "Uthi", "Amridha", "Rogam", "Labam", "Dhanam", "Sugam"],      # Tuesday
    ["Rogam", "Labam", "Dhanam", "Sugam", "Visham", "Soram", "Uthi", "Amridha"],      # Wednesday
    ["Dhanam", "Sugam", "Soram", "Uthi", "Amridha", "Visham", "Rogam", "Labam"],      # Thursday
    ["Sugam", "Soram", "Uthi", "Visham", "Amridha", "Rogam", "Labam", "Dhanam"],      # Friday
    ["Soram", "Uthi", "Visham", "Amridha", "Rogam", "Labam", "Dhanam", "Sugam"]       # Saturday
]

# Gowri Panchangam sequence for night (Sunset to next Sunrise)
GOWRI_NIGHT_SEQUENCE = [
    ["Amridha", "Visham", "Rogam", "Labam", "Dhanam", "Sugam", "Soram", "Uthi"],      # Sunday
    ["Uthi", "Amridha", "Rogam", "Labam", "Sugam", "Dhanam", "Visham", "Soram"],      # Monday
    ["Rogam", "Labam", "Dhanam", "Sugam", "Visham", "Soram", "Uthi", "Amridha"],      # Tuesday
    ["Dhanam", "Sugam", "Soram", "Uthi", "Amridha", "Visham", "Rogam", "Labam"],      # Wednesday
    ["Visham", "Soram", "Uthi", "Amridha", "Rogam", "Labam", "Dhanam", "Sugam"],      # Thursday
    ["Rogam", "Labam", "Dhanam", "Sugam", "Soram", "Uthi", "Visham", "Amridha"],      # Friday
    ["Labam", "Dhanam", "Sugam", "Visham", "Soram", "Uthi", "Amridha", "Rogam"]       # Saturday
]

# Auspicious Gowri periods (Nalla Neram)
AUSPICIOUS_GOWRI = ["Amridha", "Uthi", "Labam", "Sugam", "Dhanam"]

# Inauspicious Gowri periods
INAUSPICIOUS_GOWRI = ["Visham", "Rogam", "Soram"]

# Planetary names for Hora
PLANETS_HORA = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

# Chaldean order for Hora (repeating sequence)
# Starts with day ruler: Sun (Sunday), Moon (Monday), Mars (Tuesday), Mercury (Wednesday),
# Jupiter (Thursday), Venus (Friday), Saturn (Saturday)
HORA_DAY_RULERS = [0, 3, 6, 2, 5, 1, 4]  # Indices in PLANETS_HORA

# Nakshatra classifications based on sight direction
# Mel Nokku (Upward looking) - Good for construction, worship, planting upward-growing things
MEL_NOKKU_NAKSHATRAS = [
    "Rohini", "Thiruvathirai", "Poosam", "Uthiram", "Uthiradam", "Uthirattathi",
    "Thiruvonam", "Avittam", "Sadayam"
]

# Keezh Nokku (Downward looking) - Good for digging, mining, laying foundations
KEEZH_NOKKU_NAKSHATRAS = [
    "Bharani", "Karthigai", "Ayilyam", "Makam", "Puram", "Moolam",
    "Pooradam", "Poorattathi"
]

# Sama Nokku (Forward/Side looking) - Good for travel, vehicles, horizontal activities
SAMA_NOKKU_NAKSHATRAS = [
    "Aswini", "Mirugasiridam", "Punarpoosam", "Hastham", "Chithirai",
    "Swathi", "Anusham", "Visakam", "Kettai", "Revathi"
]

# Special Yogas: Amrita, Siddha, Marana based on weekday + nakshatra combination
# Format: {weekday: {nakshatra_index: yoga_type}}
# Sunday=0, Monday=1, Tuesday=2, Wednesday=3, Thursday=4, Friday=5, Saturday=6
# Amrita = Auspicious (Nectar), Siddha = Auspicious (Success), Marana = Inauspicious (Death-like)
SPECIAL_YOGAS = {
    0: {  # Sunday - Gnayiru
        0: "Marana", 1: "Siddha", 2: "Amrita", 3: "Marana", 4: "Siddha",
        5: "Marana", 6: "Siddha", 7: "Amrita", 8: "Marana", 9: "Siddha",
        10: "Marana", 11: "Siddha", 12: "Amrita", 13: "Marana", 14: "Siddha",
        15: "Marana", 16: "Siddha", 17: "Amrita", 18: "Marana", 19: "Siddha",
        20: "Marana", 21: "Amrita", 22: "Marana", 23: "Siddha", 24: "Marana",
        25: "Siddha", 26: "Amrita"
    },
    1: {  # Monday - Thingal
        0: "Amrita", 1: "Marana", 2: "Siddha", 3: "Marana", 4: "Amrita",
        5: "Siddha", 6: "Marana", 7: "Siddha", 8: "Amrita", 9: "Marana",
        10: "Siddha", 11: "Marana", 12: "Siddha", 13: "Amrita", 14: "Marana",
        15: "Siddha", 16: "Marana", 17: "Siddha", 18: "Amrita", 19: "Marana",
        20: "Siddha", 21: "Marana", 22: "Amrita", 23: "Marana", 24: "Siddha",
        25: "Marana", 26: "Siddha"
    },
    2: {  # Tuesday - Sevvai
        0: "Siddha", 1: "Amrita", 2: "Marana", 3: "Siddha", 4: "Marana",
        5: "Amrita", 6: "Siddha", 7: "Marana", 8: "Siddha", 9: "Amrita",
        10: "Marana", 11: "Siddha", 12: "Marana", 13: "Siddha", 14: "Amrita",
        15: "Marana", 16: "Siddha", 17: "Marana", 18: "Siddha", 19: "Amrita",
        20: "Marana", 21: "Siddha", 22: "Siddha", 23: "Amrita", 24: "Marana",
        25: "Siddha", 26: "Marana"
    },
    3: {  # Wednesday - Budhan
        0: "Marana", 1: "Siddha", 2: "Amrita", 3: "Marana", 4: "Siddha",
        5: "Marana", 6: "Amrita", 7: "Siddha", 8: "Marana", 9: "Siddha",
        10: "Amrita", 11: "Marana", 12: "Siddha", 13: "Marana", 14: "Siddha",
        15: "Amrita", 16: "Marana", 17: "Siddha", 18: "Marana", 19: "Siddha",
        20: "Amrita", 21: "Marana", 22: "Siddha", 23: "Marana", 24: "Amrita",
        25: "Siddha", 26: "Marana"
    },
    4: {  # Thursday - Viyazhan
        0: "Siddha", 1: "Marana", 2: "Siddha", 3: "Amrita", 4: "Marana",
        5: "Siddha", 6: "Marana", 7: "Marana", 8: "Amrita", 9: "Siddha",
        10: "Marana", 11: "Amrita", 12: "Marana", 13: "Siddha", 14: "Marana",
        15: "Siddha", 16: "Amrita", 17: "Marana", 18: "Siddha", 19: "Marana",
        20: "Siddha", 21: "Siddha", 22: "Marana", 23: "Siddha", 24: "Siddha",
        25: "Amrita", 26: "Marana"
    },
    5: {  # Friday - Velli
        0: "Marana", 1: "Siddha", 2: "Marana", 3: "Siddha", 4: "Amrita",
        5: "Marana", 6: "Siddha", 7: "Amrita", 8: "Siddha", 9: "Marana",
        10: "Siddha", 11: "Siddha", 12: "Amrita", 13: "Marana", 14: "Siddha",
        15: "Marana", 16: "Siddha", 17: "Amrita", 18: "Marana", 19: "Siddha",
        20: "Marana", 21: "Siddha", 22: "Amrita", 23: "Marana", 24: "Marana",
        25: "Siddha", 26: "Amrita"
    },
    6: {  # Saturday - Sani
        0: "Siddha", 1: "Marana", 2: "Siddha", 3: "Amrita", 4: "Siddha",
        5: "Amrita", 6: "Marana", 7: "Siddha", 8: "Marana", 9: "Marana",
        10: "Siddha", 11: "Amrita", 12: "Marana", 13: "Siddha", 14: "Marana",
        15: "Amrita", 16: "Marana", 17: "Siddha", 18: "Siddha", 19: "Marana",
        20: "Amrita", 21: "Marana", 22: "Siddha", 23: "Siddha", 24: "Amrita",
        25: "Marana", 26: "Siddha"
    }
}

def julian_day(year, month, day, hour=0, minute=0, second=0):
    """
    Convert a Gregorian calendar date and time to Julian Day Number.

    Julian Day Number is a continuous count of days since the beginning of the
    Julian Period (January 1, 4713 BC, Monday, 12:00 UT). It's used in astronomical
    calculations for precise time measurements.

    Args:
        year (int): Year in Gregorian calendar
        month (int): Month (1-12)
        day (int): Day of month (1-31)
        hour (int, optional): Hour of day (0-23). Defaults to 0.
        minute (int, optional): Minute (0-59). Defaults to 0.
        second (int, optional): Second (0-59). Defaults to 0.

    Returns:
        float: Julian Day Number as a decimal value

    Example:
        >>> julian_day(2025, 11, 28, 12, 30, 0)
        2460643.0208333335
    """
    decimal_time = hour + minute/60.0 + second/3600.0
    return swe.julday(year, month, day, decimal_time)

def get_sun_moon_positions(jd):
    """
    Calculate the sidereal (Nirayana) ecliptic longitude positions of the Sun and Moon.

    Uses PySwisseph library to calculate precise astronomical positions at a
    given Julian Day. Returns sidereal (Nirayana) longitude values using Lahiri
    Ayanamsa, which is the standard for Tamil panchang calculations.

    Args:
        jd (float): Julian Day Number for the calculation time

    Returns:
        tuple: (sun_longitude, moon_longitude, ayanamsa)
            - sun_longitude (float): Sun's sidereal longitude in degrees (0-360)
            - moon_longitude (float): Moon's sidereal longitude in degrees (0-360)
            - ayanamsa (float): Lahiri Ayanamsa value at the given JD

    Example:
        >>> get_sun_moon_positions(2460643.0)
        (221.45, 98.23, 24.22)  # Example sidereal values
    """
    # Set sidereal mode to Lahiri (default for Tamil/Indian astrology)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # Get Lahiri Ayanamsa for this date
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Calculate tropical positions
    sun_tropical = swe.calc_ut(jd, swe.SUN)[0][0]
    moon_tropical = swe.calc_ut(jd, swe.MOON)[0][0]

    # Convert to sidereal by subtracting ayanamsa
    sun_sidereal = (sun_tropical - ayanamsa) % 360
    moon_sidereal = (moon_tropical - ayanamsa) % 360

    return sun_sidereal, moon_sidereal, ayanamsa

def get_tithi(sun_long, moon_long):
    """
    Calculate the current Tithi (lunar day) from Sun and Moon positions.

    Tithi is the lunar day in Hindu calendar, defined by the angular relationship
    between the Sun and Moon. Each tithi spans 12 degrees of separation and there
    are 30 tithis in a lunar month (15 in waxing/Shukla Paksha, 15 in waning/Krishna Paksha).

    Calculation method:
    - Angular difference = (Moon longitude - Sun longitude) mod 360
    - Tithi number = floor(difference / 12)
    - Each 12° represents one tithi
    - Tithis 0-14: Shukla Paksha (waxing moon, leading to Pournami/Full Moon)
    - Tithis 15-29: Krishna Paksha (waning moon, leading to Amavasya/New Moon)

    Args:
        sun_long (float): Sun's tropical longitude in degrees (0-360)
        moon_long (float): Moon's tropical longitude in degrees (0-360)

    Returns:
        dict: Tithi information containing:
            - number (int): Tithi number (1-30)
            - name (str): Tamil name of the tithi
            - paksha (str): "Shukla Paksha" (waxing) or "Krishna Paksha" (waning)
            - remaining (float): Percentage of tithi remaining (0-100)

    Example:
        >>> get_tithi(245.0, 280.0)
        {'number': 3, 'name': 'Thrithiya', 'paksha': 'Shukla Paksha', 'remaining': 8.33}
    """
    # Calculate angular separation between Moon and Sun
    diff = (moon_long - sun_long) % 360
    tithi_num = int(diff / 12)  # Each tithi is 12 degrees
    tithi_remaining = (diff % 12) / 12

    paksha = "Shukla Paksha" if tithi_num < 15 else "Krishna Paksha"
    tithi_name = TITHIS_TAMIL[tithi_num % 15]

    return {
        "number": tithi_num + 1,
        "name": tithi_name,
        "paksha": paksha,
        "remaining": round((1 - tithi_remaining) * 100, 2)
    }

def get_tithi_transitions(start_jd, end_jd, timezone, reference_date):
    """
    Calculate all tithi transitions within a period (sunrise to next sunrise).
    Returns list of tithis with their start and end times.

    Args:
        start_jd: Starting Julian Day (sunrise)
        end_jd: Ending Julian Day (next sunrise)
        timezone: Timezone offset
        reference_date: Reference date string in YYYY-MM-DD format for comparison
    """
    tithis = []
    current_jd = start_jd

    # Get initial tithi (using sidereal longitudes)
    sun_long, moon_long, _ = get_sun_moon_positions(current_jd)
    current_tithi = get_tithi(sun_long, moon_long)
    tithi_start_jd = start_jd

    # Scan through the period in small increments to find transitions
    increment = 1.0 / 1440.0  # 1 minute in days

    while current_jd < end_jd:
        current_jd += increment
        sun_long, moon_long, _ = get_sun_moon_positions(current_jd)
        new_tithi = get_tithi(sun_long, moon_long)

        # Check if tithi changed
        if new_tithi["number"] != current_tithi["number"]:
            # Get end time with date
            end_time, end_date = jd_to_datetime(current_jd, timezone, include_date=True)
            start_time, start_date = jd_to_datetime(tithi_start_jd, timezone, include_date=True)

            # Check if different from reference date
            start_suffix = f" ({start_date})" if start_date != reference_date else ""
            end_suffix = f" ({end_date})" if end_date != reference_date else ""

            # Record the previous tithi
            tithis.append({
                "number": current_tithi["number"],
                "name": current_tithi["name"],
                "paksha": current_tithi["paksha"],
                "start": start_time + start_suffix,
                "end": end_time + end_suffix
            })

            # Start tracking new tithi
            current_tithi = new_tithi
            tithi_start_jd = current_jd

    # Add the final tithi that extends to end of period
    end_time, end_date = jd_to_datetime(end_jd, timezone, include_date=True)
    start_time, start_date = jd_to_datetime(tithi_start_jd, timezone, include_date=True)

    start_suffix = f" ({start_date})" if start_date != reference_date else ""
    end_suffix = f" ({end_date})" if end_date != reference_date else ""

    tithis.append({
        "number": current_tithi["number"],
        "name": current_tithi["name"],
        "paksha": current_tithi["paksha"],
        "start": start_time + start_suffix,
        "end": end_time + end_suffix
    })

    return tithis

def get_nakshatra(moon_long):
    """
    Calculate the current Nakshatra (lunar mansion) from Moon's position.

    Nakshatra is the lunar mansion in Hindu astrology. There are 27 nakshatras
    dividing the 360-degree zodiac into 27 equal parts of 13.33° each. The Moon
    spends approximately one day in each nakshatra.

    Calculation method:
    - Each nakshatra spans 13.33° (360° / 27)
    - Nakshatra number = floor(Moon longitude × 27 / 360)
    - The position determines which of the 27 nakshatras the Moon is in

    Args:
        moon_long (float): Moon's tropical longitude in degrees (0-360)

    Returns:
        dict: Nakshatra information containing:
            - number (int): Nakshatra number (1-27)
            - name (str): Tamil name of the nakshatra
            - remaining (float): Percentage of nakshatra remaining (0-100)

    Example:
        >>> get_nakshatra(123.45)
        {'number': 10, 'name': 'Makam', 'remaining': 23.45}
    """
    # Calculate which nakshatra the Moon is in (each is 13.33 degrees)
    nak_num = int(moon_long * 27 / 360)
    nak_remaining = (moon_long * 27 / 360) % 1

    return {
        "number": nak_num + 1,
        "name": NAKSHATRAS_TAMIL[nak_num],
        "remaining": round((1 - nak_remaining) * 100, 2)
    }

def get_nakshatra_transitions(start_jd, end_jd, timezone, reference_date):
    """
    Calculate all nakshatra transitions within a period (sunrise to next sunrise).
    Returns list of nakshatras with their start and end times.

    Args:
        start_jd: Starting Julian Day (sunrise)
        end_jd: Ending Julian Day (next sunrise)
        timezone: Timezone offset
        reference_date: Reference date string in YYYY-MM-DD format for comparison
    """
    nakshatras = []
    current_jd = start_jd

    # Get initial nakshatra (using sidereal longitude)
    _, moon_long, _ = get_sun_moon_positions(current_jd)
    current_nakshatra = get_nakshatra(moon_long)
    nakshatra_start_jd = start_jd

    # Scan through the period in small increments to find transitions
    increment = 1.0 / 1440.0  # 1 minute in days

    while current_jd < end_jd:
        current_jd += increment
        _, moon_long, _ = get_sun_moon_positions(current_jd)
        new_nakshatra = get_nakshatra(moon_long)

        # Check if nakshatra changed
        if new_nakshatra["number"] != current_nakshatra["number"]:
            # Get times with dates
            end_time, end_date = jd_to_datetime(current_jd, timezone, include_date=True)
            start_time, start_date = jd_to_datetime(nakshatra_start_jd, timezone, include_date=True)

            # Check if different from reference date
            start_suffix = f" ({start_date})" if start_date != reference_date else ""
            end_suffix = f" ({end_date})" if end_date != reference_date else ""

            # Record the previous nakshatra
            nakshatras.append({
                "number": current_nakshatra["number"],
                "name": current_nakshatra["name"],
                "start": start_time + start_suffix,
                "end": end_time + end_suffix
            })

            # Start tracking new nakshatra
            current_nakshatra = new_nakshatra
            nakshatra_start_jd = current_jd

    # Add the final nakshatra that extends to end of period
    end_time, end_date = jd_to_datetime(end_jd, timezone, include_date=True)
    start_time, start_date = jd_to_datetime(nakshatra_start_jd, timezone, include_date=True)

    start_suffix = f" ({start_date})" if start_date != reference_date else ""
    end_suffix = f" ({end_date})" if end_date != reference_date else ""

    nakshatras.append({
        "number": current_nakshatra["number"],
        "name": current_nakshatra["name"],
        "start": start_time + start_suffix,
        "end": end_time + end_suffix
    })

    return nakshatras

def get_yoga(sun_long, moon_long):
    """
    Calculate the current Yoga from Sun and Moon positions.

    Yoga is one of the five key elements (Panchangam) in Hindu calendar. There are
    27 yogas, each representing a specific combination of Sun and Moon positions.
    Yoga is calculated from the sum of Sun and Moon longitudes.

    Calculation method:
    - Yoga value = (Sun longitude + Moon longitude) mod 360
    - Yoga number = floor(Yoga value × 27 / 360)
    - Each yoga spans 13.33° (360° / 27)

    Some yogas are considered auspicious (e.g., Siddhi, Brahma) while others
    are inauspicious (e.g., Vyatipata, Vaidhriti).

    Args:
        sun_long (float): Sun's tropical longitude in degrees (0-360)
        moon_long (float): Moon's tropical longitude in degrees (0-360)

    Returns:
        dict: Yoga information containing:
            - number (int): Yoga number (1-27)
            - name (str): Name of the yoga
            - remaining (float): Percentage of yoga remaining (0-100)

    Example:
        >>> get_yoga(245.0, 123.0)
        {'number': 28, 'name': 'Vishkambha', 'remaining': 15.67}
    """
    # Calculate sum of Sun and Moon longitudes
    yoga_val = (sun_long + moon_long) % 360
    yoga_num = int(yoga_val * 27 / 360)  # Each yoga is 13.33 degrees
    yoga_remaining = (yoga_val * 27 / 360) % 1

    return {
        "number": yoga_num + 1,
        "name": YOGAS[yoga_num],
        "remaining": round((1 - yoga_remaining) * 100, 2)
    }

def get_yoga_transitions(start_jd, end_jd, timezone, reference_date):
    """
    Calculate all yoga transitions within a period (sunrise to next sunrise).
    Returns list of yogas with their start and end times.

    Args:
        start_jd: Starting Julian Day (sunrise)
        end_jd: Ending Julian Day (next sunrise)
        timezone: Timezone offset
        reference_date: Reference date string in YYYY-MM-DD format for comparison
    """
    yogas = []
    current_jd = start_jd

    # Get initial yoga (using sidereal longitudes)
    sun_long, moon_long, _ = get_sun_moon_positions(current_jd)
    current_yoga = get_yoga(sun_long, moon_long)
    yoga_start_jd = start_jd

    # Scan through the period in small increments to find transitions
    increment = 1.0 / 1440.0  # 1 minute in days

    while current_jd < end_jd:
        current_jd += increment
        sun_long, moon_long, _ = get_sun_moon_positions(current_jd)
        new_yoga = get_yoga(sun_long, moon_long)

        # Check if yoga changed
        if new_yoga["number"] != current_yoga["number"]:
            # Get times with dates
            end_time, end_date = jd_to_datetime(current_jd, timezone, include_date=True)
            start_time, start_date = jd_to_datetime(yoga_start_jd, timezone, include_date=True)

            # Check if different from reference date
            start_suffix = f" ({start_date})" if start_date != reference_date else ""
            end_suffix = f" ({end_date})" if end_date != reference_date else ""

            # Record the previous yoga
            yogas.append({
                "number": current_yoga["number"],
                "name": current_yoga["name"],
                "start": start_time + start_suffix,
                "end": end_time + end_suffix
            })

            # Start tracking new yoga
            current_yoga = new_yoga
            yoga_start_jd = current_jd

    # Add the final yoga that extends to end of period
    end_time, end_date = jd_to_datetime(end_jd, timezone, include_date=True)
    start_time, start_date = jd_to_datetime(yoga_start_jd, timezone, include_date=True)

    start_suffix = f" ({start_date})" if start_date != reference_date else ""
    end_suffix = f" ({end_date})" if end_date != reference_date else ""

    yogas.append({
        "number": current_yoga["number"],
        "name": current_yoga["name"],
        "start": start_time + start_suffix,
        "end": end_time + end_suffix
    })

    return yogas

def get_karana(sun_long, moon_long):
    """
    Calculate the current Karana from Sun and Moon positions.

    Karana is half of a Tithi. While there are 30 tithis in a lunar month,
    there are 60 karanas. Each karana is 6 degrees of separation between
    Moon and Sun (half of tithi's 12 degrees).

    There are 11 karanas total:
    - 7 movable karanas (Bava, Balava, Kaulava, Taitila, Garaja, Vanija, Vishti)
      that repeat 8 times in sequence
    - 4 fixed karanas (Shakuni, Chatushpada, Naga, Kimstughna) that occur once
      at the end of the lunar month

    Calculation method:
    - Angular difference = (Moon longitude - Sun longitude) mod 360
    - Karana number = floor(difference / 6)
    - Karanas 0-56: Cycling through 7 movable karanas
    - Karanas 57-60: Fixed karanas

    Args:
        sun_long (float): Sun's tropical longitude in degrees (0-360)
        moon_long (float): Moon's tropical longitude in degrees (0-360)

    Returns:
        dict: Karana information containing:
            - number (int): Karana number (1-60)
            - name (str): Name of the karana

    Example:
        >>> get_karana(245.0, 280.0)
        {'number': 6, 'name': 'Kaulava'}
    """
    # Calculate angular separation between Moon and Sun
    diff = (moon_long - sun_long) % 360
    karana_num = int(diff / 6)  # Each karana is 6 degrees (half of tithi)

    # Fixed Karanas (last 4) occur at the end of Krishna Paksha
    if karana_num >= 57:
        karana_idx = 7 + (karana_num - 57)  # Indices 7-10 for fixed karanas
    else:
        karana_idx = karana_num % 7  # Cycle through 7 movable karanas

    return {
        "number": karana_num + 1,
        "name": KARANAS[min(karana_idx, 10)]
    }

def get_sunrise_sunset(jd, lat, lon):
    """
    Calculate sunrise and sunset times for a given location and date.

    This function is critical for Tamil panchang calculations because the Tamil
    calendar day begins at sunrise, not midnight. All panchang elements are
    calculated based on sunrise time.

    Uses PySwisseph's rise_trans function which accounts for:
    - Atmospheric refraction
    - Observer's geographic location
    - Earth's topography (altitude)

    Args:
        jd (float): Approximate Julian Day Number for the date
        lat (float): Latitude of location in decimal degrees (-90 to +90)
        lon (float): Longitude of location in decimal degrees (-180 to +180)

    Returns:
        tuple: (sunrise_jd, sunset_jd)
            - sunrise_jd (float): Julian Day Number of sunrise
            - sunset_jd (float): Julian Day Number of sunset

    Example:
        >>> get_sunrise_sunset(2460643.0, 13.0827, 80.2707)
        (2460642.7123, 2460643.0234)  # Example values for Trichy, India
    """
    geopos = (lon, lat, 0)  # longitude, latitude, altitude in meters

    # Sunrise (rsmi=1 for rise) - search from previous day to find the sunrise
    # near the given Julian Day
    sunrise_jd = swe.rise_trans(
        jd - 1, swe.SUN, 1, geopos, 0, 0
    )[1][0]

    # Sunset (rsmi=2 for set) - search from sunrise to get the NEXT sunset
    # This ensures we get the sunset for the same day
    sunset_jd = swe.rise_trans(
        sunrise_jd, swe.SUN, 2, geopos, 0, 0
    )[1][0]

    return sunrise_jd, sunset_jd

def jd_to_datetime(jd, timezone, include_date=False):
    """
    Convert Julian Day Number to human-readable time string with timezone adjustment.

    Converts astronomical Julian Day to local time format (HH:MM:SS) accounting
    for the observer's timezone. Properly handles day transitions when timezone
    adjustment causes the time to cross midnight.

    Args:
        jd (float): Julian Day Number to convert
        timezone (float): Timezone offset from UTC in hours (e.g., 5.5 for IST)
        include_date (bool, optional): If True, also returns the date. Defaults to False.

    Returns:
        str or tuple:
            - If include_date is False: Time string in "HH:MM:SS" format
            - If include_date is True: Tuple of (time_str, date_str) where
              date_str is in "YYYY-MM-DD" format

    Example:
        >>> jd_to_datetime(2460643.25, 5.5)
        '11:30:00'
        >>> jd_to_datetime(2460643.25, 5.5, include_date=True)
        ('11:30:00', '2025-11-28')
    """
    # Convert Julian Day to calendar date and time (UTC)
    result = swe.revjul(jd)
    year, month, day, hour = result[0], result[1], result[2], result[3]

    # Adjust for timezone offset
    hour_adjusted = hour + timezone

    # Handle day overflow (time crosses midnight due to timezone)
    if hour_adjusted >= 24:
        hour_adjusted -= 24
        day += 1
    elif hour_adjusted < 0:
        hour_adjusted += 24
        day -= 1

    # Convert decimal hour to hours, minutes, seconds
    hours = int(hour_adjusted)
    minutes = int((hour_adjusted - hours) * 60)
    seconds = int(((hour_adjusted - hours) * 60 - minutes) * 60)

    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    if include_date:
        return time_str, f"{year:04d}-{month:02d}-{day:02d}"

    return time_str

def get_rahu_kalam(sunrise_jd, sunset_jd, weekday, timezone):
    """
    Calculate Rahu Kalam (Rahu Kaal) - an inauspicious period ruled by Rahu.

    Rahu Kalam is considered highly inauspicious in Hindu astrology. No new
    ventures, important activities, or auspicious events should be started during
    this period. It lasts approximately 90 minutes each day.

    Calculation method:
    1. Divide daylight (sunrise to sunset) into 8 equal parts
    2. Select the specific part based on weekday (each day has different position)

    Weekday positions (1-based, from sunrise):
    - Sunday: 8th part (last part before sunset)
    - Monday: 2nd part (early morning)
    - Tuesday: 7th part (late afternoon)
    - Wednesday: 5th part (mid-afternoon)
    - Thursday: 6th part (late afternoon)
    - Friday: 4th part (late morning)
    - Saturday: 3rd part (morning)

    Args:
        sunrise_jd (float): Julian Day of sunrise
        sunset_jd (float): Julian Day of sunset
        weekday (int): Weekday number (0=Sunday, 1=Monday, ..., 6=Saturday)
        timezone (float): Timezone offset from UTC in hours

    Returns:
        dict: Rahu Kalam timing with 'start' and 'end' times in HH:MM:SS format

    Example:
        >>> get_rahu_kalam(2460643.25, 2460643.75, 0, 5.5)
        {'start': '16:30:00', 'end': '18:00:00'}
    """
    day_duration = (sunset_jd - sunrise_jd) * 24  # daylight hours
    part_duration = day_duration / 8  # each part duration in hours

    # Rahu Kalam position based on weekday (0=Sunday, 1=Monday, etc.)
    # Position values represent which 1/8th part of the day (1-8)
    rahu_positions = [8, 2, 7, 5, 6, 4, 3]  # Sun, Mon, Tue, Wed, Thu, Fri, Sat
    position = rahu_positions[weekday]

    # Calculate start and end times based on position
    start_jd = sunrise_jd + ((position - 1) * part_duration / 24)
    end_jd = sunrise_jd + (position * part_duration / 24)

    # Check if end time is on next day (crosses midnight)
    end_time = jd_to_datetime(end_jd, timezone)
    is_next_day = end_jd >= (sunrise_jd + 1.0)

    return {
        "start": jd_to_datetime(start_jd, timezone),
        "end": end_time + (" (next day)" if is_next_day else "")
    }

def get_yamagandam(sunrise_jd, sunset_jd, weekday, timezone):
    """
    Calculate Yamagandam (Yama Ghantam) - an inauspicious period ruled by Yama.

    Yamagandam is another inauspicious time period in Hindu astrology, associated
    with Lord Yama (the god of death). Like Rahu Kalam, it's avoided for starting
    new ventures, important work, or auspicious activities.

    Calculation method:
    1. Divide daylight (sunrise to sunset) into 8 equal parts
    2. Select the specific part based on weekday (different position than Rahu Kalam)

    Weekday positions (1-based, from sunrise):
    - Sunday: 5th part (afternoon)
    - Monday: 4th part (late morning)
    - Tuesday: 3rd part (morning)
    - Wednesday: 2nd part (early morning)
    - Thursday: 1st part (right after sunrise)
    - Friday: 7th part (late afternoon)
    - Saturday: 6th part (late afternoon)

    Args:
        sunrise_jd (float): Julian Day of sunrise
        sunset_jd (float): Julian Day of sunset
        weekday (int): Weekday number (0=Sunday, 1=Monday, ..., 6=Saturday)
        timezone (float): Timezone offset from UTC in hours

    Returns:
        dict: Yamagandam timing with 'start' and 'end' times in HH:MM:SS format

    Example:
        >>> get_yamagandam(2460643.25, 2460643.75, 0, 5.5)
        {'start': '12:00:00', 'end': '13:30:00'}
    """
    day_duration = (sunset_jd - sunrise_jd) * 24  # daylight hours
    part_duration = day_duration / 8  # each part duration in hours

    # Yamagandam position based on weekday (0=Sunday, 1=Monday, etc.)
    # Position values represent which 1/8th part of the day (1-8)
    yama_positions = [5, 4, 3, 2, 1, 7, 6]  # Sun, Mon, Tue, Wed, Thu, Fri, Sat
    position = yama_positions[weekday]

    # Calculate start and end times based on position
    start_jd = sunrise_jd + ((position - 1) * part_duration / 24)
    end_jd = sunrise_jd + (position * part_duration / 24)

    # Check if end time is on next day (crosses midnight)
    end_time = jd_to_datetime(end_jd, timezone)
    is_next_day = end_jd >= (sunrise_jd + 1.0)

    return {
        "start": jd_to_datetime(start_jd, timezone),
        "end": end_time + (" (next day)" if is_next_day else "")
    }

def get_gulikai_kalam(sunrise_jd, sunset_jd, weekday, timezone):
    """
    Calculate Gulikai Kalam (Gulika Kaal) - an inauspicious period ruled by Saturn's son.

    Gulikai (also spelled Gulika or Mandi) is considered the son of Saturn and
    represents inauspicious timing in Hindu astrology. This period is avoided for
    starting new ventures, important meetings, and auspicious ceremonies.

    Calculation method:
    1. Divide daylight (sunrise to sunset) into 8 equal parts
    2. Select the specific part based on weekday (yet another pattern)

    Weekday positions (1-based, from sunrise):
    - Sunday: 7th part (late afternoon)
    - Monday: 6th part (late afternoon)
    - Tuesday: 5th part (afternoon)
    - Wednesday: 4th part (late morning)
    - Thursday: 3rd part (morning)
    - Friday: 2nd part (early morning)
    - Saturday: 1st part (right after sunrise)

    Args:
        sunrise_jd (float): Julian Day of sunrise
        sunset_jd (float): Julian Day of sunset
        weekday (int): Weekday number (0=Sunday, 1=Monday, ..., 6=Saturday)
        timezone (float): Timezone offset from UTC in hours

    Returns:
        dict: Gulikai Kalam timing with 'start' and 'end' times in HH:MM:SS format

    Example:
        >>> get_gulikai_kalam(2460643.25, 2460643.75, 0, 5.5)
        {'start': '15:00:00', 'end': '16:30:00'}
    """
    day_duration = (sunset_jd - sunrise_jd) * 24  # daylight hours
    part_duration = day_duration / 8  # each part duration in hours

    # Gulikai position based on weekday (0=Sunday, 1=Monday, etc.)
    # Position values represent which 1/8th part of the day (1-8)
    gulikai_positions = [7, 6, 5, 4, 3, 2, 1]  # Sun, Mon, Tue, Wed, Thu, Fri, Sat
    position = gulikai_positions[weekday]

    # Calculate start and end times based on position
    start_jd = sunrise_jd + ((position - 1) * part_duration / 24)
    end_jd = sunrise_jd + (position * part_duration / 24)

    # Check if end time is on next day (crosses midnight)
    end_time = jd_to_datetime(end_jd, timezone)
    is_next_day = end_jd >= (sunrise_jd + 1.0)

    return {
        "start": jd_to_datetime(start_jd, timezone),
        "end": end_time + (" (next day)" if is_next_day else "")
    }

def get_dhurmuhurtham(sunrise_jd, sunset_jd, weekday, timezone):
    """
    Calculate Dhurmuhurtham timing.
    Dhurmuhurtham is an inauspicious period considered unsuitable for starting new ventures.

    Calculation method:
    - Day is divided into 30 muhurtas (each muhurta = day_duration / 30)
    - Position varies by weekday following traditional Tamil panchang
    - Duration is typically 48 minutes (1.6 muhurtas or 1/30th of the day)

    Weekday-based positions (1-based, counting from sunrise):
    - Sunday: 14th muhurta
    - Monday: 12th muhurta
    - Tuesday: 11th muhurta
    - Wednesday: 10th muhurta
    - Thursday: 9th muhurta
    - Friday: 6th muhurta
    - Saturday: 8th muhurta
    """
    day_duration = (sunset_jd - sunrise_jd) * 24  # in hours
    muhurta_duration = day_duration / 30  # Each muhurta in hours

    # Dhurmuhurtham position based on weekday (0=Sunday)
    # These are the starting muhurta positions (1-based)
    dhur_positions = [14, 12, 11, 10, 9, 6, 8]  # Sun, Mon, Tue, Wed, Thu, Fri, Sat
    position = dhur_positions[weekday]

    # Calculate start and end times
    # Position is 1-based, so subtract 1 to convert to 0-based for calculation
    start_jd = sunrise_jd + ((position - 1) * muhurta_duration / 24)
    end_jd = sunrise_jd + (position * muhurta_duration / 24)

    # Check if end time is on next day (crosses midnight)
    end_time = jd_to_datetime(end_jd, timezone)
    is_next_day = end_jd >= (sunrise_jd + 1.0)

    return {
        "start": jd_to_datetime(start_jd, timezone),
        "end": end_time + (" (next day)" if is_next_day else ""),
        "muhurta_number": position,
        "duration_minutes": round(muhurta_duration * 60, 0)
    }

def get_sidereal_longitude(tropical_long):
    """
    Convert tropical longitude to sidereal longitude using Lahiri Ayanamsa.
    Tamil calendar uses sidereal (Nirayana) zodiac, not tropical.
    PySwisseph constant: swe.SIDM_LAHIRI
    """
    # Get Lahiri Ayanamsa for current date
    # We'll use a reference JD - this will be updated with actual JD in the calling function
    ayanamsa = swe.get_ayanamsa_ut(swe.julday(2025, 11, 28, 0))  # Placeholder
    sidereal_long = (tropical_long - ayanamsa) % 360
    return sidereal_long

def get_tamil_month(sun_long, jd):
    """
    Get Tamil month based on Sun's sidereal position.
    Tamil months are solar-based (sidereal zodiac), starting with Chithirai when Sun enters Mesha (Aries).

    Month mapping (0-based index):
    0 = Chithirai (Mesha/Aries: 0-30°)
    1 = Vaikasi (Vrishabha/Taurus: 30-60°)
    2 = Aani (Mithuna/Gemini: 60-90°)
    3 = Aadi (Kataka/Cancer: 90-120°)
    4 = Aavani (Simha/Leo: 120-150°)
    5 = Purattasi (Kanya/Virgo: 150-180°)
    6 = Aippasi (Tula/Libra: 180-210°)
    7 = Karthigai (Vrischika/Scorpio: 210-240°)
    8 = Margazhi (Dhanus/Sagittarius: 240-270°)
    9 = Thai (Makara/Capricorn: 270-300°)
    10 = Maasi (Kumbha/Aquarius: 300-330°)
    11 = Panguni (Meena/Pisces: 330-360°)
    """
    # Get Lahiri Ayanamsa for the given date
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Convert tropical to sidereal longitude
    sidereal_sun = (sun_long - ayanamsa) % 360

    # Calculate month number based on sidereal position
    month_num = int(sidereal_sun / 30)

    return TAMIL_MONTHS[month_num], sidereal_sun

def get_gowri_panchangam(sunrise_jd, sunset_jd, next_sunrise_jd, weekday, timezone):
    """
    Calculate Gowri Panchangam - divides day and night into 8 equal parts
    Returns both day and night Gowri periods with their timings
    """
    # Calculate day duration (sunrise to sunset)
    day_duration_hours = (sunset_jd - sunrise_jd) * 24
    day_part_duration = day_duration_hours / 8  # Each part in hours

    # Calculate night duration (sunset to next sunrise)
    night_duration_hours = (next_sunrise_jd - sunset_jd) * 24
    night_part_duration = night_duration_hours / 8

    # Get the sequence for this weekday
    day_sequence = GOWRI_DAY_SEQUENCE[weekday]
    night_sequence = GOWRI_NIGHT_SEQUENCE[weekday]

    # Calculate day Gowri timings
    day_gowri = []
    for i, name in enumerate(day_sequence):
        start_jd = sunrise_jd + (i * day_part_duration / 24)
        end_jd = sunrise_jd + ((i + 1) * day_part_duration / 24)

        day_gowri.append({
            "name": name,
            "type": "auspicious" if name in AUSPICIOUS_GOWRI else "inauspicious",
            "start": jd_to_datetime(start_jd, timezone),
            "end": jd_to_datetime(end_jd, timezone)
        })

    # Calculate night Gowri timings
    night_gowri = []
    for i, name in enumerate(night_sequence):
        start_jd = sunset_jd + (i * night_part_duration / 24)
        end_jd = sunset_jd + ((i + 1) * night_part_duration / 24)

        # Check if times are on next day
        start_time = jd_to_datetime(start_jd, timezone)
        end_time = jd_to_datetime(end_jd, timezone)
        start_is_next_day = start_jd >= (sunrise_jd + 1.0)
        end_is_next_day = end_jd >= (sunrise_jd + 1.0)

        night_gowri.append({
            "name": name,
            "type": "auspicious" if name in AUSPICIOUS_GOWRI else "inauspicious",
            "start": start_time + (" (next day)" if start_is_next_day else ""),
            "end": end_time + (" (next day)" if end_is_next_day else "")
        })

    return {
        "day": day_gowri,
        "night": night_gowri
    }

def get_nalla_neram(gowri_panchangam):
    """
    Extract Nalla Neram (auspicious times) from Gowri Panchangam
    Returns only the auspicious periods (Amridha, Uthi, Labam, Sugam, Dhanam)
    """
    day_nalla_neram = [
        period for period in gowri_panchangam["day"]
        if period["type"] == "auspicious"
    ]

    night_nalla_neram = [
        period for period in gowri_panchangam["night"]
        if period["type"] == "auspicious"
    ]

    return {
        "day": day_nalla_neram,
        "night": night_nalla_neram
    }

def get_hora(sunrise_jd, sunset_jd, next_sunrise_jd, weekday, timezone):
    """
    Calculate Hora (planetary hours) for the day.
    Day is divided into 12 horas from sunrise to sunset.
    Night is divided into 12 horas from sunset to next sunrise.
    Each day starts with the ruling planet in Chaldean order.

    Chaldean order: Sun, Venus, Mercury, Moon, Saturn, Jupiter, Mars (repeating)
    """
    # Calculate day duration and hora duration
    day_duration_hours = (sunset_jd - sunrise_jd) * 24
    day_hora_duration = day_duration_hours / 12  # Each hora in hours

    # Calculate night duration and hora duration
    night_duration_hours = (next_sunrise_jd - sunset_jd) * 24
    night_hora_duration = night_duration_hours / 12

    # Get starting planet index for this weekday
    start_planet_idx = HORA_DAY_RULERS[weekday]

    # Calculate day horas (12 horas from sunrise to sunset)
    day_horas = []
    for i in range(12):
        planet_idx = (start_planet_idx + i) % 7
        start_jd = sunrise_jd + (i * day_hora_duration / 24)
        end_jd = sunrise_jd + ((i + 1) * day_hora_duration / 24)

        day_horas.append({
            "hora_number": i + 1,
            "planet": PLANETS_HORA[planet_idx],
            "start": jd_to_datetime(start_jd, timezone),
            "end": jd_to_datetime(end_jd, timezone)
        })

    # Calculate night horas (12 horas from sunset to next sunrise)
    # Continue the sequence from where day ended
    night_horas = []
    for i in range(12):
        planet_idx = (start_planet_idx + 12 + i) % 7
        start_jd = sunset_jd + (i * night_hora_duration / 24)
        end_jd = sunset_jd + ((i + 1) * night_hora_duration / 24)

        # Check if times are on next day
        start_time = jd_to_datetime(start_jd, timezone)
        end_time = jd_to_datetime(end_jd, timezone)
        start_is_next_day = start_jd >= (sunrise_jd + 1.0)
        end_is_next_day = end_jd >= (sunrise_jd + 1.0)

        night_horas.append({
            "hora_number": i + 13,  # Continue numbering from 13-24
            "planet": PLANETS_HORA[planet_idx],
            "start": start_time + (" (next day)" if start_is_next_day else ""),
            "end": end_time + (" (next day)" if end_is_next_day else "")
        })

    return {
        "day": day_horas,
        "night": night_horas
    }

def get_nokku_naal(nakshatra_name):
    """
    Determine the Nokku Naal classification for the given nakshatra.

    Classifications:
    - Mel Nokku Naal (Upward looking): Good for construction, worship, upward activities
    - Keezh Nokku Naal (Downward looking): Good for digging, mining, laying foundations
    - Sama Nokku Naal (Forward/Side looking): Good for travel, vehicles, horizontal activities

    Returns the classification and its meaning/usage.
    """
    if nakshatra_name in MEL_NOKKU_NAKSHATRAS:
        return {
            "classification": "Mel Nokku Naal",
            "tamil": "மேல் நோக்கு நாள்",
            "direction": "Upward Looking",
            "suitable_for": "Construction, building upper floors, worship, coronation, planting trees, horticulture, religious ceremonies"
        }
    elif nakshatra_name in KEEZH_NOKKU_NAKSHATRAS:
        return {
            "classification": "Keezh Nokku Naal",
            "tamil": "கீழ் நோக்கு நாள்",
            "direction": "Downward Looking",
            "suitable_for": "Digging wells, laying foundations, mining, underground work, sowing seeds (especially root vegetables)"
        }
    elif nakshatra_name in SAMA_NOKKU_NAKSHATRAS:
        return {
            "classification": "Sama Nokku Naal",
            "tamil": "சம நோக்கு நாள்",
            "direction": "Forward/Side Looking",
            "suitable_for": "Travel, starting journeys, buying vehicles, landscaping, gardening, horizontal activities"
        }
    else:
        return {
            "classification": "Unknown",
            "tamil": "தெரியாத",
            "direction": "Not Classified",
            "suitable_for": "Classification not available for this nakshatra"
        }

def get_ayana(sun_sidereal_longitude):
    """
    Determine Ayana (solar movement) based on sun's sidereal position.

    Uttarayana: Sun moving northward (Makara to Mithuna)
    Dakshinayana: Sun moving southward (Kataka to Dhanus)

    Args:
        sun_sidereal_longitude: Sun's sidereal longitude in degrees

    Returns:
        Dictionary with ayana name and description
    """
    # Uttarayana starts when sun enters Makara (Capricorn) = 270-360 and 0-90 degrees
    # Dakshinayana starts when sun enters Kataka (Cancer) = 90-270 degrees

    if (sun_sidereal_longitude >= 270) or (sun_sidereal_longitude < 90):
        return {
            "name": "Uttarayana",
            "description": "Sun's northward journey (Winter Solstice to Summer Solstice)",
            "significance": "Auspicious period for spiritual practices and positive endeavors"
        }
    else:
        return {
            "name": "Dakshinayana",
            "description": "Sun's southward journey (Summer Solstice to Winter Solstice)",
            "significance": "Period associated with introspection and ancestral worship"
        }

def get_location_name(latitude, longitude):
    """
    Get approximate location name from coordinates.
    For now, returns formatted coordinates. Can be enhanced with reverse geocoding.

    Args:
        latitude: Latitude in degrees
        longitude: Longitude in degrees

    Returns:
        Formatted location string
    """
    lat_dir = "N" if latitude >= 0 else "S"
    lon_dir = "E" if longitude >= 0 else "W"
    return f"{abs(latitude):.4f}°{lat_dir}, {abs(longitude):.4f}°{lon_dir}"

def get_amirthathi_yoga(weekday, nakshatra_number):
    """
    Calculate Amirthathi Yoga based on weekday and nakshatra combination.
    This is a system of 27 yogas that cycle based on the weekday and nakshatra.

    Formula: (weekday + nakshatra - 1) % 27

    Args:
        weekday: Weekday (0=Sunday, 1=Monday, ..., 6=Saturday)
        nakshatra_number: Nakshatra number (1-27)

    Returns:
        Dictionary with yoga name and characteristics
    """
    # Calculate Amirthathi Yoga index
    yoga_index = (weekday + nakshatra_number - 1) % 27
    yoga_name = AMIRTHATHI_YOGAS[yoga_index]

    # Classify as auspicious or inauspicious
    auspicious_yogas = ["Amirtha", "Siddha", "Uttama", "Sobhana", "Dhana", "Vradhi",
                        "Sowmya", "Siddhi", "Siva", "Sadhya", "Brahma", "Indra"]
    inauspicious_yogas = ["Marana", "Arishta", "Atiganda", "Kalana", "Mudgara", "Kala",
                          "Vyatipata", "Parigha", "Vaidhriti"]

    if yoga_name in auspicious_yogas:
        yoga_type = "Auspicious"
    elif yoga_name in inauspicious_yogas:
        yoga_type = "Inauspicious"
    else:
        yoga_type = "Neutral"

    return {
        "number": yoga_index + 1,
        "name": yoga_name,
        "type": yoga_type
    }

def get_special_yoga(weekday, nakshatra_number):
    """
    Calculate special yoga (Amrita, Siddha, Marana) based on weekday and nakshatra combination.
    These are different from the standard 27 yogas and are based on fixed weekday-nakshatra combinations.

    Args:
        weekday: Weekday (0=Sunday, 1=Monday, ..., 6=Saturday)
        nakshatra_number: Nakshatra number (1-27)

    Returns:
        Dictionary with yoga name, type, and Tamil name
    """
    # Convert nakshatra number to index (0-26)
    nak_index = nakshatra_number - 1

    # Get the yoga type from the mapping
    yoga_type = SPECIAL_YOGAS[weekday].get(nak_index, "Unknown")

    # Tamil names for special yogas
    tamil_names = {
        "Amrita": "அமிர்தம்",
        "Siddha": "சித்தம்",
        "Marana": "மரணம்"
    }

    # Yoga characteristics
    characteristics = {
        "Amrita": {
            "type": "Highly Auspicious",
            "description": "Nectar-like yoga, excellent for all auspicious activities, marriages, housewarming, starting new ventures",
            "color": "green"
        },
        "Siddha": {
            "type": "Auspicious",
            "description": "Success-oriented yoga, good for important work, business deals, spiritual practices",
            "color": "blue"
        },
        "Marana": {
            "type": "Inauspicious",
            "description": "Death-like yoga, avoid starting new ventures, marriages, important decisions",
            "color": "red"
        }
    }

    return {
        "name": yoga_type,
        "tamil": tamil_names.get(yoga_type, "தெரியாத"),
        "type": characteristics.get(yoga_type, {}).get("type", "Unknown"),
        "description": characteristics.get(yoga_type, {}).get("description", "No description available"),
        "color": characteristics.get(yoga_type, {}).get("color", "gray")
    }

def get_chandrashtamam(moon_rasi_index, moon_nakshatra_index, moon_nakshatra_name):
    """
    Calculate Chandrashtamam - the 8th nakshatra and rasi from the current Moon position.
    Chandrashtamam is considered inauspicious for starting new activities.

    In Tamil astrology:
    - 8th rasi from current Moon rasi: (current_rasi + 7) % 12
    - 8th nakshatra from current Moon nakshatra: (current_nakshatra + 7) % 27

    Args:
        moon_rasi_index: Current Moon's rasi index (0-11)
        moon_nakshatra_index: Current Moon's nakshatra index (0-26)
        moon_nakshatra_name: Current Moon's nakshatra name

    Returns:
        Dictionary with Chandrashtamam rasi and nakshatra information
    """
    rasi_names = [
        "Mesha", "Vrishabha", "Mithuna", "Kataka", "Simha", "Kanya",
        "Tula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
    ]

    rasi_tamil_names = [
        "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
        "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
    ]

    # Calculate 8th house from current Moon rasi (count 8 from current = add 7)
    chandrashtamam_rasi_index = (moon_rasi_index + 7) % 12

    # Calculate 8th nakshatra from current Moon nakshatra
    chandrashtamam_nakshatra_index = (moon_nakshatra_index + 7) % 27

    return {
        "current_moon": {
            "rasi": {
                "name": rasi_names[moon_rasi_index],
                "tamil": rasi_tamil_names[moon_rasi_index],
                "number": moon_rasi_index + 1
            },
            "nakshatra": {
                "name": moon_nakshatra_name,
                "tamil": NAKSHATRAS_TAMIL[moon_nakshatra_index],
                "number": moon_nakshatra_index + 1
            }
        },
        "chandrashtamam": {
            "rasi": {
                "name": rasi_names[chandrashtamam_rasi_index],
                "tamil": rasi_tamil_names[chandrashtamam_rasi_index],
                "number": chandrashtamam_rasi_index + 1
            },
            "nakshatra": {
                "name": NAKSHATRAS_TAMIL[chandrashtamam_nakshatra_index],
                "number": chandrashtamam_nakshatra_index + 1
            }
        },
        "description": "People born with Moon in {} rasi or {} nakshatra are experiencing Chandrashtamam today. This is an inauspicious period lasting approximately 2.25 days.".format(
            rasi_names[chandrashtamam_rasi_index],
            NAKSHATRAS_TAMIL[chandrashtamam_nakshatra_index]
        ),
        "advice": "If your birth Moon (Janma Rasi) is {} or birth nakshatra is {}, avoid important activities, new ventures, travel, and major decisions during this period.".format(
            rasi_names[chandrashtamam_rasi_index],
            NAKSHATRAS_TAMIL[chandrashtamam_nakshatra_index]
        )
    }

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

        # Get next day's sunrise for night Gowri calculations
        next_day_jd = julian_day(dt.year, dt.month, dt.day + 1, 6, 0, 0)
        next_sunrise_jd, _ = get_sunrise_sunset(
            next_day_jd, request.latitude, request.longitude
        )

        # Use sunrise JD for calculations (Tamil day starts at sunrise)
        # Get sidereal positions for accurate Tamil panchang
        sun_long, moon_long, ayanamsa = get_sun_moon_positions(sunrise_jd)

        # Calculate panchang elements (now using sidereal longitudes)
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
        dhurmuhurtham = get_dhurmuhurtham(
            sunrise_jd, sunset_jd, weekday_sunday_start, request.timezone
        )

        # Calculate Gowri Panchangam and Nalla Neram
        gowri_panchangam = get_gowri_panchangam(
            sunrise_jd, sunset_jd, next_sunrise_jd, weekday_sunday_start, request.timezone
        )
        nalla_neram = get_nalla_neram(gowri_panchangam)

        # Calculate Hora (planetary hours)
        hora = get_hora(
            sunrise_jd, sunset_jd, next_sunrise_jd, weekday_sunday_start, request.timezone
        )

        # Get Nokku Naal classification based on nakshatra
        nokku_naal = get_nokku_naal(nakshatra["name"])

        # Get Amirthathi Yoga based on weekday and nakshatra
        amirthathi_yoga = get_amirthathi_yoga(weekday_sunday_start, nakshatra["number"])

        # Get special yoga (Amrita/Siddha/Marana) based on weekday and nakshatra
        special_yoga = get_special_yoga(weekday_sunday_start, nakshatra["number"])

        # Get Tamil month (sun_long is already sidereal from get_sun_moon_positions)
        # Calculate month based on sidereal sun position
        month_num = int(sun_long / 30)
        tamil_month = TAMIL_MONTHS[month_num]

        # Get Rutu (season) based on Tamil month
        rutu = RUTU_NAMES.get(tamil_month, "Unknown")

        # Get Ayana (Uttarayana/Dakshinayana) based on sun position
        ayana = get_ayana(sun_long)

        # Get location name from coordinates
        location_name = get_location_name(request.latitude, request.longitude)

        # Calculate rasi from sidereal moon position (already sidereal)
        moon_rasi_index = int(moon_long / 30)

        # Calculate Chandrashtamam (includes both rasi and nakshatra)
        chandrashtamam = get_chandrashtamam(
            moon_rasi_index,
            nakshatra["number"] - 1,  # Convert to 0-based index
            nakshatra["name"]
        )

        # Calculate all transitions for the Tamil day (sunrise to next sunrise)
        # Tamil panchang day starts at sunrise, not midnight
        # Get all tithi, nakshatra, and yoga transitions from sunrise to next sunrise
        tithi_list = get_tithi_transitions(sunrise_jd, next_sunrise_jd, request.timezone, request.date)
        nakshatra_list = get_nakshatra_transitions(sunrise_jd, next_sunrise_jd, request.timezone, request.date)
        yoga_list = get_yoga_transitions(sunrise_jd, next_sunrise_jd, request.timezone, request.date)

        return {
            "date": request.date,
            "location": {
                "name": location_name,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "timezone": request.timezone
            },
            "tamil_month": tamil_month,
            "rutu": rutu,
            "ayana": ayana,
            "weekday": {
                "english": dt.strftime("%A"),
                "tamil": WEEKDAYS_TAMIL[weekday_sunday_start]
            },
            "sunrise": jd_to_datetime(sunrise_jd, request.timezone),
            "sunset": jd_to_datetime(sunset_jd, request.timezone),
            "tithi": tithi,
            "tithi_list": tithi_list,
            "nakshatra": nakshatra,
            "nakshatra_list": nakshatra_list,
            "naama_yoga": yoga,
            "naama_yoga_list": yoga_list,
            "amirthathi_yoga": amirthathi_yoga,
            "karana": karana,
            "lagnam": {
                "sidereal_longitude": round(sun_long, 2),
                "rasi": ["Mesha", "Vrishabha", "Mithuna", "Kataka", "Simha", "Kanya",
                        "Tula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"][int(sun_long/30)]
            },
            "moon_sign": {
                "sidereal_longitude": round(moon_long, 2),
                "rasi": ["Mesha", "Vrishabha", "Mithuna", "Kataka", "Simha", "Kanya",
                        "Tula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"][int(moon_long/30)]
            },
            "inauspicious_timings": {
                "rahu_kalam": rahu_kalam,
                "yamagandam": yamagandam,
                "gulikai_kalam": gulikai,
                "dhurmuhurtham": dhurmuhurtham
            },
            "gowri_panchangam": gowri_panchangam,
            "nalla_neram": nalla_neram,
            "hora": hora,
            "naal": nokku_naal,
            "special_yoga": special_yoga,
            "chandrashtamam": chandrashtamam
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

    return get_panchang(request)

# --- MCP Server Integration ---

mcp_server = Server("tamil-panchang")

def format_panchang_response(data: dict) -> str:
    """Format the panchang JSON response into readable text for AI agents."""
    lines = []
    if "date" in data:
        lines.append(f"📅 Date: {data['date']}")
    if "location" in data:
        loc = data["location"]
        lines.append(f"📍 Location: {loc.get('latitude')}°N, {loc.get('longitude')}°E (Timezone: UTC+{loc.get('timezone')})")
    
    lines.append("")
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
    lines.append("☀️ Sun Timings:")
    if "sunrise" in data:
        lines.append(f"  Sunrise: {data['sunrise']}")
    if "sunset" in data:
        lines.append(f"  Sunset: {data['sunset']}")

    lines.append("")
    lines.append("⚠️ Inauspicious Timings (Avoid for important activities):")
    if "rahu_kalam" in data:
        lines.append(f"  Rahu Kalam: {data['rahu_kalam']}")
    if "yamagandam" in data:
        lines.append(f"  Yamagandam: {data['yamagandam']}")
    if "gulikai_kalam" in data:
        lines.append(f"  Gulikai Kalam: {data['gulikai_kalam']}")

    lines.append("")
    lines.append("---")
    lines.append("Raw JSON data (for detailed analysis):")
    lines.append(json.dumps(data, indent=2, ensure_ascii=False))

    return "\n".join(lines)

@mcp_server.list_tools()
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

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool invocations."""
    try:
        if name == "get_panchang":
            req = PanchangRequest(
                date=arguments.get("date"),
                latitude=arguments.get("latitude"),
                longitude=arguments.get("longitude"),
                timezone=arguments.get("timezone", 5.5)
            )
            result = get_panchang(req)
            return [TextContent(
                type="text",
                text=f"Tamil Panchang for {arguments.get('date')}:\n\n{format_panchang_response(result)}"
            )]

        elif name == "get_today_panchang":
            today = date.today().strftime("%Y-%m-%d")
            req = PanchangRequest(
                date=today,
                latitude=arguments.get("latitude"),
                longitude=arguments.get("longitude"),
                timezone=arguments.get("timezone", 5.5)
            )
            result = get_panchang(req)
            return [TextContent(
                type="text",
                text=f"Today's Tamil Panchang:\n\n{format_panchang_response(result)}"
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error processing request: {str(e)}"
        )]

# SSE Transport for MCP
sse = SseServerTransport("/mcp/messages/")

@app.api_route("/mcp/sse", methods=["GET", "POST"])
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

app.mount("/mcp/messages/", sse.handle_post_message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
