#!/usr/bin/env bash
set -euo pipefail

# Resolve project root (one level up from stage_02_evaluation/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Ensure npm-global bin (claude) is on PATH
export PATH="$HOME/.npm-global/bin:$PATH"

METADATA_CSV="instance/data/mappings/runs_metadata.csv"
PROMPT_TEMPLATE="stage_02_evaluation/investigation_prompt.md"
PER_RUN_DIR="instance/evaluation_runs"

# ── Usage ───────────────────────────────────────────────────────────────────
usage() {
  cat <<'EOF'
Usage: ./run_evaluate.sh --model MODEL --prompt N --run M
       ./run_evaluate.sh --all [--skip-existing]

Evaluate LLM analysis runs by auditing their outputs with Claude Opus.

Single-run mode:
  --model MODEL   Model shorthand: opus | gpt | gemini
  --prompt N      Prompt variant: 1 | 2 | 3
  --run M         Run number: 1 | 2 | 3

Batch mode:
  --all           Run all 27 evaluations sequentially
  --skip-existing Skip runs that already have findings.csv, feedbacks.csv, and report.md

Other:
  --help          Show this help message

Examples:
  ./run_evaluate.sh --model opus --prompt 1 --run 1
  ./run_evaluate.sh --all --skip-existing
EOF
  exit 0
}

# ── Parse arguments ─────────────────────────────────────────────────────────
MODEL=""
PROMPT_NUM=""
RUN_NUM=""
ALL=false
SKIP_EXISTING=false

[[ $# -eq 0 ]] && usage

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)         MODEL="$2";      shift 2 ;;
    --prompt)        PROMPT_NUM="$2"; shift 2 ;;
    --run)           RUN_NUM="$2";    shift 2 ;;
    --all)           ALL=true;        shift ;;
    --skip-existing) SKIP_EXISTING=true; shift ;;
    --help)          usage ;;
    *)               echo "Error: unknown argument '$1'"; usage ;;
  esac
done

# ── Validate ────────────────────────────────────────────────────────────────
if [[ "$ALL" == false ]]; then
  if [[ -z "$MODEL" || -z "$PROMPT_NUM" || -z "$RUN_NUM" ]]; then
    echo "Error: --model, --prompt, and --run are all required in single-run mode"
    usage
  fi

  case "$MODEL" in
    opus|gpt|gemini) ;;
    *) echo "Error: invalid model '$MODEL'. Must be one of: opus, gpt, gemini"; exit 1 ;;
  esac

  case "$PROMPT_NUM" in
    1|2|3) ;;
    *) echo "Error: invalid prompt '$PROMPT_NUM'. Must be one of: 1, 2, 3"; exit 1 ;;
  esac

  case "$RUN_NUM" in
    1|2|3) ;;
    *) echo "Error: invalid run '$RUN_NUM'. Must be one of: 1, 2, 3"; exit 1 ;;
  esac
fi

if [[ ! -f "$METADATA_CSV" ]]; then
  echo "Error: metadata file not found: $METADATA_CSV"
  exit 1
fi

if [[ ! -f "$PROMPT_TEMPLATE" ]]; then
  echo "Error: investigation prompt not found: $PROMPT_TEMPLATE"
  exit 1
fi

# ── Lookup function: find experiment run directory from metadata CSV ─────────
lookup_run_dir() {
  local prompt="$1" model="$2" run="$3"
  local canonical_id="p${prompt}_${model}_r${run}"

  # Search CSV for matching canonical_id and extract directory column
  local dir
  dir=$(awk -F',' -v id="$canonical_id" '$1 == id { print $7 }' "$METADATA_CSV" | tr -d '\r')

  if [[ -z "$dir" ]]; then
    echo "Error: no entry found for $canonical_id in $METADATA_CSV" >&2
    return 1
  fi

  echo "$dir"
}

# ── Run a single evaluation ─────────────────────────────────────────────────
run_single_evaluation() {
  local prompt="$1" model="$2" run="$3"
  local canonical_id="p${prompt}_${model}_r${run}"
  local folder_name="prompt-${prompt}_${model}_run-${run}"
  local output_dir="${PER_RUN_DIR}/${folder_name}"

  # Skip if already done (all 3 files must exist)
  if [[ "$SKIP_EXISTING" == true && -f "${output_dir}/findings.csv" && -f "${output_dir}/feedbacks.csv" && -f "${output_dir}/report.md" ]]; then
    echo "  [SKIP] ${canonical_id} — findings.csv + feedbacks.csv + report.md already exist"
    return 0
  fi

  # Lookup experiment run directory
  local run_dir
  run_dir=$(lookup_run_dir "$prompt" "$model" "$run") || return 1

  # Verify experiment run directory exists
  if [[ ! -d "$run_dir" ]]; then
    echo "  [ERROR] ${canonical_id} — run directory not found: $run_dir"
    return 1
  fi

  # Create output directory
  mkdir -p "$output_dir"

  # Fill template placeholders
  local filled_prompt
  filled_prompt=$(sed \
    -e "s|{{RUN_ID}}|${canonical_id}|g" \
    -e "s|{{RUN_DIR}}|${run_dir}|g" \
    -e "s|{{OUTPUT_DIR}}|${output_dir}|g" \
    "$PROMPT_TEMPLATE")

  local start_ts start_human
  start_ts=$(date +%s)
  start_human=$(date '+%Y-%m-%d %H:%M:%S')

  echo "  [$start_human] ${canonical_id} — starting evaluation..."
  echo "    Run dir:    $run_dir"
  echo "    Output dir: $output_dir"

  set +e
  claude -p \
    --model claude-opus-4-6 \
    --allowedTools "Bash,Read,Write,Edit" \
    --dangerously-skip-permissions \
    "$filled_prompt" \
    > /dev/null 2>&1
  local cmd_status=$?
  set -e

  local end_ts end_human elapsed
  end_ts=$(date +%s)
  end_human=$(date '+%Y-%m-%d %H:%M:%S')
  elapsed=$((end_ts - start_ts))

  # Validate outputs
  local findings_ok="NO" feedbacks_ok="NO" report_ok="NO"
  [[ -f "${output_dir}/findings.csv" ]] && findings_ok="YES"
  [[ -f "${output_dir}/feedbacks.csv" ]] && feedbacks_ok="YES"
  [[ -f "${output_dir}/report.md" ]] && report_ok="YES"

  if [[ "$cmd_status" -ne 0 ]]; then
    echo "  [$end_human] ${canonical_id} — FAILED (status=$cmd_status, ${elapsed}s)"
  elif [[ "$findings_ok" == "NO" || "$feedbacks_ok" == "NO" || "$report_ok" == "NO" ]]; then
    echo "  [$end_human] ${canonical_id} — INCOMPLETE (findings=$findings_ok, feedbacks=$feedbacks_ok, report=$report_ok, ${elapsed}s)"
  else
    echo "  [$end_human] ${canonical_id} — OK (${elapsed}s)"
  fi

  return $cmd_status
}

# ── Main ────────────────────────────────────────────────────────────────────
if [[ "$ALL" == true ]]; then
  echo "=== Batch Evaluation: All 27 Runs ==="
  echo "  Skip existing: $SKIP_EXISTING"
  echo ""

  total=0
  ok=0
  skipped=0
  failed=0

  for prompt in 1 2 3; do
    for model in opus gpt gemini; do
      for run in 1 2 3; do
        total=$((total + 1))

        # Check skip before running
        local_folder="prompt-${prompt}_${model}_run-${run}"
        if [[ "$SKIP_EXISTING" == true && -f "${PER_RUN_DIR}/${local_folder}/findings.csv" && -f "${PER_RUN_DIR}/${local_folder}/feedbacks.csv" && -f "${PER_RUN_DIR}/${local_folder}/report.md" ]]; then
          skipped=$((skipped + 1))
          echo "  [SKIP] p${prompt}_${model}_r${run}"
          continue
        fi

        if run_single_evaluation "$prompt" "$model" "$run"; then
          ok=$((ok + 1))
        else
          failed=$((failed + 1))
        fi
      done
    done
  done

  echo ""
  echo "=== Batch Complete: $ok ok, $skipped skipped, $failed failed (of $total total) ==="
else
  echo "=== Single Evaluation ==="
  run_single_evaluation "$PROMPT_NUM" "$MODEL" "$RUN_NUM"
fi
