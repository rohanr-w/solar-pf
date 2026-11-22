"""
Weekend 1: turn sunlight into electricity.

The physics
-----------
Panels are rated under 1 kW/m² of sunlight. So a year with 1,700 kWh/m² of
sunlight is like 1,700 hours at full rating ("peak sun hours").

    Year-1 energy (MWh) = capacity (MWp) × annual GHI (kWh/m²) × performance ratio

Then each later year loses output to degradation:

    Energy in year t = Year-1 energy × (1 - degradation) ** (t - 1)

Sense check: Malaysian solar farms usually produce roughly 1,200 to 1,450 MWh
per MWp per year. If number is far outside that, something is off.

Your tasks
----------
1. Load data/processed/annual_irradiance.csv
2. Calculate the average-year energy output for the 50 MWp plant (the P50 case)
3. Build a 25-year table: year, degradation factor, energy_mwh
4. Save it to outputs/energy_profile.csv
5. Plot energy by year (matplotlib) and save to outputs/energy_profile.png
6. Bonus: what is the energy output in the WORST historical year? That idea
   becomes P90 in Weekend 3.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).parent))
import config  # noqa: E402


def year1_energy_mwh(annual_ghi_kwh_m2: float) -> float:
    return config.CAPACITY_MWP * annual_ghi_kwh_m2 * config.PERFORMANCE_RATIO

def energy_profile(year1_mwh: float) -> pd.DataFrame:
    rows = []
    for year in range(1, config.PPA_YEARS + 1):
        factor = (1 - config.DEGRADATION_PER_YEAR) ** (year - 1)
        energy = year1_mwh * factor
        rows.append({"year": year, "degradation_factor": factor, "energy_mwh": energy})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    annual = pd.read_csv(config.ANNUAL_FILE)
    avg_ghi = annual["annual_ghi_kwh_m2"].mean()
    y1 = year1_energy_mwh(avg_ghi)
    profile = energy_profile(y1)

    Path("outputs").mkdir(exist_ok=True)
    profile.to_csv("outputs/energy_profile.csv", index=False)

    print(f"Average sunlight: {avg_ghi:,.0f} kWh/m²")
    print(f"Year 1 energy: {y1:,.0f} MWh ({y1 / config.CAPACITY_MWP:,.0f} MWh per MWp)")
    print(profile.head())
    print("...")
    print(profile.tail())