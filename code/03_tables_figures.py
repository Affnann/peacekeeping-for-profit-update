"""Step 3: short summary tables and figures from the local panel.

Only short summaries are written to the repository. The full panel stays in data/build/
(not committed), because it contains the UN's figures, which may not be redistributed.

Outputs:
  tables/reimbursement_share_top20_2019.csv
  tables/reimbursement_share_top20_2025.csv
  tables/reimbursement_share_summary_by_year.csv
  figures/reimbursement_share_of_military_spending_2019.png

Usage:  python code/03_tables_figures.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
y = pd.read_csv(ROOT / "data" / "build" / "panel_country_year.csv")
TAB = ROOT / "tables"
FIG = ROOT / "figures"
TAB.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

COLS = ["iso3", "country", "year", "avg_contingent", "est_reimbursement_usd", "military_expenditure_usd",
        "reimbursement_pct_of_military_expenditure", "gdp_per_capita_usd"]


def top(year, n=20):
    t = (y[y.year == year].dropna(subset=["reimbursement_pct_of_military_expenditure"])
         .sort_values("reimbursement_pct_of_military_expenditure", ascending=False).head(n)[COLS])
    return t.round({"avg_contingent": 0, "est_reimbursement_usd": 0, "military_expenditure_usd": 0,
                    "reimbursement_pct_of_military_expenditure": 1, "gdp_per_capita_usd": 0})


for yr in (2019, 2025):
    top(yr).to_csv(TAB / f"reimbursement_share_top20_{yr}.csv", index=False)

has = y.dropna(subset=["est_reimbursement_usd"])
rows = []
for yr, g in has.groupby("year"):
    share = g.reimbursement_pct_of_military_expenditure
    rows.append({"year": yr,
                 "countries_with_contingents": int((g.avg_contingent > 0).sum()),
                 "total_est_reimbursement_usd": round(g.est_reimbursement_usd.sum()),
                 "countries_with_military_spending_data": int(share.notna().sum()),
                 "countries_over_5pct": int((share > 5).sum()),
                 "countries_over_10pct": int((share > 10).sum()),
                 "countries_over_25pct": int((share > 25).sum())})
pd.DataFrame(rows).to_csv(TAB / "reimbursement_share_summary_by_year.csv", index=False)

x = top(2019, 15).iloc[::-1]
fig, ax = plt.subplots(figsize=(8.5, 6), dpi=150)
ax.barh(x.country, x.reimbursement_pct_of_military_expenditure, color="#2f5d8a")
ax.set_title("Estimated UN troop reimbursements as a share of military spending, 2019",
             loc="left", fontsize=11.5, fontweight="bold")
ax.set_xlabel("Percent of the country's military expenditure")
ax.grid(axis="x", color="#dddddd", linewidth=0.8)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
fig.text(0.01, 0.01, "Estimate: troops and formed police units x UN standard monthly rate. Money owed to governments, "
         "not profit; equipment payments not included.\nSources: UN personnel data via peacekeeping-tracker v1.0.0 "
         "(doi:10.5281/zenodo.23752307); World Bank (military expenditure, based on SIPRI).", fontsize=7, color="#555555")
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(FIG / "reimbursement_share_of_military_spending_2019.png")
print("tables and figure written")
