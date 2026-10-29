"""Figures: UN troop-cost reimbursements compared with each country's military budget.

Usage:  python code/03_make_figures.py
Output: figures/reimbursement_share_of_military_spending_2019.png
        figures/uniformed_personnel_world_total.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
p = pd.read_csv(ROOT / "data" / "clean" / "panel_country_year.csv")
m = pd.read_csv(ROOT / "data" / "clean" / "un_personnel_monthly.csv")
FIG = ROOT / "figures"
NOTE_COLOR = "#555555"


def style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_axisbelow(True)


# 1. Reimbursement as a share of military spending, 2019
y = 2019
x = (p[p.year == y].dropna(subset=["reimbursement_pct_of_military_expenditure"])
     .sort_values("reimbursement_pct_of_military_expenditure", ascending=False).head(15).iloc[::-1])
fig, ax = plt.subplots(figsize=(8.5, 6), dpi=150)
ax.barh(x.country, x.reimbursement_pct_of_military_expenditure, color="#2f5d8a")
ax.set_title(f"Estimated UN troop reimbursements as a share of military spending, {y}",
             loc="left", fontsize=11.5, fontweight="bold")
ax.set_xlabel("Percent of the country's military expenditure")
ax.grid(axis="x", color="#dddddd", linewidth=0.8)
style(ax)
fig.text(0.01, 0.01, "Estimate: troops and formed police units x UN monthly rate. Gross payments to governments, "
         "not profit; equipment payments not included.\nSources: UN Peace and Security Data Hub; World Bank "
         "(military expenditure, based on SIPRI); UN General Assembly resolutions.", fontsize=7, color=NOTE_COLOR)
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(FIG / f"reimbursement_share_of_military_spending_{y}.png")

# 2. World total of uniformed personnel, monthly
t = m.groupby("month").total_uniformed.sum()
t.index = pd.PeriodIndex(t.index, freq="M").to_timestamp()
fig, ax = plt.subplots(figsize=(9, 4.4), dpi=150)
ax.plot(t.index, t / 1000, color="#2f5d8a", linewidth=1.8)
ax.set_title("Uniformed personnel in UN peacekeeping, all contributing countries", loc="left",
             fontsize=11.5, fontweight="bold")
ax.set_ylabel("Personnel (thousands)")
ax.grid(axis="y", color="#dddddd", linewidth=0.8)
ax.set_ylim(bottom=0)
style(ax)
fig.text(0.01, 0.01, "Source: UN Peace and Security Data Hub, monthly contributions by country, Nov 1990 onward.",
         fontsize=7.5, color=NOTE_COLOR)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(FIG / "uniformed_personnel_world_total.png")
print("figures saved")
