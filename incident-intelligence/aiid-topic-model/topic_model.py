#!/usr/bin/env python3
"""Topic modelling across AI Incident Database incident descriptions.

Uses AIID's own editorial fields only (title, description), never the
underlying third-party report text. TF-IDF vectorisation followed by
k-means clustering surfaces recurring failure classes without requiring
any labelled training data or external model calls, so the method is
fully reproducible from the committed corpus alone.

Usage:
    python3 topic_model.py data/incidents.csv -o findings/ --k 12
"""

import argparse
import csv
import json
import pathlib

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

STOPWORDS_EXTRA = {
    "ai", "system", "systems", "app", "algorithm", "company", "used",
    "using", "reportedly", "allegedly", "incident",
}


def load_incidents(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("incidents_csv")
    ap.add_argument("-o", "--out", default="findings")
    ap.add_argument("--k", type=int, default=12, help="number of clusters")
    ap.add_argument("--top-terms", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20260721,
                    help="fixed seed for reproducible clustering")
    args = ap.parse_args()

    incidents = load_incidents(args.incidents_csv)
    docs = [f"{r['title']} {r['description']}" for r in incidents]

    vectorizer = TfidfVectorizer(
        max_df=0.6, min_df=3, stop_words="english", ngram_range=(1, 2),
    )
    X = vectorizer.fit_transform(docs)
    terms = vectorizer.get_feature_names_out()

    km = KMeans(n_clusters=args.k, random_state=args.seed, n_init=10)
    labels = km.fit_predict(X)

    clusters = []
    for c in range(args.k):
        centroid = km.cluster_centers_[c]
        top_idx = centroid.argsort()[::-1]
        top = [terms[i] for i in top_idx
               if terms[i] not in STOPWORDS_EXTRA][: args.top_terms]
        members = [i for i, lab in enumerate(labels) if lab == c]
        clusters.append({
            "cluster": c,
            "size": len(members),
            "top_terms": top,
            "sample_titles": [incidents[i]["title"] for i in members[:5]],
        })
    clusters.sort(key=lambda c: -c["size"])

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    assignments_path = out_dir / "topic_clusters.csv"
    with assignments_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["incident_id", "title", "cluster"])
        for r, lab in zip(incidents, labels):
            w.writerow([r["incident_id"], r["title"], int(lab)])

    summary_path = out_dir / "topic_clusters_summary.json"
    summary_path.write_text(json.dumps(clusters, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")

    print(f"{len(incidents)} incidents, {args.k} clusters")
    for c in clusters:
        print(f"  cluster {c['cluster']}: {c['size']} incidents | "
              f"{', '.join(c['top_terms'][:6])}")
    print(f"wrote {assignments_path}, {summary_path}")


if __name__ == "__main__":
    main()
