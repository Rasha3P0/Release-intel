#!/usr/bin/env python3
"""Summarise scored 5R output for the findings section.

Reads scored/scores.json (produced by score_notes.py) and prints base
rates per R-code, co-occurrence of yes stamps, threshold-rule outcomes,
and R4 hard-gate proportions, overall and per release.

Usage:
    python3 analyze_findings.py scored/scores.json
"""

import itertools
import json
import sys
from collections import Counter

CODES = ["R1", "R2", "R3", "R4", "R5"]


def pct(n, d):
    return f"{n}/{d} ({100 * n / d:.0f}%)" if d else "0/0"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "scored/scores.json"
    results = json.loads(open(path, encoding="utf-8").read())
    n = len(results)
    releases = sorted({r["release"] for r in results})

    print(f"corpus: {n} notes across releases {', '.join(releases)}")
    for rel in releases:
        print(f"  {rel}: {sum(1 for r in results if r['release'] == rel)} notes")

    print("\nbase rates (stamp per R-code):")
    for code in CODES:
        c = Counter(r["scores"][code]["stamp"] for r in results)
        print(f"  {code}: yes {pct(c['yes'], n)}, no {pct(c['no'], n)}, "
              f"unclear {pct(c['unclear'], n)}")

    print("\nyes-stamp co-occurrence (pairs):")
    pair_counts = Counter()
    for r in results:
        stamped = [c for c in CODES if r["scores"][c]["stamp"] == "yes"]
        for a, b in itertools.combinations(stamped, 2):
            pair_counts[(a, b)] += 1
    for (a, b), count in pair_counts.most_common():
        print(f"  {a}+{b}: {count}")

    print("\nthreshold outcomes:")
    for stamps, count in sorted(Counter(r["stamps"] for r in results).items()):
        print(f"  {stamps} stamp(s): {pct(count, n)}")
    for action, count in Counter(r["action"] for r in results).most_common():
        print(f"  action '{action}': {count}")

    gate = [r for r in results if r["r4_hard_gate"]]
    print(f"\nR4 hard gate: {pct(len(gate), n)} of notes")
    for rel in releases:
        rel_all = [r for r in results if r["release"] == rel]
        rel_gate = [r for r in rel_all if r["r4_hard_gate"]]
        print(f"  {rel}: {pct(len(rel_gate), len(rel_all))}")

    print("\nhighest-stamp notes:")
    for r in sorted(results, key=lambda r: -r["stamps"])[:8]:
        print(f"  [{r['stamps']}] {r['release']} {r['title']} "
              f"({'+'.join(r['stamped_codes'])})")

    print("\nzero-stamp notes:")
    for r in results:
        if r["stamps"] == 0:
            print(f"  {r['release']} {r['title']}")


if __name__ == "__main__":
    main()
