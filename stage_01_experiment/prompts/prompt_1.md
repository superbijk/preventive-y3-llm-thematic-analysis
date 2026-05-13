# Dental Course Evaluation Analysis — Full Pipeline

You are analyzing anonymized student evaluation data for a preventive dentistry course taught to 3rd-year dental students across three academic years.

**Execute all steps below in order. Write Python code and run it to produce each output file.**

**Python environment**: Use the `dental-eval` conda environment. Run all Python commands with `conda run -n dental-eval python ...` (it has pandas, openpyxl, matplotlib, numpy).

---

## Section A: Data Description

**Input file**: `{{DATA_FILE}}`
- Single sheet named `feedbacks`, 89 rows, 6 columns
- All student IDs are already anonymized (S001–S089)

| Column | Type | Description |
|--------|------|-------------|
| `student_id` | str | Anonymized ID (S001–S089) |
| `academic_year` | int | 2566 (n=29), 2567 (n=30), 2568 (n=30) |
| `satisfaction_teaching_process` | int | Likert 1–5 |
| `satisfaction_learning` | int | Likert 1–5 |
| `dissatisfaction_rating` | int | 1–5 (1 = no dissatisfaction) |
| `likes_dislikes` | str | Thai free-text feedback (some rows are null) |

**First step**: Read the xlsx file with pandas + openpyxl. Confirm the shape and column names before proceeding.

---

## Section B: Output 1 — `{{RUN_DIR}}/statistics_summary.md`

Compute descriptive statistics and write a Markdown report.

### Structure:

```markdown
# Statistical Summary Report

รายงานสรุปผลการวิเคราะห์ความพึงพอใจในการเรียนการสอน

## Data Overview

| รายการ | จำนวน |
|--------|-------|
| จำนวนนิสิตทั้งหมด | XX คน |
| ปีการศึกษา 2566 | XX คน |
| ปีการศึกษา 2567 | XX คน |
| ปีการศึกษา 2568 | XX คน |

---

## Satisfaction Scores Summary

### 1. ความพึงพอใจกระบวนการสอน (Satisfaction with Teaching Process)

| ปีการศึกษา | N | Mean | SD | Min | Max | Median |
|------------|---|------|-----|-----|-----|--------|
| 2566 | ... | ... | ... | ... | ... | ... |
| 2567 | ... | ... | ... | ... | ... | ... |
| 2568 | ... | ... | ... | ... | ... | ... |
| **รวมทุกปี** | **...** | **...** | **...** | **...** | **...** | **...** |
```

Repeat the table for:
- **2. ความพึงพอใจการเรียนรู้ (Satisfaction with Learning)**
- **3. ความไม่พึงพอใจ (Dissatisfaction Rating)**

**Important notes on statistics**:
- Mean rounded to 2 decimal places, SD rounded to 2 decimal places
- Median rounded to 1 decimal place (e.g., 5.0, 4.5, 1.0)
- Min and Max as integers
- N = count of non-null values for that column in that year group
- For dissatisfaction_rating, note that some rows may have null values — use `.dropna()` before computing

### Frequency Distribution (รวมทุกปี)

For each of the 3 metrics, create a table:

```markdown
### ความพึงพอใจกระบวนการสอน

| คะแนน | จำนวน | ร้อยละ |
|-------|-------|--------|
| 1 | ... | ...% |
| 2 | ... | ...% |
| 3 | ... | ...% |
| 4 | ... | ...% |
| 5 | ... | ...% |
```

Percentages should be of the non-null total for that column, rounded to 1 decimal place.

### Key Findings section

Write in Thai:

```markdown
## Key Findings

### ผลการวิเคราะห์โดยรวม

1. **ความพึงพอใจกระบวนการสอน**: ค่าเฉลี่ยรวม X.XX (SD=X.XX) อยู่ในระดับ...
   - ปี XXXX มีค่าเฉลี่ยสูงสุด (X.XX)
   - ปี XXXX มีค่าเฉลี่ยต่ำสุด (X.XX)...

2. **ความพึงพอใจการเรียนรู้**: ...

3. **ความไม่พึงพอใจ**: ...

### สรุป

- [3-5 bullet points summarizing the key findings]
```

End with:
```
---

*Report generated from deduplicated data (89 unique students)*
```

---

## Section C: Detailed Thematic Analysis (do this BEFORE the summary)

### What to do

Read every non-null `likes_dislikes` entry. Each entry is Thai free-text that may contain things the student liked, disliked, or both.

**Your task**: Discover thematic categories by reading all the feedback. Do NOT use pre-defined categories. Instead:

1. Read through all feedback entries
2. Identify recurring themes for "likes" (สิ่งที่ชอบ) and "dislikes/suggestions" (สิ่งที่ไม่ชอบ/ข้อเสนอแนะ) that naturally emerge from the text
3. Name each category with a Thai label and English translation
4. Assign each student's feedback to the appropriate categories (a student can appear in multiple categories)

### Output file: `{{RUN_DIR}}/feedback_analysis_llm.md`

```markdown
# Feedback Analysis (LLM-Based)

การวิเคราะห์ความคิดเห็นจากแบบประเมินความพึงพอใจ โดยใช้ LLM ในการอ่านและจัดกลุ่มข้อความ

---

## Data Summary

| ปีการศึกษา | จำนวนนิสิต | จำนวนความคิดเห็น |
|------------|------------|------------------|
| 2566 | ... | ... |
| 2567 | ... | ... |
| 2568 | ... | ... |
| **รวม** | **...** | **...** |
```

Count "จำนวนความคิดเห็น" as non-null entries in `likes_dislikes` per year.

### Likes Section

For each discovered category:

```markdown
## สิ่งที่ชอบ (Likes)

### 1. [Thai Category Name] / [English Translation]

**จำนวน: XX คน**

[2-3 sentence Thai description of what students said in this category]

| Student ID | ปี | ความคิดเห็น |
|------------|-----|-------------|
| SXXX | 2566 | [relevant excerpt from feedback] |
| SXXX | 2567 | [relevant excerpt] |
| ... | ... | ... |

---
```

### Dislikes Section

Same format:

```markdown
## สิ่งที่ไม่ชอบ/ข้อเสนอแนะ (Dislikes & Suggestions)

### 1. [Thai Category Name] / [English Translation]

**จำนวน: XX คน**

[2-3 sentence Thai description]

| Student ID | ปี | ความคิดเห็น |
|------------|-----|-------------|
| SXXX | 2566 | [relevant excerpt] |
| ... | ... | ... |

---
```

**Formatting rules**:
- Use the anonymized student IDs (S001–S089) from the data
- For students whose feedback contains both likes and dislikes, show the full text under the relevant "like" category, and use "..." prefix/suffix when showing partial quotes under "dislike" categories
- A single student can appear in multiple categories
- Show the original Thai text as-is — do not translate or modify

---

## Section D: Feedback Summary (write AFTER Section C, using its results)

This is a summary-level report derived from the detailed analysis in Section C. It contains NO individual student rows — only aggregate counts and observations.

### Output file: `{{RUN_DIR}}/feedback_summary.md`

```markdown
# Feedback Summary Report

สรุปภาพรวมความคิดเห็นจากแบบประเมินความพึงพอใจ

## Data Summary

| ปีการศึกษา | จำนวนนิสิต | จำนวนความคิดเห็น |
|------------|------------|------------------|
| 2566 | ... | ... |
| 2567 | ... | ... |
| 2568 | ... | ... |
| **รวม** | **...** | **...** |
```

### Cross-tabulation tables

Use the **same categories and counts** discovered in Section C. Reproduce the cross-tabulation tables for likes and dislikes (same data, just without individual student rows).

### Observations

Write in Thai:

```markdown
## แนวโน้มและข้อสังเกต

1. **จุดเด่นของการจัดการเรียนการสอนและการเรียนรู้**: ...
2. **แนวโน้มในแต่ละปีการศึกษา**: ... (describe what changed or stayed consistent across years)
3. **ข้อเสนอแนะ**: ...
4. [Additional observations if any]

---

*Summary generated using LLM-based text analysis ({{MODEL_NAME}})*
```

---

## Section E: Four PNG Charts

Write Python code to generate 4 chart files. Use `pandas`, `matplotlib`, and `numpy`.

### Chart 1: `{{RUN_DIR}}/figures/1_satisfaction_charts.png`

**Overview bar chart** — 1×3 subplots showing all 3 metrics side by side.

- Figure size: `(14, 5)`
- Main title (bold): `'Satisfaction Survey Results by Academic Year'`
- 3 subplots, one per metric:
  - Subplot 1: `satisfaction_teaching_process` — title `'Teaching Process'`
  - Subplot 2: `satisfaction_learning` — title `'Learning'`
  - Subplot 3: `dissatisfaction_rating` — title `'Dissatisfaction'`
- Each subplot: bars for years 2566, 2567, 2568 (x-axis)
- Colors: `['#4472C4', '#ED7D31', '#70AD47']` (blue for subplot 1, orange for subplot 2, green for subplot 3)
- Bar edge: black, linewidth 0.5
- Y-axis: 0 to 5.5, label `'Score'`
- X-axis: label `'Academic Year'`, ticks at [2566, 2567, 2568]
- Value labels: mean value (2 decimal) on top of each bar, bold, fontsize 10
- Sample size: white bold text `'n=XX'` inside each bar at y=0.3
- Gridlines: horizontal dashed, alpha 0.7
- DPI: 150, white background, tight layout

### Charts 2–4: Detailed per-metric charts

Each chart has **1×4 subplots** (figure size `16×4.5`):
- **Left subplot**: mean bars by year (same as Chart 1 for that metric)
- **Right 3 subplots**: rating frequency histograms, one per year

**Chart 2**: `{{RUN_DIR}}/figures/2_satisfaction_teaching_process.png`
- Color: `#4472C4` (blue)
- Title: `'Satisfaction with Teaching Process'`

**Chart 3**: `{{RUN_DIR}}/figures/3_satisfaction_learning.png`
- Color: `#ED7D31` (orange)
- Title: `'Satisfaction with Learning'`

**Chart 4**: `{{RUN_DIR}}/figures/4_dissatisfaction_rating.png`
- Color: `#70AD47` (green)
- Title: `'Dissatisfaction Rating'`

**Histogram subplot details**:
- X-axis: ratings 1–5, range 0.5 to 5.5
- Y-axis: count of students
- Bar color: gray `#B0B0B0`, edge `#808080`, linewidth 0.5
- Count labels on top of each bar (only if count > 0), fontsize 9
- Vertical line at mean: color = metric color, linewidth 3, solid
- Mean annotation: `f'{mean:.2f}'`, bold, dark text `#333333`, fontsize 11, positioned at 85% of max count height, right-aligned just left of the line
- Title: `f'Year {year}\n(n={count})'`
- X-axis label: `'Rating'`
- Y-axis label: `'Count'`
- Gridlines: horizontal dashed, alpha 0.5

**Left subplot title**: `'All Years'`
- Has the same bar chart as Chart 1 (means by year with n= labels)

All charts: DPI 150, white background, tight layout.

---

## Section F: Execution Order

Follow this exact sequence:

1. **Read data**: Load `{{DATA_FILE}}`, verify shape and columns
2. **Statistics**: Compute all statistics → write `{{RUN_DIR}}/statistics_summary.md`
3. **Detailed thematic analysis**: Read all Thai feedback, discover categories, code each student → write `{{RUN_DIR}}/feedback_analysis_llm.md`
4. **Feedback summary**: Summarize the categories from step 3 → write `{{RUN_DIR}}/feedback_summary.md`
5. **Charts**: Write Python visualization code → execute → save 4 PNGs to `{{RUN_DIR}}/figures/`
6. **Save scripts**: Save all Python code used in the analysis to `{{RUN_DIR}}/` (e.g. `{{RUN_DIR}}/generate_statistics.py`, `{{RUN_DIR}}/generate_charts.py`)
7. **Verify**: List all output files and confirm they exist

**Critical requirements**:
- All student IDs must use the anonymized format from the data (S001–S089)
- All Thai text in feedback must be preserved exactly as-is
- Statistical values must be computed from the data (not hardcoded)
- Thematic categories must be discovered from the data — do not use pre-defined categories
- All chart text (titles, labels, annotations) must be in English

---

## Section G: Completion Gate (MUST PASS BEFORE FINISHING)

Do not stop after writing code. You must execute the scripts and verify all required outputs exist and are non-empty.

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

At the end, run verification commands and print their output:

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

If any check fails, continue working and rerun generation until all checks pass.
Only finish after printing `ALL_REQUIRED_OUTPUTS_PRESENT`.
