#!/usr/bin/env python3
"""Extract per-run wall-clock runtime from each experiment run.log.

Each run.log line of interest:
    [YYYY-MM-DD HH:MM:SS] Run X/X started (model=..., run_dir=...)
    [YYYY-MM-DD HH:MM:SS] Run X/X finished (status=..., elapsed=Ns)

Output: instance/data/mappings/runtimes.csv with one row per canonical run ID.
"""

import csv
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
INSTANCE_DIR = PROJECT_ROOT / "instance"
META_PATH = INSTANCE_DIR / "data" / "mappings" / "runs_metadata.csv"
OUT_PATH = INSTANCE_DIR / "data" / "mappings" / "runtimes.csv"

STARTED_RE  = re.compile(r"^\[(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] Run \d+/\d+ started")
FINISHED_RE = re.compile(r"^\[(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] Run \d+/\d+ finished \(status=(?P<status>-?\d+), elapsed=(?P<elapsed>\d+)s\)")


def parse_run_log(log_path: Path):
    start_ts = end_ts = status = elapsed = None
    if not log_path.exists():
        return None
    text = log_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        m = STARTED_RE.match(line)
        if m and start_ts is None:
            start_ts = m.group("ts")
            continue
        m = FINISHED_RE.match(line)
        if m:
            end_ts = m.group("ts")
            status = int(m.group("status"))
            elapsed = int(m.group("elapsed"))
    if elapsed is None:
        return None
    return {"started_at": start_ts, "finished_at": end_ts,
            "status": status, "elapsed_seconds": elapsed,
            "elapsed_minutes": round(elapsed / 60, 2)}


def main():
    with open(META_PATH, encoding="utf-8-sig") as f:
        meta = list(csv.DictReader(f))

    rows = []
    missing = []
    for m in meta:
        run_dir = PROJECT_ROOT / m["directory"]
        log = run_dir / "run.log"
        info = parse_run_log(log)
        if info is None:
            missing.append(m["canonical_id"])
            continue
        rows.append({
            "canonical_id": m["canonical_id"],
            "prompt":       m["prompt"],
            "model":        m["model"],
            "rep":          m["rep"],
            **info,
        })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "canonical_id", "prompt", "model", "rep",
            "started_at", "finished_at", "status",
            "elapsed_seconds", "elapsed_minutes",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote: {OUT_PATH}  ({len(rows)} runs)")
    if missing:
        print(f"  WARNING: no runtime parsed for: {missing}")

    # Quick summary by model
    by_model = {}
    for r in rows:
        by_model.setdefault(r["model"], []).append(r["elapsed_minutes"])
    print("\nPer-model wall-clock summary (minutes):")
    for model, mins in sorted(by_model.items()):
        avg = sum(mins) / len(mins)
        print(f"  {model:>6}: n={len(mins)}  mean={avg:.2f}  min={min(mins):.2f}  max={max(mins):.2f}")


if __name__ == "__main__":
    main()
