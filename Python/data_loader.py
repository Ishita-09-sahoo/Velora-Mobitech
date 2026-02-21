import pandas as pd
from datetime import time


def normalize_time_to_minutes(x):
    if pd.isna(x):
        return None

    if isinstance(x, (int, float)):
        return int(round(x * 24 * 60))

    if isinstance(x, time):
        return x.hour * 60 + x.minute

    if isinstance(x, pd.Timestamp):
        return x.hour * 60 + x.minute

    if isinstance(x, str):
        h, m = x.strip().split(":")
        return int(h) * 60 + int(m)

    raise ValueError(f"Unknown time format: {x}")


def load_data(FILE):

    employees = pd.read_excel(FILE, sheet_name=0)
    vehicles = pd.read_excel(FILE, sheet_name=1)
    baseline = pd.read_excel(FILE, sheet_name=2)
    metadata = pd.read_excel(FILE, sheet_name=3)

    employees["earliest_pickup"] = employees["earliest_pickup"].apply(
        normalize_time_to_minutes)
    employees["latest_drop"] = employees["latest_drop"].apply(
        normalize_time_to_minutes)

    vehicles["available_from"] = vehicles["available_from"].apply(
        normalize_time_to_minutes)

    meta_dict = dict(zip(metadata["key"], metadata["value"]))

    max_delay = {
        int(k.split("_")[1]): float(v)
        for k, v in meta_dict.items()
        if k.startswith("priority_") and k.endswith("_max_delay_min")
    }

    return employees, vehicles, baseline, meta_dict, max_delay
