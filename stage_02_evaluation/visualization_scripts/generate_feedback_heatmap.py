#!/usr/bin/env python3
"""Generate a feedback-categories heatmap from per-run feedbacks.csv files using seaborn."""

import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, str(Path(__file__).parent))
from heatmap_common import (RUN_ORDER, FOLDER_TO_RUN_ID, add_multilevel_columns,
                            add_summary_columns_counts,
                            P1_COLS, P2_COLS, P3_COLS)

SCRIPTS_DIR = Path(__file__).resolve().parent
STAGE_DIR = SCRIPTS_DIR.parent
PROJECT_ROOT = STAGE_DIR.parent
INSTANCE_DIR = PROJECT_ROOT / "instance"
EVAL_RUNS_DIR = INSTANCE_DIR / "evaluation_runs"
MAPPING_PATH = INSTANCE_DIR / "data" / "mappings" / "raw_themes_per_run.csv"
OUTPUT_PATH = INSTANCE_DIR / "outputs" / "heatmaps" / "feedback_categories.png"
CSV_PATH = INSTANCE_DIR / "outputs" / "heatmaps" / "feedback_categories.csv"

SHOW_SUMMARY = False  # Hide P1/P2/P3/All summary columns on heatmap


def load_explicit_mapping():
    """Load the explicit raw_theme -> canonical_label mapping per run."""
    mapping = {}  # (run_folder, raw_theme) -> canonical_label
    with open(MAPPING_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["run_folder"], row["raw_theme"])
            mapping[key] = row["canonical_label"]
    return mapping


def load_feedback_data(mapping):
    """Build feedback counts using explicit mapping from raw_themes_per_run.csv.

    Uses MAX aggregation: when multiple raw themes in the same run map to the
    same canonical, take the maximum count (not the sum) to avoid inflation.
    """
    data = {}

    if not EVAL_RUNS_DIR.exists():
        return data

    for folder in sorted(EVAL_RUNS_DIR.iterdir()):
        if not folder.is_dir() or not folder.name.startswith("prompt-"):
            continue
        feedbacks_path = folder / "feedbacks.csv"
        if not feedbacks_path.exists():
            continue

        run_id = FOLDER_TO_RUN_ID.get(folder.name)
        if not run_id:
            continue

        counts = {}  # canonical_label -> max count
        with open(feedbacks_path, encoding="utf-8") as f:
            header = f.readline()  # skip header
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
                    print(f"  WARNING: malformed count in {folder.name} for theme {theme!r}: {count_str!r}")
                    continue

                canonical = mapping.get((folder.name, theme))
                if canonical:
                    # MAX aggregation: take the larger count if collision
                    counts[canonical] = max(counts.get(canonical, 0), count_val)
                else:
                    print(f"  WARNING: unmapped theme in {folder.name}: {theme}")

        data[run_id] = counts

    return data


MISC_LABEL = "Miscellaneous / Uncategorized"  # canonical name in CSV
MISC_DISPLAY = "Miscellaneous / Other"
CANONICAL_PATH = INSTANCE_DIR / "data" / "mappings" / "theme_canonical_mapping.csv"

# Display labels: strip redundant "Issues" suffix and compact long labels
# so y-tick text doesn't overflow into the heatmap body at print width.
DISPLAY_OVERRIDES = {
    "Time & Scheduling Issues": "Time & Scheduling",
    "Content Clarity Issues": "Content Clarity",
    "Knowledge Integration / Cross-course": "Knowledge Integration",
    "Teaching Materials / Documentation": "Teaching Materials",
    "Professional Identity / Motivation": "Prof. Motivation",
    "Enjoyment / Positive Atmosphere": "Positive Atmosphere",
    "Real Clinic / Clinical Setting": "Clinical Setting",
    "Assessment / Grading Pressure": "Grading Pressure",
}


def load_polarity_map():
    """Load canonical_label -> polarity from theme_canonical_mapping.csv."""
    polarity = {}
    with open(CANONICAL_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            polarity[row["canonical_label"]] = row["polarity"]
    return polarity


def build_dataframe(data):
    """Build a DataFrame grouped by polarity: Positive, then Issue, then Misc.

    Within each polarity group, sorted by total count descending.
    Separator row index returned for drawing horizontal line.
    """
    polarity_map = load_polarity_map()

    # Collect all canonical labels seen across runs
    all_labels = set()
    for counts in data.values():
        all_labels.update(counts.keys())

    # Compute total count across all runs for each canonical
    totals = {}
    for label in all_labels:
        totals[label] = sum(data.get(r, {}).get(label, 0) for r in RUN_ORDER)

    # Split into polarity groups (exclude misc)
    positive = sorted(
        [l for l in all_labels if l != MISC_LABEL and polarity_map.get(l) == "positive"],
        key=lambda l: -totals[l],
    )
    negative = sorted(
        [l for l in all_labels if l != MISC_LABEL and polarity_map.get(l) == "negative"],
        key=lambda l: -totals[l],
    )

    row_labels = []
    row_data = []
    rank = 1

    # Positive group (row position + green color convey polarity — no prefix needed)
    for label in positive:
        cid = f"C{rank:02d}"
        display = DISPLAY_OVERRIDES.get(label, label)
        row = [data.get(r, {}).get(label, 0) for r in RUN_ORDER]
        row_data.append(row)
        row_labels.append(f"{cid}  {display}")
        rank += 1

    separator_row = len(row_labels)  # separator after positive group

    # Issue (negative) group (row position + red/orange color convey polarity)
    for label in negative:
        cid = f"C{rank:02d}"
        display = DISPLAY_OVERRIDES.get(label, label)
        row = [data.get(r, {}).get(label, 0) for r in RUN_ORDER]
        row_data.append(row)
        row_labels.append(f"{cid}  {display}")
        rank += 1

    # Misc row omitted — mostly empty/vague responses, not meaningful
    # if MISC_LABEL in all_labels:
    #     row = [data.get(r, {}).get(MISC_LABEL, 0) for r in RUN_ORDER]
    #     row_data.append(row)
    #     row_labels.append(f"     {MISC_DISPLAY}")

    df = pd.DataFrame(row_data, index=row_labels,
                      columns=[str(i) for i in range(len(RUN_ORDER))])
    return df, separator_row


def main():
    print("Loading data...")
    mapping = load_explicit_mapping()
    data = load_feedback_data(mapping)
    n_canonicals = len(set(mapping.values()))
    print(f"  {n_canonicals} canonical categories, {len(data)} runs")

    df, separator_row = build_dataframe(data)
    n_rows, n_cols = df.shape
    print(f"  Matrix: {n_rows} x {n_cols}")

    # ── CSV export ──────────────────────────────────────────────────
    df_csv = df.copy()
    df_csv.columns = RUN_ORDER
    arr = df_csv.values.astype(int)
    df_csv["P1"] = arr[:, list(P1_COLS)].sum(axis=1)
    df_csv["P2"] = arr[:, list(P2_COLS)].sum(axis=1)
    df_csv["P3"] = arr[:, list(P3_COLS)].sum(axis=1)
    df_csv["All"] = arr.sum(axis=1)
    df_csv.index.name = "category"
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_csv.to_csv(CSV_PATH)
    print(f"  Saved → {CSV_PATH}")

    # ── Figure setup ────────────────────────────────────────────────
    cell_size = 0.4
    fig_w = n_cols * cell_size + 8   # extra for labels + summary columns
    fig_h = n_rows * cell_size + 4
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # ── Find the Miscellaneous row to mask from color ──────────────
    null_row = None
    for i, label in enumerate(df.index):
        if "Miscellaneous" in label:
            null_row = i
            break

    # ── Dual-colormap heatmap: Greens for positive, YlOrRd for negative ──
    values = df.values.astype(float)
    vmax_pos = values[:separator_row, :].max() if separator_row > 0 else 1
    vmax_neg = values[separator_row:, :].max() if separator_row < n_rows else 1

    cmap_pos = plt.cm.Greens
    cmap_neg = plt.cm.YlOrRd
    norm_pos = plt.Normalize(vmin=0, vmax=vmax_pos)
    norm_neg = plt.Normalize(vmin=0, vmax=vmax_neg)

    # Draw cells manually with polarity-based coloring
    for i in range(n_rows):
        for j in range(n_cols):
            if null_row is not None and i == null_row:
                fc = "#F0F0F0"
            else:
                val = values[i, j]
                if i < separator_row:
                    fc = cmap_pos(norm_pos(val))
                else:
                    fc = cmap_neg(norm_neg(val))
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=fc,
                         edgecolor="white", linewidth=0.5))

    ax.set_xlim(0, n_cols)
    ax.set_ylim(n_rows, 0)
    ax.set_aspect("equal")
    ax.set_yticks([i + 0.5 for i in range(n_rows)])
    ax.set_yticklabels(df.index)
    ax.set_xticks([])

    # ── Annotations: 0 in light gray, high values in white, others black ──
    for i in range(n_rows):
        for j in range(n_cols):
            if null_row is not None and i == null_row:
                val = int(values[i, j])
                if val > 0:
                    ax.text(j + 0.5, i + 0.5, str(val), ha="center", va="center",
                            fontsize=8.5, color="#666666")
                continue
            val = int(values[i, j])
            if val == 0:
                color = "#e0e0e0"
            elif i < separator_row and val > vmax_pos * 0.5:
                color = "white"
            elif i >= separator_row and val > vmax_neg * 0.5:
                color = "white"
            else:
                color = "black"
            ax.text(j + 0.5, i + 0.5, str(val), ha="center", va="center",
                    fontsize=11, color=color)

    # Colorbars dropped — row position + cell shade communicate polarity
    # and magnitude, and the redundant cbar consumed lateral space.

    # ── y-axis labels left-aligned to match Figure 2 (task heatmap) ──
    # Every label starts at the same x so the C-prefix anchors line up
    # vertically and visually match Figure 2's R-prefix column.
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=12.5, rotation=0, ha='left')
    ax.tick_params(axis='y', which='major', pad=240)

    # ── Remove auto-generated axis labels ──────────────────────────
    ax.set_xlabel("")
    ax.set_ylabel("")

    # ── Shared multi-level column labels ───────────────────────────
    add_multilevel_columns(ax, fig, n_cols, x_offset=0.5)

    # ── Horizontal separator between Positive and Issue groups ─────
    ax.axhline(y=separator_row, color="black", linewidth=1.5)

    # ── Outer border ────────────────────────────────────────────────
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("black")
        spine.set_linewidth(1.0)

    # ── Summary columns: P1/P2/P3/All in right margin ─────────────
    data_array = df.values.astype(int)
    add_summary_columns_counts(ax, data_array, n_cols, y_offset=0.5,
                               show_summary=SHOW_SUMMARY)

    # ── Title ──────────────────────────────────────────────────────
    ax.set_title("Feedback Categories from 72 Students Across Three Academic Years",
                 fontsize=13, fontweight="bold", pad=75)

    fig.tight_layout()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Saved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
