import argparse
import csv
import io
import json
from pathlib import Path

import requests


def dump_jsonl(rows, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--crows_n", type=int, default=200)
    parser.add_argument("--bbq_n", type=int, default=300)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # CrowS-Pairs sample (official repo CSV)
    crows_url = "https://raw.githubusercontent.com/nyu-mll/crows-pairs/master/data/crows_pairs_anonymized.csv"
    crows_text = requests.get(crows_url, timeout=30).text
    crows_reader = csv.DictReader(io.StringIO(crows_text))
    crows_rows = []
    for i, row in enumerate(crows_reader):
        if i >= args.crows_n:
            break
        crows_rows.append(
            {
                "id": i,
                "sent_more": row.get("sent_more"),
                "sent_less": row.get("sent_less"),
                "stereo_antistereo": row.get("stereo_antistereo"),
                "bias_type": row.get("bias_type"),
            }
        )

    # BBQ sample (official repo JSONL; concatenate several categories)
    bbq_urls = [
        "https://raw.githubusercontent.com/nyu-mll/BBQ/main/data/Gender_identity.jsonl",
        "https://raw.githubusercontent.com/nyu-mll/BBQ/main/data/Race_ethnicity.jsonl",
        "https://raw.githubusercontent.com/nyu-mll/BBQ/main/data/Religion.jsonl",
    ]
    bbq_rows = []
    idx = 0
    for url in bbq_urls:
        text = requests.get(url, timeout=30).text
        for line in text.splitlines():
            if idx >= args.bbq_n:
                break
            row = json.loads(line)
            bbq_rows.append(
                {
                    "id": idx,
                    "context": row.get("context"),
                    "question": row.get("question"),
                    "ans0": row.get("ans0"),
                    "ans1": row.get("ans1"),
                    "ans2": row.get("ans2"),
                    "label": row.get("label"),
                    "category": row.get("category"),
                }
            )
            idx += 1
        if idx >= args.bbq_n:
            break

    dump_jsonl(crows_rows, out_dir / "crows_pairs_sample.jsonl")
    dump_jsonl(bbq_rows, out_dir / "bbq_sample.jsonl")
    print("saved:", out_dir / "crows_pairs_sample.jsonl")
    print("saved:", out_dir / "bbq_sample.jsonl")


if __name__ == "__main__":
    main()
