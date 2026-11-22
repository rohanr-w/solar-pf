"""
Project assumptions in one place.

Every number here is a public-source assumption for a HYPOTHETICAL project.
Change them here, not inside the other scripts.
"""

# --- Site ---------------------------------------------------------------
# Default: Gurun, Kedah. Northern Peninsular Malaysia gets some of the
# strongest sunlight in the country, and several LSS projects are in Kedah.
SITE_NAME = "Gurun, Kedah"
LATITUDE = 5.81
LONGITUDE = 100.47

# Years of historical sunlight data to pull (NASA POWER covers 1981 onwards)
START_YEAR = 2001
END_YEAR = 2025

# --- Plant (used from Weekend 1, step 2) ---------------------------------
CAPACITY_MWP = 50            # DC capacity of the hypothetical solar farm
PERFORMANCE_RATIO = 0.77     # share of theoretical output actually delivered, I lowered for tropical heat losses in Malaysia
                             # (heat, inverter, cable and soiling losses)
DEGRADATION_PER_YEAR = 0.005 # panels lose ~0.5% output a year
PPA_YEARS = 25               # LSS PPAs run for 25 years

# --- File paths -----------------------------------------------------------
RAW_FILE = "data/raw/nasa_power_daily.csv"
ANNUAL_FILE = "data/processed/annual_irradiance.csv"


# Turning MWh into CAFDS 

# --- Cash flow assumptions (Weekend 2) ----------------------------------
# Rough public-benchmark assumptions for a hypothetical project; refine later.
# tariff I initially used 200   ~RM0.20/kWh, roughly LSS-level pricing LSS5 was RM0.17/kWh - 27 projects and LSS5+ was RM0.15/kWh - 13 projects
# capex I initially used 3_000_000  build cost per MWp (check against IRENA) 
TARIFF_RM_PER_MWH = 152        # LSS5+ average awarded price, 15.2 sen/kWh (Energy Commission, Nov 2025). Upside case: 170 (LSS5)
CAPEX_RM_PER_MWP = 2_300_000   # Total project cost. EPCC ~RM1.8m/MWp (recent LSS5/LSS5+ awards) + ~25% for grid, development, contingency, financing. Range RM2.0m–2.9m 
OPEX_PCT_OF_CAPEX = 0.015      # yearly O&M, insurance, land as % of capex
OPEX_INFLATION = 0.02          # costs rise 2% a year
TAX_RATE = 0.24                # Malaysian corporate tax rate

# --- Debt assumptions (Weekend 3) ---------------------------------------
DSCR_TARGET = 1.30          # lender wants CFADS to be 1.30x the debt payment each year
DEBT_TENOR_YEARS = 18       # loan repaid over 18 years, shorter than the 25-year PPA
INTEREST_RATE = 0.055       # assumed all-in ringgit project loan rate (benchmark + bank margin)