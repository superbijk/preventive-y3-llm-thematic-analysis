#!/usr/bin/env python3
"""Generate the blinded R2.5 dual-coding form.

For each of the 27 experiment runs, locate the Python script that performed
the thematic analysis (usually generate_feedback_reports.py) and emit a row
in the coding form with:
  - coding_id (randomized, e.g. E01–E27)
  - script_excerpt (first ~80 lines of the script, the part that exposes
    whether categorization uses LLM-based reading or keyword matching)
  - coder_A, coder_B, adjudicated, notes (blank, to be filled by coders)

A private key (coding_id -> canonical_id) is written to
instance/data/mappings/r2_5_coding_key.csv so blinding is preserved during
coding while still allowing re-attribution after κ is computed.

See r2_5_dual_coding_protocol.md for the full procedure.
"""

import csv
import random
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
INSTANCE_DIR = PROJECT_ROOT / "instance"
META_PATH = INSTANCE_DIR / "data" / "mappings" / "runs_metadata.csv"
FORM_PATH = PROJECT_ROOT / ".manuscript" / "manuscript_1_llm_thematic_analysis" / "r2_5_coding_form.csv"
KEY_PATH  = INSTANCE_DIR / "data" / "mappings" / "r2_5_coding_key.csv"

SEED = 42                 # frozen so re-runs produce the same coding order
EXCERPT_LINES = 80        # lines of script body to include in the form
CANDIDATE_FILENAMES = [
    "generate_feedback_reports.py",
    "generate_feedback_report.py",
    "thematic_analysis.py",
    "feedback_analysis.py",
]


def find_analysis_script(run_dir: Path) -> Path | None:
    # Exact-name match first
    for name in CANDIDATE_FILENAMES:
        p = run_dir / name
        if p.exists():
            return p
    # Substring match: any .py whose name implies thematic / feedback work.
    # Prompt-3 runs often use names like '02_thematic_analysis.py'.
    candidates = []
    for p in run_dir.glob("*.py"):
        lname = p.name.lower()
        if any(t in lname for t in ("thematic", "theme", "feedback", "categor")):
            candidates.append(p)
    if candidates:
        candidates.sort(key=lambda x: ("statistical" in x.name.lower(), x.name))
        return candidates[0]

    # Last resort: a generic 'analysis' script (Prompt-3 runs often use one
    # combined file). Exclude statistical-only and inspection scripts.
    fallback = []
    for p in run_dir.glob("*.py"):
        lname = p.name.lower()
        if "analysis" in lname or "analyze" in lname:
            if not any(t in lname for t in ("statistical", "stat_", "inspect", "chart", "visual")):
                fallback.append(p)
    if fallback:
        fallback.sort(key=lambda x: x.name)
        return fallback[0]
    return None


def excerpt(script_path: Path, n_lines: int) -> str:
    lines = script_path.read_text(encoding="utf-8", errors="replace").splitlines()
    head = lines[:n_lines]
    return "\n".join(head)


def main():
    with open(META_PATH, encoding="utf-8-sig") as f:
        meta = list(csv.DictReader(f))

    rng = random.Random(SEED)
    order = list(range(len(meta)))
    rng.shuffle(order)

    form_rows = []
    key_rows = []
    missing = []
    for new_pos, original_idx in enumerate(order, start=1):
        m = meta[original_idx]
        coding_id = f"E{new_pos:02d}"
        run_dir = PROJECT_ROOT / m["directory"]
        script = find_analysis_script(run_dir)
        if script is None:
            missing.append(m["canonical_id"])
            script_text = "[NO ANALYSIS SCRIPT FOUND IN RUN DIRECTORY]"
            script_name = "(missing)"
        else:
            script_text = excerpt(script, EXCERPT_LINES)
            script_name = script.name
        form_rows.append({
            "coding_id": coding_id,
            "script_filename": script_name,
            "script_excerpt": script_text,
            "coder_A": "",
            "coder_B": "",
            "adjudicated": "",
            "notes": "",
        })
        key_rows.append({
            "coding_id": coding_id,
            "canonical_id": m["canonical_id"],
            "prompt": m["prompt"],
            "model": m["model"],
            "rep": m["rep"],
        })

    FORM_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FORM_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "coding_id", "script_filename", "script_excerpt",
            "coder_A", "coder_B", "adjudicated", "notes",
        ])
        writer.writeheader()
        writer.writerows(form_rows)
    print(f"Wrote form: {FORM_PATH}  ({len(form_rows)} rows)")

    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(KEY_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "coding_id", "canonical_id", "prompt", "model", "rep",
        ])
        writer.writeheader()
        writer.writerows(key_rows)
    print(f"Wrote private key: {KEY_PATH}  (gitignored under instance/)")

    if missing:
        print(f"\nWARNING: no analysis script found for: {missing}")
        print("These runs cannot be coded for R2.5 from script inspection alone.")


if __name__ == "__main__":
    main()
