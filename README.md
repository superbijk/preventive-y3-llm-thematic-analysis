# Preventive Y3 LLM Thematic Analysis

Code and analysis pipeline for **Evaluating CLI-Based Agentic LLM Coding Tools for Non-English Thematic Analysis: A 3×3×3 Factorial Study of Models, Prompts, and Stochastic Variability**. The repository implements a fully crossed factorial experiment comparing three frontier large language models — Claude Opus 4.6, GPT-5.3 Codex, and Gemini 3 Pro Preview — across three prompt tiers with three repetitions per cell (27 runs total). Each run processes 89 anonymized Thai-language student evaluations from a Year 3 preventive dentistry course; outputs are then audited by Claude Opus 4.6 against a 52-item rubric covering statistical computation, thematic analysis, and visualization.

Submitted to the *International Journal of Learning, Teaching and Educational Research* (IJLTER).

## Repository layout

```
stage_01_experiment/
├── run_analysis.sh                 # orchestrates the 27 model × prompt × rep runs
├── environment.yml                 # conda env for the experiment stage (dental-eval)
└── prompts/
    ├── prompt_1.md                 # detailed procedural (372 lines)
    ├── prompt_2.md                 # structured-concise (101 lines)
    └── prompt_3.md                 # exploratory (23 lines)
stage_02_evaluation/
├── run_evaluate.sh                 # rubric audit dispatch
├── investigation_prompt.md         # 52-item evaluation rubric template
├── aggregate_r_items.py            # per-item pass-rate aggregation
├── extract_runtimes.py             # parses run.log to derive runtime CSV
├── generate_r2_5_coding_form.py    # blinded dual-coding form for R2.5
├── compute_r2_5_kappa.py           # Cohen's kappa on the filled R2.5 form
└── visualization_scripts/
    ├── heatmap_common.py           # shared heatmap utilities
    ├── shared_labels.py            # single source for R-item display labels
    ├── generate_task_heatmaps.py   # task-completion heatmaps (Figure 2)
    ├── generate_feedback_heatmap.py# feedback-category heatmap (Figure 4)
    ├── generate_visualization_grid.py  # 3×3 visualization grid (Figure 3)
    └── generate_theme_mapping_csv.py   # canonical theme mapping export
instance/                           # Runtime bundle (unzipped from instance.zip)
├── data/
│   ├── survey/satisfaction_anonymous.xlsx   # 89 students × 3 academic years
│   └── mappings/                            # runs_metadata, theme mappings, runtimes
├── experiment_runs/prompt_{1,2,3}/…         # 27 raw run directories
├── evaluation_runs/prompt-N_model_run-M/    # 27 rubric audit folders
└── outputs/heatmaps/                        # rendered PNGs and aggregate CSVs
```

## Data and runtime bundle

The full dataset and all 27 experiment runs ship in a separate archive — they are not redistributed inside this repository.

**`instance.zip` download:** [Google Drive folder](https://drive.google.com/drive/folders/1mnPNtNS6OAic_YABL-mIJxMeYHImXiT3?usp=sharing). The archive contains the anonymized Thai-language student evaluation data, the 27 experiment-run output directories, the 27 evaluation-run audit folders (each with `findings.csv`, `feedbacks.csv`, `report.md`), theme mapping CSVs, and runtime logs. Download it and unzip at the repository root so its contents live at `<repo>/instance/`.

## Quick start

1. **Clone this repository.**
2. **Download and unpack `instance.zip`** from the Google Drive folder above; unzip at the repository root.
3. **Create the conda environment and activate it:**

```bash
conda env create -f stage_01_experiment/environment.yml
conda activate dental-eval
pip install seaborn python-docx Pillow   # additional deps for the visualization + manuscript build
```

CLI tools used for the experiment stage are vendor-supplied and must be installed separately:

| Model alias | Executed model ID        | CLI tool  | CLI version |
|-------------|--------------------------|-----------|-------------|
| `opus`      | `claude-opus-4-6`        | `claude`  | 2.1.34      |
| `gpt`       | `gpt-5.3-codex`          | `codex`   | 0.98.0      |
| `gemini`    | `gemini-3-pro-preview`   | `gemini`  | 0.27.3      |

All 27 experiment runs were executed on **2026-02-07**.

## Usage

### Stage 1 — run the experiment

```bash
cd stage_01_experiment
./run_analysis.sh --model opus --prompt 1 --runs 3
./run_analysis.sh --model gpt --prompt 2 --runs 3
./run_analysis.sh --model gemini --prompt 3 --runs 3
```

Arguments: `--model` is `opus|gpt|gemini`, `--prompt` is `1|2|3`, `--runs` is the repetition count. Each command writes a session to `instance/experiment_runs/prompt_<N>/<timestamp>__<model>/`.

### Stage 2 — audit each run against the rubric

```bash
cd stage_02_evaluation
./run_evaluate.sh --all --skip-existing             # batch mode
./run_evaluate.sh --model opus --prompt 1 --run 1   # single run
```

Outputs land in `instance/evaluation_runs/prompt-<N>_<model>_run-<M>/`: `findings.csv` (52 rubric items, `FOUND`/`NOT_FOUND`/`YES`/`NO` with evidence), `feedbacks.csv` (extracted theme counts), and `report.md` (qualitative assessment).

### Stage 3 — aggregate and visualize

```bash
cd stage_02_evaluation
python aggregate_r_items.py            # per-R-item pass rates
python extract_runtimes.py             # runtime CSV from run.log files

cd visualization_scripts
python generate_task_heatmaps.py       # Figure 2 family (required + curated + full)
python generate_feedback_heatmap.py    # Figure 4 — feedback category frequencies
python generate_visualization_grid.py  # Figure 3 — 3×3 chart grid
python generate_theme_mapping_csv.py   # canonical theme mapping export
```

## Reproducibility

- `instance/data/mappings/runs_metadata.csv` is the master index of all 27 runs. Re-runs should add rows, not overwrite.
- Theme aggregation uses **MAX** (not SUM) when multiple raw theme labels map to the same canonical category, to avoid inflation.
- Model identifiers in manuscript prose match the executed IDs verbatim: `claude-opus-4-6`, `gpt-5.3-codex`, `gemini-3-pro-preview`. The execution date is recorded in the Methods section (2026-02-07).

## Citation

The manuscript is under review at IJLTER. A citation block will be added here on acceptance.
