import csv
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing_extensions import List, Tuple
from pprint import pprint

# 1 = Date (YYYY-MM-DD HH:MM:SS)
# 4 = Distance (mi)
# 6 = Time (HH:MM:SS)
# 7 = Avg HR
# 12 = Avg Pace (MM:SS)
SCHEMA = [
    "Activity Type",
    "Date",
    "Favorite",
    "Title",
    "Distance",
    "Calories",
    "Time",
    "Avg HR",
    "Max HR",
    "Aerobic TE",
    "Avg Run Cadence",
    "Max Run Cadence",
    "Avg Pace",
    "Best Pace",
    "Total Ascent",
    "Total Descent",
    "Avg Stride Length",
    "Avg Vertical Ratio",
    "Avg Vertical Oscillation",
    "Avg Ground Contact Time",
    "Normalized Power® (NP®)",
    "Training Stress Score®",
    "Avg Power",
    "Max Power",
    "Grit",
    "Flow",
    "Avg. Swolf",
    "Avg Stroke Rate",
    "Total Reps",
    "Decompression",
    "Best Lap Time",
    "Number of Laps",
    "Max Temp",
    "Moving Time",
    "Elapsed Time",
    "Min Elevation",
    "Max Elevation",
]

# use schema defined above
headers = [["Date", "Distance", "Time", "Avg HR", "Avg Pace"]]
data = []


def sumData(index):
    return sum([float(row[index]) for row in data[1:]])


def avgData(index):
    return sumData(index) / (len(data) - 1)


def formatPace(pace: timedelta):
    [m, s] = str(pace).split(":")[1:]
    s = s.split(".")[0]
    return m + ":" + s


def avgPace(bucket: List[str] | None = None):
    avg = timedelta()
    pace = (
        [row[4] for row in data[1:] if float(row[3]) > 138]
        if bucket is None
        else bucket
    )
    for interval in pace:
        (m, s) = interval.split(":")
        d = timedelta(minutes=int(m), seconds=int(s))
        avg += d
    return formatPace(avg / len(pace))


def toDatetime(datestring):
    return datetime.strptime(datestring, "%Y-%m-%d")


def extractYYYYMMDD(date: timedelta):
    return str(date).split(" ")[0]


def weeklyAvgPace():
    date_bucketed_pace_list = [
        [row[i] for i in range(len(row)) if i in [0, 4]]
        for row in data[1:]
        if float(row[3]) >= 138
    ]

    dates_and_paces: List[Tuple[timedelta, str]] = [
        (toDatetime(row[0].split(" ")[0]), row[1]) for row in date_bucketed_pace_list
    ]
    dates_and_paces.reverse()

    (init_date, init_pace) = dates_and_paces[0]
    buckets = defaultdict()
    week = [init_pace]
    index = 1
    week_start = init_date

    while index < len(dates_and_paces):
        (current_date, current_pace) = dates_and_paces[index]
        if current_date >= week_start + timedelta(days=7):
            buckets.setdefault(current_date, week)
            week = [current_pace]
            week_start = current_date
        else:
            week.append(current_pace)
        index += 1

    return {extractYYYYMMDD(i): avgPace(buckets[i]) for i in buckets}


def printStat(name, stat):
    print(f"\n{name}:")
    pprint(stat, width=60)


# Get Garmin Connect activities data
print("Copying activities data to local dir...")
os.system("mv ~/Downloads/Activities.csv ./activities.csv")
print("Successfully moved and renamed ~/Downloads/Activities.csv -> ./activities.csv")

# Process data
print("Processing Garmin activities data...")
with open("./activities.csv") as activities:
    reader = csv.reader(activities)

    for i, row in enumerate(reader):
        if i == 0:
            continue

        if row[0] == "Running":
            data.append([row[x] for x in range(len(row)) if x in [1, 4, 6, 7, 12]])

with open("./all-runs.csv", "w") as all_runs:
    writer = csv.writer(all_runs)
    writer.writerows(headers)
    writer.writerows(data)
print("[SUCCESS] extracted all run data and wrote to csv")

with open("./long-runs.csv", "w") as long_runs:
    writer = csv.writer(long_runs)
    writer.writerows(headers)
    writer.writerows([r for r in data if r[1] != "Distance" and float(r[1]) >= 7])
print("[SUCCESS] extracted long run data and wrote to csv")

hr_zones = [
    (0, 99),
    (99, 119),
    (119, 139),
    (139, 159),
    (159, 179),
    (179, 199),  # 199 == Max HR
]

for i, (bottom, top) in enumerate(hr_zones):
    with open(f"./zone-{i}-runs.csv", "w") as hr_zone_runs:
        writer = csv.writer(hr_zone_runs)
        writer.writerows(headers)
        writer.writerows(
            [
                r
                for r in data
                if r[1] != "Distance" and float(r[3]) >= bottom and float(r[3]) < top
            ]
        )
    print(f"[SUCCESS] extracted zone {i} run data and wrote to csv")

with open("./avg-pace.csv", "w") as avg_pace:
    writer = csv.writer(avg_pace)
    writer.writerows([["Date", "Avg Pace"]])
    writer.writerows(list(weeklyAvgPace().items()))
print("[SUCCESS] extracted weekly avg pace data and wrote to csv")

print("\n/* --- STATS --- */")

printStat("Total mileage", sumData(1))
printStat("Avg heart rate", avgData(3))
printStat("Weekly avg pace", list(weeklyAvgPace().items()))

print("\n/* ------------- */\n")
