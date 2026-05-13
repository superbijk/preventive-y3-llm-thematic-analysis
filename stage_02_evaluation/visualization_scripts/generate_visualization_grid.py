#!/usr/bin/env python3
"""Generate a 3×3 visualization grid (Figure 4) showing representative
experiment figures across prompt tiers and models.

Rows: Prompt 1 (Detailed), Prompt 2 (Structured), Prompt 3 (Exploratory)
Cols: Claude Opus 4.6, GPT-5.3 Codex, Gemini 3 Pro

Output: instance/outputs/heatmaps/visualization_grid.png
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
EXPERIMENT_DIR = PROJECT_ROOT / "instance" / "experiment_runs"
HEATMAPS_DIR = PROJECT_ROOT / "instance" / "outputs" / "heatmaps"

# ── Source figure paths (Run 1 for each cell) ────────────────────────────────
GRID = [
    # Row 0: Prompt 1 (Detailed) — all produce similar satisfaction bar charts
    [
        "prompt_1/20260207_010100__opus4-6/figures/1_satisfaction_charts.png",
        "prompt_1/20260207_012518__gpt5-3/figures/1_satisfaction_charts.png",
        "prompt_1/20260207_012929__gemini-pro/figures/1_satisfaction_charts.png",
    ],
    # Row 1: Prompt 2 (Structured) — same chart type, different styles
    [
        "prompt_2/20260207_114248__opus4-6/figures/1_satisfaction_charts.png",
        "prompt_2/20260207_114724__gpt5-3/figures/1_satisfaction_charts.png",
        "prompt_2/20260207_115134__gemini-pro/figures/1_satisfaction_charts.png",
    ],
    # Row 2: Prompt 3 (Exploratory) — different chart types entirely
    [
        "prompt_3/20260207_122851__opus4-6/figures/fig1_mean_scores_by_year.png",
        "prompt_3/20260207_123510__gpt5-3/figures/02_metric_mean_trends.png",
        "prompt_3/20260207_124050__gemini-pro/figures/trend_analysis.png",
    ],
]

ROW_LABELS = [
    "Prompt 1\n(Detailed)",
    "Prompt 2\n(Structured)",
    "Prompt 3\n(Exploratory)",
]

COL_LABELS = [
    "Claude Opus 4.6",
    "GPT-5.3 Codex",
    "Gemini 3 Pro",
]


def pad_to_target(img, target_w, target_h):
    """Pad an image to target dimensions with white fill, centered."""
    h, w = img.shape[:2]
    if img.dtype == np.float32 or img.dtype == np.float64:
        canvas = np.ones((target_h, target_w, img.shape[2]), dtype=img.dtype)
    else:
        canvas = np.full((target_h, target_w, img.shape[2]), 255, dtype=img.dtype)
    y_off = (target_h - h) // 2
    x_off = (target_w - w) // 2
    canvas[y_off:y_off + h, x_off:x_off + w] = img
    return canvas


def main():
    # First pass: read all images and find a common aspect ratio
    images = {}
    for row in range(3):
        for col in range(3):
            src = EXPERIMENT_DIR / GRID[row][col]
            if src.exists():
                images[(row, col)] = mpimg.imread(str(src))

    # Find max width and max height across all images, then scale each
    # to fit within that box (preserving ratio) before padding
    max_w = max(img.shape[1] for img in images.values())
    max_h = max(img.shape[0] for img in images.values())

    # Scale each image so its largest dimension matches the target,
    # then pad the other dimension to the target size
    from PIL import Image

    processed = {}
    for key, img in images.items():
        h, w = img.shape[:2]
        scale = min(max_w / w, max_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        # Resize using PIL for quality
        is_float = img.dtype in (np.float32, np.float64)
        if is_float:
            pil_img = Image.fromarray((img * 255).astype(np.uint8))
        else:
            pil_img = Image.fromarray(img)
        pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
        arr = np.array(pil_img)
        if is_float:
            arr = arr.astype(np.float32) / 255.0
        processed[key] = pad_to_target(arr, max_w, max_h)

    fig_aspect = max_h / max_w
    fig, axes = plt.subplots(3, 3, figsize=(11, 11 * fig_aspect),
                             facecolor="white")
    fig.subplots_adjust(left=0.12, right=0.98, top=0.94, bottom=0.02,
                        wspace=0.02, hspace=0.02)

    # Padding (fraction of image dimensions) so content doesn't touch borders
    pad_frac = 0.02
    for row in range(3):
        for col in range(3):
            ax = axes[row, col]
            if (row, col) in processed:
                img = processed[(row, col)]
                ax.imshow(img, aspect="equal")
                h, w = img.shape[:2]
                ax.set_xlim(-w * pad_frac, w * (1 + pad_frac))
                ax.set_ylim(h * (1 + pad_frac), -h * pad_frac)
            else:
                ax.set_facecolor("#e0e0e0")
                ax.text(0.5, 0.5, "N/A", transform=ax.transAxes,
                        ha="center", va="center", fontsize=16, color="#888")

            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_linewidth(0.5)
                spine.set_color("#bbbbbb")

    # Column labels (top) — more padding
    for col, label in enumerate(COL_LABELS):
        axes[0, col].set_title(label, fontsize=11, fontweight="normal", pad=16)

    # Row labels (left) — centered on each row
    for row, label in enumerate(ROW_LABELS):
        axes[row, 0].set_ylabel(label, fontsize=10, fontweight="normal",
                                rotation=0, labelpad=60, va="center")

    # Save
    HEATMAPS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = HEATMAPS_DIR / "visualization_grid.png"
    fig.savefig(str(out_path), dpi=300, bbox_inches="tight", facecolor="white")
    print(f"Saved: {out_path}")

    plt.close(fig)


if __name__ == "__main__":
    main()
