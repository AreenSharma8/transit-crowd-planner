"""DuckDB aggregation for the demo and larger local ticket CSV imports."""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import re
from typing import Any
import duckdb

REQUIRED_COLUMNS = {"passenger_count", "amount", "vehicle_number", "ticket_type_id", "end_stop_name", "route", "start_stop_name", "created_at", "is_ac"}

@lru_cache(maxsize=4)
def _aggregate_cached(path_text: str, mtime_ns: int, size: int) -> dict[str, Any]:
    """Read only compact route/hour aggregates; avoid loading millions of CSV rows into Python."""
    path = Path(path_text)
    con = duckdb.connect(database=":memory:")
    try:
        # Field names match the supplied hackathon CSV schema. Everything is read as text so
        # blank/NULL values and mixed amount formats do not trigger brittle type inference.
        result = con.execute("""
            SELECT upper(trim(route)) AS route_key,
                   try_cast(regexp_extract(created_at, '[ T]([0-2][0-9]):', 1) AS INTEGER) AS hour,
                   count(*)::BIGINT AS records,
                   count(DISTINCT substr(created_at, 1, 10))::BIGINT AS service_days,
                   sum(coalesce(try_cast(passenger_count AS DOUBLE), 0)) AS passengers,
                   sum(CASE WHEN vehicle_number IS NULL OR trim(vehicle_number) = '' OR upper(trim(vehicle_number)) IN ('NULL','NA') THEN 1 ELSE 0 END)::BIGINT AS missing_vehicle
            FROM read_csv_auto(?, header=true, all_varchar=true, ignore_errors=true)
            WHERE route IS NOT NULL AND trim(route) <> ''
            GROUP BY 1, 2
        """, [str(path)]).fetchall()
    finally:
        con.close()
    routes: dict[str, dict[int, dict[str, float]]] = {}
    total_rows = 0
    missing_vehicle = 0
    for route_key, hour, records, service_days, passengers, missing in result:
        if not route_key:
            continue
        route = routes.setdefault(route_key, {})
        if hour is not None and 0 <= int(hour) <= 23:
            route[int(hour)] = {"records": int(records), "service_days": int(service_days), "passengers": float(passengers or 0)}
        total_rows += int(records)
        missing_vehicle += int(missing)
    return {"routes": routes, "ticket_rows": total_rows,
            "missing_vehicle_number_percent": round(100 * missing_vehicle / total_rows, 1) if total_rows else None,
            "mtime_ns": mtime_ns, "file_size": size}

def load_aggregate(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return _aggregate_cached(str(path.resolve()), stat.st_mtime_ns, stat.st_size)

def _hour_from_depart(depart: str) -> int | None:
    match = re.search(r"(?:T|^)([0-2][0-9]):", depart or "")
    if not match:
        return None
    hour = int(match.group(1))
    return hour if 0 <= hour <= 23 else None

def _confidence(records: int) -> str:
    if records >= 40: return "high"
    if records >= 15: return "medium"
    return "low"

def ticket_signal(aggregate: dict[str, Any], route_key: str, depart: str) -> dict[str, Any]:
    hourly = aggregate["routes"].get(route_key.upper(), {})
    hour = _hour_from_depart(depart)
    window = [(hour + d) % 24 for d in (-1, 0, 1)] if hour is not None else list(range(24))
    records = sum(hourly.get(h, {}).get("records", 0) for h in window)
    passengers = sum(hourly.get(h, {}).get("passengers", 0) for h in window)
    peak_3h = max((sum(hourly.get((h + d) % 24, {}).get("passengers", 0) for d in (-1, 0, 1)) for h in range(24)), default=0)
    score = max(0, min(100, round(100 * passengers / peak_3h))) if peak_3h else 0
    return {"route_key": route_key, "score": score, "label": _label(score) if records else "No matching samples", "confidence": _confidence(records), "records": records, "ticketed_passengers": round(passengers)}

def _label(score: int) -> str:
    if score < 30: return "Lighter signal"
    if score < 58: return "Moderate signal"
    if score < 78: return "Busy signal"
    return "High activity"

def missing_vehicle_percent(aggregate: dict[str, Any]) -> float | None:
    return aggregate["missing_vehicle_number_percent"]

def validation_summary(aggregate: dict[str, Any], route_key: str) -> dict[str, Any]:
    hourly = aggregate["routes"].get(route_key.upper(), {})
    peak_hours = [7, 8, 9, 10, 16, 17, 18, 19]
    midday_hours = [11, 12, 13, 14, 15]
    def means(hours: list[int]) -> tuple[int, float]:
        records = sum(hourly.get(h, {}).get("records", 0) for h in hours)
        normalized = []
        for h in hours:
            cell = hourly.get(h, {})
            days = cell.get("service_days", 0)
            if days:
                normalized.append(cell.get("passengers", 0) / days)
        return records, round(sum(normalized) / len(normalized), 2) if normalized else 0.0
    peak_n, peak_avg = means(peak_hours)
    midday_n, midday_avg = means(midday_hours)
    enough = peak_n >= 10 and midday_n >= 10
    if peak_n == 0 and midday_n == 0:
        trend = "No matching samples"
    elif not enough:
        trend = "Too few rows for comparison"
    else:
        trend = "Peak sample is higher" if peak_avg > midday_avg else "Midday sample is higher or similar"
    return {"route_key": route_key, "peak_records": peak_n, "midday_records": midday_n,
            "peak_avg_passengers_per_hour": peak_avg, "midday_avg_passengers_per_hour": midday_avg,
            "trend": trend, "sufficient_sample": enough,
            "note": "Descriptive per-service-day sanity check only; not a held-out accuracy test or occupancy estimate."}
