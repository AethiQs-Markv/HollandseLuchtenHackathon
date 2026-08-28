#!/usr/bin/env python3
"""Validate exported CSV datasets against the checklist in datatsets.md.

Default input directory:
- data_exports/full

Run:
- python validate_exports.py
- python validate_exports.py --data-dir data_exports/full --min-fault-events 20 --min-wind-sample-count 5
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass
class Finding:
    level: str  # PASS | WARN | FAIL
    rule: str
    file: str
    details: str


def parse_iso_utc(value: str) -> Optional[datetime]:
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


def to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def load_csv(path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames or []
    return rows, headers


def has_required_columns(headers: List[str], required: Iterable[str]) -> bool:
    present = set(headers)
    return all(col in present for col in required)


def check_duplicate_keys(rows: List[Dict[str, str]], key_cols: List[str]) -> Tuple[int, int]:
    if not rows:
        return 0, 0
    seen = set()
    duplicates = 0
    for row in rows:
        key = tuple((row.get(col) or "").strip() for col in key_cols)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return duplicates, len(rows)


def add_findings_for_duplicates(findings: List[Finding], file_name: str, rows: List[Dict[str, str]], key_cols: List[str]) -> None:
    duplicates, total = check_duplicate_keys(rows, key_cols)
    rule = "No duplicate primary keys"
    if total == 0:
        findings.append(Finding("WARN", rule, file_name, "File is empty; duplicate-key check skipped."))
        return
    if duplicates == 0:
        findings.append(Finding("PASS", rule, file_name, f"No duplicate keys across {total} rows using {key_cols}."))
    else:
        findings.append(Finding("FAIL", rule, file_name, f"Found {duplicates} duplicate key rows using {key_cols}."))


def check_timestamp_coverage_sensor_observations(rows: List[Dict[str, str]]) -> Finding:
    rule = "Timestamp coverage cadence"
    file_name = "sensor_observations_long.csv"
    if not rows:
        return Finding("WARN", rule, file_name, "File is empty; cadence check skipped.")

    by_sensor: Dict[str, List[datetime]] = defaultdict(list)
    invalid_ts = 0
    for row in rows:
        sensor_id = (row.get("sensor_id") or "").strip()
        dt = parse_iso_utc((row.get("timestamp_utc") or "").strip())
        if not sensor_id or dt is None:
            invalid_ts += 1
            continue
        by_sensor[sensor_id].append(dt)

    if not by_sensor:
        return Finding("WARN", rule, file_name, "No valid sensor/timestamp rows found.")

    unstable = 0
    checked = 0
    for sensor_id, timestamps in by_sensor.items():
        if len(timestamps) < 3:
            continue
        timestamps.sort()
        deltas = []
        for i in range(1, len(timestamps)):
            sec = int((timestamps[i] - timestamps[i - 1]).total_seconds())
            if sec > 0:
                deltas.append(sec)
        if len(deltas) < 2:
            continue
        checked += 1
        counts = Counter(deltas)
        dominant_count = counts.most_common(1)[0][1]
        ratio = dominant_count / len(deltas)
        if ratio < 0.8:
            unstable += 1

    if checked == 0:
        return Finding(
            "WARN",
            rule,
            file_name,
            f"Not enough per-sensor points for cadence stability check (invalid timestamps: {invalid_ts}).",
        )

    if unstable == 0:
        return Finding(
            "PASS",
            rule,
            file_name,
            f"Cadence appears stable for {checked} sensors (>=80% dominant interval). Invalid timestamps: {invalid_ts}.",
        )

    return Finding(
        "WARN",
        rule,
        file_name,
        f"Cadence instability in {unstable}/{checked} sensors (<80% dominant interval). Invalid timestamps: {invalid_ts}.",
    )


def check_unit_consistency(sensor_rows: List[Dict[str, str]], ref_rows: List[Dict[str, str]]) -> List[Finding]:
    findings: List[Finding] = []
    rule = "Unit consistency per pollutant"

    def collect(rows: List[Dict[str, str]], pollutant_col: str, unit_col: str) -> Dict[str, set]:
        m: Dict[str, set] = defaultdict(set)
        for row in rows:
            pollutant = (row.get(pollutant_col) or "").strip()
            unit = (row.get(unit_col) or "").strip()
            if pollutant and unit:
                m[pollutant].add(unit)
        return m

    sensor_units = collect(sensor_rows, "pollutant_name", "unit")
    ref_units = collect(ref_rows, "pollutant_name", "unit")

    # Sensor observations
    if not sensor_rows:
        findings.append(Finding("WARN", rule, "sensor_observations_long.csv", "File empty; check skipped."))
    else:
        inconsistent = {p: u for p, u in sensor_units.items() if len(u) > 1}
        if inconsistent:
            details = "; ".join(f"{p}={sorted(list(u))}" for p, u in sorted(inconsistent.items()))
            findings.append(Finding("FAIL", rule, "sensor_observations_long.csv", f"Inconsistent units found: {details}"))
        else:
            findings.append(Finding("PASS", rule, "sensor_observations_long.csv", "Units consistent per pollutant."))

    # Reference observations
    if not ref_rows:
        findings.append(Finding("WARN", rule, "reference_station_observations.csv", "File empty; check skipped."))
    else:
        inconsistent_ref = {p: u for p, u in ref_units.items() if len(u) > 1}
        if inconsistent_ref:
            details = "; ".join(f"{p}={sorted(list(u))}" for p, u in sorted(inconsistent_ref.items()))
            findings.append(Finding("FAIL", rule, "reference_station_observations.csv", f"Inconsistent units found: {details}"))
        else:
            findings.append(Finding("PASS", rule, "reference_station_observations.csv", "Units consistent per pollutant."))

    return findings


def check_negative_pm(sensor_rows: List[Dict[str, str]]) -> Finding:
    rule = "No physically impossible negative PM values"
    file_name = "sensor_observations_long.csv"
    if not sensor_rows:
        return Finding("WARN", rule, file_name, "File empty; check skipped.")

    negatives = 0
    checked = 0
    for row in sensor_rows:
        pollutant = (row.get("pollutant_name") or "").lower().replace(" ", "")
        if "pm" not in pollutant:
            continue
        value = to_float(row.get("value_raw"))
        if value is None:
            continue
        checked += 1
        if value < 0:
            negatives += 1

    if checked == 0:
        return Finding("WARN", rule, file_name, "No PM rows with numeric values found.")
    if negatives == 0:
        return Finding("PASS", rule, file_name, f"No negative PM values across {checked} checked rows.")
    return Finding("FAIL", rule, file_name, f"Found {negatives} negative PM values across {checked} checked rows.")


def check_wind_validation(sensor_rows: List[Dict[str, str]], wind_rows: List[Dict[str, str]]) -> List[Finding]:
    findings: List[Finding] = []
    rule = "Wind validation: direction in 0-360 and speed >= 0"

    # Check direct wind columns in sensor observations if present with values.
    bad_dir = 0
    bad_speed = 0
    present = 0
    for row in sensor_rows:
        d = to_float(row.get("wind_direction_deg"))
        s = to_float(row.get("wind_speed_mps"))
        if d is None and s is None:
            continue
        present += 1
        if d is not None and not (0.0 <= d <= 360.0):
            bad_dir += 1
        if s is not None and s < 0.0:
            bad_speed += 1

    if present == 0:
        findings.append(Finding("WARN", rule, "sensor_observations_long.csv", "No direct wind columns populated; skipped direct check."))
    elif bad_dir == 0 and bad_speed == 0:
        findings.append(Finding("PASS", rule, "sensor_observations_long.csv", f"Direct wind columns valid in {present} rows."))
    else:
        findings.append(
            Finding(
                "FAIL",
                rule,
                "sensor_observations_long.csv",
                f"Invalid wind values in direct columns: bad direction={bad_dir}, bad speed={bad_speed}, rows checked={present}.",
            )
        )

    # Check wind-rose bins if present.
    if not wind_rows:
        findings.append(Finding("WARN", rule, "wind_rose_aggregates.csv", "No wind-rose rows; check skipped."))
    else:
        bad_bins = 0
        for row in wind_rows:
            ds = to_float(row.get("direction_bin_deg_start"))
            de = to_float(row.get("direction_bin_deg_end"))
            ss = to_float(row.get("speed_bin_mps_start"))
            se = to_float(row.get("speed_bin_mps_end"))
            if ds is None or de is None or ss is None or se is None:
                bad_bins += 1
                continue
            if not (0.0 <= ds <= 360.0 and 0.0 <= de <= 360.0 + 360.0 and ss >= 0.0 and se >= 0.0):
                bad_bins += 1
        if bad_bins == 0:
            findings.append(Finding("PASS", rule, "wind_rose_aggregates.csv", f"Wind-rose bins valid for {len(wind_rows)} rows."))
        else:
            findings.append(Finding("FAIL", rule, "wind_rose_aggregates.csv", f"Invalid wind-rose bin values in {bad_bins}/{len(wind_rows)} rows."))

    return findings


def check_sensor_reference_overlap(
    sensor_rows: List[Dict[str, str]],
    ref_rows: List[Dict[str, str]],
    mapping_rows: List[Dict[str, str]],
) -> Finding:
    rule = "Sensor-reference overlap windows exist"
    file_name = "sensor_reference_mapping.csv"

    if not mapping_rows:
        return Finding("WARN", rule, file_name, "Mapping file empty; cannot validate overlap.")
    if not sensor_rows:
        return Finding("WARN", rule, file_name, "Sensor observations empty; cannot validate overlap.")
    if not ref_rows:
        return Finding("WARN", rule, file_name, "Reference observations empty; cannot validate overlap.")

    sensor_window: Dict[str, Tuple[datetime, datetime]] = {}
    ref_window: Dict[str, Tuple[datetime, datetime]] = {}

    for row in sensor_rows:
        sid = (row.get("sensor_id") or "").strip()
        ts = parse_iso_utc((row.get("timestamp_utc") or "").strip())
        if not sid or ts is None:
            continue
        if sid not in sensor_window:
            sensor_window[sid] = (ts, ts)
        else:
            start, end = sensor_window[sid]
            sensor_window[sid] = (min(start, ts), max(end, ts))

    for row in ref_rows:
        rid = (row.get("reference_station_id") or "").strip()
        ts = parse_iso_utc((row.get("timestamp_utc") or "").strip())
        if not rid or ts is None:
            continue
        if rid not in ref_window:
            ref_window[rid] = (ts, ts)
        else:
            start, end = ref_window[rid]
            ref_window[rid] = (min(start, ts), max(end, ts))

    total = 0
    overlap = 0
    missing = 0
    for row in mapping_rows:
        sid = (row.get("sensor_id") or "").strip()
        rid = (row.get("reference_station_id") or "").strip()
        if not sid or not rid:
            continue
        total += 1
        sw = sensor_window.get(sid)
        rw = ref_window.get(rid)
        if sw is None or rw is None:
            missing += 1
            continue
        s0, s1 = sw
        r0, r1 = rw
        if s0 <= r1 and r0 <= s1:
            overlap += 1

    if total == 0:
        return Finding("WARN", rule, file_name, "No valid mapping rows found.")
    if overlap == 0:
        return Finding("FAIL", rule, file_name, f"No overlap found across {total} mappings (missing windows for {missing}).")
    if overlap < total:
        return Finding("WARN", rule, file_name, f"Overlap found for {overlap}/{total} mappings (missing windows for {missing}).")
    return Finding("PASS", rule, file_name, f"Overlap found for all {total} mappings.")


def check_fault_event_volume(events_rows: List[Dict[str, str]], min_events: int) -> Finding:
    rule = "Sufficient labeled fault windows for challenge 1"
    file_name = "historical_quality_events.csv"
    if not events_rows:
        return Finding("WARN", rule, file_name, "File empty; no labeled events available yet.")

    valid = 0
    for row in events_rows:
        sid = (row.get("sensor_id") or "").strip()
        start = parse_iso_utc((row.get("start_time_utc") or "").strip())
        end = parse_iso_utc((row.get("end_time_utc") or "").strip())
        label = (row.get("label_type") or "").strip()
        if sid and start is not None and end is not None and label:
            valid += 1

    if valid >= min_events:
        return Finding("PASS", rule, file_name, f"Found {valid} valid labeled events (threshold {min_events}).")
    return Finding("WARN", rule, file_name, f"Found {valid} valid labeled events (threshold {min_events}).")


def check_wind_rose_sample_count(wind_rows: List[Dict[str, str]], min_sample_count: int) -> Finding:
    rule = "Each wind-rose period has enough samples"
    file_name = "wind_rose_aggregates.csv"

    if not wind_rows:
        return Finding("WARN", rule, file_name, "File empty; no wind-rose periods available.")

    low = 0
    bad = 0
    for row in wind_rows:
        sc = to_float(row.get("sample_count"))
        if sc is None:
            bad += 1
            continue
        if sc < min_sample_count:
            low += 1

    if bad > 0:
        return Finding("WARN", rule, file_name, f"{bad} rows missing/non-numeric sample_count.")
    if low == 0:
        return Finding("PASS", rule, file_name, f"All {len(wind_rows)} rows meet sample_count >= {min_sample_count}.")
    ratio = low / len(wind_rows)
    level = "WARN" if ratio <= 0.2 else "FAIL"
    return Finding(level, rule, file_name, f"{low}/{len(wind_rows)} rows below sample_count {min_sample_count}.")


def check_tool_catalog_examples(data_dir: Path) -> Finding:
    rule = "Every tool in catalog has at least one executable example"
    file_name = "analysis_tool_catalog.csv"
    path = data_dir / file_name

    if not path.exists():
        return Finding("WARN", rule, file_name, "File missing; challenge 3 validation skipped.")

    rows, _ = load_csv(path)
    if not rows:
        return Finding("WARN", rule, file_name, "File empty; challenge 3 validation skipped.")

    missing_examples = 0
    for row in rows:
        examples = (row.get("examples") or "").strip()
        if not examples:
            missing_examples += 1
            continue
        # Accept plain text or JSON arrays; validate JSON when it looks like JSON.
        text = examples.strip()
        if text.startswith("[") or text.startswith("{"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list) and len(parsed) == 0:
                    missing_examples += 1
            except json.JSONDecodeError:
                missing_examples += 1

    if missing_examples == 0:
        return Finding("PASS", rule, file_name, f"All {len(rows)} tools include at least one example.")
    return Finding("WARN", rule, file_name, f"Missing/invalid examples for {missing_examples}/{len(rows)} tools.")


def check_sentinel_values(sensor_rows: List[Dict[str, str]]) -> Finding:
    rule = "No sentinel missing values like -999"
    file_name = "sensor_observations_long.csv"
    if not sensor_rows:
        return Finding("WARN", rule, file_name, "File empty; check skipped.")

    sentinel_hits = 0
    numeric_cols = ["value_raw", "value_calibrated", "temperature_c", "relative_humidity_pct", "wind_speed_mps", "wind_direction_deg"]
    for row in sensor_rows:
        for col in numeric_cols:
            val = (row.get(col) or "").strip()
            if val in {"-999", "-999.0", "-9999", "-9999.0"}:
                sentinel_hits += 1

    if sentinel_hits == 0:
        return Finding("PASS", rule, file_name, "No sentinel values found in numeric columns.")
    return Finding("FAIL", rule, file_name, f"Found {sentinel_hits} sentinel values in numeric columns.")


def run_validation(data_dir: Path, min_fault_events: int, min_wind_sample_count: int) -> List[Finding]:
    findings: List[Finding] = []

    sensor_obs_rows, sensor_obs_headers = load_csv(data_dir / "sensor_observations_long.csv")
    sensor_meta_rows, sensor_meta_headers = load_csv(data_dir / "sensor_metadata.csv")
    ref_obs_rows, ref_obs_headers = load_csv(data_dir / "reference_station_observations.csv")
    mapping_rows, mapping_headers = load_csv(data_dir / "sensor_reference_mapping.csv")
    events_rows, events_headers = load_csv(data_dir / "historical_quality_events.csv")
    wind_rows, wind_headers = load_csv(data_dir / "wind_rose_aggregates.csv")

    # Required-column checks for core files.
    core_requirements = {
        "sensor_observations_long.csv": ["sensor_id", "timestamp_utc", "pollutant_name", "unit"],
        "sensor_metadata.csv": ["sensor_id", "latitude", "longitude", "status"],
        "reference_station_observations.csv": ["reference_station_id", "timestamp_utc", "pollutant_name", "unit"],
        "sensor_reference_mapping.csv": ["sensor_id", "reference_station_id", "mapping_method"],
        "historical_quality_events.csv": ["event_id", "sensor_id", "start_time_utc", "end_time_utc", "label_type"],
    }
    header_map = {
        "sensor_observations_long.csv": sensor_obs_headers,
        "sensor_metadata.csv": sensor_meta_headers,
        "reference_station_observations.csv": ref_obs_headers,
        "sensor_reference_mapping.csv": mapping_headers,
        "historical_quality_events.csv": events_headers,
    }

    for file_name, req_cols in core_requirements.items():
        headers = header_map[file_name]
        if not headers:
            findings.append(Finding("WARN", "Required columns present", file_name, "File missing or empty; schema check skipped."))
            continue
        if has_required_columns(headers, req_cols):
            findings.append(Finding("PASS", "Required columns present", file_name, "All required columns found."))
        else:
            missing = [c for c in req_cols if c not in headers]
            findings.append(Finding("FAIL", "Required columns present", file_name, f"Missing columns: {missing}"))

    # Rule 1: Duplicate keys
    add_findings_for_duplicates(findings, "sensor_observations_long.csv", sensor_obs_rows, ["sensor_id", "timestamp_utc", "pollutant_name"])
    add_findings_for_duplicates(findings, "sensor_metadata.csv", sensor_meta_rows, ["sensor_id"])
    add_findings_for_duplicates(findings, "reference_station_observations.csv", ref_obs_rows, ["reference_station_id", "timestamp_utc", "pollutant_name"])
    add_findings_for_duplicates(findings, "historical_quality_events.csv", events_rows, ["event_id"])

    # Rule 2
    findings.append(check_timestamp_coverage_sensor_observations(sensor_obs_rows))

    # Rule 3
    findings.extend(check_unit_consistency(sensor_obs_rows, ref_obs_rows))

    # Rule 4
    findings.append(check_negative_pm(sensor_obs_rows))

    # Rule 5
    findings.extend(check_wind_validation(sensor_obs_rows, wind_rows))

    # Rule 6
    findings.append(check_sensor_reference_overlap(sensor_obs_rows, ref_obs_rows, mapping_rows))

    # Rule 7
    findings.append(check_fault_event_volume(events_rows, min_events=min_fault_events))

    # Rule 8
    findings.append(check_wind_rose_sample_count(wind_rows, min_sample_count=min_wind_sample_count))

    # Rule 9
    findings.append(check_tool_catalog_examples(data_dir))

    # Extra global sentinel check
    findings.append(check_sentinel_values(sensor_obs_rows))

    return findings


def print_report(findings: List[Finding]) -> int:
    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    sorted_findings = sorted(findings, key=lambda f: (order.get(f.level, 99), f.rule, f.file))

    for f in sorted_findings:
        print(f"[{f.level}] {f.rule} | {f.file} | {f.details}")

    counts = Counter(f.level for f in findings)
    print("\nSummary")
    print(f"- FAIL: {counts.get('FAIL', 0)}")
    print(f"- WARN: {counts.get('WARN', 0)}")
    print(f"- PASS: {counts.get('PASS', 0)}")

    return 1 if counts.get("FAIL", 0) > 0 else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate exported CSVs against hackathon dataset checklist.")
    parser.add_argument("--data-dir", default="data_exports/full", help="Directory containing exported CSV files")
    parser.add_argument("--min-fault-events", type=int, default=20, help="Minimum valid labeled events for challenge 1 readiness")
    parser.add_argument("--min-wind-sample-count", type=int, default=5, help="Minimum sample_count threshold per wind-rose row")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    data_dir = Path(args.data_dir)

    if not data_dir.exists():
        print(f"Data directory does not exist: {data_dir}")
        return 2

    findings = run_validation(
        data_dir=data_dir,
        min_fault_events=args.min_fault_events,
        min_wind_sample_count=args.min_wind_sample_count,
    )
    return print_report(findings)


if __name__ == "__main__":
    raise SystemExit(main())
