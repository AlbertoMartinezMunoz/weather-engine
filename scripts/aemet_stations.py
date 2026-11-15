#!/usr/bin/env python3
import argparse
import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

import requests

from envconfig.envconfig import EnvConfig

URL = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"


def get_json(url, api_key):
    resp = requests.get(url, headers={"api_key": api_key}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def dms_to_decimal(value):
    """Convert AEMET coordinates like '413300N' or '0044500W' to decimal degrees."""
    hemi, digits = value[-1], value[:-1]
    deg_len = len(digits) - 4  # last 4 digits are minutes and seconds
    deg = int(digits[:deg_len])
    minutes = int(digits[deg_len : deg_len + 2])
    seconds = int(digits[deg_len + 2 :])
    decimal = deg + minutes / 60 + seconds / 3600
    return -decimal if hemi in "SW" else decimal


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def nearest_stations(lat, lon, n, api_key):
    # AEMET answers with a JSON containing the real data URL in "datos"
    meta = get_json(URL, api_key)
    if meta.get("estado") != 200:
        raise RuntimeError(f"AEMET error: {meta}")
    data = get_json(meta["datos"], api_key)

    stations = []
    for s in data:
        try:
            s_lat = dms_to_decimal(s["latitud"])
            s_lon = dms_to_decimal(s["longitud"])
        except (KeyError, ValueError):
            continue
        stations.append(
            {
                "indicativo": s["indicativo"],
                "nombre": s["nombre"],
                "provincia": s.get("provincia"),
                "altitud_m": s.get("altitud"),
                "lat": round(s_lat, 5),
                "lon": round(s_lon, 5),
                "distance_km": round(haversine_km(lat, lon, s_lat, s_lon), 2),
            }
        )

    stations.sort(key=lambda s: s["distance_km"])
    return stations[:n]


def parse_args():
    env = EnvConfig()
    parser = argparse.ArgumentParser(description="Find the n AEMET weather stations closest to a GPS position.")
    parser.add_argument("latitude", type=float, help="latitude in decimal degrees (e.g. 41.6523)")
    parser.add_argument("longitude", type=float, help="longitude in decimal degrees (e.g. -4.7245)")
    parser.add_argument("n", type=int, help="number of stations to return")
    parser.add_argument(
        "--api-key",
        default=env.get("AEMET_API_KEY"),
        help="AEMET OpenData API key (default: AEMET_API_KEY environment variable)",
    )
    args = parser.parse_args()

    if not -90 <= args.latitude <= 90:
        parser.error("latitude must be between -90 and 90")
    if not -180 <= args.longitude <= 180:
        parser.error("longitude must be between -180 and 180")
    if args.n < 1:
        parser.error("n must be at least 1")
    if not args.api_key:
        parser.error("an API key is required (use --api-key or set AEMET_API_KEY)")
    return args


if __name__ == "__main__":
    args = parse_args()
    stations = nearest_stations(args.latitude, args.longitude, args.n, args.api_key)
    for s in stations:
        print(s)
