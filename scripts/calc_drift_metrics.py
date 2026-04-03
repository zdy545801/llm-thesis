import argparse
import json
import re
from pathlib import Path


def load_round_file(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    crows = data.get("crows", {})
    bbq = data.get("bbq", {})
    return {
        "path": str(path),
        "round": None,
        "prefer_stereo_rate": crows.get("prefer_stereo_rate"),
        "bbq_accuracy_proxy": bbq.get("accuracy_proxy"),
    }


def infer_round(name: str):
    m = re.search(r"round[_-]?(\d+)", name.lower())
    if m:
        return int(m.group(1))
    m2 = re.search(r"(\d+)", name)
    if m2:
        return int(m2.group(1))
    return None


def fairness_risk(stereo_rate, bbq_acc, alpha):
    # Higher = worse fairness
    # stereo_rate: higher worse; bbq_acc: lower worse
    if stereo_rate is None or bbq_acc is None:
        return None
    return alpha * stereo_rate + (1 - alpha) * (1 - bbq_acc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True, help="Directory with round JSON files.")
    parser.add_argument("--pattern", type=str, default="*.json")
    parser.add_argument("--alpha", type=float, default=0.5, help="Weight for CrowS stereotype rate.")
    parser.add_argument("--out", type=str, default="results/drift_metrics.json")
    args = parser.parse_args()

    in_dir = Path(args.input_dir)
    files = sorted(in_dir.glob(args.pattern))
    if not files:
        raise FileNotFoundError(f"No files matched in {in_dir} with pattern {args.pattern}")

    rows = []
    for p in files:
        row = load_round_file(p)
        row["round"] = infer_round(p.stem)
        rows.append(row)

    # If round not found, keep input order by assigning 0..n-1
    if any(r["round"] is None for r in rows):
        for i, r in enumerate(rows):
            r["round"] = i

    rows = sorted(rows, key=lambda x: x["round"])

    for r in rows:
        r["fairness_risk"] = fairness_risk(
            r["prefer_stereo_rate"], r["bbq_accuracy_proxy"], args.alpha
        )

    base = rows[0]["fairness_risk"]
    if base is None:
        raise ValueError("Baseline fairness_risk is None; check crows/bbq fields in round0 file.")

    cda = 0.0
    prev = base
    for r in rows:
        risk = r["fairness_risk"]
        if risk is None:
            r["fdr"] = None
            r["delta_from_base"] = None
            continue
        r["fdr"] = risk - prev  # Fairness Drift Rate (incremental)
        r["delta_from_base"] = risk - base
        cda += max(0.0, risk - base)  # Cumulative Drift Area (positive part)
        prev = risk

    out = {
        "alpha": args.alpha,
        "definition": {
            "fairness_risk": "alpha*prefer_stereo_rate + (1-alpha)*(1-bbq_accuracy_proxy)",
            "fdr": "fairness_risk_t - fairness_risk_(t-1)",
            "cda": "sum_t max(0, fairness_risk_t - fairness_risk_0)",
        },
        "cda": cda,
        "rounds": rows,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved:", out_path)
    print("CDA:", round(cda, 6))


if __name__ == "__main__":
    main()

