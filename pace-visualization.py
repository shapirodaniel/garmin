import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.axes import Axes
from matplotlib import figure


def pace_formatter(x, pos=None):
    mins = int(x // 60)
    secs = int(x % 60)
    return f"{mins}:{secs:02d}"


def plot(ax: Axes, df: pd.DataFrame, title: str):
    ax.plot(
        df["Date"],
        df["Avg Pace"],
        marker="o",
        linestyle="-",
        color="b",
    )
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Pace (min:sec)")
    ax.xaxis.set_tick_params(rotation=45)
    ax.grid(True)
    ax.yaxis.set_major_formatter(FuncFormatter(pace_formatter))


for hr_zone in range(0, 6):
    with open(f"./zone-{hr_zone}-runs.csv") as hr_zone_runs_csv:
        hr_zone_runs = pd.read_csv(hr_zone_runs_csv)
        if hr_zone_runs.size < 2:
            continue

        hr_zone_runs["Date"] = pd.to_datetime(hr_zone_runs["Date"])

        hr_zone_runs["Avg Pace"] = pd.to_timedelta(
            "00:" + hr_zone_runs["Avg Pace"]
        ).dt.total_seconds()

        df_less_than_5_miles = hr_zone_runs[(hr_zone_runs["Distance"] < 5)]
        df_5_to_10_miles = hr_zone_runs[
            (hr_zone_runs["Distance"] >= 5) & (hr_zone_runs["Distance"] <= 10)
        ]
        df_greater_than_10_miles = hr_zone_runs[hr_zone_runs["Distance"] > 10]

        plt.rc("font", size=8)

        fig: figure
        ax1: Axes
        ax2: Axes
        ax3: Axes
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 6))

        plot(ax1, df_less_than_5_miles, f"< 5 Mile Runs - Zone {hr_zone}")
        plot(ax2, df_5_to_10_miles, f"5-10 Mile Runs - Zone {hr_zone}")
        plot(ax3, df_greater_than_10_miles, f"10+ Mile Runs - Zone {hr_zone}")

        # Adjust layout
        plt.tight_layout()
        plt.show()
