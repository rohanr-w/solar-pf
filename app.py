"""
Interactive solar project finance app.

Run from the project folder:
    streamlit run app.py
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
import config  # noqa: E402
from cashflows import build_cashflows  # noqa: E402
from debt_sizing import size_debt  # noqa: E402

st.set_page_config(page_title="Solar Project Finance Model", layout="wide")
st.title("How much can a bank lend to a solar farm?")
st.caption(
    f"Hypothetical {config.CAPACITY_MWP} MWp solar farm in {config.SITE_NAME}, "
    "using 25 years of NASA sunlight data. Move the sliders to see how debt capacity changes."
)

# --- Sliders -------------------------------------------------------------
st.sidebar.header("Project")
tariff = st.sidebar.slider("Tariff (RM/MWh)", 120, 220, int(config.TARIFF_RM_PER_MWH), 2)
capex_m = st.sidebar.slider("Capex (RM m per MWp)", 1.8, 3.2, config.CAPEX_RM_PER_MWP / 1e6, 0.05)
energy_pct = st.sidebar.slider("Energy output (% of expected)", 85, 105, 100, 1,
                               help="Below 100% = a bad sunlight case, like a P90")

st.sidebar.header("Lender")
dscr = st.sidebar.slider("Target DSCR (x)", 1.10, 1.50, config.DSCR_TARGET, 0.05)
tenor = st.sidebar.slider("Loan tenor (years)", 10, config.PPA_YEARS, config.DEBT_TENOR_YEARS, 1)
rate_pct = st.sidebar.slider("Interest rate (%)", 3.0, 8.0, config.INTEREST_RATE * 100, 0.25)

# --- Run the model -------------------------------------------------------
profile = pd.read_csv("outputs/energy_profile.csv")

# build the cash flows using the slider values.
# capex_m is in RM millions, so multiply by 1e6. energy_pct is a %, so divide by 100.
cf = build_cashflows(profile, tariff=tariff, capex_per_mwp=capex_m * 1e6, energy_factor=energy_pct / 100)

# size the debt using the slider values.
debt, loan = size_debt(cf, dscr=dscr, tenor=tenor, rate=rate_pct / 100)

capex = config.CAPACITY_MWP * capex_m * 1e6
gearing = debt / capex

# --- Results -------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Capex", f"RM{capex / 1e6:,.1f}m")
c2.metric("Debt the bank can lend", f"RM{debt / 1e6:,.1f}m")
c3.metric("Gearing (debt / capex)", f"{gearing:.0%}")
c4.metric("Equity needed", f"RM{(capex - debt) / 1e6:,.1f}m")

st.subheader("Cash available vs debt payments (RM m)")
chart = pd.DataFrame({
    "year": cf["year"],
    "CFADS": cf["cfads"] / 1e6,
    "Debt service": pd.Series(loan["debt_service"].values / 1e6, index=loan.index).reindex(cf.index).fillna(0),
}).set_index("year")
st.bar_chart(chart, stack=False)

st.subheader("Loan balance over time (RM m)")
st.line_chart(loan.set_index("year")["closing_balance"] / 1e6)

with st.expander("See the full debt schedule"):
    show = loan[["year", "cfads", "debt_service", "interest", "principal", "closing_balance", "dscr"]].copy()
    for col in ["cfads", "debt_service", "interest", "principal", "closing_balance"]:
        show[col] = (show[col] / 1e6).round(2)
    show["dscr"] = show["dscr"].round(2)
    st.dataframe(show, hide_index=True)

with st.expander("Assumptions behind the model"):
    st.markdown(f"""
**Plant**
- Capacity: {config.CAPACITY_MWP} MWp in {config.SITE_NAME}
- Performance ratio: {config.PERFORMANCE_RATIO:.2f} (heat, inverter, cable and soiling losses)
- Panel degradation: {config.DEGRADATION_PER_YEAR:.1%} a year, so output falls slightly every year
- PPA: {config.PPA_YEARS} years with TNB at a fixed tariff

**Costs and tax**
- Opex: {config.OPEX_PCT_OF_CAPEX:.1%} of capex a year, rising {config.OPEX_INFLATION:.0%} a year
- Corporate tax: {config.TAX_RATE:.0%} (interest deduction ignored, so CFADS is slightly conservative)

**Base case (before sliders)**
- Tariff RM{config.TARIFF_RM_PER_MWH}/MWh · Capex RM{config.CAPEX_RM_PER_MWP / 1e6:.1f}m per MWp
- DSCR {config.DSCR_TARGET:.2f}x · Tenor {config.DEBT_TENOR_YEARS} years · Interest {config.INTEREST_RATE:.1%}

**Not yet modelled:** construction period, reserve accounts, full P90 analysis.
""")
    
st.caption("Hypothetical project using public assumptions (Energy Commission LSS tariffs, recent LSS EPCC contracts). Not investment advice.")