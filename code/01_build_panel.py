"""Build a country-by-year panel of UN uniformed personnel, armed forces, military spending
and estimated UN troop-cost reimbursements.

Inputs (data/raw/):
  un_DPPADPO-UCPre2010.csv.gz        UN monthly contributions, Nov 1990 - Dec 2009 (by mission)
  un_DPO-UCHISTORICAL.csv.gz         UN monthly contributions, Jan 2010 onward (by mission, sex)
  worldbank_*.json.gz                World Bank indicators
  un_troop_reimbursement_rates.csv   Official UN rate per person per month, from July 2014

Outputs (data/clean/):
  un_personnel_monthly.csv   one row per country per month, personnel by category
  panel_country_year.csv     one row per country per year, with indicators

Definitions:
  total_uniformed = troops + all police + staff officers + experts on mission.
  contingent personnel = troops + formed police units. These are the units the UN reimburses
  at the single monthly rate. Staff officers, individual police and experts on mission are
  paid differently and are not included in the reimbursement estimate.
  estimated_reimbursement_usd = sum over the year's months of contingent personnel x the rate
  in force that month. Only calculated for years in which every month has a verified rate.
"""

import gzip
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"

CATS = ["troops", "formed_police_units", "individual_police", "police_total", "staff_officers", "experts_on_mission"]


def monthly_pre2010():
    d = pd.read_csv(RAW / "un_DPPADPO-UCPre2010.csv.gz", low_memory=False)
    d["month"] = pd.to_datetime(d["Date"]).dt.to_period("M")
    # Before 2010: "Observers" and "Experts_on_Mission" record the same people (they are equal
    # where both are filled), so the larger of the two is used, not their sum.
    d["experts_on_mission"] = d[["Experts_on_Mission", "Observers"]].fillna(0).max(axis=1)
    # "Civilian_Police" is the total of all police. The split into individual police and
    # formed police units exists only for the last few years before 2010.
    d["police_total"] = d["Civilian_Police"].fillna(0)
    d["individual_police"] = d["Individual_Police"].fillna(0)
    d["formed_police_units"] = d["Formed_Police_Units"].fillna(0)
    d["troops"] = d["Troops"].fillna(0)
    d["staff_officers"] = 0.0
    g = d.groupby(["Contributor_ISO-3", "Contributor", "month"])[CATS].sum().reset_index()
    return g.rename(columns={"Contributor_ISO-3": "iso3", "Contributor": "country"})


def monthly_2010():
    d = pd.read_csv(RAW / "un_DPO-UCHISTORICAL.csv.gz")
    d["month"] = pd.to_datetime(d["last_reporting_date"]).dt.to_period("M")
    d["n"] = d["male_personnel"].fillna(0) + d["female_personnel"].fillna(0)
    names = {"Troops": "troops", "Formed Police Units": "formed_police_units",
             "Staff Officer": "staff_officers", "Individual Police": "individual_police",
             "Experts on Mission": "experts_on_mission"}
    d["cat"] = d["personnel_type"].map(names)
    g = d.pivot_table(index=["isocode3", "contributing_country", "month"], columns="cat",
                      values="n", aggfunc="sum", fill_value=0).reset_index()
    for c in CATS:
        if c not in g:
            g[c] = 0.0
    g["police_total"] = g["individual_police"] + g["formed_police_units"]
    return g.rename(columns={"isocode3": "iso3", "contributing_country": "country"})[["iso3", "country", "month"] + CATS]


def worldbank(code, name):
    rows = json.loads(gzip.open(RAW / f"worldbank_{code}.json.gz").read())[1]
    return pd.DataFrame([{"iso3": r["countryiso3code"], "year": int(r["date"]), name: r["value"]}
                         for r in rows if r["countryiso3code"]])


def main():
    m = pd.concat([monthly_pre2010(), monthly_2010()], ignore_index=True)
    m = m[m.iso3.notna() & (m.iso3 != "")]
    m["contingent"] = m.troops + m.formed_police_units
    m["total_uniformed"] = m[["troops", "police_total", "staff_officers", "experts_on_mission"]].sum(axis=1)

    rates = pd.read_csv(RAW / "un_troop_reimbursement_rates.csv", parse_dates=["effective_from"])
    rates = rates.sort_values("effective_from")
    first_rate = rates.effective_from.min().to_period("M")
    def rate_for(p):
        r = rates[rates.effective_from.dt.to_period("M") <= p]
        return r.usd_per_person_per_month.iloc[-1] if len(r) else float("nan")
    rate_map = {p: rate_for(p) for p in m.month.unique()}
    m["rate_usd"] = m.month.map(rate_map)
    m["reimbursement_usd"] = m.contingent * m.rate_usd

    CLEAN.mkdir(parents=True, exist_ok=True)
    out = m.sort_values(["month", "iso3"]).copy()
    out["month"] = out.month.astype(str)
    out.to_csv(CLEAN / "un_personnel_monthly.csv", index=False)

    m["year"] = m.month.dt.year
    names = m.groupby("iso3").country.agg(lambda s: s.iloc[-1])
    # Yearly average = sum over the year's months / number of months the UN has data for in
    # that year. A month in which a country contributed nobody counts as zero.
    months_in_year = m.groupby("year").month.nunique()
    vals = CATS + ["contingent", "total_uniformed"]
    y = m.groupby(["iso3", "year"])[vals].sum().reset_index()
    y["months_with_data"] = y.year.map(months_in_year)
    for c in vals:
        y[f"avg_{c}"] = y[c] / y.months_with_data
    y["months_contributing"] = y.set_index(["iso3", "year"]).index.map(
        m[m.total_uniformed > 0].groupby(["iso3", "year"]).month.nunique()).fillna(0).astype(int)
    y = y.drop(columns=vals)
    # Reimbursement: only years where all 12 months have a verified rate and are reported
    reimb = m[m.month >= first_rate].groupby(["iso3", "year"]).agg(
        est_reimbursement_usd=("reimbursement_usd", "sum"), rate_months=("month", "nunique")).reset_index()
    reimb = reimb[reimb.rate_months == 12].drop(columns="rate_months")
    y = y.merge(reimb, on=["iso3", "year"], how="left")
    y.insert(1, "country", y.iso3.map(names))

    for code, name in [("MS.MIL.TOTL.P1", "armed_forces_personnel"),
                       ("MS.MIL.XPND.CD", "military_expenditure_usd"),
                       ("MS.MIL.XPND.GD.ZS", "military_expenditure_pct_gdp"),
                       ("NY.GDP.PCAP.CD", "gdp_per_capita_usd")]:
        y = y.merge(worldbank(code, name), on=["iso3", "year"], how="left")

    # The World Bank reports 0 for a few countries where the true value is unknown; treat as missing.
    for c in ["armed_forces_personnel", "military_expenditure_usd"]:
        y.loc[y[c] == 0, c] = float("nan")
    y["contingent_pct_of_armed_forces"] = 100 * y.avg_contingent / y.armed_forces_personnel
    y["reimbursement_pct_of_military_expenditure"] = 100 * y.est_reimbursement_usd / y.military_expenditure_usd
    y = y.sort_values(["year", "avg_total_uniformed"], ascending=[True, False])
    y.to_csv(CLEAN / "panel_country_year.csv", index=False)
    print(f"monthly rows: {len(out):,}; panel rows: {len(y):,}; years {y.year.min()}-{y.year.max()}; "
          f"countries {y.iso3.nunique()}")


if __name__ == "__main__":
    main()
