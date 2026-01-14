#!/usr/bin/env python3
"""
Khmer TXT dataset cleaner:
- Measures character length per line
- Filters by recommended thresholds
- Optionally splits long lines into sentences (using Khmer punctuation)
- Writes: cleaned.txt + removed.txt + stats.json

Usage:
  python khmer_clean_txt.py --input raw.txt --outdir out --split-long
"""

from __future__ import annotations
import argparse
import json
import os
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, asdict
from typing import List, Tuple


# --- Khmer sentence boundary punctuation (extend if needed)
SENT_BOUNDARY_RE = re.compile(r"(?<=[។?!])\s*")  # split after ។ ? !


@dataclass
class CleanConfig:
    min_chars: int = 10
    ideal_min: int = 20
    ideal_max: int = 200
    review_min: int = 201
    review_max: int = 300
    hard_max: int = 300
    normalize_unicode: bool = True
    strip_lines: bool = True
    collapse_whitespace: bool = True
    split_long: bool = False


def normalize_text(s: str, cfg: CleanConfig) -> str:
    """Basic normalization that is safe for Khmer corpora."""
    if cfg.strip_lines:
        s = s.strip()

    if cfg.normalize_unicode:
        # NFC is usually safe; NFKC can change some characters, so avoid unless needed.
        s = unicodedata.normalize("NFC", s)

    if cfg.collapse_whitespace:
        # Collapse internal whitespace to single spaces
        s = re.sub(r"\s+", " ", s).strip()

    return s


def split_into_sentences(line: str) -> List[str]:
    """
    Split a line into sentences using Khmer/Latin punctuation boundaries.
    Keeps punctuation attached to the sentence.
    """
    # SENT_BOUNDARY_RE splits after punctuation; it may produce empty fragments.
    parts = [p.strip() for p in SENT_BOUNDARY_RE.split(line) if p.strip()]
    return parts if parts else []


def categorize_len(n: int, cfg: CleanConfig) -> str:
    """Assign a category label based on char length (for stats/reporting)."""
    if n < cfg.min_chars:
        return "too_short"
    if cfg.ideal_min <= n <= cfg.ideal_max:
        return "ideal"
    if cfg.min_chars <= n < cfg.ideal_min:
        return "short_ok"
    if cfg.review_min <= n <= cfg.review_max:
        return "very_long_review"
    if n > cfg.hard_max:
        return "too_long"
    # Shouldn't happen, but keep safe:
    return "other"


def process_lines(
    lines: List[str], cfg: CleanConfig
) -> Tuple[List[str], List[Tuple[str, str]], Counter]:
    """
    Returns:
      kept_lines: cleaned lines that pass filters (and optional splitting)
      removed: list of tuples (reason, original_line)
      stats: Counter with length category counts
    """
    kept: List[str] = []
    removed: List[Tuple[str, str]] = []
    stats = Counter()

    for raw in lines:
        original = raw.rstrip("\n")
        cleaned = normalize_text(original, cfg)

        # Skip empty lines
        if not cleaned:
            removed.append(("empty", original))
            stats["empty"] += 1
            continue

        # Optional: split long lines into sentences
        candidates = [cleaned]
        if cfg.split_long and len(cleaned) > cfg.ideal_max:
            sents = split_into_sentences(cleaned)
            if sents:
                candidates = sents

        # Evaluate each candidate sentence
        for sent in candidates:
            sent = normalize_text(sent, cfg)
            if not sent:
                removed.append(("empty_after_split", original))
                stats["empty_after_split"] += 1
                continue

            n = len(sent)
            cat = categorize_len(n, cfg)
            stats[cat] += 1

            if cat == "too_short":
                removed.append(("too_short(<min_chars)", sent))
            elif cat == "too_long":
                removed.append(("too_long(>hard_max)", sent))
            else:
                # Keep: includes ideal, short_ok, very_long_review
                kept.append(sent)

    return kept, removed, stats


def percentile(sorted_vals: List[int], p: float) -> int:
    """Simple percentile (p in [0,100])."""
    if not sorted_vals:
        return 0
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return int(round(d0 + d1))


def write_list(path: str, lines: List[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to raw TXT (one line per record)")
    ap.add_argument("--outdir", default="out", help="Output directory")
    ap.add_argument("--min-chars", type=int, default=10)
    ap.add_argument("--ideal-min", type=int, default=20)
    ap.add_argument("--ideal-max", type=int, default=200)
    ap.add_argument("--hard-max", type=int, default=300)
    ap.add_argument("--split-long", action="store_true", help="Split long lines into sentences")
    args = ap.parse_args()

    cfg = CleanConfig(
        min_chars=args.min_chars,
        ideal_min=args.ideal_min,
        ideal_max=args.ideal_max,
        hard_max=args.hard_max,
        split_long=args.split_long,
        # review range defaults to 201–300; keep consistent with hard_max if changed
        review_min=args.ideal_max + 1,
        review_max=args.hard_max,
    )

    os.makedirs(args.outdir, exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    kept, removed, stats = process_lines(raw_lines, cfg)

    # De-duplicate while preserving order (optional but often helpful)
    seen = set()
    kept_dedup = []
    for ln in kept:
        if ln not in seen:
            seen.add(ln)
            kept_dedup.append(ln)

    # Save outputs
    cleaned_path = os.path.join(args.outdir, "cleaned.txt")
    removed_path = os.path.join(args.outdir, "removed.txt")
    stats_path = os.path.join(args.outdir, "stats.json")

    write_list(cleaned_path, kept_dedup)

    with open(removed_path, "w", encoding="utf-8") as f:
        for reason, ln in removed:
            f.write(f"[{reason}] {ln}\n")

    # Extra numeric stats
    lengths = [len(x) for x in kept_dedup]
    lengths_sorted = sorted(lengths)

    report = {
        "config": asdict(cfg),
        "input_lines": len(raw_lines),
        "kept_lines": len(kept_dedup),
        "removed_items": len(removed),
        "length_categories": dict(stats),
        "kept_length_summary": {
            "min": min(lengths) if lengths else 0,
            "max": max(lengths) if lengths else 0,
            "p50": percentile(lengths_sorted, 50),
            "p90": percentile(lengths_sorted, 90),
            "p95": percentile(lengths_sorted, 95),
            "mean": (sum(lengths) / len(lengths)) if lengths else 0.0,
        },
    }

    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("Done.")
    print(f"Cleaned:  {cleaned_path}")
    print(f"Removed:  {removed_path}")
    print(f"Stats:    {stats_path}")
    print(f"Kept lines: {len(kept_dedup)} / {len(raw_lines)}")


if __name__ == "__main__":
    main()
