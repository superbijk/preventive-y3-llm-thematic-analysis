"""Shared constants and helpers for evaluation heatmaps."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.transforms as mtransforms
import matplotlib.text as mtext
from matplotlib.legend_handler import HandlerPatch
import numpy as np

# ── Canonical run order (27 runs) ───────────────────────────────────
RUN_ORDER = [
    "p1_opus_r1", "p1_opus_r2", "p1_opus_r3",
    "p1_gpt_r1",  "p1_gpt_r2",  "p1_gpt_r3",
    "p1_gemini_r1","p1_gemini_r2","p1_gemini_r3",
    "p2_opus_r1", "p2_opus_r2", "p2_opus_r3",
    "p2_gpt_r1",  "p2_gpt_r2",  "p2_gpt_r3",
    "p2_gemini_r1","p2_gemini_r2","p2_gemini_r3",
    "p3_opus_r1", "p3_opus_r2", "p3_opus_r3",
    "p3_gpt_r1",  "p3_gpt_r2",  "p3_gpt_r3",
    "p3_gemini_r1","p3_gemini_r2","p3_gemini_r3",
]

PROMPT_LABELS = ["Prompt 1", "Prompt 2", "Prompt 3"]
MODEL_LABELS = ["Opus", "GPT", "Gemini"]
REP_LABELS = ["1", "2", "3"]

# Column index ranges for each prompt group
P1_COLS = range(0, 9)
P2_COLS = range(9, 18)
P3_COLS = range(18, 27)

# Discrete colormaps — green/orange pairing matched to Figure 4's polarity
# palette so the manuscript figure family reads consistently:
#   Present = #66BD63 (medium green, mid-range of RdYlGn Greens)
#   Absent  = #FDAE61 (RdYlGn orange, distinct in greyscale and deuteranopia)
#   NA      = #DDDDDD (neutral light gray)
# The earlier blue/vermillion pair (Okabe-Ito) was technically colourblind-safe
# but visually divorced from Figure 4's green/red polarity coding; the
# RdYlGn pair below preserves accessibility while aligning the figure set.
CMAP = mcolors.ListedColormap(["#FDAE61", "#66BD63"])
CMAP_WITH_NA = mcolors.ListedColormap(["#FDAE61", "#DDDDDD", "#66BD63"])

# Mapping from folder name to run_id
FOLDER_TO_RUN_ID = {
    f"prompt-{p}_{m}_run-{r}": f"p{p}_{m}_r{r}"
    for p in [1, 2, 3] for m in ["opus", "gpt", "gemini"] for r in [1, 2, 3]
}


def add_multilevel_columns(ax, fig, n_cols, x_offset=0.0):
    """Draw 2-tier column labels above the plot: rotated Model(Rep) + Prompt header.

    x_offset: 0 for imshow, 0.5 for seaborn heatmap.
    """
    # Build per-column labels: "Opus (1)", "Opus (2)", ..., "Gemini (3)"
    col_labels = []
    for _p in range(3):
        for model in MODEL_LABELS:
            for rep in REP_LABELS:
                col_labels.append(f"{model} ({rep})")

    ax.set_xticks([i + x_offset for i in range(n_cols)])
    ax.set_xticklabels(col_labels, fontsize=9.5, rotation=45, ha="left",
                       rotation_mode="anchor")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.tick_params(axis="x", which="major", length=0, pad=4)

    # Prompt headers above rotated labels
    base = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    prompt_tx = mtransforms.offset_copy(base, fig=fig, y=42, units='points')

    for p, label in enumerate(PROMPT_LABELS):
        cx = p * 9 + 4 + x_offset
        ax.text(cx, 1.0, label, transform=prompt_tx,
                ha="center", va="bottom", fontsize=10.5)

    # Vertical dividers
    for bx in [9, 18]:
        ax.axvline(x=bx - 0.5 + x_offset, color="black", linewidth=2)
    for p in range(3):
        for mb in [3, 6]:
            bx = p * 9 + mb
            if bx not in [9, 18]:
                ax.axvline(x=bx - 0.5 + x_offset, color="#333333",
                           linewidth=1.0, linestyle="--")


def add_summary_columns_binary(ax, data, n_cols, show_summary=True):
    """Add P1/P2/P3/All summary columns in right margin for binary heatmaps."""
    if not show_summary:
        return
    n_rows = data.shape[0]
    headers = ["P1", "P2", "P3", "All"]
    col_ranges = [P1_COLS, P2_COLS, P3_COLS, range(27)]

    # Headers at top
    blend = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    for j, hdr in enumerate(headers):
        x = n_cols + 0.8 + j * 1.2
        ax.text(x, 1.01, hdr, transform=blend,
                va="bottom", ha="center", fontsize=8.5, fontweight="bold")

    # Values per row
    for i in range(n_rows):
        for j, cols in enumerate(col_ranges):
            count = sum(1 for c in cols if data[i, c] == 1.0)
            x = n_cols + 0.8 + j * 1.2
            ax.text(x, i, str(count), va="center", ha="center",
                    fontsize=8, color="black")


def add_summary_columns_counts(ax, data_array, n_cols, y_offset=0.5, show_summary=True):
    """Add P1/P2/P3/All summary columns in right margin for count heatmaps."""
    if not show_summary:
        return
    n_rows = data_array.shape[0]
    headers = ["P1", "P2", "P3", "All"]
    col_ranges = [P1_COLS, P2_COLS, P3_COLS, range(27)]

    # Headers at top
    for j, hdr in enumerate(headers):
        x = n_cols + 0.8 + j * 1.2
        ax.text(x, -0.3, hdr, va="center", ha="center",
                fontsize=8.5, fontweight="bold")

    # Values per row
    for i in range(n_rows):
        for j, cols in enumerate(col_ranges):
            total = sum(int(data_array[i, c]) for c in cols)
            x = n_cols + 0.8 + j * 1.2
            ax.text(x, i + y_offset, str(total), va="center", ha="center",
                    fontsize=8, color="black")


def style_heatmap(ax, fig, data, row_labels, separator_rows=None, has_na=False,
                  show_summary=True):
    """Render a binary/ternary heatmap with square cells and multi-level columns."""
    n_rows, n_cols = data.shape
    cmap = CMAP_WITH_NA if has_na else CMAP
    vmax = 1.0

    ax.imshow(data, aspect="equal", cmap=cmap, vmin=0, vmax=vmax,
              interpolation="nearest")

    # ── Multi-level column labels (at top) ──────────────────────────
    add_multilevel_columns(ax, fig, n_cols, x_offset=0.0)

    # ── Row labels (left-aligned) ────────────────────────────────────
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(row_labels, fontsize=12.5, ha='left')
    ax.tick_params(axis='y', which='major', pad=240)

    # ── Horizontal separators ───────────────────────────────────────
    if separator_rows:
        for sr in separator_rows:
            ax.axhline(y=sr - 0.5, color="black", linewidth=1.5)

    # ── Summary columns in right margin ─────────────────────────────
    add_summary_columns_binary(ax, data, n_cols, show_summary=show_summary)

    # ── Cell grid ───────────────────────────────────────────────────
    ax.set_xticks([x - 0.5 for x in range(1, n_cols)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, n_rows)], minor=True)
    ax.tick_params(which="minor", length=0)
    ax.grid(which="minor", color="white", linewidth=0.5)

    # ── Legend (square swatches, black '✓' centered inside Present) ───
    class _HandlerPatchCheck(HandlerPatch):
        """Draw a square swatch with a black check mark optically centered.

        The default HandlerPatch draws a wide rectangle (~3:1) keyed off the
        text length; we override both width and height to the same `side`
        value so the swatch reads as a square box. The check glyph is placed
        at the rectangle's geometric centre and uses ``va='center_baseline'``
        so the visual mass of the tick sits on the centre rather than above it.
        """
        def __init__(self, side_pts):
            super().__init__()
            self._side_pts = side_pts

        def create_artists(self, legend, orig_handle,
                           xdescent, ydescent, width, height, fontsize, trans):
            side = self._side_pts
            artists = super().create_artists(
                legend, orig_handle, xdescent, ydescent, side, side,
                fontsize, trans)
            cx = -xdescent + side / 2
            cy = -ydescent + side / 2
            txt = mtext.Text(cx, cy, "✓", ha="center", va="center_baseline",
                             fontsize=side * 0.75, color="black",
                             fontweight="bold", transform=trans)
            artists.append(txt)
            return artists

    # Plain absent-patch handler also forced square so both swatches match.
    class _HandlerPatchSquare(HandlerPatch):
        def __init__(self, side_pts):
            super().__init__()
            self._side_pts = side_pts
        def create_artists(self, legend, orig_handle,
                           xdescent, ydescent, width, height, fontsize, trans):
            side = self._side_pts
            return super().create_artists(
                legend, orig_handle, xdescent, ydescent, side, side,
                fontsize, trans)

    SWATCH_PTS = 22  # legend swatch side in points (square)
    present_patch = mpatches.Patch(facecolor="#66BD63", edgecolor="gray",
                                   label="Present")
    absent_patch = mpatches.Patch(facecolor="#FDAE61", edgecolor="gray",
                                  label="Absent")
    ax.legend(handles=[present_patch, absent_patch], loc="upper center",
              bbox_to_anchor=(0.5, -0.04), ncol=2, fontsize=11,
              frameon=False,
              handlelength=SWATCH_PTS / 11,  # in font-size units
              handleheight=SWATCH_PTS / 11,
              handletextpad=0.6, columnspacing=2.2,
              handler_map={
                  present_patch: _HandlerPatchCheck(SWATCH_PTS),
                  absent_patch:  _HandlerPatchSquare(SWATCH_PTS),
              })

    ax.set_xlim(-0.5, n_cols - 0.5)
    ax.set_ylim(n_rows - 0.5, -0.5)
