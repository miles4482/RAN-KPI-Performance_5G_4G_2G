"""Create practice Excel files for a general RAN KPI dashboard.

The numbers are fake practice data only. Real network files can replace
this workbook later without changing the chart style.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
DATA.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

HOURS = [f"{h:02d}:00" for h in range(24)]
DATES = ["27-Aug-26", "1-Sep-26", "2-Sep-26", "3-Sep-26"]
SKIP_SHEETS = {"HowTo", "KPI_Settings"}

# Typical daily traffic shape: low at night, busy in the evening.
TRAFFIC = np.array(
    [
        0.26, 0.18, 0.13, 0.11, 0.10, 0.15, 0.30, 0.55,
        0.70, 0.76, 0.80, 0.82, 0.79, 0.77, 0.75, 0.78,
        0.86, 0.93, 0.98, 1.00, 0.94, 0.86, 0.68, 0.42,
    ]
)

# Small day-to-day mix so the four dates are not copies of each other.
DATE_MIX = {
    "27-Aug-26": TRAFFIC * 0.98 + 0.01,
    "1-Sep-26": TRAFFIC * 1.03 - 0.01,
    "2-Sep-26": TRAFFIC * 0.96 + 0.02,
    "3-Sep-26": TRAFFIC * 1.01,
}


def clip_round(values, decimals, low=None, high=None):
    out = np.round(values, decimals)
    if low is not None:
        out = np.maximum(out, low)
    if high is not None:
        out = np.minimum(out, high)
    return out


def wide_from_traffic(formula, decimals, low=None, high=None):
    frame = pd.DataFrame({"Hour": HOURS})
    for date in DATES:
        values = formula(DATE_MIX[date])
        values = clip_round(values, decimals, low, high).astype(float)
        if date == "3-Sep-26":
            values[15:] = np.nan
        frame[date] = values
    return frame


KPI_LIST = [
    {
        "sheet": "RRC_Setup_Success_Rate",
        "title": "RRC Setup Success Rate,%",
        "y_min": 98,
        "y_max": 100,
        "y_step": 0.5,
        "decimals": 2,
        "low": 98.0,
        "high": 100.0,
        "formula": lambda t: 99.95 - 0.70 * t,
    },
    {
        "sheet": "ERAB_Setup_Success_Rate",
        "title": "ERAB Setup Success Rate,%",
        "y_min": 98,
        "y_max": 100,
        "y_step": 0.5,
        "decimals": 2,
        "low": 98.0,
        "high": 100.0,
        "formula": lambda t: 99.90 - 0.55 * t,
    },
    {
        "sheet": "ERAB_Drop_Rate",
        "title": "ERAB Drop Rate,%",
        "y_min": 0,
        "y_max": 1.0,
        "y_step": 0.1,
        "decimals": 2,
        "low": 0.0,
        "high": 2.0,
        "formula": lambda t: 0.08 + 0.35 * t,
    },
    {
        "sheet": "Intra_HO_Success_Rate",
        "title": "Intra-freq HO Success Rate,%",
        "y_min": 96,
        "y_max": 100,
        "y_step": 1,
        "decimals": 2,
        "low": 95.0,
        "high": 100.0,
        "formula": lambda t: 99.65 - 1.10 * t,
    },
    {
        "sheet": "DL_PRB_Utilization",
        "title": "DL PRB Utilization,%",
        "y_min": 0,
        "y_max": 100,
        "y_step": 10,
        "decimals": 1,
        "low": 0.0,
        "high": 100.0,
        "formula": lambda t: 12 + 68 * t,
    },
    {
        "sheet": "UL_PRB_Utilization",
        "title": "UL PRB Utilization,%",
        "y_min": 0,
        "y_max": 100,
        "y_step": 10,
        "decimals": 1,
        "low": 0.0,
        "high": 100.0,
        "formula": lambda t: 7 + 38 * t,
    },
    {
        "sheet": "User_DL_Throughput_Mbps",
        "title": "User DL Throughput, Mbps",
        "y_min": 0,
        "y_max": 50,
        "y_step": 10,
        "decimals": 1,
        "low": 0.0,
        "high": 80.0,
        "formula": lambda t: 42 - 28 * t,
    },
    {
        "sheet": "Cell_Availability",
        "title": "Cell Availability,%",
        "y_min": 99.0,
        "y_max": 100,
        "y_step": 0.2,
        "decimals": 3,
        "low": 99.0,
        "high": 100.0,
        "formula": lambda t: 99.98 - 0.04 * t,
    },
]

tables = {}
settings_rows = []
for kpi in KPI_LIST:
    tables[kpi["sheet"]] = wide_from_traffic(
        kpi["formula"], kpi["decimals"], kpi["low"], kpi["high"]
    )
    settings_rows.append(
        {
            "Sheet_Name": kpi["sheet"],
            "Title": kpi["title"],
            "Y_Min": kpi["y_min"],
            "Y_Max": kpi["y_max"],
            "Y_Step": kpi["y_step"],
        }
    )

settings = pd.DataFrame(settings_rows)
howto = pd.DataFrame(
    {
        "How_to_use_this_file": [
            "This workbook is PRACTICE data. Replace it later with your live OSS Excel.",
            "One sheet = one KPI. Sheet name must match KPI_Settings column Sheet_Name.",
            "First column name must be Hour, with values 00:00 to 23:00.",
            "Other columns are dates. Those names appear in the chart legend.",
            "Green / yellow / gray bars = earlier dates. Black line = last date column.",
            "If a day is not finished, leave later hours blank. Do not fill 0.",
            "KPI_Settings controls the chart title and Y-axis for every sheet.",
            "Add more KPI sheets any time. The notebook will draw them automatically.",
            "If your real Excel layout is different, keep the file. We will adapt the code.",
        ]
    }
)

dashboard_path = DATA / "sample_ran_kpi_dashboard.xlsx"
with pd.ExcelWriter(dashboard_path, engine="openpyxl") as writer:
    howto.to_excel(writer, sheet_name="HowTo", index=False)
    settings.to_excel(writer, sheet_name="KPI_Settings", index=False)
    for kpi in KPI_LIST:
        tables[kpi["sheet"]].to_excel(writer, sheet_name=kpi["sheet"], index=False)

# Empty template the user can copy when their real file is ready.
empty = pd.DataFrame({"Hour": HOURS})
for date in ["Date1", "Date2", "Date3", "Date4"]:
    empty[date] = np.nan

template_settings = pd.DataFrame(
    [
        {
            "Sheet_Name": "KPI_1",
            "Title": "Rename this title",
            "Y_Min": 0,
            "Y_Max": 100,
            "Y_Step": 10,
        },
        {
            "Sheet_Name": "KPI_2",
            "Title": "Rename this title",
            "Y_Min": 0,
            "Y_Max": 100,
            "Y_Step": 10,
        },
    ]
)
template_howto = pd.DataFrame(
    {
        "How_to_use_this_file": [
            "Copy this file and rename it, for example my_ran_kpis.xlsx.",
            "Put one KPI on each sheet. Use the same Hour + date-column layout.",
            "Change KPI_Settings so Sheet_Name, Title, and Y-axis match your KPIs.",
            "You may add more sheets. Also add a matching row in KPI_Settings.",
            "If your OSS export looks different, send the file and we will adapt.",
        ]
    }
)
template_path = DATA / "YOUR_KPI_TEMPLATE.xlsx"
with pd.ExcelWriter(template_path, engine="openpyxl") as writer:
    template_howto.to_excel(writer, sheet_name="HowTo", index=False)
    template_settings.to_excel(writer, sheet_name="KPI_Settings", index=False)
    empty.to_excel(writer, sheet_name="KPI_1", index=False)
    empty.to_excel(writer, sheet_name="KPI_2", index=False)

BAR_COLORS = ["#92D050", "#FFC000", "#A6A6A6", "#5B9BD5", "#ED7D31"]


def plot_kpi(ax, table, title, y_min, y_max, y_step, show_legend=True):
    hour_labels = table["Hour"].astype(str)
    date_columns = [col for col in table.columns if col != "Hour"]
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
            label=date,
            zorder=3,
        )
    ax.plot(
        x,
        table[line_date],
        color="#000000",
        linewidth=2.2,
        marker="o",
        markersize=3.5,
        label=line_date,
        zorder=4,
    )
    ax.set_title(title, fontsize=11, pad=8)
    ax.set_ylim(y_min, y_max)
    ax.set_yticks(np.arange(y_min, y_max + (y_step / 10), y_step))
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


n_kpis = len(KPI_LIST)
n_cols = 2
n_rows = int(np.ceil(n_kpis / n_cols))
fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4.6 * n_rows))
axes = np.atleast_2d(axes)
for i, kpi in enumerate(KPI_LIST):
    row, col = divmod(i, n_cols)
    plot_kpi(
        axes[row, col],
        tables[kpi["sheet"]],
        kpi["title"],
        kpi["y_min"],
        kpi["y_max"],
        kpi["y_step"],
        show_legend=False,
    )
for j in range(n_kpis, n_rows * n_cols):
    row, col = divmod(j, n_cols)
    axes[row, col].axis("off")

handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=4, frameon=True, fontsize=9, bbox_to_anchor=(0.5, 1.0))
fig.suptitle("RAN KPI Dashboard (practice data)", fontsize=16, y=1.02)
fig.tight_layout(rect=[0, 0, 1, 0.97])
out_path = OUTPUT / "ran_kpi_dashboard.png"
fig.savefig(out_path, dpi=140, bbox_inches="tight")
print(f"Wrote {dashboard_path}")
print(f"Wrote {template_path}")
print(f"Wrote {out_path}")
print("Sheets:", [k["sheet"] for k in KPI_LIST])
