#!/usr/bin/env python3
"""Merge KNMI wind samples into sensor_observations_long.csv.

Fills the wind_speed_mps and wind_direction_deg columns in the air-quality
observation CSV by matching each row to the nearest KNMI 10-minute reading
within the same sensor_id and hour bucket.

Usage:
    python data_scripts/merge_wind.py

    python data_scripts/merge_wind.py \\
        --obs     data_exports/full/sensor_observations_long.csv \\
        --wind    data_exports/knmi/knmi_wind_samples.csv \\
        --out     data_exports/full/sensor_observations_long.csv \\
        --max-gap-minutes 60

The script writes a backup of the original observations file before overwriting.
If --out points to the same file as --obs, the original is saved as <file>.bak.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _parse_iso(value: str) -> Optional[datetime]:
    if not value:
        return None
    text = value.strip()
    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _hour_bucket_key(dt: datetime) -> str:
    """Round down to hour, return ISO string as dict key."""
    floored = dt.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    return floored.isoformat()


def _to_float(value: str) -> Optional[float]:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def load_wind_index(
    wind_path: Path,
) -> Dict[Tuple[str, str], List[Tuple[datetime, float, float]]]:
    """Return {(sensor_id, hour_bucket_iso): [(dt, wind_speed, wind_dir), ...]}."""
    index: Dict[Tuple[str, str], List[Tuple[datetime, float, float]]] = defaultdict(list)

    with wind_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            sensor_id = (row.get("sensor_id") or "").strip()
            ts = _parse_iso((row.get("timestamp_utc") or "").strip())
            speed = _to_float(row.get("wind_speed_mps"))
            direction = _to_float(row.get("wind_direction_deg"))

            if not sensor_id or ts is None or speed is None or direction is None:
                continue

            bucket = _hour_bucket_key(ts)
            index[(sensor_id, bucket)].append((ts, speed, direction))

    return index


def _find_nearest_wind(
    sensor_id: str,
    obs_dt: datetime,
    wind_index: Dict[Tuple[str, str], List[Tuple[datetime, float, float]]],
    max_gap: timedelta,
) -> Tuple[Optional[float], Optional[float]]:
    """Return (wind_speed_mps, wind_direction_deg) for the closest KNMI reading within max_gap."""
    bucket = _hour_bucket_key(obs_dt)
    candidates = wind_index.get((sensor_id, bucket), [])

    # Also check adjacent hour bucket in case the obs is near an hour boundary.
    prev_bucket = _hour_bucket_key(obs_dt - timedelta(hours=1))
    candidates = candidates + wind_index.get((sensor_id, prev_bucket), [])

    best_speed: Optional[float] = None
    best_dir: Optional[float] = None
    best_gap = max_gap + timedelta(seconds=1)  # start worse than threshold

    for wind_dt, speed, direction in candidates:
        gap = abs((obs_dt - wind_dt).total_seconds())
        gap_td = timedelta(seconds=gap)
        if gap_td < best_gap:
            best_gap = gap_td
            best_speed = speed
            best_dir = direction

    if best_gap <= max_gap:
        return best_speed, best_dir
    return None, None


def merge(
    obs_path: Path,
    wind_path: Path,
    out_path: Path,
    max_gap_minutes: int,
) -> None:
    max_gap = timedelta(minutes=max_gap_minutes)

    print(f"Loading wind samples from: {wind_path}")
    wind_index = load_wind_index(wind_path)
    total_wind_keys = len(wind_index)
    print(f"  Wind index: {total_wind_keys} (sensor_id, hour) buckets")

    print(f"Reading observations from: {obs_path}")
    with obs_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        obs_rows = list(reader)
    print(f"  Loaded {len(obs_rows)} rows")

    if "wind_speed_mps" not in fieldnames or "wind_direction_deg" not in fieldnames:
        print("  Warning: wind_speed_mps or wind_direction_deg columns missing; they will be appended.")
        if "wind_speed_mps" not in fieldnames:
            fieldnames = list(fieldnames) + ["wind_speed_mps"]
        if "wind_direction_deg" not in fieldnames:
            fieldnames = list(fieldnames) + ["wind_direction_deg"]

    matched = 0
    skipped_no_wind_sensor = 0
    skipped_no_ts = 0
    skipped_gap = 0

    for row in obs_rows:
        # Skip if wind is already populated.
        existing_speed = (row.get("wind_speed_mps") or "").strip()
        existing_dir = (row.get("wind_direction_deg") or "").strip()
        if existing_speed and existing_dir:
            matched += 1
            continue

        sensor_id = (row.get("sensor_id") or "").strip()
        ts_raw = (row.get("timestamp_utc") or "").strip()
        obs_dt = _parse_iso(ts_raw)

        if obs_dt is None:
            skipped_no_ts += 1
            continue

        bucket = _hour_bucket_key(obs_dt)
        if (sensor_id, bucket) not in wind_index:
            # Check adjacent bucket too before giving up.
            prev_bucket = _hour_bucket_key(obs_dt - timedelta(hours=1))
            if (sensor_id, prev_bucket) not in wind_index:
                skipped_no_wind_sensor += 1
                continue

        speed, direction = _find_nearest_wind(sensor_id, obs_dt, wind_index, max_gap)
        if speed is None or direction is None:
            skipped_gap += 1
            continue

        row["wind_speed_mps"] = speed
        row["wind_direction_deg"] = direction
        matched += 1

    # Back up original if writing to the same file.
    if out_path.resolve() == obs_path.resolve():
        bak_path = obs_path.with_suffix(obs_path.suffix + ".bak")
        shutil.copy2(obs_path, bak_path)
        print(f"  Backup saved: {bak_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(obs_rows)

    total = len(obs_rows)
    print(f"\nResults")
    print(f"  Total observation rows:       {total}")
    print(f"  Wind matched/already set:     {matched}")
    print(f"  Skipped (no sensor in wind):  {skipped_no_wind_sensor}")
    print(f"  Skipped (invalid timestamp):  {skipped_no_ts}")
    print(f"  Skipped (gap > {max_gap_minutes} min):       {skipped_gap}")
    fill_rate = matched / total * 100 if total > 0 else 0
    print(f"  Fill rate:                    {fill_rate:.1f}%")
    print(f"\nWrote: {out_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge KNMI wind samples into sensor_observations_long.csv")
    parser.add_argument(
        "--obs",
        default="data_exports/full/sensor_observations_long.csv",
        help="Air-quality observations CSV (input)",
    )
    parser.add_argument(
        "--wind",
        default="data_exports/knmi/knmi_wind_samples.csv",
        help="KNMI wind samples CSV produced by knmi.py",
    )
    parser.add_argument(
        "--out",
        default="data_exports/full/sensor_observations_long.csv",
        help="Output path (can be same as --obs to update in place)",
    )
    parser.add_argument(
        "--max-gap-minutes",
        type=int,
        default=60,
        help="Maximum allowed time gap in minutes between obs and wind reading",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    obs_path = Path(args.obs)
    wind_path = Path(args.wind)
    out_path = Path(args.out)

    if not obs_path.exists():
        print(f"Observations file not found: {obs_path}")
        return 2
    if not wind_path.exists():
        print(f"Wind samples file not found: {wind_path}")
        return 2

    merge(
        obs_path=obs_path,
        wind_path=wind_path,
        out_path=out_path,
        max_gap_minutes=args.max_gap_minutes,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
