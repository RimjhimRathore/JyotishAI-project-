from datetime import datetime
from zoneinfo import ZoneInfo

import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
]

PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE,
}

# MOSEPH = built-in data (no extra files), SIDEREAL = Vedic zodiac
FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL

_geolocator = Nominatim(user_agent="jyotish-ai-student-project")
_tf = TimezoneFinder()


def geocode(place):
    """'Bhopal, India' -> (latitude, longitude, 'Asia/Kolkata')"""
    loc = _geolocator.geocode(place, timeout=10)
    if loc is None:
        raise ValueError(f"Could not find place: {place}")
    tz = _tf.timezone_at(lat=loc.latitude, lng=loc.longitude)
    return loc.latitude, loc.longitude, tz

def describe(longitude):
    """Turn a 0-360 degree position into sign, degree, nakshatra, pada."""
    longitude %= 360
    sign_idx = int(longitude // 30)              # 12 signs x 30 degrees
    nak_len = 360 / 27                           # 27 nakshatras = 13.33 degrees each
    nak_idx = int(longitude // nak_len)
    pada = int((longitude % nak_len) // (nak_len / 4)) + 1   # 4 padas each
    return {
        "longitude": round(longitude, 4),
        "sign": SIGNS[sign_idx],
        "sign_num": sign_idx + 1,
        "degree": round(longitude % 30, 2),
        "nakshatra": NAKSHATRAS[nak_idx],
        "pada": pada,
    }

def calculate_chart(dob, tob, place):
    """dob='YYYY-MM-DD', tob='HH:MM', place='City, Country'"""
    lat, lon, tz_name = geocode(place)

    # Birth time is LOCAL time. Astronomy needs UTC.
    local = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M").replace(
        tzinfo=ZoneInfo(tz_name))
    utc = local.astimezone(ZoneInfo("UTC"))

    # Julian Day = one number that represents a moment in time
    jd = swe.julday(utc.year, utc.month, utc.day,
                    utc.hour + utc.minute / 60 + utc.second / 3600)

    swe.set_sid_mode(swe.SIDM_LAHIRI)            # Indian standard ayanamsa

    # Lagna depends on exact time AND place
    _, ascmc = swe.houses_ex(jd, lat, lon, b"W", FLAGS)
    lagna = describe(ascmc[0])

    planets = {}
    for name, pid in PLANETS.items():
        pos, _ = swe.calc_ut(jd, pid, FLAGS)     # pos[0]=angle, pos[3]=speed
        info = describe(pos[0])
        info["retrograde"] = pos[3] < 0
        planets[name] = info

    # Ketu is always exactly opposite Rahu
    planets["Ketu"] = describe(planets["Rahu"]["longitude"] + 180)
    planets["Rahu"]["retrograde"] = False
    planets["Ketu"]["retrograde"] = False

    # House 1 = Lagna sign, house 2 = next sign, and so on
    for info in planets.values():
        info["house"] = (info["sign_num"] - lagna["sign_num"]) % 12 + 1

    return {
        "location": {"lat": lat, "lon": lon, "timezone": tz_name},
        "lagna": lagna,
        "planets": planets,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(calculate_chart("2003-08-15", "10:30", "Bhopal, India"), indent=2))