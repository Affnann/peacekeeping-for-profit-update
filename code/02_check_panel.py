"""Step 2: check the panel.

Checks:
  1. peacekeeping-tracker v1.0.0's own checks passed (its check 9 confirms the rebuilt UN data
     matches that release).
  2. The panel's world totals equal peacekeeping-tracker's published monthly totals, every month.
  3. Every reimbursement rate used is in peacekeeping-tracker's rate table, with its resolution.
  4. Months covered and years with fewer than 12 months.
  5. Implausible values: more personnel deployed than the country's whole armed forces.

Usage:  python code/02_check_panel.py
Output: data/check_report.md
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
EXT = ROOT / "external" / "peacekeeping-tracker"
BUILD = ROOT / "data" / "build"


def main():
    out, problems = ["# Check report", ""], 0
    m = pd.read_csv(BUILD / "panel_country_month.csv")
    y = pd.read_csv(BUILD / "panel_country_year.csv")

    rep = (EXT / "data" / "check_report.md").read_text(encoding="utf-8")
    ok = "All checks passed." in rep
    problems += not ok
    out.append(f"1. peacekeeping-tracker v1.0.0 checks on the rebuilt UN data: **{'all passed' if ok else 'FAILED'}** "
               "(see external/peacekeeping-tracker/data/check_report.md).")

    pub = pd.read_csv(EXT / "tables" / "monthly_totals.csv").set_index("month")["total"]
    ours = m.groupby("month").total_uniformed.sum()
    j = pd.concat([ours, pub], axis=1, keys=["ours", "published"]).fillna(-1)
    bad = j[(j.ours - j.published).abs() > 0.5]
    problems += len(bad) > 0
    out.append(f"2. World totals vs peacekeeping-tracker's tables/monthly_totals.csv: {len(j) - len(bad)} of {len(j)} months equal.")
    for mo, r in bad.head(5).iterrows():
        out.append(f"   - {mo}: ours {r.ours:,.0f}, published {r.published:,.0f}")

    rates = pd.read_csv(EXT / "data" / "reference" / "reimbursement_rates.csv")
    used = sorted(m.rate_usd.dropna().unique())
    missing = [x for x in used if x not in set(rates.usd_per_person_per_month)]
    problems += len(missing) > 0
    out.append(f"3. Reimbursement rates used: {', '.join(f'${x:,.2f}' for x in used)}; all in the rate table: "
               f"**{'yes' if not missing else 'NO'}**. Resolutions: {', '.join(sorted(rates.resolution.unique()))}.")

    mm = m.assign(year=m.month.str[:4].astype(int)).groupby("year").month.nunique()
    short = mm[mm < 12]
    out.append(f"4. Months covered: {m.month.min()} to {m.month.max()} ({m.month.nunique()} months). "
               "Years with fewer than 12 months: " + ", ".join(f"{yr} ({n})" for yr, n in short.items()) +
               ". Yearly averages for these years cover only the months available, and no reimbursement is estimated for them.")

    big = y[y.contingent_pct_of_armed_forces > 100]
    out.append(f"5. Country-years with more personnel deployed than the whole armed forces: {len(big)}")
    for _, r in big.head(10).iterrows():
        out.append(f"   - {r.country} {r.year}: {r.avg_contingent:,.0f} deployed vs {r.armed_forces_personnel:,.0f}")

    out.append("\nResult: " + ("all checks passed." if problems == 0 else f"{problems} check(s) failed."))
    text = "\n".join(out) + "\n"
    (ROOT / "data" / "check_report.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
