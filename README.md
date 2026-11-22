# Malaysia Solar Project Finance Model

**Live app:** https://rohan-solar-pf.streamlit.app

**Code:** https://github.com/rohanr-w/solar-pf

A Python model of how a lender sizes debt for a utility-scale solar farm in Malaysia,
using real historical sunlight data and public assumptions, with an interactive app.

**Question it answers:** for a hypothetical 50 MWp solar farm in Kedah on a 25-year PPA,
how much can a bank safely lend, and how sensitive is that to a bad sunlight year?

> All data is public (NASA POWER sunlight data, Energy Commission LSS tariffs,
> recent LSS EPCC contract values). The project is hypothetical and not based on
> any real company or bank data.

## Results (base case)

| | Value |
|---|---|
| Capex | RM115.0m (RM2.3m per MWp) |
| Tariff | RM152/MWh (LSS5+ average, Energy Commission, Nov 2025) |
| Year 1 CFADS | RM8.0m |
| Debt (1.30x DSCR, 18 years, 5.5%) | RM64.9m |
| Gearing | 56% |

### Sensitivities (one change at a time)

| Change | Debt | Gearing |
|---|---|---|
| Tenor 18 → 20 years | RM68.5m | 60% |
| DSCR 1.30x → 1.20x | RM70.3m | 61% |
| Interest 5.5% → 4.5% | RM70.0m | 61% |
| All three together | RM80.6m | 70% |
| Energy at 90% of expected | RM58.1m | 51% |

### Key findings
- **Banks lend against cash flow, not cost.** Updating capex and tariff to 2025–26 Malaysian levels barely changed gearing (57% → 56%), because both fell by about 24%.
- **DSCR is the biggest lender lever.** 1.30x → 1.20x raised debt by 8.3%, more than adding two years of tenor.
- **Fixed costs amplify bad years.** A 10% drop in energy cut debt by about 10.5%, which is why lenders size on P90 rather than P50.

## Interactive app

```bash
streamlit run app.py
```

Move the sliders (tariff, capex, energy output, DSCR, tenor, interest rate) to see
debt capacity, gearing and the debt schedule update live.

## Structure

```
solar-pf/
├── app.py                    # interactive Streamlit app            ✅
├── src/
│   ├── config.py             # all assumptions in one place
│   ├── fetch_irradiance.py   # Step 1: pull NASA sunlight data      ✅
│   ├── energy_yield.py       # Step 2: sunlight → MWh               ✅
│   ├── cashflows.py          # Step 3: revenue, opex, tax, CFADS    ✅
│   ├── debt_sizing.py        # Step 4: size debt on DSCR            ✅
│   ├── charts.py             # charts of cash flows                 ✅
│   └── monte_carlo.py        # Step 5: P50 / P90 risk (planned)     ⬜
├── data/raw/                 # downloaded data (not edited by hand)
├── data/processed/           # cleaned data
└── outputs/                  # charts and result tables
```

## Setup

```bash
pip install -r requirements.txt
python src/fetch_irradiance.py
python src/energy_yield.py
python src/cashflows.py
python src/debt_sizing.py
streamlit run app.py
```

## Roadmap

| Stage | Goal | Key concept | Status |
|---|---|---|---|
| 1 | Sunlight data → yearly energy output | Irradiance, performance ratio, degradation | ✅ |
| 2 | 25-year cash flows | Tariff, opex, tax, CFADS | ✅ |
| 3 | Debt sizing + sensitivities + app | DSCR, sculpted repayments, gearing | ✅ |
| 4 | P90 risk, write-up | P50 vs P90, findings and limitations | ⬜ |

## Assumptions and limitations
- Hypothetical project; all inputs are public benchmarks.
- Capex: recent LSS5/LSS5+ EPCC contracts (~RM1.5–1.8m per MWp) plus ~25% for grid, development, contingency and financing. Converted from MWac at an assumed 1.4 DC/AC ratio.
- Tax ignores the interest deduction, so CFADS is slightly conservative.
- No construction period or reserve accounts yet; P90 is tested with the energy slider, not a full statistical model.

## Glossary

- **GHI**: sunlight energy hitting the ground (kWh/m²)
- **Performance ratio**: share of theoretical output the plant actually delivers
- **CFADS**: cash flow available for debt service
- **DSCR**: CFADS ÷ debt repayments due. Lenders want a buffer, e.g. 1.3x
- **Gearing**: share of the project funded by debt (debt ÷ capex)
- **Sculpted repayments**: debt payments set each year so CFADS ÷ debt service equals the target DSCR
- **P50 / P90**: output exceeded in 50% / 90% of years. Lenders size debt on P90