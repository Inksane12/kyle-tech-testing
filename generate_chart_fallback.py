"""Generate an offline-friendly chart data fallback from the included evidence CSVs."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ("timestamp_utc", "temperature_c", "utilization_pct", "memory_used_mib", "power_w")
OUTPUT = ROOT / "data" / "telemetry-fallback.js"

data = {}
for key, filename in (("idle", "idle.csv"), ("mixed", "mixed-comfyui.csv")):
    with (ROOT / "data" / filename).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 59:
        raise SystemExit(f"Expected 59 rows in {filename}; got {len(rows)}")
    data[key] = [{field: row[field] if field == "timestamp_utc" else float(row[field]) for field in FIELDS} for row in rows]

OUTPUT.write_text("window.KTT_TELEMETRY_DATA = " + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8")
print(f"Generated CSV-derived local fallback: {OUTPUT.name} ({sum(map(len, data.values()))} samples)")
