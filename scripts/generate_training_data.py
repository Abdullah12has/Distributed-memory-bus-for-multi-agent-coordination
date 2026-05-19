#!/usr/bin/env python3
"""Generate QA training JSONL from HotpotQA for the ICAE trainer.

Produces ``data/processed/training/qa.jsonl`` with rows matching the schema
expected by :class:`m6.compressors.training.dataset.QADataset`::

    {"context": "...", "question": "...", "answer": "..."}

Usage::

    python scripts/generate_training_data.py            # default 10k rows
    python scripts/generate_training_data.py --n 5000   # custom count
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _flatten_context(ctx: dict) -> str:
    """Join HotpotQA context paragraphs into a single string.

    HotpotQA context has ``title`` (list[str]) and ``sentences`` (list[list[str]]).
    We join the sentences of each paragraph, then join paragraphs with newlines.
    """
    parts: list[str] = []
    for title, sents in zip(ctx["title"], ctx["sentences"], strict=False):
        parts.append(f"[{title}] " + " ".join(sents).strip())
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=10_000, help="Number of examples to generate.")
    parser.add_argument(
        "--out",
        type=str,
        default="data/processed/training/qa.jsonl",
        help="Output path.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Shuffle seed.")
    args = parser.parse_args(argv)

    try:
        from datasets import load_dataset
    except ImportError:
        print("ERROR: `datasets` package not installed. Run: pip install datasets", file=sys.stderr)
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("Loading HotpotQA (fullwiki, train split) ...")
    ds = load_dataset("hotpot_qa", "fullwiki", split="train")
    print(f"  Total rows in split: {len(ds)}")

    # Shuffle deterministically and take first n.
    ds = ds.shuffle(seed=args.seed)
    n = min(args.n, len(ds))

    written = 0
    skipped = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for i in range(n):
            row = ds[i]
            context = _flatten_context(row["context"])
            question = row["question"]
            answer = row["answer"]

            # Skip rows with very short context (< 50 chars) — not useful for compression training.
            if len(context) < 50:
                skipped += 1
                continue

            record = {
                "context": context,
                "question": question,
                "answer": answer,
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1

    print(f"Wrote {written} examples to {out_path}  (skipped {skipped})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
