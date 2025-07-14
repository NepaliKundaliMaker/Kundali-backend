# district_coords.py

import os
import json
from geopy.geocoders import Nominatim
from time import sleep

# List of all 77 Nepali districts by name
DISTRICT_LIST = [
    # Koshi (14)
    "Taplejung","Panchthar","Ilam","Jhapa","Morang","Sunsari","Dhankuta",
    "Sankhuwasabha","Solukhumbu","Okhaldhunga","Khotang","Bhojpur",
    "Terhathum","Udayapur",
    # Madhesh (8)
    "Sarlahi","Rautahat","Bara","Parsa","Mahottari","Dhanusha","Siraha","Saptari",
    # Bagmati (13)
    "Kathmandu","Lalitpur","Bhaktapur","Kavrepalanchok","Dhading",
    "Sindhupalchok","Sindhuli","Ramechhap","Dolakha","Nuwakot",
    "Chitwan","Makwanpur","Rasuwa",
    # Gandaki (11)
    "Baglung","Gorkha","Kaski","Lamjung","Manang","Mustang","Myagdi",
    "Nawalpur","Parbat","Syangja","Tanahun",
    # Lumbini (12)
    "Arghakhanchi","Banke","Bardiya","Dang","Gulmi","Kapilvastu",
    "Parasi","Palpa","Pyuthan","Rupandehi","Rolpa","Eastern Rukum",
    # Karnali (10)
    "Dailekh","Dolpa","Humla","Jajarkot","Jumla","Kalikot","Mugu",
    "Salyan","Surkhet","Western Rukum",
    # Sudurpashchim (9)
    "Achham","Bajhang","Bajura","Baitadi","Dadeldhura","Darchula",
    "Doti","Kailali","Kanchanpur"
]

# Cache file path
CACHE_FILE = os.path.join(os.path.dirname(__file__), "district_coords_cache.json")

def _generate_coords():
    geolocator = Nominatim(user_agent="nepal_district_locator")
    coords = {}
    for name in DISTRICT_LIST:
        try:
            loc = geolocator.geocode(f"{name} District, Nepal", timeout=10)
            if loc:
                coords[name] = (round(loc.latitude, 6), round(loc.longitude, 6))
            else:
                coords[name] = (None, None)
        except Exception:
            coords[name] = (None, None)
        # be polite to the geocoding service
        sleep(1)
    # cache to disk
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(coords, f, ensure_ascii=False, indent=2)
    return coords

def _load_coords():
    # if cached, load and return
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # else generate
    return _generate_coords()

# At import, build or load the full dict
DISTRICT_COORDS = _load_coords()

def get_coords(district_name):
    """
    Return (lat, lon) tuple for a given district name.
    Falls back to Kathmandu coords if not found.
    """
    return tuple(DISTRICT_COORDS.get(district_name, DISTRICT_COORDS.get("Kathmandu")))

# Example usage:
# from district_coords import get_coords
# lat, lon = get_coords("Pokhara")