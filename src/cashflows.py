"""
Step 3: turn energy (MWh) into cash available for debt service (CFADS).
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).parent))
import config  # noqa: E402

CAPEX = config.CAPACITY_MWP * config.CAPEX_RM_PER_MWP
def build_cashflows(
    profile: pd.DataFrame,
    tariff: float = config.TARIFF_RM_PER_MWH,
    capex_per_mwp: float = config.CAPEX_RM_PER_MWP,
    energy_factor: float = 1.0,
) -> pd.DataFrame:
    capex = config.CAPACITY_MWP * capex_per_mwp
    depreciation = capex / config.PPA_YEARS   # straight line over the PPA

    df = profile.copy()
    df["energy_mwh"] = df["energy_mwh"] * energy_factor   # e.g. 0.95 = a bad sunlight case
    df["revenue"] = df["energy_mwh"] * tariff
    df["opex"] = capex * config.OPEX_PCT_OF_CAPEX * (1 + config.OPEX_INFLATION) ** (df["year"] - 1)
    df["ebitda"] = df["revenue"] - df["opex"]
    df["tax"] = (df["ebitda"] - depreciation) * config.TAX_RATE
    df["cfads"] = df["ebitda"] - df["tax"]
    return df