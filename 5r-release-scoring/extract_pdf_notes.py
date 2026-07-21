#!/usr/bin/env python3
"""Split GitLab release-notes page captures (PDF) into individual note items.

Alternative ingestion path to fetch_notes.py for environments without
outbound network access: the three public release pages are saved as PDF
in a browser, and this script extracts and splits them into the same
data/ layout that fetch_notes.py produces. The canonical source remains
the live pages at https://docs.gitlab.com/releases/; the PDFs are only a
capture mechanism and are not committed to the repository.

Page structure relied on: each release-note item is a title line followed
by a "Tier:" line, optional "Offering:"/"Add-ons:"/"Links:" metadata
lines, then body text. Everything from "Was this page helpful?" onward is
page footer. Category headings (a known set of section headings directly before
a title) are recorded but excluded from item bodies.

Usage:
    python3 extract_pdf_notes.py 19.0=capture-19.0.pdf 19.1=capture-19.1.pdf \
        19.2=capture-19.2.pdf --out data

Requires pypdf.
"""

import argparse
import pathlib
import re
import sys

from pypdf import PdfReader

SOURCES = {
    "19.0": "https://docs.gitlab.com/releases/19/gitlab-19-0-released/",
    "19.1": "https://docs.gitlab.com/releases/19/gitlab-19-1-released/",
    "19.2": "https://docs.gitlab.com/releases/19/gitlab-19-2-released/",
}

META_PREFIXES = ("Tier:", "Offering:", "Add-ons:", "Links:")
FOOTER_MARKER = "Was this page helpful?"

# Section headings used on the 19.x release pages. Category detection is an
# explicit allowlist: a loose "short unpunctuated line" heuristic wrongly
# captures trailing list lines from the preceding item's body.
CATEGORY_HEADINGS = {
    "Primary features",
    "Agentic Core",
    "Scale and Deployments",
    "Unified DevOps and Security",
}


def slugify(text, maxlen=60):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:maxlen].rstrip("-") or "item"


def pdf_lines(path):
    reader = PdfReader(path)
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    if FOOTER_MARKER in text:
        text = text.split(FOOTER_MARKER)[0]
    return [ln.strip() for ln in text.splitlines()]


def looks_like_category(line):
    return line in CATEGORY_HEADINGS


def split_items(lines):
    """Yield (category, title, meta_lines, body_lines) per note item."""
    tier_idx = [i for i, ln in enumerate(lines) if ln.startswith("Tier:")]
    items = []
    for n, i in enumerate(tier_idx):
        title = lines[i - 1] if i else ""
        cat_line = lines[i - 2] if i >= 2 else ""
        meta, j = [], i
        while j < len(lines) and (lines[j].startswith(META_PREFIXES) or not lines[j]):
            if lines[j]:
                meta.append(lines[j])
            j += 1
        end = tier_idx[n + 1] - 1 if n + 1 < len(tier_idx) else len(lines)
        body = [ln for ln in lines[j:end] if ln]
        # The next item's category heading, if present, sits at the end of
        # this body (directly above the next title); peel it off.
        if body and n + 1 < len(tier_idx) and looks_like_category(body[-1]) \
                and lines[tier_idx[n + 1] - 1] != body[-1]:
            body = body[:-1]
        items.append((cat_line if looks_like_category(cat_line) else "",
                      title, meta, body))
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("captures", nargs="+",
                    help="version=pdf-path pairs, e.g. 19.0=gitlab-19.0.pdf")
    ap.add_argument("--out", default="data")
    args = ap.parse_args()

    out_root = pathlib.Path(args.out)
    total = 0
    for pair in args.captures:
        version, _, pdf_path = pair.partition("=")
        if version not in SOURCES:
            print(f"error: unknown version {version}", file=sys.stderr)
            sys.exit(1)
        items = split_items(pdf_lines(pdf_path))
        if not items:
            print(f"error: no items found in {pdf_path}", file=sys.stderr)
            sys.exit(1)
        vdir = out_root / version
        vdir.mkdir(parents=True, exist_ok=True)
        for n, (category, title, meta, body) in enumerate(items, start=1):
            head = [f"Title: {title}", f"Release: {version}",
                    f"Source: {SOURCES[version]}"]
            if category:
                head.append(f"Category: {category}")
            head += meta
            path = vdir / f"{n:03d}-{slugify(title)}.txt"
            path.write_text("\n".join(head) + "\n\n" + "\n".join(body) + "\n",
                            encoding="utf-8")
        total += len(items)
        print(f"{version}: {len(items)} items -> {vdir}/")
    print(f"done: {total} items")


if __name__ == "__main__":
    main()
