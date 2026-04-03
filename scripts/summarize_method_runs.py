import argparse
import csv
import json
from pathlib import Path
from statistics import mean, stdev


def _safe_mean(vals):
    vals = [v for v in vals if v is not None]
    return mean(vals) if vals else None


def _safe_std(vals):
    vals = [v for v in vals if v is not None]
    if len(vals) < 2:
        return 0.0 if vals else None
    return stdev(vals)


def _read_drift_metrics(run_dir: Path):
    p = run_dir / "drift_metrics.json"
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    rounds = data.get("rounds", [])
    if not rounds:
        return None
    r0 = rounds[0]
    rlast = rounds[-1]
    return {
        "cda": data.get("cda"),
        "risk_0": r0.get("fairness_risk"),
        "risk_last": rlast.get("fairness_risk"),
        "delta_last": rlast.get("delta_from_base"),
        "fdr_abs_mean": _safe_mean([abs(r.get("fdr")) for r in rounds[1:] if r.get("fdr") is not None]),
        "rounds_n": len(rounds) - 1,
    }


def _to_scalar(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, list):
        nums = [float(v) for v in x if isinstance(v, (int, float))]
        return _safe_mean(nums)
    return None


def _read_esr(run_dir: Path):
    rounds_dir = run_dir / "rounds"
    if not rounds_dir.exists():
        return None
    vals = []
    for p in sorted(rounds_dir.glob("round_*.json")):
        try:
            r = int(p.stem.split("_")[1])
        except Exception:
            continue
        if r == 0:
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        edit_metrics = data.get("edit_metrics", [])
        if not edit_metrics:
            continue
        per_round = []
        for item in edit_metrics:
            post = item.get("post", {})
            per_round.append(_to_scalar(post.get("rewrite_acc")))
        x = _safe_mean(per_round)
        if x is not None:
            vals.append(x)
    return _safe_mean(vals)


def _guess_method(run_name: str):
    n = run_name.upper()
    if "MEMIT" in n:
        return "MEMIT"
    if "ROME" in n:
        return "ROME"
    if "FT" in n:
        return "FT"
    if "MEND" in n:
        return "MEND"
    return "OTHER"


def _fmt(x, nd=4):
    if x is None:
        return "NA"
    return f"{x:.{nd}f}"


def _collect_runs(results_root: Path):
    run_dirs = []
    for method_dir in ["FT", "MEMIT", "ROME", "MEND"]:
        p = results_root / method_dir
        if not p.exists():
            continue
        for child in sorted(p.iterdir()):
            if child.is_dir() and (child / "drift_metrics.json").exists() and (child / "rounds").exists():
                run_dirs.append(child)
    return run_dirs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_root", default="results")
    parser.add_argument("--out_csv", default="results/method_run_stats.csv")
    parser.add_argument("--out_md", default="results/method_run_stats.md")
    args = parser.parse_args()

    results_root = Path(args.results_root)
    run_dirs = _collect_runs(results_root)

    rows = []
    for d in run_dirs:
        dm = _read_drift_metrics(d)
        if dm is None:
            continue
        rows.append(
            {
                "method": _guess_method(d.name),
                "run_dir": str(d).replace("\\", "/"),
                "cda": dm["cda"],
                "risk_0": dm["risk_0"],
                "risk_last": dm["risk_last"],
                "delta_last": dm["delta_last"],
                "fdr_abs_mean": dm["fdr_abs_mean"],
                "esr_mean": _read_esr(d),
                "rounds_n": dm["rounds_n"],
            }
        )

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "method",
                "run_dir",
                "cda",
                "risk_0",
                "risk_last",
                "delta_last",
                "fdr_abs_mean",
                "esr_mean",
                "rounds_n",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    # aggregate method-level mean/std
    by_method = {}
    for r in rows:
        by_method.setdefault(r["method"], []).append(r)

    lines = [
        "# 方法级运行统计（自动汇总）",
        "",
        "说明：",
        "- `delta_last = risk_last - risk_0`（负值表示最终风险下降）。",
        "- `fdr_abs_mean` 越大表示轮次波动越强。",
        "",
        "## 单次运行明细",
        "",
        "| method | run_dir | cda | risk_0 | risk_last | delta_last | fdr_abs_mean | esr_mean | rounds_n |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['method']} | {r['run_dir']} | {_fmt(r['cda'])} | {_fmt(r['risk_0'])} | {_fmt(r['risk_last'])} | "
            f"{_fmt(r['delta_last'])} | {_fmt(r['fdr_abs_mean'])} | {_fmt(r['esr_mean'])} | {r['rounds_n']} |"
        )

    lines += [
        "",
        "## 方法级均值±标准差",
        "",
        "| method | runs | delta_last_mean | delta_last_std | esr_mean_mean | esr_mean_std | fdr_abs_mean_mean |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for m, rs in sorted(by_method.items()):
        delta = [x["delta_last"] for x in rs]
        esr = [x["esr_mean"] for x in rs]
        fdr = [x["fdr_abs_mean"] for x in rs]
        lines.append(
            f"| {m} | {len(rs)} | {_fmt(_safe_mean(delta))} | {_fmt(_safe_std(delta))} | "
            f"{_fmt(_safe_mean(esr))} | {_fmt(_safe_std(esr))} | {_fmt(_safe_mean(fdr))} |"
        )

    out_md = Path(args.out_md)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"saved: {out_csv}")
    print(f"saved: {out_md}")


if __name__ == "__main__":
    main()
