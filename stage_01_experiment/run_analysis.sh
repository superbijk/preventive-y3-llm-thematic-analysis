#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Ensure npm-global bin (codex, gemini) is on PATH
export PATH="$HOME/.npm-global/bin:$PATH"

# ── Usage ───────────────────────────────────────────────────────────────────
usage() {
  cat <<'EOF'
Usage: ./run_analysis.sh --model MODEL --prompt N [--runs N]

Run LLM-based analysis of dental course evaluation data.

Required:
  --model MODEL   Model shorthand: opus | gpt | gemini
  --prompt N      Prompt variant: 1 (detailed) | 2 (structured-concise) | 3 (exploratory-minimal)

Optional:
  --runs N        Number of analysis runs (default: 1)
  --help          Show this help message

Model mapping:
  opus    → claude-opus-4-6       (via claude CLI)
  gpt     → gpt-5.3-codex        (via codex CLI)
  gemini  → gemini-3-pro-preview   (via gemini CLI)

Examples:
  ./run_analysis.sh --model opus --prompt 1 --runs 3
  ./run_analysis.sh --model gpt --prompt 2
  ./run_analysis.sh --model gemini --prompt 3 --runs 2
EOF
  exit 0
}

# ── Parse arguments ─────────────────────────────────────────────────────────
MODEL=""
PROMPT_NUM=""
RUNS=1

[[ $# -eq 0 ]] && usage

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)  MODEL="$2";      shift 2 ;;
    --prompt) PROMPT_NUM="$2"; shift 2 ;;
    --runs)   RUNS="$2";       shift 2 ;;
    --help)   usage ;;
    *)        echo "Error: unknown argument '$1'"; usage ;;
  esac
done

# ── Validate ────────────────────────────────────────────────────────────────
if [[ -z "$MODEL" ]]; then
  echo "Error: --model is required"
  usage
fi

if [[ -z "$PROMPT_NUM" ]]; then
  echo "Error: --prompt is required"
  usage
fi

# Model mapping
case "$MODEL" in
  opus)
    MODEL_ID="claude-opus-4-6"
    MODEL_LABEL="opus4-6"
    ;;
  gpt)
    MODEL_ID="gpt-5.3-codex"
    MODEL_LABEL="gpt5-3"
    ;;
  gemini)
    MODEL_ID="gemini-3-pro-preview"
    MODEL_LABEL="gemini-pro"
    ;;
  *)
    echo "Error: invalid model '$MODEL'. Must be one of: opus, gpt, gemini"
    exit 1
    ;;
esac

# Prompt validation
case "$PROMPT_NUM" in
  1|2|3) ;;
  *)
    echo "Error: invalid prompt '$PROMPT_NUM'. Must be one of: 1, 2, 3"
    exit 1
    ;;
esac

PROMPT_FILE="prompts/prompt_${PROMPT_NUM}.md"
if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "Error: prompt file not found: $PROMPT_FILE"
  exit 1
fi

PROMPT_DIR="../instance/experiment_runs/prompt_${PROMPT_NUM}"
DATA_FILE="../instance/data/survey/satisfaction_anonymous.xlsx"

if [[ ! -f "$DATA_FILE" ]]; then
  echo "Error: data file not found: $DATA_FILE"
  exit 1
fi

# ── Run loop ────────────────────────────────────────────────────────────────
echo "=== Analysis Configuration ==="
echo "  Model:   $MODEL → $MODEL_ID ($MODEL_LABEL)"
echo "  Prompt:  $PROMPT_NUM ($PROMPT_FILE)"
echo "  Runs:    $RUNS"
echo ""

mkdir -p "$PROMPT_DIR"

for ((i = 1; i <= RUNS; i++)); do
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  RUN_DIR="${PROMPT_DIR}/${TIMESTAMP}__${MODEL_LABEL}"

  mkdir -p "${RUN_DIR}/figures"

  # Substitute placeholders in prompt
  PROMPT=$(sed \
    -e "s|{{RUN_DIR}}|${RUN_DIR}|g" \
    -e "s|{{MODEL_NAME}}|${MODEL_ID}|g" \
    -e "s|{{DATA_FILE}}|${DATA_FILE}|g" \
    "$PROMPT_FILE")

  LOG_FILE="${RUN_DIR}/run.log"
  START_TS=$(date +%s)
  START_HUMAN=$(date '+%Y-%m-%d %H:%M:%S')

  echo "[$START_HUMAN] Run $i/$RUNS started (model=$MODEL_ID, run_dir=$RUN_DIR)" | tee "$LOG_FILE"

  set +e
  case "$MODEL" in
    opus)
      claude -p \
        --model "$MODEL_ID" \
        --verbose \
        --allowedTools "Bash,Read,Write,Edit" \
        --dangerously-skip-permissions \
        "$PROMPT" \
        2>&1 | tee -a "$LOG_FILE"
      ;;
    gpt)
      codex exec \
        --model "$MODEL_ID" \
        --dangerously-bypass-approvals-and-sandbox \
        "$PROMPT" \
        2>&1 | tee -a "$LOG_FILE"
      ;;
    gemini)
      gemini \
        --yolo \
        -m "$MODEL_ID" \
        -p "$PROMPT" \
        2>&1 | tee -a "$LOG_FILE"
      ;;
  esac
  CMD_STATUS=${PIPESTATUS[0]}
  set -e

  END_TS=$(date +%s)
  END_HUMAN=$(date '+%Y-%m-%d %H:%M:%S')
  ELAPSED_SECONDS=$((END_TS - START_TS))

  echo "[$END_HUMAN] Run $i/$RUNS finished (status=$CMD_STATUS, elapsed=${ELAPSED_SECONDS}s)" | tee -a "$LOG_FILE"
  echo ""
  ls -lR "$RUN_DIR"
  echo ""

  if [[ $CMD_STATUS -ne 0 ]]; then
    echo "Warning: run $i exited with status $CMD_STATUS"
  fi
done

echo "=== All $RUNS run(s) complete ==="
