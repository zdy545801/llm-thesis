import argparse
import csv
import json
from pathlib import Path
from statistics import mean


def _mean_or_none(values):
    values = [v for v in values if v is not None]
    return mean(values) if values else None


def _to_scalar(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, list):
        nums = [float(v) for v in x if isinstance(v, (int, float))]
        return _mean_or_none(nums)
    return None


def round_esr(round_json: Path):
    data = json.loads(round_json.read_text(encoding="utf-8"))
    edit_metrics = data.get("edit_metrics", [])
    if not edit_metrics:
        return None
    vals = []
    for item in edit_metrics:
        post = item.get("post", {})
        vals.append(_to_scalar(post.get("rewrite_acc")))
    return _mean_or_none(vals)


def summarize_run(run_dir: Path):
    rounds_dir = run_dir / "rounds"
    if not rounds_dir.exists():
        return None

    by_round = {}
    for p in sorted(rounds_dir.glob("round_*.json")):
        try:
            r = int(p.stem.split("_")[1])
        except Exception:
            continue
        by_round[r] = round_esr(p)

    edited_rounds = sorted([r for r in by_round if r >= 1 and by_round[r] is not None])
    if not edited_rounds:
        return None

    first_r = edited_rounds[0]
    last_r = edited_rounds[-1]
    seq = [by_round[r] for r in edited_rounds]

    return {
        "run_dir": str(run_dir).replace("\\", "/"),
        "first_round": first_r,
        "last_round": last_r,
        "esr_first": by_round[first_r],
        "esr_last": by_round[last_r],
        "esr_mean": _mean_or_none(seq),
        "esr_min": min(seq),
        "esr_max": max(seq),
        "num_rounds": len(seq),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run_dirs",
        nargs="*",
        default=[
            "results/FT/FT_stress_10rounds_20260319",
            "results/FT/FT_stress_10rounds_20260319_r2",
            "results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260320",
            "results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260320_r2",
            "results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260325_r3_shuffle",
            "results/ROME/ROME_gpt2_ft_compare_10rounds_20260325",
            "results/ROME/ROME_gpt2_ft_compare_10rounds_20260325_r2",
        ],
    )
    parser.add_argument("--out_csv", default="results/edit_success_summary.csv")
    parser.add_argument("--out_md", default="results/edit_success_summary.md")
    args = parser.parse_args()

    rows = []
    for d in args.run_dirs:
        p = Path(d)
        if not p.exists():
            continue
        s = summarize_run(p)
        if s is not None:
            rows.append(s)

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "run_dir",
                "first_round",
                "last_round",
                "esr_first",
                "esr_last",
                "esr_mean",
                "esr_min",
                "esr_max",
                "num_rounds",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    out_md = Path(args.out_md)
    lines = [
        "# 编辑成功率汇总（ESR）",
        "",
        "定义：每轮编辑成功率 ESR = 该轮 `post.rewrite_acc` 的均值。",
        "",
        "| run_dir | first_round | last_round | esr_first | esr_last | esr_mean | esr_min | esr_max | num_rounds |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['run_dir']} | {r['first_round']} | {r['last_round']} | "
            f"{r['esr_first']:.4f} | {r['esr_last']:.4f} | {r['esr_mean']:.4f} | "
            f"{r['esr_min']:.4f} | {r['esr_max']:.4f} | {r['num_rounds']} |"
        )

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved: {out_csv}")
    print(f"saved: {out_md}")


if __name__ == "__main__":
    main()
