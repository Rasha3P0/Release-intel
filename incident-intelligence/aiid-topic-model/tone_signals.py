#!/usr/bin/env python3
"""Tone, urgency and description-richness signals across AIID incidents.

Rule-based and fully reproducible, in the same spirit as score_notes.py
in ../../5r-release-scoring: fixed lexicons, quoted matches, no model
calls. Reports the proportion of incidents whose AIID-authored
description carries each signal, plus a description-length distribution
that echoes the R4 brevity trigger from the 5R framework (see
../../5r-release-scoring/framework.md): a short account of an incident
carries the same "not enough to plan from" property as a short release
note, even though nothing here scores 5R directly against incidents.

Usage:
    python3 tone_signals.py data/incidents.csv -o findings/
"""

import argparse
import csv
import json
import pathlib
import re
from collections import Counter

LEXICONS = {
    "fatality_injury": [
        "died", "death", "killed", "fatal", "injur", "hospitaliz",
        "wounded", "casualt",
    ],
    "legal_regulatory": [
        "lawsuit", "sued", "sue ", "court", "litigation", "regulator",
        "investigat", "fine", "fined", "violat", "class action", "settlement",
    ],
    "financial_business": [
        "lost $", "cost $", "million", "billion", "stock", "revenue",
        "fraud", "scam", "financial loss",
    ],
    "urgency_emergency": [
        "immediately", "urgent", "emergency", "recall", "shut down",
        "suspend", "halt", "evacuat",
    ],
    "uncertainty_hedging": [
        "allegedly", "reportedly", "purported", "claim", "appears to",
        "may have", "believed to",
    ],
}


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if re.search(r"[a-zA-Z]", p)]


def scan(text):
    lower = text.lower()
    hits = {}
    for category, terms in LEXICONS.items():
        matched = [t for t in terms if t in lower]
        if matched:
            hits[category] = matched
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("incidents_csv")
    ap.add_argument("-o", "--out", default="findings")
    args = ap.parse_args()

    with open(args.incidents_csv, newline="", encoding="utf-8") as f:
        incidents = list(csv.DictReader(f))

    n = len(incidents)
    category_counts = Counter()
    sentence_counts = []
    rows = []
    for r in incidents:
        text = f"{r['title']}. {r['description']}"
        hits = scan(text)
        for cat in hits:
            category_counts[cat] += 1
        n_sent = len(sentences(r["description"]))
        sentence_counts.append(n_sent)
        rows.append({
            "incident_id": r["incident_id"], "title": r["title"],
            "sentence_count": n_sent,
            "signals": sorted(hits.keys()),
        })

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "tone_signals.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    sentence_counts.sort()
    brief_threshold = 2  # mirrors the R4 "three sentences or fewer" gate
    n_brief = sum(1 for c in sentence_counts if c <= brief_threshold)

    summary = {
        "total_incidents": n,
        "signal_prevalence": {cat: {"count": c, "pct": round(100 * c / n, 1)}
                             for cat, c in category_counts.most_common()},
        "description_sentence_count": {
            "min": sentence_counts[0], "median": sentence_counts[n // 2],
            "max": sentence_counts[-1],
        },
        "descriptions_two_sentences_or_fewer": {
            "count": n_brief, "pct": round(100 * n_brief / n, 1),
        },
    }
    (out_dir / "tone_signals_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
