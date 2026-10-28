# Data

## Source

| Item | Details |
|---|---|
| Tables | *Defense Base Act Case Summary by Nation* |
| Publisher | U.S. Department of Labor, Office of Workers' Compensation Programs, Division of Longshore and Harbor Workers' Compensation |
| Listing page | https://www.dol.gov/agencies/owcp/dlhwc/lsdbareports |
| Definitions | https://www.dol.gov/agencies/owcp/dlhwc/lsaboutdbareports |
| Coverage | Fiscal years 2009-2024 (one table each), plus a cumulative table for 2001-2024 |
| Downloaded on | 29 October 2026 |
| License / terms | Works of the U.S. federal government are not subject to U.S. copyright (17 U.S.C. § 105). |

The exact page or file for each table is in the `source_url` column of the clean files and in the `#SRC` lines of the raw file.

## Files

- `raw/dba_country_tables_fy2009-2024.txt`: the 17 source tables copied cell by cell, with nothing changed. Each table starts with a `#SRC` line giving its label, its address on www.dol.gov and its column names as published. Rows where every cell is blank were left out.
- The Labor Department's site blocks automated downloads, so the tables were read in an ordinary web browser.
- `clean/`: the clean files (see the main README). License: CC BY 4.0.
