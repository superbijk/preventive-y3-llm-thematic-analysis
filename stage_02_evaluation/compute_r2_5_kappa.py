#!/usr/bin/env python3
"""Compute Cohen's kappa for the R2.5 dual-coding form.

Reads the filled-in coding form, joins with the private coding key for
re-attribution, computes Cohen's kappa over the (coder_A, coder_B) columns,
and prints both the overall κ and a breakdown by label.

Run after `generate_r2_5_coding_form.py` and after both coders have filled
in their columns. See r2_5_dual_coding_protocol.md.
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
FORM_PATH = PROJECT_ROOT / ".manuscript" / "manuscript_1_llm_thematic_analysis" / "r2_5_coding_form.csv"
KEY_PATH  = PROJECT_ROOT / "instance" / "data" / "mappings" / "r2_5_coding_key.csv"

VALID_LABELS = {"LLM", "KEYWORD", "MIXED", "UNCLEAR"}


def cohens_kappa(pairs: list[tuple[str, str]]) -> float:
    """Cohen's kappa for two raters with categorical labels.

    Implements κ = (p_o - p_e) / (1 - p_e) where p_o is observed agreement
    and p_e is the agreement expected by chance under independence.
    """
    n = len(pairs)
    if n == 0:
        return float("nan")
    labels = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    a_counts = Counter(a for a, _ in pairs)
    b_counts = Counter(b for _, b in pairs)
    p_o = sum(1 for a, b in pairs if a == b) / n
    p_e = sum((a_counts[lab] / n) * (b_counts[lab] / n) for lab in labels)
    if p_e == 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


def main():
    if not FORM_PATH.exists():
        raise SystemExit(f"Coding form not found: {FORM_PATH}\nRun generate_r2_5_coding_form.py first.")

    with open(FORM_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    pairs = []
    invalid = []
    blank = []
    for r in rows:
        a, b = r["coder_A"].strip().upper(), r["coder_B"].strip().upper()
        if not a or not b:
            blank.append(r["coding_id"])
            continue
        if a not in VALID_LABELS or b not in VALID_LABELS:
            invalid.append((r["coding_id"], a, b))
            continue
        pairs.append((a, b))

    if not pairs:
        raise SystemExit("No fully coded rows yet — fill in coder_A and coder_B first.")

    kappa = cohens_kappa(pairs)
    agreements = sum(1 for a, b in pairs if a == b)
    print(f"Cohen's kappa: {kappa:.3f}  (n={len(pairs)} of {len(rows)} rows, "
          f"{agreements} agreements, {len(pairs) - agreements} disagreements)")
    print()

    if blank:
        print(f"Not yet coded ({len(blank)}): {blank}")
    if invalid:
        print(f"Invalid labels in {len(invalid)} rows: {invalid}")
        print(f"Allowed: {sorted(VALID_LABELS)}")

    # Marginal distributions
    a_counts = Counter(a for a, _ in pairs)
    b_counts = Counter(b for _, b in pairs)
    print("\nCoder A label distribution:", dict(a_counts))
    print("Coder B label distribution:", dict(b_counts))

    # Disagreement detail
    disag = defaultdict(int)
    for a, b in pairs:
        if a != b:
            disag[(a, b)] += 1
    if disag:
        print("\nDisagreement matrix (coder_A → coder_B):")
        for (a, b), ct in sorted(disag.items(), key=lambda kv: -kv[1]):
            print(f"  {a} vs {b}: {ct}")

    # Optional: re-attribute disagreements to canonical run IDs for adjudication discussion
    if KEY_PATH.exists():
        with open(KEY_PATH, encoding="utf-8") as f:
            key_map = {r["coding_id"]: r for r in csv.DictReader(f)}
        print("\nRows requiring adjudication (with run attribution):")
        for r in rows:
            a, b = r["coder_A"].strip().upper(), r["coder_B"].strip().upper()
            if a and b and a != b:
                key = key_map.get(r["coding_id"], {})
                print(f"  {r['coding_id']}  {key.get('canonical_id', '?')}: A={a} B={b}  notes={r['notes'][:60]!r}")


if __name__ == "__main__":
    main()
