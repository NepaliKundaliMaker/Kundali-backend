import swisseph as swe
from datetime import datetime, timedelta
from dateutil import parser

# Rashi & Nakshatra data
RASHIS = [
    "मेष", "वृष", "मिथुन", "कर्कट", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"
]

NAKSHATRAS = [
    "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा",
    "पुनर्वसु", "पुष्य", "आश्लेषा", "मघा", "पूर्वाफाल्गुनी", "उत्तराफाल्गुनी",
    "हस्त", "चित्रा", "स्वाति", "विशाखा", "अनुराधा", "ज्येष्ठा",
    "मूल", "पूर्वाषाढा", "उत्तराषाढा", "श्रवण", "धनिष्ठा", "शतभिषा",
    "पूर्वाभाद्रपदा", "उत्तराभाद्रपदा", "रेवती"
]

# Nakshatra Pada (1-4) durations and deity/lord mappings
PADA_SIZE = 360.0 / 27.0 / 4.0  # 3°20' / 4
NAK_DEITIES = {
    # sample, fill with accurate Vedic info
    "अश्विनी": ("अश्विनीकुमार", "राहु"),
    "भरणी": ("यम", "शुक्र"),
    # … all 27 …
}
NAK_LORDS = {
    # sample, fill with accurate planetary rulers
    "अश्विनी": "केतु",
    "भरणी": "शुक्र",
    # … all 27 …
}

# Vimshottari Dasha sequence (years)
DASHA_SEQUENCE = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6),
    ("Moon", 10), ("Mars", 7), ("Rahu", 18),
    ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)
]

def get_rashi(lon):
    return RASHIS[int(lon // 30) % 12]

def get_nakshatra_and_pada(moon_lon):
    nak_index = int(moon_lon / (360 / 27)) % 27
    nak_name = NAKSHATRAS[nak_index]
    pos_in_nak = moon_lon % (360 / 27)
    pada = int(pos_in_nak // PADA_SIZE) + 1
    deity, _ = NAK_DEITIES.get(nak_name, ("", ""))
    _, lord = NAK_LORDS.get(nak_name, ("", ""))
    return nak_name, pada, deity, lord

def jd_to_datetime(jd):
    # Julian day to Python datetime (UTC)
    unix_time = (jd - 2440587.5) * 86400.0
    return datetime.utcfromtimestamp(unix_time)

def get_vimshottari_dasha(jd, moon_lon):
    # Calculate fraction into the current Nakshatra
    nak_length = 360 / 27
    pos_in_nak = moon_lon % nak_length
    frac = pos_in_nak / nak_length

    # Find starting Dasha index
    nak_index = int(moon_lon / nak_length) % 27
    # Each Nakshatra maps to a starting Dasha in sequence:
    start_index = nak_index % len(DASHA_SEQUENCE)

    periods = []
    current_jd = jd
    # Initial Mahadasha remaining
    name, full_years = DASHA_SEQUENCE[start_index]
    rem_years = full_years * (1 - frac)
    end_jd = current_jd + rem_years * 365.25
    periods.append({
        "name": name,
        "start": jd_to_datetime(current_jd).isoformat(),
        "end": jd_to_datetime(end_jd).isoformat()
    })
    current_jd = end_jd

    # Next 4 Dashas
    idx = (start_index + 1) % len(DASHA_SEQUENCE)
    for _ in range(4):
        name, yrs = DASHA_SEQUENCE[idx]
        end_jd = current_jd + yrs * 365.25
        periods.append({
            "name": name,
            "start": jd_to_datetime(current_jd).isoformat(),
            "end": jd_to_datetime(end_jd).isoformat()
        })
        current_jd = end_jd
        idx = (idx + 1) % len(DASHA_SEQUENCE)

    return periods

def get_divisional_navamsa(lon):
    # Navamsa = 1/9th division of a sign (30°/9 = 3°20')
    sign_index = int(lon // 30) % 12
    offset = lon % 30
    part = int(offset // (30 / 9))
    nav_rashi = RASHIS[(sign_index + part) % 12]
    return nav_rashi

def get_planet_data(birth_dt, birth_loc, test_mode=False):
    # Parse datetime
    if isinstance(birth_dt, str):
        dt = parser.parse(birth_dt)
    else:
        dt = birth_dt
    # Compute Julian day
    jd = swe.julday(dt.year, dt.month, dt.day,
                    dt.hour + dt.minute / 60.0)
    swe.set_ephe_path(".")

    # Graha IDs
    grahas = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE, "Ketu": swe.TRUE_NODE
    }

    positions = {}
    for name, pid in grahas.items():
        lon, _ = swe.calc_ut(jd, pid)
        deg = round(lon[0], 2)
        positions[name] = {
            "degree": deg,
            "rashi": get_rashi(deg),
            "navamsa": get_divisional_navamsa(deg)
        }

    # Ascendant (Lagna)
    lat, lon = birth_loc
    ayanamsa = swe.get_ayanamsa(jd)
    asc_lon = swe.ascendant(jd, lat, lon, 0)[0] - ayanamsa
    asc_lon %= 360.0
    positions["Lagna"] = {
        "degree": round(asc_lon, 2),
        "rashi": get_rashi(asc_lon),
        "navamsa": get_divisional_navamsa(asc_lon)
    }

    # Moon Nakshatra + Pada + Deity + Lord
    moon_lon = positions["Moon"]["degree"]
    nak_name, pada, deity, lord = get_nakshatra_and_pada(moon_lon)

    # Vimshottari Dasha periods
    dasha = get_vimshottari_dasha(jd, moon_lon)

    return {
        "grahas": positions,
        "moon_nakshatra": nak_name,
        "moon_pada": pada,
        "nakshatra_deity": deity,
        "nakshatra_lord": lord,
        "dasha": dasha
    }