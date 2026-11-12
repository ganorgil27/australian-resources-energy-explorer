#!/usr/bin/env python3
"""Validate and flatten the Geoscience Australia operating-mines extract."""

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "ga-operating-mines.json"
OUTPUT = ROOT / "data" / "clean" / "operating_mines.csv"

STATE_NAMES = {
    "NSW": "New South Wales",
    "NT": "Northern Territory",
    "QLD": "Queensland",
    "SA": "South Australia",
    "TAS": "Tasmania",
    "VIC": "Victoria",
    "WA": "Western Australia",
    "IOT": "Indian Ocean Territories",
}


def commodity_name(group: str) -> str:
    """Map the publisher's detailed groups to a small report-friendly dimension."""
    rules = (
        ("Iron ore", "Iron ore"),
        ("Coal", "Coal"),
        ("Precious metals", "Gold & silver"),
        ("Battery/alloy metals - Li", "Lithium"),
        ("Battery/alloy metals - Ni", "Nickel"),
        ("Base metals - Cu", "Copper & base metals"),
        ("Base metals - Zn", "Zinc & lead"),
        ("Bauxite", "Bauxite"),
        ("Heavy mineral sands", "Mineral sands"),
        ("Uranium", "Uranium"),
        ("Manganese", "Manganese"),
        ("Rare earth", "Rare earths"),
    )
    return next((label for prefix, label in rules if group.startswith(prefix)), "Other")


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = [feature["attributes"] for feature in payload["features"]]

    required = {
        "objectid", "name", "state", "latitude", "longitude",
        "status", "commodity_group", "source",
    }
    assert rows, "No mine records found"
    assert required <= rows[0].keys(), "Required source fields are missing"
    assert len(rows) == len({row["objectid"] for row in rows}), "Duplicate object IDs"
    assert not any(row[field] is None for row in rows for field in required), "Null required value"
    assert set(row["state"] for row in rows) <= STATE_NAMES.keys(), "Unknown state code"
    assert all(-90 <= row["latitude"] <= 90 for row in rows), "Invalid latitude"
    assert all(-180 <= row["longitude"] <= 180 for row in rows), "Invalid longitude"

    clean = []
    for row in rows:
        clean.append({
            "MineKey": row["objectid"],
            "MineName": row["name"].strip(),
            "StateCode": row["state"],
            "RegionName": STATE_NAMES[row["state"]],
            "CommodityName": commodity_name(row["commodity_group"]),
            "CommodityGroupSource": row["commodity_group"],
            "Latitude": row["latitude"],
            "Longitude": row["longitude"],
            "Status": row["status"],
            "Source": row["source"],
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=clean[0].keys())
        writer.writeheader()
        writer.writerows(clean)

    print(f"Wrote {len(clean)} records to {OUTPUT.relative_to(ROOT)}")
    print("Regions:", dict(sorted(Counter(row["RegionName"] for row in clean).items())))
    print("Commodities:", dict(Counter(row["CommodityName"] for row in clean).most_common()))


if __name__ == "__main__":
    main()

