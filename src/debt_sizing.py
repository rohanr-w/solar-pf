"""
Step 4: size the debt. How much can a bank lend against the CFADS?

Sculpted repayments: each year the debt payment is set so that
CFADS / debt service = DSCR_TARGET exactly.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).parent))
import config  # noqa: E402

CAPEX = config.CAPACITY_MWP * config.CAPEX_RM_PER_MWP


def size_debt(
    cf: pd.DataFrame,
    dscr: float = config.DSCR_TARGET,
    tenor: int = config.DEBT_TENOR_YEARS,
    rate: float = config.INTEREST_RATE,
) -> tuple[float, pd.DataFrame]:
    loan = cf[cf["year"] <= tenor].copy()

    # debt service each year = CFADS divided by the target DSCR
    loan["debt_service"] = loan["cfads"] / dscr

    # discount each year's debt service back to today: debt_service / (1 + rate) ** year
    loan["pv_debt_service"] = loan["debt_service"] / (1 + rate) ** loan["year"]

    # The bank can lend the total present value of all the debt service
    debt = loan["pv_debt_service"].sum()

    # Repayment schedule
    balance = debt
    interest, principal, closing = [], [], []
    for ds in loan["debt_service"]:
        # interest this year = opening balance x interest rate
        i = balance * rate
        p = ds - i                     # the rest of the payment repays the loan
        balance = balance - p
        interest.append(i)
        principal.append(p)
        closing.append(balance)
    loan["interest"] = interest
    loan["principal"] = principal
    loan["closing_balance"] = closing
    loan["dscr"] = loan["cfads"] / loan["debt_service"]
    return debt, loan


if __name__ == "__main__":
    cf = pd.read_csv("outputs/cashflows.csv")
    debt, loan = size_debt(cf)
    loan.to_csv("outputs/debt_schedule.csv", index=False)

    rm = lambda x: f"RM{x / 1e6:,.1f}m"
    print(f"Capex: {rm(CAPEX)}")
    print(f"Debt the bank can lend: {rm(debt)}")
    print(f"Gearing (debt / capex): {debt / CAPEX:.0%}")
    print(f"Equity the owners must put in: {rm(CAPEX - debt)}")
    print(f"Closing balance after year {config.DEBT_TENOR_YEARS}: {rm(loan['closing_balance'].iloc[-1])}  (should be ~0)")
    show = loan[["year", "cfads", "debt_service", "interest", "principal", "closing_balance", "dscr"]].head().copy()
    for col in ["cfads", "debt_service", "interest", "principal", "closing_balance"]:
        show[col] = (show[col] / 1e6).round(2)
    show["dscr"] = show["dscr"].round(2)
    print("RM millions:")
    print(show.to_string(index=False))