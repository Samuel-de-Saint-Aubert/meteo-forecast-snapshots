import json
import pathlib
import requests
from datetime import datetime, timezone

LAT, LON = 45.7347, 4.8334
TIMEZONE  = "Europe/Paris"
MODEL     = "meteofrance_seamless"


def fetch():
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude":      LAT,
        "longitude":     LON,
        "hourly":        ["temperature_2m", "precipitation", "wind_speed_10m",
                          "shortwave_radiation"],
        "models":        MODEL,
        "forecast_days": 7,
        "timezone":      TIMEZONE,
    }, timeout=30)
    r.raise_for_status()
    data = r.json()

    now      = datetime.now(timezone.utc)
    snapshot = {
        "fetched_at_utc": now.isoformat(),
        "model":          MODEL,
        "latitude":       data["latitude"],
        "longitude":      data["longitude"],
        "hourly_units":   data["hourly_units"],
        "hourly":         data["hourly"],
    }

    pathlib.Path("data").mkdir(exist_ok=True)
    fname = f"data/forecast_{now.strftime('%Y%m%d_%H%M')}_utc.json"
    with open(fname, "w") as f:
        json.dump(snapshot, f)
    print(f"Sauvegardé : {fname} ({len(data['hourly']['time'])} pas de temps)")


if __name__ == "__main__":
    fetch()
