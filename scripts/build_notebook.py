"""Build the beginner RAN KPI dashboard notebook."""

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
    """# RAN KPI Dashboard in Python (Beginner Guide)

This notebook builds a **dashboard of many RAN KPIs**, using the same chart style as a typical Excel report:

- Green / yellow / gray **bars** = previous days
- Black **line** = latest day (a partial day is OK)
- **One sheet = one KPI**
- The code does **not** care which KPI it is. RRC success, drop rate, PRB utilization, throughput, CA, availability... same method.

Today we use **practice data** so you can learn the steps.

Later you will send a sample Excel from your network. We will plug that file in. If the layout is different, we will adapt the code. You do not need to force your OSS export to match today.

Work slowly:

1. Click the first cell.
2. Press **Shift + Enter**.
3. Wait until it finishes.
4. Go to the next cell and repeat.

If a cell turns **red**, stop and read the last line of the error.
"""
)

md(
    """## Step 0 — Install the tools (run this once)

| Package | What it does |
|---|---|
| `pandas` | Reads Excel tables |
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
"""
)

code(
    """from pathlib import Path

from IPython.display import display
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

%matplotlib inline

print("Libraries loaded.")
print("pandas version:", pd.__version__)
"""
)

md(
    """## Step 2 — The idea: one chart style for every KPI

A RAN dashboard is many small charts, not one special CA chart.

Each KPI table looks like this:

| Hour | 27-Aug-26 | 1-Sep-26 | 2-Sep-26 | 3-Sep-26 |
|---|---|---|---|---|
| 00:00 | ... | ... | ... | ... |
| 01:00 | ... | ... | ... | ... |
| 23:00 | ... | ... | ... | ... |

Rules:

- Column 1 is always **Hour**
- Other columns are **dates** (those names become the legend)
- Last date column is drawn as the **black line**
- Earlier date columns are drawn as **bars**
- Empty cells mean "no data yet"

The KPI **name** only changes:

- the Excel sheet name
- the chart title
- the Y-axis (0-100 for utilization, 98-100 for success rate, 0-50 for throughput, and so on)
"""
)

md(
    """## Step 3 — Point to the Excel file

This is the only path you will change later, when your real file arrives.

Today we use the practice workbook.
"""
)

code(
    """# -------------------------------------------------
# LATER: change this path to your own Excel file
# -------------------------------------------------
excel_path = Path("data/sample_ran_kpi_dashboard.xlsx")

if not excel_path.exists():
    raise FileNotFoundError(
        "I cannot find the Excel file.\\n"
        "Open Jupyter from the project folder (the folder that contains data/)."
    )

print("Using file:", excel_path.resolve())
"""
)

md(
    """## Step 4 — Open the workbook and list the sheets

`sheet_name=None` means: load **all** tabs.
"""
)

code(
    """workbook = pd.read_excel(excel_path, sheet_name=None)

print("Sheets in this Excel file:")
for name in workbook:
    print(" -", name)
"""
)

md(
    """## Step 5 — Read the KPI settings table

`KPI_Settings` tells Python how to draw each sheet:

- `Sheet_Name` = Excel tab name
- `Title` = text on the chart
- `Y_Min`, `Y_Max`, `Y_Step` = Y-axis scale

This is how one notebook can plot **all** KPIs without rewriting code for each one.
"""
)

code(
    """SKIP_SHEETS = {"HowTo", "KPI_Settings", "ReadMe", "Template"}

settings = workbook["KPI_Settings"].copy()
display(settings)

kpi_sheets = [name for name in workbook if name not in SKIP_SHEETS]
print("\\nKPI data sheets:")
for name in kpi_sheets:
    print(" -", name, " size:", workbook[name].shape)
"""
)

md(
    """## Step 6 — Look at one KPI table

Always look before you plot. Pick any sheet name from the list above.
"""
)

code(
    """one_sheet_name = kpi_sheets[0]
one_table = workbook[one_sheet_name]

print("Sheet:", one_sheet_name)
display(one_table.head(8))
print("...")
display(one_table.tail(3))
"""
)

md(
    """## Step 7 — The chart function (works for any KPI)

You do not need to understand every line today. The important part is:

- bars for earlier dates
- line for the last date
- title and Y-axis come from `KPI_Settings`
"""
)

code(
    """BAR_COLORS = ["#92D050", "#FFC000", "#A6A6A6", "#5B9BD5", "#ED7D31"]


def plot_kpi(ax, table, title, y_min, y_max, y_step, show_legend=True):
    hour_labels = table["Hour"].astype(str)
    date_columns = [col for col in table.columns if str(col) != "Hour"]
    bar_dates = date_columns[:-1]
    line_date = date_columns[-1]

    x = np.arange(len(hour_labels))
    bar_width = 0.8 / max(len(bar_dates), 1)

    for i, date in enumerate(bar_dates):
        offset = (i - (len(bar_dates) - 1) / 2) * bar_width
        ax.bar(
            x + offset,
            table[date],
            width=bar_width * 0.92,
            color=BAR_COLORS[i % len(BAR_COLORS)],
            edgecolor="white",
            linewidth=0.3,
            label=str(date),
            zorder=3,
        )

    ax.plot(
        x,
        table[line_date],
        color="#000000",
        linewidth=2.2,
        marker="o",
        markersize=3.5,
        label=str(line_date),
        zorder=4,
    )

    ax.set_title(title, fontsize=11, pad=8)
    ax.set_ylim(y_min, y_max)
    ax.set_yticks(np.arange(y_min, y_max + (y_step / 2), y_step))
    ax.set_xticks(x)
    ax.set_xticklabels(hour_labels, rotation=90, fontsize=7)
    ax.set_xlim(-0.6, len(hour_labels) - 0.4)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color="#D9D9D9")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if show_legend:
        ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=7)
    ax.tick_params(axis="y", labelsize=7)


print("Chart function is ready.")
"""
)

md(
    """## Step 8 — Draw ONE KPI first

We start with one chart so you can see the style clearly. Then we draw the full dashboard.
"""
)

code(
    """def settings_for(sheet_name):
    match = settings[settings["Sheet_Name"] == sheet_name]
    if len(match) == 0:
        raise KeyError("Sheet " + sheet_name + " is missing from KPI_Settings.")
    row = match.iloc[0]
    return row["Title"], float(row["Y_Min"]), float(row["Y_Max"]), float(row["Y_Step"])


title, y_min, y_max, y_step = settings_for(one_sheet_name)

fig, ax = plt.subplots(figsize=(10, 4.2))
plot_kpi(ax, one_table, title, y_min, y_max, y_step)
fig.tight_layout()
plt.show()
"""
)

md(
    """## Step 9 — Draw the full dashboard (all KPI sheets)

This loop is the heart of the dashboard:

1. Take every KPI sheet
2. Read its title and Y-axis from `KPI_Settings`
3. Draw it in a 2-column grid
"""
)

code(
    """n_kpis = len(kpi_sheets)
n_cols = 2
n_rows = int(np.ceil(n_kpis / n_cols))

fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4.6 * n_rows))
axes = np.atleast_2d(axes)

for i, sheet_name in enumerate(kpi_sheets):
    row, col = divmod(i, n_cols)
    title, y_min, y_max, y_step = settings_for(sheet_name)
    plot_kpi(
        axes[row, col],
        workbook[sheet_name],
        title,
        y_min,
        y_max,
        y_step,
        show_legend=False,
    )

# Hide leftover empty boxes if the last row is not full
for j in range(n_kpis, n_rows * n_cols):
    row, col = divmod(j, n_cols)
    axes[row, col].axis("off")

handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    loc="upper center",
    ncol=4,
    frameon=True,
    fontsize=9,
    bbox_to_anchor=(0.5, 1.0),
)
fig.suptitle("RAN KPI Dashboard", fontsize=16, y=1.02)
fig.tight_layout(rect=[0, 0, 1, 0.97])
plt.show()
"""
)

md(
    """## Step 10 — Save the dashboard picture

You can put this PNG in a report, email, or PowerPoint.
"""
)

code(
    """output_folder = Path("output")
output_folder.mkdir(exist_ok=True)
picture_path = output_folder / "ran_kpi_dashboard.png"

fig.savefig(picture_path, dpi=140, bbox_inches="tight")
print("Saved:", picture_path.resolve())
"""
)

md(
    """## Step 11 — Add or replace KPIs

You do **not** change Python to add a KPI. You change Excel:

1. Add a new sheet with `Hour` + date columns.
2. Add one row in `KPI_Settings` for that sheet.
3. Run **Kernel → Restart & Run All**.

To replace practice data with live network data later:

1. Save your OSS Excel into the `data` folder.
2. Change `excel_path` in Step 3.
3. Make sure `KPI_Settings` lists every data sheet.
4. Run all cells again.

If your file looks different (long format, vendor counter names, many objects, not hourly), **keep the file as it is**. Send it later and we will add a conversion step. Do not spend time reshaping it by hand unless you want to.
"""
)

code(
    """print("Practice file in use:", excel_path)
print("Number of KPI charts:", n_kpis)
print()
print("When your Excel is ready, put it in the data folder and change excel_path.")
print("Template you can copy: data/YOUR_KPI_TEMPLATE.xlsx")
"""
)

md(
    """## Common problems

**`FileNotFoundError`**  
Jupyter is open in the wrong folder. Open the folder that contains `data`, then open this notebook.

**`No module named pandas`**  
Run: `!pip install pandas matplotlib openpyxl`

**A chart Y-axis looks too tight or too tall**  
Change `Y_Min`, `Y_Max`, `Y_Step` in the `KPI_Settings` sheet, save Excel, run again.

**The black line stops in the afternoon**  
That is normal if the last date has empty cells.

**Sheet name error**  
`Sheet_Name` in `KPI_Settings` must match the Excel tab name exactly.

---

You now have a dashboard engine. Next time you send a sample Excel, we will connect it here.
"""
)

nb["cells"] = cells
out = Path("/workspace/01_RAN_KPI_Dashboard_Beginner.ipynb")
out.write_text(nbf.writes(nb), encoding="utf-8")
print(f"Wrote {out} with {len(cells)} cells")
