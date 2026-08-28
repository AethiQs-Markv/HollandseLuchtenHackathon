#!/usr/bin/env python3
"""Enrich sensor_metadata.csv with coordinates and KNMI station codes.

Fetches each Thing's Locations and properties.knmicode from the Samen Meten API
and back-fills latitude, longitude, and knmicode into sensor_metadata.csv.

Usage:
    python data_scripts/enrich_metadata.py
    python data_scripts/enrich_metadata.py \\
        --metadata data_exports/full/sensor_metadata.csv \\
        --base-url https://api-samenmeten.rivm.nl/v1.0 \\
        --sleep-s 0.1
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://api-samenmeten.rivm.nl/v1.0"


def _get(url: str) -> Dict[str, Any]:
    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _to_float(v: Any) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def fetch_thing_enrichment(
    base_url: str,
    thing_id: str,
    sleep_s: float,
) -> Dict[str, Any]:
    """Return dict with lat, lon, knmicode for a Thing ID."""
    result: Dict[str, Any] = {"lat": None, "lon": None, "knmicode": ""}

    # Fetch Thing properties for knmicode.
    thing_url = f"{base_url}/Things({thing_id})?$select=properties"
    thing_data = _get(thing_url)
    props = thing_data.get("properties") or {}
    knmicode = str(props.get("knmicode") or "").strip()
    result["knmicode"] = knmicode

    if sleep_s > 0:
        time.sleep(sleep_s)

    # Fetch linked Locations for coordinates.
    locs_url = f"{base_url}/Things({thing_id})/Locations?$top=1&$select=location"
    locs_data = _get(locs_url)
    for loc in (locs_data.get("value") or []):
        geo = loc.get("location") or {}
        coords = geo.get("coordinates") or []
        if len(coords) >= 2:
            result["lon"] = _to_float(coords[0])
            result["lat"] = _to_float(coords[1])
        break

    return result


def enrich(metadata_path: Path, base_url: str, sleep_s: float) -> None:
    with metadata_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames: List[str] = list(reader.fieldnames or [])
        rows = list(reader)

    if not rows:
        print("Metadata file is empty.")
        return

    # Add knmicode column if missing.
    if "knmicode" not in fieldnames:
        # Insert after intended_reference_station_id if present, else append.
        try:
            idx = fieldnames.index("intended_reference_station_id")
            fieldnames.insert(idx + 1, "knmicode")
        except ValueError:
            fieldnames.append("knmicode")

    enriched = 0
    for i, row in enumerate(rows):
        sensor_id = (row.get("sensor_id") or "").strip()
        if not sensor_id:
            continue

        already_has_coords = (row.get("latitude") or "").strip() and (row.get("longitude") or "").strip()
        already_has_knmi = (row.get("knmicode") or "").strip()
        if already_has_coords and already_has_knmi:
            continue  # nothing to fill in

        print(f"  Enriching sensor {sensor_id} ({i + 1}/{len(rows)})...")
        try:
            info = fetch_thing_enrichment(base_url, sensor_id, sleep_s=sleep_s)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"    Warning: {exc}")
            continue

        if not already_has_coords:
            if info["lat"] is not None:
                row["latitude"] = info["lat"]
            if info["lon"] is not None:
                row["longitude"] = info["lon"]
        if not already_has_knmi and info["knmicode"]:
            row["knmicode"] = info["knmicode"]

        enriched += 1

        if sleep_s > 0:
            time.sleep(sleep_s)

    # Back up original.
    bak_path = metadata_path.with_suffix(".csv.bak")
    import shutil
    shutil.copy2(metadata_path, bak_path)
    print(f"Backup saved: {bak_path}")

    with metadata_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            # Ensure all new columns have a default.
            row.setdefault("knmicode", "")
            writer.writerow(row)

    print(f"Enriched {enriched}/{len(rows)} sensors.")
    print(f"Wrote: {metadata_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enrich sensor_metadata.csv with coordinates and knmicode")
    parser.add_argument("--metadata", default="data_exports/full/sensor_metadata.csv")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--sleep-s", type=float, default=0.15)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    path = Path(args.metadata)
    if not path.exists():
        print(f"Metadata file not found: {path}")
        return 2
    enrich(path, base_url=args.base_url, sleep_s=args.sleep_s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
