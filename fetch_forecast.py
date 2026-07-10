import hashlib
import json
import pathlib
import requests
from datetime import datetime, timezone

LAT, LON = 45.7347, 4.8334
TIMEZONE  = "Europe/Paris"
MODEL     = "meteofrance_seamless"


def forecast_hash(hourly: dict) -> str:
    """Hash rapide sur les 48 premières valeurs de température."""
    key = str(hourly["temperature_2m"][:48])
    return hashlib.md5(key.encode()).hexdigest()


def last_saved_hash(data_dir: pathlib.Path) -> str | None:
    files = sorted(data_dir.glob("forecast_*.json"))
    if not files:
        return None
    with open(files[-1]) as f:
        saved = json.load(f)
    return saved.get("forecast_hash")


def fetch():
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude":      LAT,
        "longitude":     LON,
        "hourly":        ["temperature_2m", "precipitation",
                          "wind_speed_10m", "shortwave_radiation"],
        "models":        MODEL,
        "forecast_days": 7,
        "timezone":      TIMEZONE,
    }, timeout=30)
    r.raise_for_status()
    data = r.json()

    h = forecast_hash(data["hourly"])
    data_dir = pathlib.Path("data")
    data_dir.mkdir(exist_ok=True)

    if h == last_saved_hash(data_dir):
        print("Pas de changement depuis le dernier snapshot — rien sauvegardé.")
        return

    now = datetime.now(timezone.utc)
    snapshot = {
        "fetched_at_utc": now.isoformat(),
        "forecast_hash":  h,
        "model":          MODEL,
        "latitude":       data["latitude"],
        "longitude":      data["longitude"],
        "hourly_units":   data["hourly_units"],
        "hourly":         data["hourly"],
    }
    fname = data_dir / f"forecast_{now.strftime('%Y%m%d_%H%M')}_utc.json"
    with open(fname, "w") as f:
        json.dump(snapshot, f)
    print(f"Nouveau run detecte — sauvegarde : {fname}")


if __name__ == "__main__":
    fetch()
