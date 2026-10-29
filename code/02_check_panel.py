"""Check the panel against the UN's own published annual figures and for gaps.

Checks:
  1. Our yearly averages (built from the monthly data) compared with the UN's separate
     Annual Uniformed Personnel Contribution Statistics, country by country, 2010 onward.
  2. Months reported per year (the UN notes that some months are missing).
  3. The join between the two UN monthly datasets (Dec 2009 vs Jan 2010 totals).
  4. Implausible values: deployments larger than the whole armed forces.

Usage:  python code/02_check_panel.py
Output: data/clean/check_report.md
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"


def main():
    p = pd.read_csv(CLEAN / "panel_country_year.csv")
    m = pd.read_csv(CLEAN / "un_personnel_monthly.csv")
    out = ["# Check report", ""]

    # 1. Compare with the UN annual dataset. The UN averages each personnel category only
    # over the months in which that category was reported, so we rebuild that figure from
    # our monthly file and compare like with like.
    a = pd.read_csv(RAW / "un_DataCommons-UCHISTORICAL.csv.gz")
    a["n"] = a.Male.fillna(0) + a.Female.fillna(0)
    a = a.groupby(["ISOCode3", "Year"]).n.sum().reset_index().rename(columns={"ISOCode3": "iso3", "Year": "year", "n": "un_annual"})
    mm = m.assign(year=m.month.str[:4].astype(int))
    mm = mm[mm.year >= 2010]
    cats = ["troops", "formed_police_units", "individual_police", "staff_officers", "experts_on_mission"]
    long = mm.melt(id_vars=["iso3", "year", "month"], value_vars=cats)
    long = long[long.value > 0]
    un_method = long.groupby(["iso3", "year", "variable"]).value.mean().groupby(["iso3", "year"]).sum().reset_index(name="ours_un_method")
    j = un_method.merge(a, on=["iso3", "year"], how="inner")
    close = (j.ours_un_method - j.un_annual).abs() <= j.un_annual.abs() * 0.01 + 1
    out.append(f"1. Our monthly data, averaged the UN's way, vs the UN's own annual figures (2010 onward): "
               f"{close.sum():,} of {len(j):,} country-years agree within 1% (or 1 person).")
    out.append("   Note: the UN's annual figure averages each category only over months in which it was reported, "
               "which overstates countries that left or joined a mission during the year. This dataset instead "
               "averages over all months of the year, counting months with no contribution as zero.")
    p2 = p[p.year >= 2010].merge(a, on=["iso3", "year"], how="inner")
    ex = p2.assign(gap=lambda x: x.un_annual - x.avg_total_uniformed).sort_values("gap", ascending=False).head(3)
    out.append("   Largest differences between the two methods: " + "; ".join(
        f"{r.country} {r.year} (ours {r.avg_total_uniformed:,.0f}, UN {r.un_annual:,.0f}, contributing {r.months_contributing} of 12 months)"
        for _, r in ex.iterrows()))

    # 2. Months per year
    mm = m.assign(year=m.month.str[:4].astype(int)).groupby("year").month.nunique()
    short = mm[mm < 12]
    out.append(f"\n2. Years with fewer than 12 months of data: " +
               (", ".join(f"{y} ({n} months)" for y, n in short.items()) or "none"))

    # 3. Join between datasets
    tot = m.groupby("month").total_uniformed.sum()
    out.append(f"\n3. World total uniformed personnel: Dec 2009 = {tot.get('2009-12', float('nan')):,.0f}, "
               f"Jan 2010 = {tot.get('2010-01', float('nan')):,.0f}.")

    # 4. Implausible values
    big = p[p.contingent_pct_of_armed_forces > 100]
    out.append(f"\n4. Country-years where deployed contingents exceed the whole armed forces: {len(big)}")
    for _, r in big.head(10).iterrows():
        out.append(f"   - {r.country} {r.year}: {r.avg_contingent:,.0f} deployed vs {r.armed_forces_personnel:,.0f} armed forces")

    text = "\n".join(out) + "\n"
    (CLEAN / "check_report.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
