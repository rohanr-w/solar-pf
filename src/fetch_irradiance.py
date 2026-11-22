"""
Step 1: Pull daily sunlight data for the site from NASA POWER.

What it downloads
-----------------
ALLSKY_SFC_SW_DWN = Global Horizontal Irradiance (GHI): the solar energy
hitting a flat square metre of ground, in kWh/m²/day. "All sky" means it
includes cloudy days, which matters a lot in Malaysia.

What it saves
-------------
data/raw/nasa_power_daily.csv            one row per day
data/processed/annual_irradiance.csv     one row per year (total kWh/m²)

Run from the project folder:
    python src/fetch_irradiance.py
"""

import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.append(str(Path(__file__).parent))
import config  # noqa: E402

API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAM = "ALLSKY_SFC_SW_DWN"
MISSING = -999  # NASA's code for "no data"


def fetch_daily(lat: float, lon: float, start_year: int, end_year: int) -> pd.DataFrame:
    """Call the NASA POWER API and return a DataFrame of daily GHI."""
    params = {
        "parameters": PARAM,
        "community": "RE",  # renewable energy community
        "latitude": lat,
        "longitude": lon,
        "start": f"{start_year}0101",
        "end": f"{end_year}1231",
        "format": "JSON",
    }
    response = requests.get(API_URL, params=params, timeout=60)
    response.raise_for_status()
    return parse_response(response.json())


def parse_response(payload: dict) -> pd.DataFrame:
    """Turn NASA's JSON ({"20010101": 4.9, ...}) into a clean table."""
    daily = payload["properties"]["parameter"][PARAM]
    df = pd.DataFrame({"date": list(daily.keys()), "ghi_kwh_m2": list(daily.values())})
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df.loc[df["ghi_kwh_m2"] == MISSING, "ghi_kwh_m2"] = pd.NA
    return df


def to_annual(daily: pd.DataFrame) -> pd.DataFrame:
    """Sum daily GHI into yearly totals, filling any gaps with that year's average day."""
    daily = daily.copy()
    daily["year"] = daily["date"].dt.year
    annual = daily.groupby("year").agg(
        days=("ghi_kwh_m2", "size"),
        missing_days=("ghi_kwh_m2", lambda s: s.isna().sum()),
        mean_daily=("ghi_kwh_m2", "mean"),
    )
    annual["annual_ghi_kwh_m2"] = (annual["mean_daily"] * annual["days"]).round(1)
    return annual.reset_index()


def main() -> None:
    print(f"Fetching {config.START_YEAR}-{config.END_YEAR} sunlight data for {config.SITE_NAME}...")
    daily = fetch_daily(config.LATITUDE, config.LONGITUDE, config.START_YEAR, config.END_YEAR)

    Path(config.RAW_FILE).parent.mkdir(parents=True, exist_ok=True)
    Path(config.ANNUAL_FILE).parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(config.RAW_FILE, index=False)

    annual = to_annual(daily)
    annual.to_csv(config.ANNUAL_FILE, index=False)

    ghi = annual["annual_ghi_kwh_m2"]
    print(f"Saved {len(daily):,} days to {config.RAW_FILE}")
    print(f"Saved {len(annual)} years to {config.ANNUAL_FILE}\n")
    print(annual[["year", "annual_ghi_kwh_m2", "missing_days"]].to_string(index=False))
    print(f"\nAverage year: {ghi.mean():,.0f} kWh/m²   "
          f"Worst: {ghi.min():,.0f}   Best: {ghi.max():,.0f}   "
          f"Year-to-year std dev: {ghi.std():,.0f}")


if __name__ == "__main__":
    main()
