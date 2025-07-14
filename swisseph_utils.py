import swisseph as swe
from datetime import datetime

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

def get_rashi(lon):
    return RASHIS[int(lon // 30) % 12]

def get_nakshatra(moon_lon):
    return NAKSHATRAS[int(moon_lon / (360 / 27)) % 27]

def get_planet_data(birth_date, birth_time):
    dt_str = f"{birth_date} {birth_time}"
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

    swe.set_ephe_path(".")

    grahas = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE,
        "Ketu": swe.TRUE_NODE
    }

    positions = {}
    for name, pid in grahas.items():
        lon, _ = swe.calc_ut(jd, pid)
        deg = round(lon[0], 2)
        positions[name] = {
            "degree": deg,
            "rashi": get_rashi(deg)
        }

    # Lagna calculation (Kathmandu fixed for now)
    lat, lon = 27.7, 85.3
    ayanamsa = swe.get_ayanamsa(jd)
    asc_lon = swe.ascendant(jd, lat, lon, 0)[0] - ayanamsa
    if asc_lon < 0: asc_lon += 360.0

    positions["Lagna"] = {
        "degree": round(asc_lon, 2),
        "rashi": get_rashi(asc_lon)
    }

    moon_deg = positions["Moon"]["degree"]
    moon_nakshatra = get_nakshatra(moon_deg)

    return {
        "grahas": positions,
        "moon_nakshatra": moon_nakshatra,
        "lagna": positions["Lagna"]
}
