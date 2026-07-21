#!/usr/bin/env python3
"""5R categorical scorer for release-note text files.

Applies the 5R specification in framework.md to a directory of note files
(the format written by fetch_notes.py: Title/Release/Source header lines, a
blank line, then the note body) and writes scored output as CSV and JSON.

Two scoring modes, per the method's honesty rules:

- Rule-assisted (default). R4 is scored from its lexical triggers and the
  three-sentence length gate; this is fully rule-based by design. For the
  judgement codes (R1, R2, R3, R5) the rules stamp yes only when trigger
  language is present in the note, quoting the matched sentence as evidence.
  When nothing matches, the rules stamp unclear, never no: absence of a
  keyword is not evidence of absence, and stamping no would be speculation.
  Each unclear stamp names the missing information that would resolve it.

- LLM-assisted merge (--llm-scores scores.json). Judgements for R1, R2, R3
  and R5 produced with the committed prompt in scoring_prompt.md can be
  merged over the rule results; these may stamp no, because a reader can
  judge absence in a way keyword rules cannot. R4 always remains
  rule-scored: its triggers are lexical by definition. The LLM file maps
  note id to {"R1": {"stamp": "yes|no|unclear", "evidence": "..."}, ...}.

Usage:
    python3 score_notes.py data/ -o scored/
    python3 score_notes.py data/ -o scored/ --llm-scores scored/llm_scores.json
"""

import argparse
import csv
import json
import pathlib
import re
import sys

R4_LABELS = [
    "performance", "refactor", "optimisation", "optimization", "cleanup",
    "clean-up", "tech debt", "technical debt", "minor", "behind-the-scenes",
    "behind the scenes",
]

# Trigger lexicons for the judgement codes. A match stamps yes with the
# matched sentence as evidence; no match stamps unclear (never no).
LEXICONS = {
    "R1": [
        "schema", "database", "data model", "stored", "storage format",
        "column", "table structure", "calculation", "recalculat", "rounding",
        "serialis", "serializ", "data format", "interpretation",
    ],
    "R2": [
        "batch", "background job", "queue", "high volume", "high-volume",
        "bulk", "throughput", "cron", "scheduled job", "critical feed",
        "all projects", "all users", "every project", "instance-wide",
    ],
    "R3": [
        "api", "graphql", "webhook", "endpoint", "integration", "interface",
        "export", "report", "downstream", "consumer", "deprecat",
        "breaking change", "third-party", "third party",
    ],
    "R5": [
        "migration", "irreversible", "one-way", "one way", "cannot be undone",
        "forward-only", "forward only", "backfill", "permanently", "removed",
        "removal", "dropped", "no rollback",
    ],
}

UNCLEAR_RESOLUTION = {
    "R1": "confirmation from the change owner whether stored data shape, "
          "calculations or interpretation logic change",
    "R2": "which processes the change runs through and their volume profile",
    "R3": "an enumeration of downstream consumers, interfaces and reports "
          "the change touches",
    "R5": "whether the change involves one-way operations or forward-only "
          "migrations, and the rollback path if not",
}

CODES = ["R1", "R2", "R3", "R4", "R5"]


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if re.search(r"[a-zA-Z]", p)]


def find_evidence(term, text):
    """Return the first sentence containing term, for quoting."""
    for s in sentences(text):
        if term.lower() in s.lower():
            return s.strip()
    return term


def parse_note(path):
    raw = path.read_text(encoding="utf-8")
    head, _, body = raw.partition("\n\n")
    meta = {}
    for line in head.splitlines():
        key, _, value = line.partition(":")
        meta[key.strip().lower()] = value.strip()
    return {
        "id": path.stem,
        "title": meta.get("title", path.stem),
        "release": meta.get("release", ""),
        "source": meta.get("source", ""),
        "body": body.strip(),
    }


def score_rule(note):
    text = f"{note['title']}\n{note['body']}"
    result = {}

    for code in ("R1", "R2", "R3", "R5"):
        hits = [t for t in LEXICONS[code] if t in text.lower()]
        if hits:
            result[code] = {
                "stamp": "yes",
                "evidence": f"matched '{hits[0]}': \"{find_evidence(hits[0], text)}\"",
            }
        else:
            result[code] = {
                "stamp": "unclear",
                "evidence": "no trigger language in the note; missing: "
                            + UNCLEAR_RESOLUTION[code],
            }

    label_hits = [l for l in R4_LABELS if l in text.lower()]
    n_sentences = len(sentences(note["body"]))
    if label_hits:
        result["R4"] = {
            "stamp": "yes",
            "evidence": f"innocuous label '{label_hits[0]}': "
                        f"\"{find_evidence(label_hits[0], text)}\"",
        }
    elif n_sentences <= 3:
        result["R4"] = {
            "stamp": "yes",
            "evidence": f"note is {n_sentences} sentence(s); three or fewer "
                        "trips the brevity trigger",
        }
    else:
        result["R4"] = {"stamp": "no",
                        "evidence": f"no innocuous label; {n_sentences} sentences"}
    return result


def merge_llm(rule_scores, llm_scores, note_id):
    merged = dict(rule_scores)
    for code, judgement in llm_scores.get(note_id, {}).items():
        if code == "R4" or code not in CODES:
            continue  # R4 stays rule-scored; ignore unknown keys
        stamp = judgement.get("stamp")
        if stamp in ("yes", "no", "unclear"):
            merged[code] = {"stamp": stamp,
                            "evidence": judgement.get("evidence", ""),
                            "scored_by": "llm"}
    return merged


def apply_threshold(scores):
    stamped = [c for c in CODES if scores[c]["stamp"] == "yes"]
    if len(stamped) >= 2:
        action = "coordination sign-off before planning"
    elif len(stamped) == 1:
        action = f"{stamped[0]} testing protocol"
    else:
        action = "proceed normally"
    return {
        "stamps": len(stamped),
        "stamped_codes": stamped,
        "action": action,
        "r4_hard_gate": scores["R4"]["stamp"] == "yes",
        "unclear_codes": [c for c in CODES if scores[c]["stamp"] == "unclear"],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("data_dir", help="directory of note files (searched recursively)")
    ap.add_argument("-o", "--out", default="scored", help="output directory")
    ap.add_argument("--llm-scores", help="JSON file of LLM-assisted judgements "
                                         "made with scoring_prompt.md")
    args = ap.parse_args()

    notes = sorted(pathlib.Path(args.data_dir).rglob("*.txt"))
    if not notes:
        print(f"error: no .txt notes under {args.data_dir}", file=sys.stderr)
        sys.exit(1)

    llm = {}
    if args.llm_scores:
        llm = json.loads(pathlib.Path(args.llm_scores).read_text(encoding="utf-8"))

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for path in notes:
        note = parse_note(path)
        scores = score_rule(note)
        if llm:
            scores = merge_llm(scores, llm, note["id"])
        verdict = apply_threshold(scores)
        results.append({
            "id": note["id"], "release": note["release"],
            "title": note["title"], "source": note["source"],
            "scores": scores, **verdict,
        })

    json_path = out_dir / "scores.json"
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")

    csv_path = out_dir / "scores.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "release", "title"] + CODES
                        + ["stamps", "action", "r4_hard_gate"])
        for r in results:
            writer.writerow([r["id"], r["release"], r["title"]]
                            + [r["scores"][c]["stamp"] for c in CODES]
                            + [r["stamps"], r["action"], r["r4_hard_gate"]])

    n_gate = sum(1 for r in results if r["r4_hard_gate"])
    print(f"scored {len(results)} notes -> {csv_path}, {json_path}")
    print(f"R4 hard gate tripped on {n_gate}/{len(results)} notes")


if __name__ == "__main__":
    main()
