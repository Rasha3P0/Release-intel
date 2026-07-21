#!/usr/bin/env python3
"""Fetch GitLab monthly release notes and split them into individual items.

Source: GitLab release notes, versions 19.0 to 19.2, published at
https://docs.gitlab.com/releases/. The notes are quoted for analysis under
fair-dealing review purposes, with links back to the source pages.

Requires ordinary outbound HTTPS. Run from a clean clone:

    python3 fetch_notes.py            # fetch all three releases into data/
    python3 fetch_notes.py --sample 5 # also print the first items for review

Per the working method, the first run's output should be eyeballed against
the source pages before scoring is run at scale: confirm the split points
land on real per-feature items and that navigation boilerplate is excluded.
"""

import argparse
import pathlib
import re
import sys
import urllib.request
from html.parser import HTMLParser

SOURCES = {
    "19.0": "https://docs.gitlab.com/releases/19/gitlab-19-0-released/",
    "19.1": "https://docs.gitlab.com/releases/19/gitlab-19-1-released/",
    "19.2": "https://docs.gitlab.com/releases/19/gitlab-19-2-released/",
}

# Headings that are page furniture or section wrappers, not release-note items.
SKIP_HEADINGS = re.compile(
    r"^(on this page|help & feedback|table of contents|share your feedback|"
    r"key improvements|other improvements|bug fixes|performance improvements|"
    r"usability improvements|deprecations|removals|changelog|upgrade|"
    r"installation|omnibus|mattermost)",
    re.IGNORECASE,
)

USER_AGENT = "release-intelligence-fetch/1.0 (public-data analysis; see repo README)"


class ItemSplitter(HTMLParser):
    """Split a release page into (heading, body-text) items at h2/h3 boundaries."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []          # list of [heading, [text chunks]]
        self._heading_depth = 0
        self._heading_text = []
        self._in_body = False
        self._skip_stack = 0     # depth inside nav/aside/header/footer/script

    NON_CONTENT = {"nav", "aside", "header", "footer", "script", "style"}

    def handle_starttag(self, tag, attrs):
        if tag in self.NON_CONTENT:
            self._skip_stack += 1
        if self._skip_stack:
            return
        if tag in ("h2", "h3"):
            self._heading_depth += 1
            self._heading_text = []

    def handle_endtag(self, tag):
        if tag in self.NON_CONTENT and self._skip_stack:
            self._skip_stack -= 1
            return
        if self._skip_stack:
            return
        if tag in ("h2", "h3") and self._heading_depth:
            self._heading_depth -= 1
            heading = " ".join("".join(self._heading_text).split())
            if heading and not SKIP_HEADINGS.match(heading):
                self.items.append([heading, []])
                self._in_body = True
            else:
                self._in_body = False

    def handle_data(self, data):
        if self._skip_stack:
            return
        if self._heading_depth:
            self._heading_text.append(data)
        elif self._in_body and self.items:
            self.items[-1][1].append(data)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def slugify(text, maxlen=60):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:maxlen].rstrip("-") or "item"


def clean_body(chunks):
    text = "".join(chunks)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="data", help="output directory (default: data)")
    ap.add_argument("--sample", type=int, default=0,
                    help="print the first N items per release for review")
    args = ap.parse_args()

    out_root = pathlib.Path(args.out)
    total = 0
    for version, url in SOURCES.items():
        try:
            html = fetch(url)
        except OSError as exc:
            print(f"error: could not fetch {url}: {exc}", file=sys.stderr)
            sys.exit(1)
        splitter = ItemSplitter()
        splitter.feed(html)
        items = [(h, clean_body(b)) for h, b in splitter.items if clean_body(b)]
        if not items:
            print(f"error: no items parsed from {url}; page structure may "
                  f"have changed, inspect it before scoring", file=sys.stderr)
            sys.exit(1)

        vdir = out_root / version
        vdir.mkdir(parents=True, exist_ok=True)
        for n, (heading, body) in enumerate(items, start=1):
            path = vdir / f"{n:03d}-{slugify(heading)}.txt"
            path.write_text(
                f"Title: {heading}\nRelease: {version}\nSource: {url}\n\n{body}\n",
                encoding="utf-8",
            )
        total += len(items)
        print(f"{version}: {len(items)} items -> {vdir}/")
        for heading, body in items[: args.sample]:
            print(f"  sample: {heading}\n    {body[:200]}")

    print(f"done: {total} items across {len(SOURCES)} releases")


if __name__ == "__main__":
    main()
