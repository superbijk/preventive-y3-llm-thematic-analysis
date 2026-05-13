"""Single source of truth for R-item display labels.

Imported by:
  - generate_task_heatmaps.py (Figure 2 y-tick labels)
  - .manuscript/manuscript_1_llm_thematic_analysis/build_tables.py (Table 1 row labels)

Editing rule (see manuscript_writing_guide.md): never duplicate these strings
elsewhere in the codebase. Change here and re-run figure/table builds.

R1 is a merged display row that aggregates R1.1, R1.2, R1.3 — the three
satisfaction Likert means always co-occur in a single 'satisfaction means'
task per the evaluation rubric.
"""

R_DISPLAY = ["R1", "R2.1", "R2.2", "R2.3", "R2.4", "R2.5", "R3.1", "R3.2"]

R_LABELS = {
    "R1":   "Satisfaction means",
    "R2.1": "Categorize into themes",
    "R2.2": "Separate likes vs dislikes",
    "R2.3": "Cross-tabulation tables by year",
    "R2.4": "Year trend analysis",
    "R2.5": "LLM-based thematic analysis",
    "R3.1": "Satisfaction bar charts",
    "R3.2": "Per-satisfaction detail charts",
}


def heatmap_label(item: str) -> str:
    """Label for figure y-ticks: 'R1  Satisfaction means'."""
    return f"{item}  {R_LABELS[item]}"


def table_label(item: str) -> str:
    """Label for manuscript tables: '(R1) Satisfaction means'."""
    return f"({item}) {R_LABELS[item]}"
