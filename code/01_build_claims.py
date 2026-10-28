"""Turn the Labor Department's Defense Base Act country tables into one clean file.

Input:  data/raw/dba_country_tables_fy2009-2024.txt
        An exact copy of the published "Defense Base Act Case Summary by Nation"
        tables (FY2009-FY2020 web pages; FY2021-FY2024 and the 2001-2024 cumulative
        table from spreadsheets). Each table starts with a line
        "#SRC|<label>|<source path on www.dol.gov>|<column names as published>".

Output: data/clean/dba_claims_by_country_year.csv   one row per country per year
        data/clean/dba_claims_year_totals.csv       the totals printed for each year
        data/clean/dba_claims_cumulative_2001_2024.csv

Blank cells are kept blank. The Labor Department leaves small numbers out of
its tables, so a blank does NOT mean zero.
"""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "dba_country_tables_fy2009-2024.txt"
CLEAN = ROOT / "data" / "clean"

# Published column name -> standard name
COLUMN_MAP = {
    "NLT": "no_lost_time", "SUM(NLT)": "no_lost_time",
    "LTO": "lost_time_3_days_or_less", "SUM(LTO3)": "lost_time_3_days_or_less",
    "LT4": "lost_time_4_days_or_more", "SUM(LTO4)": "lost_time_4_days_or_more",
    "DEA": "death", "SUM(DEA)": "death",
    "COP": "salary_continuation", "SUM(COP)": "salary_continuation",
    "OTH": "other", "SUM(OTH)": "other",
    "TOTAL": "total", "SUM(TOTAL)": "total",
}
CASE_TYPES = ["no_lost_time", "lost_time_3_days_or_less", "lost_time_4_days_or_more",
              "death", "salary_continuation", "other", "total"]

# Different spellings of the same place across years -> one standard name
NAME_FIXES = {
    "UNITED STATES OF AMERICA": "UNITED STATES",
    "UNITED KINGDOM OF GREAT BRITAIN AND NORTHERN IRELAND": "UNITED KINGDOM",
    "MACEDONIA, THE FORMER YUGOSLAV": "NORTH MACEDONIA",
    "MACEDONIA, THE FORMER YUGOSLAV REPUBLIC": "NORTH MACEDONIA",
    "MACEDONIA (THE FORMER YUGOSLAV REPUBLIC OF)": "NORTH MACEDONIA",
    "IRAN (ISLAMIC REPUBLIC OF)": "IRAN", "IRAN, ISLAMIC REPUBLIC OF": "IRAN",
    "BOLIVIA (PLURINATIONAL STATE OF)": "BOLIVIA",
    "KOREA (THE REPUBLIC OF)": "SOUTH KOREA", "KOREA, REPUBLIC OF": "SOUTH KOREA",
    "KOREA (THE DEMOCRATIC PEOPLES REPUBLIC OF)": "NORTH KOREA",
    "KOREA, DEMOCRATIC PEOPLES REPUBLIC OF": "NORTH KOREA",
    "LIBYAN ARAB JAMAHIRIYA": "LIBYA",
    "PALESTINE, STATE OF": "PALESTINE", "PALESTINIAN TERRITORY, OCCUPIED": "PALESTINE",
    "TAIWAN (PROVINCE OF CHINA)": "TAIWAN",
    "VIET NAM": "VIETNAM",
    "ACENSION ISLAND, BRITISH": "ASCENSION ISLAND, BRITISH",
    "SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA": "SAINT HELENA",
    "Ã…LAND ISLANDS": "ALAND ISLANDS",
    "NATION PENDING": "NATION PENDING",
}


def standard_name(name: str) -> str:
    n = re.sub(r"\s*\(THE\)\s*$", "", name.strip().upper())
    return NAME_FIXES.get(n, n)


def number(cell: str):
    cell = cell.replace(",", "").strip()
    return int(float(cell)) if cell else ""


def is_total_row(first: str, cells) -> bool:
    f = first.strip().lower()
    return f.startswith(("total", "grand total")) or (f == "" and any(c.strip().lower() == "total" for c in cells))


def main():
    tables, current = {}, None
    for line in RAW.read_text(encoding="utf-8").splitlines():
        if line.startswith("#SRC|"):
            _, label, path, cols = line.split("|", 3)
            current = {"label": label, "url": "https://www.dol.gov" + path,
                       "cols": [COLUMN_MAP.get(c) for c in cols.split(",")[1:]], "rows": []}
            tables[label] = current
        else:
            current["rows"].append(line.split("|"))

    rows, totals, cumulative = [], [], []
    for label, t in tables.items():
        for cells in t["rows"]:
            first, rest = cells[0], cells[1:]
            if is_total_row(first, rest):
                if first.strip() == "":           # FY2021-22 style: "...|Total|18520"
                    rec = {c: "" for c in CASE_TYPES}
                    rec["total"] = number(rest[-1])
                else:
                    rec = {col: number(v) for col, v in zip(t["cols"], rest)}
                rec.update(table=label, source_url=t["url"], label_in_source=first.strip() or "Total")
                totals.append(rec)
                continue
            rec = {col: number(v) for col, v in zip(t["cols"], rest)}
            rec.update(country=standard_name(first), country_in_source=first.strip(),
                       table=label, source_url=t["url"])
            (cumulative if label.startswith("CUM") else rows).append(rec)

    CLEAN.mkdir(parents=True, exist_ok=True)
    def write(name, recs, lead):
        with (CLEAN / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=lead + CASE_TYPES + ["source_url"])
            w.writeheader()
            for r in recs:
                w.writerow({k: r.get(k, "") for k in w.fieldnames})
        print(f"{name}: {len(recs)} rows")

    for r in rows:
        r["fiscal_year"] = int(r["table"][2:])
    rows.sort(key=lambda r: (r["fiscal_year"], -(r["total"] or 0), r["country"]))
    write("dba_claims_by_country_year.csv", rows, ["fiscal_year", "country", "country_in_source"])
    write("dba_claims_year_totals.csv", totals, ["table", "label_in_source"])
    write("dba_claims_cumulative_2001_2024.csv", cumulative, ["country", "country_in_source"])


if __name__ == "__main__":
    main()
