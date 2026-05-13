# Investigation Prompt: Evaluate an LLM Analysis Run

You are auditing a single LLM analysis run for a dental course evaluation study. The LLM was given student survey data and asked to produce statistical summaries, thematic feedback analysis, and visualizations.

Your job: check which required tasks (R items) and bonus analyses (M items) the LLM actually completed, and output structured CSV files plus a qualitative report.

---

## Run Information

- **Run ID:** `{{RUN_ID}}` (e.g., `p1_opus_r1`)
- **Run directory:** `{{RUN_DIR}}` (e.g., `experiment/runs/prompt_1/20260207_010100__opus4-6/`)
- **Output directory:** `{{OUTPUT_DIR}}` (e.g., `evaluation/tasks_achieved/runs/prompt-1_opus_run-1/`)

---

## Step 1: Read All Files in the Run Directory

Read every file in `{{RUN_DIR}}/` (markdown, python, log files) and list the figures in `{{RUN_DIR}}/figures/`. Understand what the LLM produced before evaluating.

---

## Step 2: Evaluate Required Tasks (R Items)

Check whether the LLM completed each of these 10 required tasks. Each maps to a section of the original analysis prompt.

### Statistics Tasks (Section B — statistics_summary.md)

| ID | Task | How to verify |
|---|---|---|
| R1.1 | Report overall teaching effectiveness mean | Look for the "รวมทุกปี" (all-years combined) row in the teaching satisfaction table. The correct value is **4.39**. Status: FOUND if value = 4.39, INCORRECT if different value reported, NOT_FOUND if no combined mean exists. |
| R1.2 | Report overall learning outcome mean | Same "รวมทุกปี" row in learning satisfaction table. Correct value: **4.51**. |
| R1.3 | Report overall dissatisfaction mean | Same "รวมทุกปี" row in dissatisfaction table. Correct value: **1.84**. |

### Feedback Analysis Tasks (Sections C+D — feedback files)

| ID | Task | How to verify |
|---|---|---|
| R2.1 | Categorize/group feedback into themes | Feedback is organized into named categories/themes (not just raw text or individual quotes). Look for theme headings, category labels, or grouped analysis. |
| R2.2 | Separate sentiment into likes vs dislikes | Themes are split into positive (สิ่งที่ชอบ / likes) and negative (สิ่งที่ไม่ชอบ / dislikes or suggestions) groups. Two separate sections or tables. |
| R2.3 | Present themes as cross-tabulation tables by academic year | Summary tables exist showing theme × year counts (how many students mentioned each theme per academic year 2566, 2567, 2568). |
| R2.4 | Year trend analysis | Explicit discussion of trends across academic years 2566→2567→2568 (rising, falling, peak year). Look for an observations section (แนวโน้มและข้อสังเกต) or similar that discusses year-over-year patterns. FOUND if explicit trend discussion exists. NOT_FOUND if no trend analysis. |
| R2.5 | Use LLM-based thematic analysis | Themes were discovered by the LLM reading Thai text and identifying patterns — NOT by hardcoded keyword matching or regex. Check Python scripts: if themes come from `if "keyword" in text` patterns, this is NOT_FOUND. If themes come from the LLM's own categorization in markdown, this is FOUND. |

### Visualization Tasks (Section E — figures/)

| ID | Task | How to verify |
|---|---|---|
| R3.1 | Generate satisfaction bar charts | `figures/` directory contains PNG(s) showing satisfaction scores (bar charts, grouped by year or metric). |
| R3.2 | Generate per-metric detail charts | `figures/` contains separate charts for individual metrics (teaching, learning, dissatisfaction) — not just one combined chart. At least 2 separate metric charts required. |

---

## Step 3: Catalog Additional Analyses (M Items)

Check for each bonus analysis below. These go beyond the explicitly required tasks.

| ID | Category | What to look for |
|---|---|---|
| M2 | Correlation analysis | Correlation coefficients between metrics, or correlation matrix |
| M3 | Box plot visualization | Box-and-whisker plots in figures/ |
| M4 | Heatmap visualization | Heatmap figures in figures/ |
| M5 | Theme frequency by year | Table or chart showing how often each theme appeared per year |
| M6 | Sentiment analysis | Explicit sentiment scoring or polarity assignment to feedback |
| M7 | 2567 peak analysis | Specific discussion of 2567 as the highest-satisfaction year |
| M8 | 2568 decline analysis | Specific discussion of 2568 decline in satisfaction scores |
| M9 | Score-of-1 in 2568 analysis | Analysis of extreme low scores (rating=1) specifically in 2568 |
| M10 | Satisfaction distribution | Frequency distributions or histograms of satisfaction scores |
| M11 | Theme co-occurrence | Analysis of which themes appear together in same student responses |
| M12 | Response rate analysis | Discussion of how many students left text comments vs total |
| M13 | Sentiment classification | Classifying individual responses as positive/negative/neutral |
| M14 | Statistical testing | Significance tests (t-test, ANOVA, chi-square, etc.) |
| M15 | Median / mode reporting | Reporting median or mode alongside mean |
| M16 | Polarization / bimodal analysis | Discussion of bimodal distributions or opinion polarization |
| M17 | Professional identity themes | Theme about feeling like a dentist / professional identity |
| M18 | Cross-course integration | Theme about connections to other courses (cariology, perio, etc.) |
| M19 | Actionable recommendations | Specific improvement suggestions for the course |
| M20 | Assessment methodology critique | Discussion of survey methodology limitations |
| M21 | Clinical skills breakdown | Detailed listing of specific clinical skills practiced |
| M22 | Over-granular splitting | Splitting feedback into too many tiny categories (>15 themes) |
| M23 | Data inspection script | Separate Python script for data validation/inspection |
| M24 | IQR / quartile reporting | Interquartile range or quartile values reported |
| M25 | Trend line visualization | Line charts showing trends across years |
| M26 | Theme data as JSON | Structured JSON output for theme data |
| M27 | Stacked distribution viz | Stacked bar charts for score distributions |
| M28 | Satisfaction by year | Year-wise satisfaction comparison charts |
| M29 | Pairwise post-hoc tests | Post-hoc pairwise comparisons after ANOVA |
| M30 | Effect size reporting | Cohen's d, rank-biserial, or other effect sizes |
| M31 | Skewness / kurtosis | Reporting distribution shape statistics |
| M32 | Unmatched response tracking | Tracking which student comments couldn't be categorized |
| M33 | Dissatisfaction detail viz | Separate visualization focused on dissatisfaction patterns |
| M34 | Evaluation method recommendations | Suggestions for improving the evaluation instrument |
| M35 | CSV structured output | Analysis results exported as CSV files |
| M36 | Output manifest | Index or README listing all output files |
| M37 | Student-level coding | Individual student responses mapped to theme codes |
| M38 | Theme keyword tokens | Explicit keyword lists for each theme |
| M39 | Slope calculation | Numeric slope/rate of change across years |
| M40 | Excel workbook output | Results exported as .xlsx |
| M41 | Percent change calculation | Year-to-year percentage changes computed |
| M42 | Comments compilation | All student comments compiled in one document |
| M43 | Facilities & Equipment | Theme about facilities, equipment, or physical environment |

If you discover an analysis not in this list, add it as M44+ with a descriptive category name.

---

## Step 4: Write Output CSV Files

Create the output directory `{{OUTPUT_DIR}}/` and write exactly two CSV files:

### File 1: `{{OUTPUT_DIR}}/findings.csv`

One row per R and M item. Columns:

```
item_id,status,value,evidence_file,notes
```

- **item_id**: R1.1, R1.2, ..., R3.2, M2, M3, ..., M43
- **status**: For R items: `FOUND`, `INCORRECT`, or `NOT_FOUND`. For M items: `YES` or `NO`.
- **value**: The numeric value found (only for R1.1, R1.2, R1.3 — leave blank for all others)
- **evidence_file**: The filename within the run directory where evidence was found (e.g., `statistics_summary.md`, `figures/1_satisfaction_charts.png`). Leave blank if status is NOT_FOUND/NO.
- **notes**: Brief explanation (1 sentence). Leave blank if NO/NOT_FOUND with nothing to note.

Example rows:
```csv
item_id,status,value,evidence_file,notes
R1.1,FOUND,4.39,statistics_summary.md,"Exact match in รวมทุกปี row"
R1.2,FOUND,4.51,statistics_summary.md,"Exact match"
R1.3,INCORRECT,1.85,statistics_summary.md,"Reported 1.85 instead of 1.84"
R2.1,FOUND,,feedback_analysis_llm.md,"6 themes identified with student evidence"
R2.2,FOUND,,feedback_summary.md,"Separate likes and dislikes sections"
R2.3,FOUND,,feedback_summary.md,"Cross-tabulation table with year columns"
R2.4,FOUND,,statistics_summary.md,"Discusses 2567 peak and 2568 decline trends across years"
R2.5,FOUND,,feedback_analysis_llm.md,"Themes from LLM reading; no keyword scripts"
R3.1,FOUND,,figures/1_satisfaction_charts.png,"Bar chart with 3 metrics by year"
R3.2,FOUND,,figures/2_satisfaction_teaching_process.png,"4 separate metric charts"
M2,NO,,,
M3,NO,,,
```

### File 2: `{{OUTPUT_DIR}}/feedbacks.csv`

One row per feedback theme found in the run's output. Extract themes **exactly as the LLM named them** — do not rename or map to canonical categories.

Columns:

```
theme_name,polarity,count
```

- **theme_name**: The theme name as used by the LLM in this run (Thai or English — use exactly what the LLM wrote)
- **polarity**: `positive`, `negative`, or `neutral`
- **count**: Total number of student mentions across all years (integer). If the LLM provides per-year counts, sum them. If no count is available, estimate from the number of students listed.

Example:
```csv
theme_name,polarity,count
การฝึกปฏิบัติจริง / Hands-on Practice,positive,61
อาจารย์ดี / Teaching Staff Quality,positive,12
เชื่อมโยงวิชา / Cross-course Integration,positive,11
สนุกและประทับใจ / Enjoyment,positive,9
ได้เรียนรู้สิ่งใหม่ / Learning,positive,6
เวลาไม่เพียงพอ / Time Issues,negative,5
อาจารย์ไม่เพียงพอ / Insufficient Supervision,negative,4
เอกสารภาษาไทย / Thai Materials,negative,3
กดดันเรื่องคะแนน / Grading Pressure,negative,2
```

Only include themes that are actually present in the run's output. If the run has 0 themes (e.g., it failed to analyze feedback), write just the header row.

---

## Step 5: Write Qualitative Report

Write a qualitative assessment to `{{OUTPUT_DIR}}/report.md` that captures observations **not** covered by findings.csv or feedbacks.csv — things like output organization, format compliance, and overall quality.

Use this template:

```markdown
# Evaluation Report: {{RUN_ID}}

## Output Structure
- Total files produced: N
- File types: md, py, png, csv, xlsx, etc.
- Follows expected format: YES/NO (statistics_summary.md + feedback files + figures/)
- Extra/unexpected files: [list if any]

## Output Organization
- Rating: Clean / Moderate / Messy
- Notes: [e.g., "Well-structured with clear sections" or "22 files including __pycache__, CSVs scattered"]

## Visualization Quality
- Number of figures: N
- Types: [bar charts, heatmaps, boxplots, trend lines, etc.]
- Relevant to the analysis: YES/PARTIAL/NO

## Analysis Depth
- Statistical summary: Thorough / Adequate / Minimal
- Feedback analysis: Thorough / Adequate / Minimal
- Goes beyond requirements: YES/NO — [brief description]

## Notable Observations
- [Free-form observations about this particular run's strengths or weaknesses]
```

Fill in each section based on your review of the run's files. Be specific and factual.

---

## Important Notes

- Read files carefully — do not guess or assume. Base every status on actual file contents.
- For R2.5, check Python scripts (.py files) in the run directory. If a script uses hardcoded keyword lists to classify Thai text (e.g., `if "ฝึก" in text: category = "practical"`), mark R2.5 as NOT_FOUND. If the thematic analysis comes from the LLM's own writing in .md files, mark as FOUND.
- Write the CSV files using proper quoting (quote fields that contain commas).
- Create exactly three output files: `findings.csv`, `feedbacks.csv`, and `report.md`.
