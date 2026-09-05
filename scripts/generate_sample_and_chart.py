"""Generate sample RAN CA KPI data and a chart matching the user's Excel sample."""

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

# Diurnal shape taken from the attached Excel sample:
# DL dips overnight (~12-14% at 04:00-05:00), recovers to ~19-21% in the day.
# UL dips to ~0.5% at 05:00, then climbs toward ~1.8-1.9% in the evening.
DL_BASE = np.array(
    [
        20.1, 18.7, 16.4, 14.3, 12.9, 13.4, 15.6, 17.4,
        18.6, 19.5, 20.1, 20.4, 20.0, 19.7, 19.5, 19.6,
        19.8, 20.0, 19.8, 19.6, 20.0, 20.4, 20.7, 20.3,
    ]
)
UL_BASE = np.array(
    [
        1.42, 1.18, 0.94, 0.72, 0.58, 0.52, 0.68, 0.90,
        1.05, 1.16, 1.23, 1.28, 1.33, 1.38, 1.43, 1.48,
        1.54, 1.59, 1.64, 1.70, 1.75, 1.83, 1.88, 1.66,
    ]
)

# Small day-to-day offsets so the four dates are not identical.
DL_OFFSETS = {
    "27-Aug-26": np.array(
        [
            0.2, 0.3, 0.1, -0.2, 0.1, 0.2, 0.0, -0.1,
            0.2, 0.1, 0.0, -0.2, 0.1, 0.2, 0.0, -0.1,
            0.1, 0.0, 0.2, 0.1, -0.1, 0.0, 0.1, 0.2,
        ]
    ),
    "1-Sep-26": np.array(
        [
            -0.3, -0.1, 0.2, 0.3, 0.0, -0.2, 0.1, 0.2,
            -0.1, 0.0, 0.2, 0.1, -0.2, 0.0, 0.1, 0.2,
            0.0, -0.1, 0.1, 0.0, 0.2, 0.1, -0.2, 0.0,
        ]
    ),
    "2-Sep-26": np.array(
        [
            0.1, -0.2, 0.0, 0.1, 0.3, 0.1, -0.1, 0.0,
            0.1, -0.2, 0.1, 0.0, 0.2, -0.1, 0.0, 0.1,
            -0.2, 0.1, 0.0, 0.2, 0.0, -0.1, 0.1, 0.0,
        ]
    ),
    "3-Sep-26": np.array(
        [
            -0.1, 0.1, -0.2, 0.0, 0.2, -0.1, 0.2, 0.1,
            0.0, 0.2, -0.1, 0.1, 0.0, -0.2, 0.1, 0.0,
            0.1, 0.2, 0.0, -0.1, 0.1, 0.0, -0.2, 0.1,
        ]
    ),
}
UL_OFFSETS = {
    "27-Aug-26": np.array(
        [
            0.02, 0.03, 0.01, -0.02, 0.01, 0.02, 0.00, -0.01,
            0.02, 0.01, 0.00, -0.02, 0.01, 0.02, 0.00, -0.01,
            0.01, 0.00, 0.02, 0.01, -0.01, 0.00, 0.01, 0.02,
        ]
    ),
    "1-Sep-26": np.array(
        [
            -0.03, -0.01, 0.02, 0.03, 0.00, -0.02, 0.01, 0.02,
            -0.01, 0.00, 0.02, 0.01, -0.02, 0.00, 0.01, 0.02,
            0.00, -0.01, 0.01, 0.00, 0.02, 0.01, -0.02, 0.00,
        ]
    ),
    "2-Sep-26": np.array(
        [
            0.01, -0.02, 0.00, 0.01, 0.03, 0.01, -0.01, 0.00,
            0.01, -0.02, 0.01, 0.00, 0.02, -0.01, 0.00, 0.01,
            -0.02, 0.01, 0.00, 0.02, 0.00, -0.01, 0.01, 0.00,
        ]
    ),
    "3-Sep-26": np.array(
        [
            -0.01, 0.01, -0.02, 0.00, 0.02, -0.01, 0.02, 0.01,
            0.00, 0.02, -0.01, 0.01, 0.00, -0.02, 0.01, 0.00,
            0.01, 0.02, 0.00, -0.01, 0.01, 0.00, -0.02, 0.01,
        ]
    ),
}


def build_wide(base, offsets):
    frame = pd.DataFrame({"Hour": HOURS})
    for date in DATES:
        values = np.round(base + offsets[date], 2)
        if date == "3-Sep-26":
            # Partial day in the sample: line stops at 14:00.
            values = values.astype(float)
            values[15:] = np.nan
        frame[date] = values
    return frame


dl = build_wide(DL_BASE, DL_OFFSETS)
ul = build_wide(UL_BASE, UL_OFFSETS)

howto = pd.DataFrame(
    {
        "How_to_use_this_file": [
            "Keep sheet names exactly: DL_CA_User_Ratio and UL_CA_User_Ratio.",
            "First column name must be Hour, with values 00:00 to 23:00.",
            "Other columns are dates. Those names appear in the chart legend.",
            "Put the KPI in percent. Example: 20.3 means 20.3%.",
            "If a day is not finished, leave later hours blank. Do not fill 0.",
            "Open 01_CA_User_Ratio_Beginner.ipynb and run the cells with Shift+Enter.",
        ]
    }
)

# Excel workbook similar to what a RAN engineer would paste from OSS.
with pd.ExcelWriter(DATA / "sample_ca_kpi.xlsx", engine="openpyxl") as writer:
    howto.to_excel(writer, sheet_name="HowTo", index=False)
    dl.to_excel(writer, sheet_name="DL_CA_User_Ratio", index=False)
    ul.to_excel(writer, sheet_name="UL_CA_User_Ratio", index=False)

dl.to_csv(DATA / "dl_ca_user_ratio.csv", index=False)
ul.to_csv(DATA / "ul_ca_user_ratio.csv", index=False)

# Long-format raw counters so beginners can also learn the KPI formula.
rows = []
avg_users_profile = np.array(
    [
        4200, 3800, 3400, 3100, 2900, 3000, 3600, 4800,
        6200, 7100, 7600, 7800, 7500, 7400, 7300, 7400,
        7600, 7900, 8100, 8000, 7700, 7400, 6800, 5400,
    ]
)
for date, day_factor in zip(DATES, [1.00, 1.04, 0.97, 1.02]):
    avg_users = np.round(avg_users_profile * day_factor).astype(int)
    dl_ratio = (dl[date].to_numpy() / 100.0)
    ul_ratio = (ul[date].to_numpy() / 100.0)
    dl_ca_users = np.round(avg_users * dl_ratio)
    ul_ca_users = np.round(avg_users * ul_ratio)
    for i, hour in enumerate(HOURS):
        if date == "3-Sep-26" and i > 14:
            continue
        rows.append(
            {
                "Date": date,
                "Hour": hour,
                "Avg_RRC_Users": int(avg_users[i]),
                "DL_CA_Users": int(dl_ca_users[i]),
                "UL_CA_Users": int(ul_ca_users[i]),
            }
        )

raw = pd.DataFrame(rows)
raw.to_csv(DATA / "sample_ca_raw_counters.csv", index=False)

# Chart styled like the attached Excel sample.
BAR_DATES = DATES[:3]
LINE_DATE = DATES[3]
COLORS = {
    "27-Aug-26": "#92D050",  # Excel light green
    "1-Sep-26": "#FFC000",  # Excel gold
    "2-Sep-26": "#A6A6A6",  # Excel gray
    "3-Sep-26": "#000000",
}


def plot_combo(ax, frame, title, ymax, yticks):
    x = np.arange(len(HOURS))
    width = 0.25
    offsets = [-width, 0, width]
    for date, off in zip(BAR_DATES, offsets):
        ax.bar(
            x + off,
            frame[date],
            width=width,
            color=COLORS[date],
            edgecolor="white",
            linewidth=0.3,
            label=date,
            zorder=3,
        )
    ax.plot(
        x,
        frame[LINE_DATE],
        color=COLORS[LINE_DATE],
        linewidth=2.2,
        marker="o",
        markersize=4,
        label=LINE_DATE,
        zorder=4,
    )
    ax.set_title(title, fontsize=13, pad=10)
    ax.set_ylim(0, ymax)
    ax.set_yticks(yticks)
    ax.set_xticks(x)
    ax.set_xticklabels(HOURS, rotation=90, fontsize=8)
    ax.set_xlim(-0.6, 23.6)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color="#D9D9D9", zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=True, fontsize=8)
    ax.tick_params(axis="y", labelsize=8)


fig, axes = plt.subplots(1, 2, figsize=(16, 5.2))
plot_combo(axes[0], dl, "DL CA User Ratio,%", 25, range(0, 26, 5))
plot_combo(axes[1], ul, "UL CA User Ratio,%", 2, np.arange(0, 2.01, 0.2))
fig.tight_layout()
out_path = OUTPUT / "ca_user_ratio_charts.png"
fig.savefig(out_path, dpi=160, bbox_inches="tight")
print(f"Wrote {out_path}")
print(f"Wrote {DATA / 'sample_ca_kpi.xlsx'}")
print(f"Wrote {DATA / 'sample_ca_raw_counters.csv'}")
print(dl.head(3).to_string(index=False))
print(ul.head(3).to_string(index=False))
