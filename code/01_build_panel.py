"""Step 1: build a country-by-year panel of UN uniformed personnel, armed forces, military
spending and estimated UN troop-cost reimbursements.

Inputs:
  external/peacekeeping-tracker/data/build/contributions_monthly.csv
      UN monthly contributions by country, mission and category, Nov 1990 - Jul 2026,
      rebuilt by code/00_get_un_data.py with peacekeeping-tracker v1.0.0
  external/peacekeeping-tracker/data/reference/reimbursement_rates.csv
      the UN's standard reimbursement rates and the resolutions that set them
  data/worldbank/*.json.gz
      World Bank indicators (CC BY 4.0), committed in this repository

Outputs (data/build/, built locally and not committed, because they contain UN figures):
  panel_country_month.csv   one row per country per month
  panel_country_year.csv    one row per country per year, with indicators

Definitions:
  contingent = troops + formed police units: the units the UN reimburses at its standard
      monthly rate. Before May 2017 the UN counted staff officers inside troops, so
      contingents for those years are slightly overstated. Before November 2009 the UN did
      not split police, so formed police units cannot be identified then.
  total_uniformed = all categories.
  Yearly averages divide by the number of months the UN has data for in that year; a month in
      which a country sent nobody counts as zero.
  est_reimbursement_usd = sum over the year's months of contingent x the standard rate in force.
      Only for years in which every month has a rate (2015 onward).
"""

import gzip
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
EXT = ROOT / "external" / "peacekeeping-tracker"
BUILD = ROOT / "data" / "build"
WB = ROOT / "data" / "worldbank"

CATS = ["troops", "staff_officers", "experts_on_mission",
        "police_individual", "police_formed_units", "police_unsplit"]


def worldbank(code, name):
    rows = json.loads(gzip.open(WB / f"worldbank_{code}.json.gz").read())[1]
    return pd.DataFrame([{"iso3": r["countryiso3code"], "year": int(r["date"]), name: r["value"]}
                         for r in rows if r["countryiso3code"]])


def main():
    c = pd.read_csv(EXT / "data" / "build" / "contributions_monthly.csv")
    # Twelve rows in the UN files have no number; they are left out (missing, not zero).
    c = c.dropna(subset=["total"])
    m = c.pivot_table(index=["iso3", "month"], columns="category", values="total",
                      aggfunc="sum", fill_value=0).reset_index()
    for k in CATS:
        if k not in m:
            m[k] = 0.0
    names = c.sort_values("month").groupby("iso3").country.last()
    m.insert(1, "country", m.iso3.map(names))
    m["police_total"] = m.police_individual + m.police_formed_units + m.police_unsplit
    m["contingent"] = m.troops + m.police_formed_units
    m["total_uniformed"] = m[CATS].sum(axis=1)

    rates = pd.read_csv(EXT / "data" / "reference" / "reimbursement_rates.csv", parse_dates=["effective_from"])
    rates["from_month"] = rates.effective_from.dt.to_period("M")
    rates = rates.sort_values("from_month")
    per = pd.PeriodIndex(m.month, freq="M")
    m["rate_usd"] = [rates.loc[rates.from_month <= p, "usd_per_person_per_month"].iloc[-1]
                     if (rates.from_month <= p).any() else float("nan") for p in per]
    m["est_reimbursement_usd"] = m.contingent * m.rate_usd

    BUILD.mkdir(parents=True, exist_ok=True)
    m.sort_values(["month", "iso3"]).to_csv(BUILD / "panel_country_month.csv", index=False)

    m["year"] = per.year
    vals = CATS + ["police_total", "contingent", "total_uniformed"]
    months_in_year = m.groupby("year").month.nunique()
    y = m.groupby(["iso3", "year"])[vals].sum().reset_index()
    y["months_with_data"] = y.year.map(months_in_year)
    for k in vals:
        y[f"avg_{k}"] = y[k] / y.months_with_data
    y = y.drop(columns=vals)
    y["months_contributing"] = y.set_index(["iso3", "year"]).index.map(
        m[m.total_uniformed > 0].groupby(["iso3", "year"]).month.nunique()).fillna(0).astype(int)

    first_rate = rates.from_month.min()
    r = m[per >= first_rate].groupby(["iso3", "year"]).agg(
        est_reimbursement_usd=("est_reimbursement_usd", "sum"), rate_months=("month", "nunique")).reset_index()
    full_years = [yr for yr, n in months_in_year.items() if n == 12 and pd.Period(f"{yr}-01", "M") >= first_rate]
    r = r[r.year.isin(full_years)].drop(columns="rate_months")
    y = y.merge(r, on=["iso3", "year"], how="left")
    y.loc[y.year.isin(full_years) & y.est_reimbursement_usd.isna(), "est_reimbursement_usd"] = 0.0
    y.insert(1, "country", y.iso3.map(names))

    for code, name in [("MS.MIL.TOTL.P1", "armed_forces_personnel"),
                       ("MS.MIL.XPND.CD", "military_expenditure_usd"),
                       ("MS.MIL.XPND.GD.ZS", "military_expenditure_pct_gdp"),
                       ("NY.GDP.PCAP.CD", "gdp_per_capita_usd")]:
        y = y.merge(worldbank(code, name), on=["iso3", "year"], how="left")
    # The World Bank reports 0 for a few countries where the true value is unknown; treat as missing.
    for k in ["armed_forces_personnel", "military_expenditure_usd"]:
        y.loc[y[k] == 0, k] = float("nan")
    y["contingent_pct_of_armed_forces"] = 100 * y.avg_contingent / y.armed_forces_personnel
    y["reimbursement_pct_of_military_expenditure"] = 100 * y.est_reimbursement_usd / y.military_expenditure_usd

    y = y.sort_values(["year", "avg_total_uniformed"], ascending=[True, False])
    y.to_csv(BUILD / "panel_country_year.csv", index=False)
    print(f"panel: {len(y):,} country-years, {y.year.min()}-{y.year.max()}, {y.iso3.nunique()} countries; "
          f"reimbursement estimated for {min(full_years)}-{max(full_years)}")


if __name__ == "__main__":
    main()
