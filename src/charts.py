"""Charts for the solar project finance model."""
import matplotlib.pyplot as plt
import pandas as pd

cf = pd.read_csv("outputs/cashflows.csv")
m = lambda s: s / 1e6

# Chart 1: 25-year cash flows
plt.figure(figsize=(9, 5))
for col, label in [("revenue", "Revenue"), ("cfads", "CFADS"), ("opex", "Opex"), ("tax", "Tax")]:
    plt.plot(cf["year"], m(cf[col]), label=label, linewidth=2)
plt.title("50 MW Kedah solar farm: 25-year cash flows")
plt.xlabel("Year of operation")
plt.ylabel("RM millions")
plt.ylim(bottom=0)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("outputs/cashflows_25yr.png", dpi=150)

# Chart 2: year 1 bridge from revenue to CFADS
y1 = cf.iloc[0]
steps = [("Revenue", m(y1["revenue"])), ("Opex", -m(y1["opex"])), ("Tax", -m(y1["tax"]))]
plt.figure(figsize=(7, 5))
running = 0
for name, val in steps:
    bottom = running if val > 0 else running + val
    plt.bar(name, abs(val), bottom=bottom, color="tab:green" if val > 0 else "tab:red")
    running += val
plt.bar("CFADS", running, color="tab:blue")
plt.title("Year 1: from revenue to cash available for the bank")
plt.ylabel("RM millions")
plt.tight_layout()
plt.savefig("outputs/year1_bridge.png", dpi=150)

print("Saved charts to outputs/")