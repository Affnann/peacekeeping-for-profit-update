"""Step 4: apply Coleman and Nyblade's (2018) first condition, December 2015 to December 2025.

The article's first condition: for profit to be a plausible motive, a deployment and its
reimbursements must be significant "in relation to the state's total armed forces and
military expenditure". This script measures that for the 20 largest military contributors
each December, built the same way for every year:

  military personnel  = troops + staff officers + experts on mission deployed that December
                        (before May 2017 the UN counted staff officers inside troops)
  annual reimbursement = military personnel x 12 x the UN standard monthly rate in force that December
  reimbursement share  = annual reimbursement / military expenditure of the PREVIOUS year
                        (World Bank, based on SIPRI)
  deployment share     = military personnel / armed forces personnel of the SAME year
                        (World Bank, based on IISS; not available after 2020)

Groups (counts and shares of all UN military personnel deployed that December):
  - reimbursement share of 10% or more: our reading of "very significant"; we also report 5% and 20%
  - reimbursement share below 1%
Condition 2 (an exceptional ability to profit, through cheap equipment or low deployment
allowances) depends on national policies and is not measured here.

Usage:  python code/04_condition1.py
Output: tables/condition1_top20_by_december.csv
        tables/condition1_summary_by_december.csv
        figures/condition1_shares_by_december.png
"""

import gzip
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
EXT = ROOT / "external" / "peacekeeping-tracker"
YEARS = range(2015, 2026)


def wb(code):
    rows = json.loads(gzip.open(ROOT / "data" / "worldbank" / f"worldbank_{code}.json.gz").read())[1]
    return {(r["countryiso3code"], int(r["date"])): r["value"] for r in rows
            if r["countryiso3code"] and r["value"] not in (None, 0)}


def main():
    m = pd.read_csv(ROOT / "data" / "build" / "panel_country_month.csv")
    m["military"] = m.troops + m.staff_officers + m.experts_on_mission
    milex, armed = wb("MS.MIL.XPND.CD"), wb("MS.MIL.TOTL.P1")
    rates = pd.read_csv(EXT / "data" / "reference" / "reimbursement_rates.csv", parse_dates=["effective_from"])

    rows, summary = [], []
    for y in YEARS:
        dec = m[m.month == f"{y}-12"].copy()
        rate = rates.loc[rates.effective_from <= pd.Timestamp(f"{y}-12-31"), "usd_per_person_per_month"].iloc[-1]
        dec["annual_reimbursement_usd"] = dec.military * 12 * rate
        dec["military_expenditure_usd"] = [milex.get((i, y - 1)) for i in dec.iso3]
        dec["armed_forces_personnel"] = [armed.get((i, y)) for i in dec.iso3]
        dec["reimbursement_pct_of_military_expenditure"] = 100 * dec.annual_reimbursement_usd / dec.military_expenditure_usd
        dec["deployment_pct_of_armed_forces"] = 100 * dec.military / dec.armed_forces_personnel
        total = dec.military.sum()

        top = dec.sort_values("military", ascending=False).head(20).copy()
        top.insert(0, "rank", range(1, len(top) + 1))
        top.insert(0, "december", y)
        top["rate_usd_per_month"] = rate
        top["military_expenditure_year"] = y - 1
        top["armed_forces_year"] = y
        rows.append(top[["december", "rank", "iso3", "country", "military", "rate_usd_per_month",
                         "annual_reimbursement_usd", "military_expenditure_year", "military_expenditure_usd",
                         "reimbursement_pct_of_military_expenditure", "armed_forces_year",
                         "armed_forces_personnel", "deployment_pct_of_armed_forces"]])

        s = {"december": y, "rate_usd_per_month": rate, "un_military_personnel_total": int(total),
             "top20_military_personnel": int(top.military.sum()),
             "top20_with_military_expenditure_data": int(top.reimbursement_pct_of_military_expenditure.notna().sum())}
        share = top.reimbursement_pct_of_military_expenditure
        for cut in (5, 10, 20):
            g = top[share >= cut]
            s[f"top20_countries_at_or_above_{cut}pct"] = len(g)
            s[f"top20_personnel_share_at_or_above_{cut}pct"] = round(100 * g.military.sum() / total, 1)
        low = top[share < 1]
        s["top20_countries_below_1pct"] = len(low)
        s["top20_personnel_share_below_1pct"] = round(100 * low.military.sum() / total, 1)
        s["countries_at_or_above_10pct_all_contributors"] = ", ".join(
            dec[dec.reimbursement_pct_of_military_expenditure >= 10].sort_values(
                "reimbursement_pct_of_military_expenditure", ascending=False).country)
        summary.append(s)

    t = pd.concat(rows).round({"reimbursement_pct_of_military_expenditure": 2, "deployment_pct_of_armed_forces": 2,
                               "military_expenditure_usd": 0, "annual_reimbursement_usd": 0})
    t.to_csv(ROOT / "tables" / "condition1_top20_by_december.csv", index=False)
    s = pd.DataFrame(summary)
    s.to_csv(ROOT / "tables" / "condition1_summary_by_december.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    ax.plot(s.december, s.top20_personnel_share_at_or_above_10pct, marker="o", color="#2f5d8a",
            label="Top-20 contributors whose UN payments are 10% or more of military spending")
    ax.plot(s.december, s.top20_personnel_share_below_1pct, marker="o", color="#d08c2c",
            label="Top-20 contributors whose UN payments are below 1% of military spending")
    ax.set_title("Share of all UN military peacekeepers supplied by each group, December of each year",
                 loc="left", fontsize=11, fontweight="bold")
    ax.set_ylabel("Percent of UN military personnel")
    ax.set_ylim(0, max(50, s[["top20_personnel_share_at_or_above_10pct", "top20_personnel_share_below_1pct"]].max().max() + 5))
    ax.set_xticks(list(YEARS))
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.text(0.01, 0.01, "Payments: military personnel x 12 x UN standard rate, against the previous year's military "
             "expenditure (World Bank, based on SIPRI).\nUN personnel via peacekeeping-tracker v1.0.0 "
             "(doi:10.5281/zenodo.23752307). Test of condition 1 of Coleman and Nyblade (2018).",
             fontsize=7, color="#555555")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(ROOT / "figures" / "condition1_shares_by_december.png")
    print(s[["december", "un_military_personnel_total", "top20_countries_at_or_above_10pct",
             "top20_personnel_share_at_or_above_10pct", "top20_countries_below_1pct",
             "top20_personnel_share_below_1pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
