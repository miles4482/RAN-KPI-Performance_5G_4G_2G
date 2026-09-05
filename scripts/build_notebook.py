"""Build the beginner Jupyter notebook as a valid .ipynb file."""

from pathlib import Path

import nbformat as nbf

nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "pygments_lexer": "ipython3",
    },
}

cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    cells.append(nbf.v4.new_code_cell(text))


md(
    """# RAN KPI in Python — CA User Ratio (Beginner Guide)

This notebook rebuilds the **same style of chart** as the Excel sample:

- Left chart: **DL CA User Ratio, %** (Downlink Carrier Aggregation)
- Right chart: **UL CA User Ratio, %** (Uplink Carrier Aggregation)
- Green / yellow / gray **bars** = last 3 full days
- Black **line** = today (partial day is OK)

You do **not** need to be a programmer. Work slowly:

1. Click the first cell.
2. Press **Shift + Enter** to run it.
3. Wait until it finishes.
4. Go to the next cell and repeat.

If a cell turns **red**, stop and read the last line of the error. Most beginner issues are a missing library or the wrong folder.
"""
)

md(
    """## Step 0 — Install the tools (run this once)

Python needs 3 extra packages:

| Package | What it does |
|---|---|
| `pandas` | Reads Excel / CSV tables |
| `matplotlib` | Draws the charts |
| `openpyxl` | Lets pandas open `.xlsx` files |

If they are already installed, this cell does nothing harmful.
"""
)

code(
    """# The ! means: run this as a terminal command, not as Python.
# Remove the comment (#) on the next line if you get "No module named pandas".
# !pip install pandas matplotlib openpyxl

print("Step 0 is ready. Run the next cell.")
"""
)

md(
    """## Step 1 — Load the Python libraries

Think of this as opening Excel, then opening the chart menu.

- `pandas` as `pd` → we will use `pd.read_excel(...)` to open the table
- `matplotlib.pyplot` as `plt` → we will use `plt.bar(...)` and `plt.plot(...)` to draw
- `numpy` as `np` → simple number help (hour positions on the X axis)
"""
)

code(
    """from IPython.display import display
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Show charts inside this notebook (not in a pop-up window)
%matplotlib inline

print("Libraries loaded.")
print("pandas version:", pd.__version__)
"""
)

md(
    """## Step 2 — What is CA User Ratio?

**Carrier Aggregation (CA)** lets one user use more than one LTE/NR carrier at the same time, which can improve throughput.

The KPI is a percentage of users:

\\[
\\text{DL CA User Ratio (\\%)} = \\frac{\\text{Users with Downlink CA}}{\\text{Average RRC users}} \\times 100
\\]

\\[
\\text{UL CA User Ratio (\\%)} = \\frac{\\text{Users with Uplink CA}}{\\text{Average RRC users}} \\times 100
\\]

Typical live-network behaviour (same as the sample):

- **DL CA** is much higher than **UL CA** (many phones do DL CA, fewer do UL CA)
- Both drop in the **night** (fewer CA-capable users / less demand)
- **UL CA** often rises in the evening

Vendor counter names differ (Huawei / Ericsson / Nokia), but the idea is the same: CA users ÷ total users × 100.
"""
)

md(
    """## Step 3 — Open the sample Excel file

The file `data/sample_ca_kpi.xlsx` has these sheets (Excel tabs):

- `HowTo` — short instructions
- `DL_CA_User_Ratio` — the downlink KPI table
- `UL_CA_User_Ratio` — the uplink KPI table

Each sheet looks like this:

| Hour | 27-Aug-26 | 1-Sep-26 | 2-Sep-26 | 3-Sep-26 |
|---|---|---|---|---|
| 00:00 | 20.3 | 19.8 | 20.2 | 20.0 |
| 01:00 | 19.0 | 18.6 | 18.5 | 18.8 |
| ... | ... | ... | ... | ... |

Empty cells after 14:00 on **3-Sep-26** mean "today is not finished yet". The black line will stop there.

> **Folder tip:** Open Jupyter from the **project folder** (the folder that contains `data` and this notebook). Then the path below will work.
"""
)

code(
    """from pathlib import Path

# Path to the sample Excel file
excel_path = Path("data/sample_ca_kpi.xlsx")

if not excel_path.exists():
    raise FileNotFoundError(
        "I cannot find data/sample_ca_kpi.xlsx.\\n"
        "In Jupyter, use File -> Open and open the project folder first, "
        "then open this notebook."
    )

# sheet_name=None means: load ALL sheets
workbook = pd.read_excel(excel_path, sheet_name=None)

print("Sheets inside the Excel file:")
for name in workbook:
    print(" -", name)

dl = workbook["DL_CA_User_Ratio"]
ul = workbook["UL_CA_User_Ratio"]

print("\\nDL table size (rows, columns):", dl.shape)
print("UL table size (rows, columns):", ul.shape)
"""
)

md(
    """## Step 4 — Look at the tables

Always look at the data **before** you draw a chart. This is the same as scrolling through Excel.
"""
)

code(
    """print("===== DL CA User Ratio (%) =====")
display(dl)

print("===== UL CA User Ratio (%) =====")
display(ul)
"""
)

md(
    """### Quick check

- There should be **24 rows** (00:00 to 23:00).
- The last date column can contain `NaN` (Not a Number). That is normal for a partial day.
- DL values should be around **10 to 25**.
- UL values should be around **0.5 to 2.0**.
"""
)

code(
    """print("DL column names:", list(dl.columns))
print("UL column names:", list(ul.columns))
print()
print("DL min / max:")
print(dl.select_dtypes(include="number").agg(["min", "max"]))
print()
print("UL min / max:")
print(ul.select_dtypes(include="number").agg(["min", "max"]))
"""
)

md(
    """## Step 5 — Draw one combined chart (bars + line)

We will copy the Excel style:

- **Bars** for the first 3 dates
- **Line with dots** for the latest date
- Green / yellow / gray / black colors like Excel
- Horizontal grid lines
- Y-axis from 0 to 25 for DL, 0 to 2 for UL

Read the comments. You can change colors or titles later.
"""
)

code(
    """def plot_ca_kpi(ax, table, title, y_max, y_step):
    \"\"\"Draw one KPI chart on one subplot.

    ax     = the empty box where matplotlib will draw
    table  = pandas DataFrame (Hour + one column per date)
    title  = text on top of the chart
    y_max  = highest number on the Y axis
    y_step = gap between Y-axis ticks
    \"\"\"
    # Column 0 is Hour. The other columns are dates.
    hour_labels = table["Hour"].astype(str)
    date_columns = [col for col in table.columns if col != "Hour"]

    # First 3 dates = bars, last date = line (same as the sample)
    bar_dates = date_columns[:-1]
    line_date = date_columns[-1]

    # Excel-like colors
    bar_colors = ["#92D050", "#FFC000", "#A6A6A6"]  # green, gold, gray
    line_color = "#000000"  # black

    # Positions 0, 1, 2, ... 23 on the X axis
    x = np.arange(len(hour_labels))
    bar_width = 0.25

    # Draw grouped bars: one group per hour
    # The 3 bars sit slightly left, center, and slightly right
    offsets = [-bar_width, 0.0, bar_width]
    for date, offset, color in zip(bar_dates, offsets, bar_colors):
        ax.bar(
            x + offset,
            table[date],
            width=bar_width,
            color=color,
            edgecolor="white",
            linewidth=0.3,
            label=date,
            zorder=3,
        )

    # Draw today's values as a line on top of the bars
    ax.plot(
        x,
        table[line_date],
        color=line_color,
        linewidth=2.2,
        marker="o",
        markersize=4,
        label=line_date,
        zorder=4,
    )

    ax.set_title(title, fontsize=13, pad=10)
    ax.set_ylim(0, y_max)
    ax.set_yticks(np.arange(0, y_max + 0.0001, y_step))
    ax.set_xticks(x)
    ax.set_xticklabels(hour_labels, rotation=90, fontsize=8)
    ax.set_xlim(-0.6, len(hour_labels) - 0.4)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color="#D9D9D9")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8)
    ax.tick_params(axis="y", labelsize=8)


# Create 1 row and 2 columns of charts (side by side like the sample)
fig, axes = plt.subplots(1, 2, figsize=(16, 5.2))

plot_ca_kpi(
    ax=axes[0],
    table=dl,
    title="DL CA User Ratio,%",
    y_max=25,
    y_step=5,
)
plot_ca_kpi(
    ax=axes[1],
    table=ul,
    title="UL CA User Ratio,%",
    y_max=2,
    y_step=0.2,
)

fig.tight_layout()
plt.show()
"""
)

md(
    """## Step 6 — Save the picture

This writes a PNG file you can put in a report, email, or PowerPoint.
"""
)

code(
    """from pathlib import Path

output_folder = Path("output")
output_folder.mkdir(exist_ok=True)
picture_path = output_folder / "ca_user_ratio_charts.png"

# Draw again and save. (plt.show() above already displayed it.)
fig.savefig(picture_path, dpi=160, bbox_inches="tight")
print("Saved:", picture_path.resolve())
"""
)

md(
    """## Step 7 — Optional: calculate the KPI from raw counters

In a live network you usually export **counters**, not the finished percentage.

Example:

| Date | Hour | Avg_RRC_Users | DL_CA_Users | UL_CA_Users |
|---|---|---|---|---|
| 27-Aug-26 | 00:00 | 4200 | 853 | 60 |

Then:

```text
DL CA User Ratio % = DL_CA_Users / Avg_RRC_Users * 100
UL CA User Ratio % = UL_CA_Users / Avg_RRC_Users * 100
```

Run the next cell to do that with the sample counter file.
"""
)

code(
    """raw = pd.read_csv("data/sample_ca_raw_counters.csv")

print("First 8 rows of raw counters:")
display(raw.head(8))

# Calculate the two KPIs. This is the most important formula in this notebook.
raw["DL_CA_User_Ratio"] = raw["DL_CA_Users"] / raw["Avg_RRC_Users"] * 100
raw["UL_CA_User_Ratio"] = raw["UL_CA_Users"] / raw["Avg_RRC_Users"] * 100

print("After adding the KPI columns:")
display(raw.head(8))
"""
)

md(
    """### Turn the long table into Excel-style wide tables

Raw OSS files are usually **long** (one row per hour per date). Charts like the sample need **wide** tables (one column per date). `pivot` does that.
"""
)

code(
    """dl_from_counters = raw.pivot(
    index="Hour",
    columns="Date",
    values="DL_CA_User_Ratio",
).reset_index()

ul_from_counters = raw.pivot(
    index="Hour",
    columns="Date",
    values="UL_CA_User_Ratio",
).reset_index()

# Keep the date columns in the same order as the sample
date_order = ["Hour", "27-Aug-26", "1-Sep-26", "2-Sep-26", "3-Sep-26"]
dl_from_counters = dl_from_counters[date_order]
ul_from_counters = ul_from_counters[date_order]

print("DL KPI built from counters (first 5 hours):")
display(dl_from_counters.head())
"""
)

md(
    """## Step 8 — Use YOUR own Excel file

Make a copy of `data/sample_ca_kpi.xlsx` and replace the numbers.

Rules (please follow them exactly):

1. Keep the two data sheets named `DL_CA_User_Ratio` and `UL_CA_User_Ratio`.
2. First column name must be **Hour**.
3. Other column names are the **dates** you want in the legend.
4. Put hours as `00:00`, `01:00`, ... `23:00`.
5. If today is incomplete, leave the empty cells blank. Do not write `0` unless the KPI is really zero.

Then change **only** the file name in the next cell and run it.
"""
)

code(
    """# -------------------------------------------------
# CHANGE THIS PATH to your own file when you are ready
# -------------------------------------------------
my_file = Path("data/sample_ca_kpi.xlsx")

my_book = pd.read_excel(my_file, sheet_name=None)
my_dl = my_book["DL_CA_User_Ratio"]
my_ul = my_book["UL_CA_User_Ratio"]

fig, axes = plt.subplots(1, 2, figsize=(16, 5.2))
plot_ca_kpi(axes[0], my_dl, "DL CA User Ratio,%", 25, 5)
plot_ca_kpi(axes[1], my_ul, "UL CA User Ratio,%", 2, 0.2)
fig.tight_layout()
plt.show()
"""
)

md(
    """## Step 9 — Reuse this for other RAN KPIs

The drawing function does not care that the KPI is CA. You can plot **any hourly RAN KPI** if you put it in the same table shape.

Examples:

| KPI | Typical Y-axis |
|---|---|
| DL PRB Utilization % | 0 to 100 |
| UL PRB Utilization % | 0 to 100 |
| RRC Setup Success Rate % | 98 to 100 (or 0 to 100) |
| ERAB Drop Rate % | 0 to 2 |
| Intra-freq HO Success Rate % | 95 to 100 |
| Average CQI | 0 to 15 |
| User Downlink Throughput (Mbps) | 0 to 80 |

Only two things usually change:

1. The Excel sheet / column you load
2. `y_max` and `y_step` so the chart is readable

Try this with the same sample DL table, but a different title and scale:
"""
)

code(
    """# This is only a demo of changing the title and Y-axis.
# Replace `dl` with your other KPI table when you have one.

fig, ax = plt.subplots(figsize=(10, 4.5))
plot_ca_kpi(
    ax=ax,
    table=dl,
    title="Replace this title with your KPI name",
    y_max=25,   # change this, for example 100 for PRB Utilization
    y_step=5,   # change this, for example 10 for PRB Utilization
)
fig.tight_layout()
plt.show()
"""
)

md(
    """## Common problems (read this if something fails)

**`FileNotFoundError`**  
Jupyter is open in the wrong folder. Close it, open the folder that contains `data`, then open the notebook again.

**`No module named pandas` (or matplotlib / openpyxl)**  
Run this in a cell: `!pip install pandas matplotlib openpyxl`

**The black line is missing after lunch time**  
That is expected if today's column has empty cells. Fill more hours, then run the chart cell again.

**Bars look too small / too tall**  
Change `y_max`. Example: PRB utilization should use `y_max=100`.

**Excel sheet name error**  
The names must match exactly, including capital letters and underscores: `DL_CA_User_Ratio`.

---

You can now:

1. Replace the sample Excel with your OSS export.
2. Press **Kernel → Restart & Run All**.
3. Pick up `output/ca_user_ratio_charts.png` for your report.
"""
)

nb["cells"] = cells
out = Path("/workspace/01_CA_User_Ratio_Beginner.ipynb")
out.write_text(nbf.writes(nb), encoding="utf-8")
print(f"Wrote {out} with {len(cells)} cells")
