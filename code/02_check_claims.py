"""Check the clean Defense Base Act files against the totals the Labor Department printed.

Checks:
  1. Every source table was read (16 years plus the cumulative table).
  2. Each year's country rows add up to the year total printed by the Labor Department.
     Where they fall short, the gap is the claims in rows the source leaves blank.
  3. Each row's case types add up to its total, where nothing in the row is blank.
  4. The 16 yearly totals compared with the cumulative 2001-2024 table, for the
     countries with the most claims (FY2001-FY2008 are only in the cumulative table).
  5. Big year-to-year changes (over 50%) in total claims are listed for review.

Usage:  python code/02_check_claims.py
Output: data/clean/check_report.md
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean"
TYPES = ["no_lost_time", "lost_time_3_days_or_less", "lost_time_4_days_or_more",
         "death", "salary_continuation", "other"]


def main():
    d = pd.read_csv(CLEAN / "dba_claims_by_country_year.csv")
    t = pd.read_csv(CLEAN / "dba_claims_year_totals.csv")
    c = pd.read_csv(CLEAN / "dba_claims_cumulative_2001_2024.csv")
    out = ["# Check report", ""]

    years = sorted(d.fiscal_year.unique())
    out.append(f"1. Tables read: {len(years)} years ({years[0]}-{years[-1]}) plus the cumulative table "
               f"({len(t)} printed total rows found).")

    out += ["", "2. Country rows compared with the year total printed in the source:", "",
            "| Year | Printed total | Sum of countries | Gap (blank rows) | Countries listed |",
            "|---|---|---|---|---|"]
    yt = t[t.table.str.startswith("FY")].assign(fiscal_year=lambda x: x.table.str[2:].astype(int))
    for y in years:
        printed = yt.loc[yt.fiscal_year == y, "total"]
        printed = int(printed.iloc[0]) if len(printed) else None
        s = int(d.loc[d.fiscal_year == y, "total"].sum())
        n = int((d.fiscal_year == y).sum())
        gap = "" if printed is None else f"{printed - s:,}"
        out.append(f"| {y} | {printed:,} | {s:,} | {gap} | {n} |" if printed else f"| {y} | (none printed) | {s:,} | | {n} |")
    blank_total = d.total.isna().sum()
    out.append(f"\n   Rows with a blank total (suppressed in the source): {blank_total} of {len(d)}.")

    full = d.dropna(subset=["total"])
    full = full[full[TYPES].notna().any(axis=1)]
    complete = full[full[TYPES].fillna(0).sum(axis=1) == full.total]
    out.append(f"\n3. Rows where case types add up exactly to the total: {len(complete)} of {len(full)} "
               f"rows that have a total and at least one case type. The rest have blank (suppressed) cells.")

    out += ["", "4. Sum of FY2009-FY2024 compared with the cumulative 2001-2024 table (top 6 countries):", "",
            "| Country | Cumulative 2001-2024 | Sum FY2009-2024 | Implied FY2001-2008 |", "|---|---|---|---|"]
    yearly = d.groupby("country").total.sum()
    for _, r in c.sort_values("total", ascending=False).head(6).iterrows():
        s = int(yearly.get(r.country, 0))
        out.append(f"| {r.country} | {int(r.total):,} | {s:,} | {int(r.total) - s:,} |")

    tot = d.groupby("fiscal_year").total.sum()
    printed = yt.set_index("fiscal_year").total
    series = printed.reindex(years).fillna(tot)
    ch = series.pct_change()
    big = ch[ch.abs() > 0.5]
    out.append(f"\n5. Years where total claims changed by more than 50%: {len(big)}")
    for y, v in big.items():
        out.append(f"   - FY{y}: {v:+.0%} (to {int(series[y]):,})")

    text = "\n".join(out) + "\n"
    (CLEAN / "check_report.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
