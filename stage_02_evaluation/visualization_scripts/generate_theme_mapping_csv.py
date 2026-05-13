#!/usr/bin/env python3
"""Generate a combined theme_mapping.csv from raw_themes_per_run.csv + theme_canonical_mapping.csv + feedbacks.csv."""

import csv
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
STAGE_DIR = SCRIPTS_DIR.parent
PROJECT_ROOT = STAGE_DIR.parent
INSTANCE_DIR = PROJECT_ROOT / "instance"
EVAL_RUNS_DIR = INSTANCE_DIR / "evaluation_runs"
MAPPINGS_DIR = INSTANCE_DIR / "data" / "mappings"
RAW_THEMES_PATH = MAPPINGS_DIR / "raw_themes_per_run.csv"
CANONICAL_PATH = MAPPINGS_DIR / "theme_canonical_mapping.csv"
OUTPUT_PATH = INSTANCE_DIR / "outputs" / "mappings" / "theme_mapping.csv"


def load_canonical_order():
    """Load canonical labels with their polarity, preserving CSV order."""
    order = []
    polarity_map = {}
    with open(CANONICAL_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            label = row["canonical_label"]
            order.append(label)
            polarity_map[label] = row["polarity"]
    return order, polarity_map


def load_raw_theme_mapping():
    """Load (run_folder, raw_theme) -> canonical_label from raw_themes_per_run.csv."""
    mapping = {}
    with open(RAW_THEMES_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mapping[(row["run_folder"], row["raw_theme"])] = row["canonical_label"]
    return mapping


def parse_folder(run_folder):
    """Extract (prompt, model, run) from folder name like 'prompt-1_opus_run-1'."""
    parts = run_folder.replace("prompt-", "").replace("run-", "").split("_")
    return int(parts[0]), parts[1], int(parts[2])


def load_feedbacks(mapping):
    """Read all feedbacks.csv files and build combined entries with counts."""
    entries = []

    for folder in sorted(EVAL_RUNS_DIR.iterdir()):
        if not folder.is_dir() or not folder.name.startswith("prompt-"):
            continue
        feedbacks_path = folder / "feedbacks.csv"
        if not feedbacks_path.exists():
            continue

        prompt, model, run = parse_folder(folder.name)

        with open(feedbacks_path, encoding="utf-8") as f:
            f.readline()  # skip header
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.rsplit(",", 2)
                if len(parts) < 3:
                    continue
                theme = parts[0].strip().strip('"')
                count_str = parts[2].strip()
                if not theme:
                    continue
                try:
                    count_val = int(count_str)
                except ValueError:
                    continue

                canonical = mapping.get((folder.name, theme))
                if canonical:
                    entries.append({
                        "run_folder": folder.name,
                        "prompt": prompt,
                        "model": model,
                        "run": run,
                        "raw_theme": theme,
                        "canonical_label": canonical,
                        "count": count_val,
                    })
    return entries


def main():
    print("Loading canonical mapping...")
    canonical_order, polarity_map = load_canonical_order()
    canon_rank = {label: i for i, label in enumerate(canonical_order)}

    print("Loading raw theme mapping...")
    mapping = load_raw_theme_mapping()

    print(f"Scanning {EVAL_RUNS_DIR} for feedbacks.csv files...")
    entries = load_feedbacks(mapping)
    print(f"  {len(entries)} theme entries across evaluation runs")

    # Sort: canonical order → prompt → model → run
    model_order = {"opus": 0, "gpt": 1, "gemini": 2}
    entries.sort(key=lambda e: (
        canon_rank.get(e["canonical_label"], 999),
        e["prompt"],
        model_order.get(e["model"], 99),
        e["run"],
    ))

    # Add polarity column
    for e in entries:
        e["polarity"] = polarity_map.get(e["canonical_label"], "neutral")

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["canonical_label", "polarity", "run_folder", "prompt", "model", "run", "raw_theme", "count"]
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)

    print(f"  Saved → {OUTPUT_PATH}  ({len(entries)} rows)")


if __name__ == "__main__":
    main()
