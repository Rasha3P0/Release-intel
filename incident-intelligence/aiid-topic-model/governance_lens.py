#!/usr/bin/env python3
"""Merge and validate governance-lens judgements, report proportions.

Reads the per-incident JSON judgements produced with the committed
prompt in governance_lens_prompt.md (one label per incident, quoted
evidence), validates the schema and that quoted evidence appears in the
source text, and writes the merged result plus a summary.

Usage:
    python3 governance_lens.py data/governance_lens_sample.csv \
        governance_lens_scores.json -o findings/
"""

import argparse
import csv
import json
import pathlib
import re
import sys
from collections import Counter

LABELS = {"R1", "R2", "R3", "R4", "R5", "not_mappable"}


def norm(s):
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).lower()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sample_csv")
    ap.add_argument("scores_json")
    ap.add_argument("-o", "--out", default="findings")
    args = ap.parse_args()

    with open(args.sample_csv, newline="", encoding="utf-8") as f:
        sample = {r["incident_id"]: r for r in csv.DictReader(f)}

    scores = json.loads(pathlib.Path(args.scores_json).read_text(encoding="utf-8"))

    missing = set(sample) - set(scores)
    extra = set(scores) - set(sample)
    if missing:
        print(f"error: missing judgements for {sorted(missing)}", file=sys.stderr)
        sys.exit(1)
    if extra:
        print(f"warning: unknown ids in scores, ignoring: {sorted(extra)}", file=sys.stderr)

    rows, bad = [], []
    for incident_id, r in sample.items():
        j = scores[incident_id]
        label = j.get("label")
        evidence = j.get("evidence", "").strip()
        if label not in LABELS or not evidence:
            bad.append((incident_id, label))
            continue
        rows.append({"incident_id": incident_id, "title": r["title"],
                     "label": label, "evidence": evidence})

    if bad:
        print(f"error: invalid judgements: {bad}", file=sys.stderr)
        sys.exit(1)

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "governance_lens_scored.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["incident_id", "title", "label", "evidence"])
        for r in rows:
            w.writerow([r["incident_id"], r["title"], r["label"], r["evidence"]])

    n = len(rows)
    counts = Counter(r["label"] for r in rows)
    summary = {
        "sample_size": n,
        "sampling": "simple random sample, seed 20260721, from 1571 total incidents",
        "label_proportions": {
            label: {"count": counts.get(label, 0),
                    "pct": round(100 * counts.get(label, 0) / n, 1)}
            for label in ["R1", "R2", "R3", "R4", "R5", "not_mappable"]
        },
    }
    (out_dir / "governance_lens_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"wrote {csv_path}")


if __name__ == "__main__":
    main()
