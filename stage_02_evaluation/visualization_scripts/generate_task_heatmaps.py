#!/usr/bin/env python3
"""Generate 3 task-completion heatmaps from findings.csv files:
  - task_completion_required.png  (10 R items only)
  - task_completion_curated.png   (10 R + 9 selected M items)
  - task_completion_full.png      (10 R + all M items with ≥1 appearance)
"""

import csv
import re
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from heatmap_common import RUN_ORDER, FOLDER_TO_RUN_ID, style_heatmap, P1_COLS, P2_COLS, P3_COLS
from shared_labels import R_LABELS, heatmap_label

SCRIPTS_DIR = Path(__file__).resolve().parent
STAGE_DIR = SCRIPTS_DIR.parent
PROJECT_ROOT = STAGE_DIR.parent
INSTANCE_DIR = PROJECT_ROOT / "instance"
EVAL_RUNS_DIR = INSTANCE_DIR / "evaluation_runs"
OUTPUT_DIR = INSTANCE_DIR / "outputs" / "heatmaps"

TITLE = "Prompted Required (R) and Additional Tasks"
SHOW_SUMMARY = False  # Hide P1/P2/P3/All summary columns on heatmaps

# ── R items ──────────────────────────────────────────────────────
# R1.1–R1.3 always co-occur; merged into single display row
R_ITEMS_RAW = ["R1.1", "R1.2", "R1.3", "R2.1", "R2.2", "R2.3", "R2.4", "R2.5", "R3.1", "R3.2"]
R1_GROUP = ["R1.1", "R1.2", "R1.3"]

# Display rows after merging R1 (imported from shared_labels for cross-file consistency)
from shared_labels import R_DISPLAY

# ── M item descriptions and group assignments ────────────────────
M_DESCRIPTIONS = {
    "M2":  "Correlation analysis",
    "M3":  "Box plot",
    "M4":  "Heatmap visualization",
    "M5":  "Theme frequency by year",
    "M6":  "Sentiment analysis",
    "M7":  "2567 peak analysis",
    "M8":  "2568 decline analysis",
    "M9":  "Score-of-1 in 2568",
    "M10": "Satisfaction distribution",
    "M11": "Theme co-occurrence",
    "M12": "Response rate analysis",
    "M13": "Sentiment classification",
    "M14": "Significance testing",
    "M15": "Median / mode reporting",
    "M16": "Distribution polarization",
    "M17": "Professional identity themes",
    "M18": "Cross-course integration",
    "M19": "Actionable recommendations",
    "M20": "Survey methodology critique",
    "M21": "Clinical skills breakdown",
    "M22": "Over-granular splitting",
    "M23": "Data inspection script",
    "M24": "IQR / quartile reporting",
    "M25": "Trend line charts",
    "M26": "Theme data as JSON",
    "M27": "Stacked distribution charts",
    "M28": "Satisfaction by year",
    "M29": "Pairwise post-hoc tests",
    "M30": "Effect size reporting",
    "M31": "Skewness / kurtosis",
    "M32": "Unmatched response tracking",
    "M33": "Dissatisfaction detail viz",
    "M34": "Evaluation method recs",
    "M35": "CSV structured output",
    "M36": "Output manifest",
    "M37": "Student-level coding",
    "M38": "Theme keyword tokens",
    "M39": "Slope calculation",
    "M40": "Excel workbook output",
    "M41": "Percent change calc",
    "M42": "Comments compilation",
    "M43": "Facilities & Equipment",
}

M_GROUPS = {
    # Statistical
    "M2": "Statistical", "M14": "Statistical", "M15": "Statistical",
    "M16": "Statistical", "M24": "Statistical", "M29": "Statistical",
    "M30": "Statistical", "M31": "Statistical", "M39": "Statistical",
    "M41": "Statistical",
    # Visualization
    "M3": "Visualization", "M4": "Visualization", "M5": "Visualization",
    "M10": "Visualization", "M25": "Visualization", "M27": "Visualization",
    "M28": "Visualization", "M33": "Visualization",
    # Thematic
    "M6": "Thematic", "M11": "Thematic", "M13": "Thematic",
    "M17": "Thematic", "M18": "Thematic", "M21": "Thematic",
    "M37": "Thematic", "M38": "Thematic", "M42": "Thematic",
    "M43": "Thematic",
    # Contextual
    "M7": "Contextual", "M8": "Contextual", "M9": "Contextual",
    "M12": "Contextual",
    # Methodological
    "M19": "Methodological", "M20": "Methodological",
    "M22": "Methodological", "M32": "Methodological",
    "M34": "Methodological",
    # Output
    "M23": "Output", "M26": "Output", "M35": "Output",
    "M36": "Output", "M40": "Output",
}

# ── Curated subset ───────────────────────────────────────────────
CURATED_ITEMS = [
    ("Statistical", ["M2", "M14", "M29", "M30", "M24", "M20"]),
    ("Visualization", ["M3", "M25", "M27"]),
]


def parse_findings_csvs():
    """Read all findings.csv files and build item_data dict."""
    item_data = {item: {} for item in R_ITEMS_RAW}

    if not EVAL_RUNS_DIR.exists():
        return item_data

    for folder in sorted(EVAL_RUNS_DIR.iterdir()):
        if not folder.is_dir() or not folder.name.startswith("prompt-"):
            continue
        findings_path = folder / "findings.csv"
        if not findings_path.exists():
            continue

        run_id = FOLDER_TO_RUN_ID.get(folder.name)
        if not run_id:
            continue

        with open(findings_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                item_id = row.get("item_id", "").strip()
                status = row.get("status", "").strip()
                if not item_id:
                    continue

                if item_id.startswith("R"):
                    if status == "FOUND":
                        val = 1.0
                    elif status in ("INCORRECT", "NOT_FOUND"):
                        val = 0.0
                    else:
                        val = 0.5
                    if item_id not in item_data:
                        item_data[item_id] = {}
                    item_data[item_id][run_id] = val

                elif item_id.startswith("M"):
                    if item_id not in item_data:
                        item_data[item_id] = {}
                    if status == "YES":
                        item_data[item_id][run_id] = 1.0
                    elif status == "NO":
                        item_data[item_id][run_id] = 0.0
                    else:
                        item_data[item_id][run_id] = 0.5

    return item_data


def m_sort_key(item_id, item_data):
    """Sort key: appearance count desc, then M number asc."""
    count = sum(1 for r in RUN_ORDER if item_data.get(item_id, {}).get(r, 0.5) == 1.0)
    num = int(re.search(r"\d+", item_id).group())
    return (-count, num)


def m_label(item_id):
    """Build display label: 'Description' (group prefix dropped — row grouping conveys it)."""
    return M_DESCRIPTIONS.get(item_id, item_id)


def build_r_rows(item_data):
    """Build R item rows and labels, merging R1.1–R1.3 into one row."""
    labels, rows = [], []
    for item in R_DISPLAY:
        if item == "R1":
            # Merge: pass (1.0) only if all three R1 sub-items pass
            merged = []
            for r in RUN_ORDER:
                vals = [item_data.get(sub, {}).get(r, 0.5) for sub in R1_GROUP]
                if all(v == 1.0 for v in vals):
                    merged.append(1.0)
                elif any(v == 0.0 for v in vals):
                    merged.append(0.0)
                else:
                    merged.append(0.5)
            rows.append(merged)
        else:
            vals = item_data.get(item, {})
            rows.append([vals.get(r, 0.5) for r in RUN_ORDER])
        labels.append(heatmap_label(item))
    return labels, rows


def render_heatmap(data, labels, separator_rows, output_path, annotate_positive=False):
    """Render and save a heatmap."""
    n_rows, n_cols = data.shape
    cell_size = 0.4
    fig_w = n_cols * cell_size + 8
    fig_h = n_rows * cell_size + 3.5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_title(TITLE, fontsize=13, fontweight="bold", pad=75)

    style_heatmap(ax, fig, data, labels, separator_rows=separator_rows, has_na=True,
                  show_summary=SHOW_SUMMARY)

    # '✓' on present/found cells for B&W readability and quick visual scan
    if annotate_positive:
        for r in range(n_rows):
            for c in range(n_cols):
                if data[r, c] == 1.0:
                    ax.text(c, r, "✓", ha="center", va="center_baseline",
                            fontsize=10, color="black", fontweight="bold")

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Saved → {output_path}")


def save_csv(data, labels, csv_path):
    """Save a heatmap data array as CSV with run IDs and summary columns."""
    df = pd.DataFrame(data, index=labels, columns=RUN_ORDER)
    df["P1"] = (data[:, list(P1_COLS)] == 1.0).sum(axis=1)
    df["P2"] = (data[:, list(P2_COLS)] == 1.0).sum(axis=1)
    df["P3"] = (data[:, list(P3_COLS)] == 1.0).sum(axis=1)
    df["All"] = (data == 1.0).sum(axis=1)
    df.index.name = "item"
    df.to_csv(csv_path)
    print(f"  Saved → {csv_path}")


def generate_required(item_data):
    """Generate R-only heatmap (10 rows)."""
    labels, rows = build_r_rows(item_data)
    data = np.array(rows)
    render_heatmap(data, labels, [], OUTPUT_DIR / "task_completion_required.png",
                   annotate_positive=True)
    save_csv(data, labels, OUTPUT_DIR / "task_completion_required.csv")
    return data.shape[0]


def generate_curated(item_data):
    """Generate curated heatmap (10 R + selected M, grouped)."""
    r_labels, r_rows = build_r_rows(item_data)

    m_labels, m_rows = [], []
    for group_name, item_ids in CURATED_ITEMS:
        sorted_ids = sorted(item_ids, key=lambda x: m_sort_key(x, item_data))
        for item_id in sorted_ids:
            vals = item_data.get(item_id, {})
            m_rows.append([vals.get(r, 0.5) for r in RUN_ORDER])
            m_labels.append(M_DESCRIPTIONS.get(item_id, item_id))

    data = np.array(r_rows + m_rows)
    labels = r_labels + m_labels
    separator_rows = [len(R_DISPLAY)]
    render_heatmap(data, labels, separator_rows, OUTPUT_DIR / "task_completion_curated.png",
                   annotate_positive=True)
    save_csv(data, labels, OUTPUT_DIR / "task_completion_curated.csv")
    return data.shape[0]


def generate_full(item_data):
    """Generate full heatmap (10 R + all M with ≥1 appearance, grouped by category)."""
    r_labels, r_rows = build_r_rows(item_data)

    # Collect all M items with at least one appearance
    all_m = [k for k in item_data if k.startswith("M")
             and any(item_data[k].get(r, 0.5) == 1.0 for r in RUN_ORDER)]

    # Sort within each group by appearance count desc
    all_m.sort(key=lambda x: m_sort_key(x, item_data))

    m_labels, m_rows = [], []
    for item_id in all_m:
        vals = item_data[item_id]
        m_rows.append([vals.get(r, 0.5) for r in RUN_ORDER])
        m_labels.append(m_label(item_id))

    data = np.array(r_rows + m_rows)
    labels = r_labels + m_labels
    separator_rows = [len(R_DISPLAY)]
    render_heatmap(data, labels, separator_rows, OUTPUT_DIR / "task_completion_full.png",
                   annotate_positive=True)
    save_csv(data, labels, OUTPUT_DIR / "task_completion_full.csv")
    return data.shape[0]


def main():
    print(f"Scanning {EVAL_RUNS_DIR} for findings.csv files...")
    item_data = parse_findings_csvs()
    n_runs = len(set().union(*(v.keys() for v in item_data.values() if v)))
    n_m = sum(1 for k in item_data if k.startswith("M") and any(v == 1.0 for v in item_data[k].values()))
    print(f"  {len(R_ITEMS_RAW)} R-items (merged to {len(R_DISPLAY)} display rows), {n_m} M-items from {n_runs} runs\n")

    n = generate_required(item_data)
    print(f"  → Required: {n} rows")

    n = generate_curated(item_data)
    print(f"  → Curated: {n} rows")

    n = generate_full(item_data)
    print(f"  → Full: {n} rows")


if __name__ == "__main__":
    main()
