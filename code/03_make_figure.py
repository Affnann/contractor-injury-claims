"""Chart: Defense Base Act claims per fiscal year, with the totals printed by the Labor Department.

Usage:  python code/03_make_figure.py
Output: figures/dba_claims_per_year.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
t = pd.read_csv(ROOT / "data" / "clean" / "dba_claims_year_totals.csv")
t = t[t.table.str.startswith("FY")].assign(year=lambda x: x.table.str[2:].astype(int)).sort_values("year")

fig, ax = plt.subplots(figsize=(9, 4.6), dpi=150)
ax.bar(t.year, t.total / 1000, color="#2f5d8a")
ax.set_title("New Defense Base Act claims filed per U.S. fiscal year", loc="left", fontsize=12, fontweight="bold")
ax.set_ylabel("Claims (thousands)")
ax.set_xticks(t.year)
ax.set_xticklabels([f"{y % 100:02d}" for y in t.year])
ax.set_xlabel("Fiscal year (20xx)")
ax.grid(axis="y", color="#dddddd", linewidth=0.8)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
fig.text(0.01, 0.01, "Source: U.S. Department of Labor, Defense Base Act Case Summary by Nation, FY2009-FY2024. "
         "Claims filed, not confirmed injuries or deaths.", fontsize=7.5, color="#555555")
fig.tight_layout(rect=(0, 0.04, 1, 1))
out = ROOT / "figures" / "dba_claims_per_year.png"
fig.savefig(out)
print(f"Saved {out.relative_to(ROOT)}")
