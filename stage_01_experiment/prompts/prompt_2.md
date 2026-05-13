# Dental Course Evaluation Analysis — Structured-Concise

You are analyzing anonymized student evaluation data for a preventive dentistry course taught to 3rd-year dental students across three academic years.

**Execute all steps below in order. Write Python code and run it to produce each output file.**

**Python environment**: Use the `dental-eval` conda environment. Run all Python commands with `conda run -n dental-eval python ...` (it has pandas, openpyxl, matplotlib, numpy).

---

## Data Description

**Input file**: `{{DATA_FILE}}`
- Single sheet named `feedbacks`, 89 rows, 6 columns
- Columns: `student_id` (str, S001–S089), `academic_year` (int: 2566/2567/2568), `satisfaction_teaching_process` (Likert 1–5), `satisfaction_learning` (Likert 1–5), `dissatisfaction_rating` (1–5, 1 = no dissatisfaction), `likes_dislikes` (Thai free-text, some null)
- Year distribution: 2566 (n=29), 2567 (n=30), 2568 (n=30)

Read the xlsx file with pandas + openpyxl. Confirm shape and columns before proceeding.

---

## Output 1: `{{RUN_DIR}}/statistics_summary.md`

Compute descriptive statistics (N, mean, SD, min, max, median) for all 3 satisfaction/dissatisfaction metrics, grouped by academic year and overall. Include frequency distributions for each metric across all years combined. Write key findings in Thai summarizing trends across years. Round means and SDs to 2 decimal places, percentages to 1 decimal place. Handle null values with `.dropna()`.

---

## Output 2: `{{RUN_DIR}}/feedback_analysis_llm.md`

**Do this BEFORE the summary.** Read every non-null `likes_dislikes` entry. Discover thematic categories by reading all feedback — do NOT use pre-defined categories.

For each category, provide:
- Thai category name with English translation
- Count of students in the category
- Brief Thai description of what students said
- Table with Student ID, academic year, and original Thai text (preserved exactly as-is)

Organize into "สิ่งที่ชอบ (Likes)" and "สิ่งที่ไม่ชอบ/ข้อเสนอแนะ (Dislikes & Suggestions)" sections. A student can appear in multiple categories.

---

## Output 3: `{{RUN_DIR}}/feedback_summary.md`

**Write AFTER the detailed analysis, using its results.** Summary-level report with NO individual student rows — only aggregate counts and cross-tabulation tables using the same categories from the detailed analysis. Include Thai observations on trends across years and recommendations. End with: `*Summary generated using LLM-based text analysis ({{MODEL_NAME}})*`

---

## Output 4: Charts in `{{RUN_DIR}}/figures/`

Generate 4 PNG chart files (DPI 150, white background, tight layout):

1. **`1_satisfaction_charts.png`** — Overview: 1×3 subplot bar chart showing mean scores by year for all 3 metrics
2. **`2_satisfaction_teaching_process.png`** — Detail: mean bars + per-year rating histograms with mean line
3. **`3_satisfaction_learning.png`** — Detail: same layout as chart 2
4. **`4_dissatisfaction_rating.png`** — Detail: same layout as chart 2

Use distinct colors per metric. Include sample sizes and value labels on bars.

---

## Save Scripts

Save all Python code used to `{{RUN_DIR}}/` (e.g. `generate_statistics.py`, `generate_charts.py`, `generate_feedback_reports.py`).

---

## Completion Gate

Required files (must exist and file size > 0):
- `{{RUN_DIR}}/statistics_summary.md`
- `{{RUN_DIR}}/feedback_analysis_llm.md`
- `{{RUN_DIR}}/feedback_summary.md`
- `{{RUN_DIR}}/generate_statistics.py`
- `{{RUN_DIR}}/generate_feedback_reports.py`
- `{{RUN_DIR}}/generate_charts.py`
- `{{RUN_DIR}}/figures/1_satisfaction_charts.png`
- `{{RUN_DIR}}/figures/2_satisfaction_teaching_process.png`
- `{{RUN_DIR}}/figures/3_satisfaction_learning.png`
- `{{RUN_DIR}}/figures/4_dissatisfaction_rating.png`

Verify all outputs exist and are non-empty before finishing:

```bash
ls -lh {{RUN_DIR}} {{RUN_DIR}}/figures
for f in \
  {{RUN_DIR}}/statistics_summary.md \
  {{RUN_DIR}}/feedback_analysis_llm.md \
  {{RUN_DIR}}/feedback_summary.md \
  {{RUN_DIR}}/generate_statistics.py \
  {{RUN_DIR}}/generate_feedback_reports.py \
  {{RUN_DIR}}/generate_charts.py \
  {{RUN_DIR}}/figures/1_satisfaction_charts.png \
  {{RUN_DIR}}/figures/2_satisfaction_teaching_process.png \
  {{RUN_DIR}}/figures/3_satisfaction_learning.png \
  {{RUN_DIR}}/figures/4_dissatisfaction_rating.png; do
  test -s "$f" || { echo "MISSING_OR_EMPTY: $f"; exit 1; }
done
echo "ALL_REQUIRED_OUTPUTS_PRESENT"
```

Only finish after printing `ALL_REQUIRED_OUTPUTS_PRESENT`.
