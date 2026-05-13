"""Aggregate R-item pass/fail results across all 27 evaluation runs.

Reads findings.csv from each run directory and produces:
  instance/outputs/mappings/r_item_summary.csv — pass rates by R item, model, prompt
"""

import csv
import re
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent
EVAL_DIR = BASE / "instance" / "evaluation_runs"
OUT_DIR = BASE / "instance" / "outputs" / "mappings"

R_ITEMS = [
    "R1.1", "R1.2", "R1.3",
    "R2.1", "R2.2", "R2.3", "R2.4", "R2.5",
    "R3.1", "R3.2",
]

RUN_PATTERN = re.compile(r"prompt-(\d+)_(\w+)_run-(\d+)")


def parse_runs():
    """Yield (prompt, model, run, {item_id: passed}) for each run."""
    for run_dir in sorted(EVAL_DIR.iterdir()):
        m = RUN_PATTERN.match(run_dir.name)
        if not m:
            continue
        prompt, model, run = int(m.group(1)), m.group(2), int(m.group(3))
        findings_path = run_dir / "findings.csv"
        if not findings_path.exists():
            print(f"WARNING: missing {findings_path}")
            continue

        verdicts = {}
        with open(findings_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                item = row["item_id"]
                if item in R_ITEMS:
                    verdicts[item] = row["status"] == "FOUND"
        yield prompt, model, run, verdicts


def main():
    # Collect all results
    rows = list(parse_runs())
    print(f"Parsed {len(rows)} runs\n")

    # --- Per-run detail ---
    print("=" * 80)
    print("PER-RUN RESULTS")
    print("=" * 80)
    header = f"{'Run':<28}" + "".join(f"{r:<7}" for r in R_ITEMS)
    print(header)
    print("-" * len(header))
    for prompt, model, run, verdicts in rows:
        label = f"P{prompt}_{model}_R{run}"
        cells = "".join(
            f"{'PASS':<7}" if verdicts.get(item, False) else f"{'FAIL':<7}"
            for item in R_ITEMS
        )
        print(f"{label:<28}{cells}")

    # --- Overall pass rates ---
    print(f"\n{'=' * 80}")
    print("OVERALL PASS RATES")
    print("=" * 80)
    for item in R_ITEMS:
        passed = sum(1 for _, _, _, v in rows if v.get(item, False))
        print(f"  {item}: {passed}/27 ({100*passed/27:.0f}%)")

    # --- By model ---
    print(f"\n{'=' * 80}")
    print("PASS RATES BY MODEL")
    print("=" * 80)
    for model_name in ["opus", "gemini", "gpt"]:
        model_rows = [r for r in rows if r[1] == model_name]
        print(f"\n  {model_name.upper()} ({len(model_rows)} runs):")
        for item in R_ITEMS:
            passed = sum(1 for _, _, _, v in model_rows if v.get(item, False))
            total = len(model_rows)
            print(f"    {item}: {passed}/{total} ({100*passed/total:.0f}%)")

    # --- By prompt ---
    print(f"\n{'=' * 80}")
    print("PASS RATES BY PROMPT")
    print("=" * 80)
    for p in [1, 2, 3]:
        prompt_rows = [r for r in rows if r[0] == p]
        print(f"\n  PROMPT {p} ({len(prompt_rows)} runs):")
        for item in R_ITEMS:
            passed = sum(1 for _, _, _, v in prompt_rows if v.get(item, False))
            total = len(prompt_rows)
            print(f"    {item}: {passed}/{total} ({100*passed/total:.0f}%)")

    # --- Model x Prompt for key items ---
    print(f"\n{'=' * 80}")
    print("MODEL x PROMPT BREAKDOWN")
    print("=" * 80)
    for item in R_ITEMS:
        print(f"\n  {item}:")
        print(f"    {'':>8}  P1    P2    P3    Total")
        for model_name in ["opus", "gemini", "gpt"]:
            cells = []
            total_pass = 0
            for p in [1, 2, 3]:
                cell_rows = [r for r in rows if r[0] == p and r[1] == model_name]
                passed = sum(1 for _, _, _, v in cell_rows if v.get(item, False))
                total_pass += passed
                cells.append(f"{passed}/3")
            print(f"    {model_name:>8}  {'   '.join(cells)}   {total_pass}/9")

    # --- Failures detail ---
    print(f"\n{'=' * 80}")
    print("FAILURE DETAILS (which runs failed each R item)")
    print("=" * 80)
    for item in R_ITEMS:
        failures = [
            f"P{p}_{m}_R{r}"
            for p, m, r, v in rows
            if not v.get(item, False)
        ]
        if failures:
            print(f"  {item} failures ({len(failures)}): {', '.join(failures)}")
        else:
            print(f"  {item}: ALL PASSED")

    # --- Write summary CSV ---
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "r_item_summary.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item", "model", "prompt", "passed", "total", "rate"])
        for item in R_ITEMS:
            for model_name in ["opus", "gemini", "gpt"]:
                for p in [1, 2, 3]:
                    cell_rows = [r for r in rows if r[0] == p and r[1] == model_name]
                    passed = sum(1 for _, _, _, v in cell_rows if v.get(item, False))
                    total = len(cell_rows)
                    writer.writerow([item, model_name, p, passed, total, f"{passed/total:.2f}"])
            # Overall row
            passed = sum(1 for _, _, _, v in rows if v.get(item, False))
            writer.writerow([item, "ALL", "ALL", passed, 27, f"{passed/27:.2f}"])

    print(f"\nSummary CSV written to: {out_path}")


if __name__ == "__main__":
    main()
