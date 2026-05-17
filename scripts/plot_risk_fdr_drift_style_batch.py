import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "thesis_figures_ch4_drift_style"
OUT.mkdir(parents=True, exist_ok=True)


RUNS = {
    "ft_full_risk_fdr": ROOT / "results" / "FT" / "FT_gpt2_full_e120_20260404" / "drift_metrics.json",
    "rome_full_risk_fdr": ROOT / "results" / "ROME" / "ROME_gpt2_full_e120_20260404" / "drift_metrics.json",
    "memit_full_risk_fdr": ROOT / "results" / "MEMIT" / "MEMIT_gpt2_full_e120_20260405" / "drift_metrics.json",
    "memit_shuffle_risk_fdr": ROOT / "results" / "MEMIT" / "MEMIT_gpt2_ft_compare_10rounds_20260325_r3_shuffle" / "drift_metrics.json",
    "ft_sample_r1_risk_fdr": ROOT / "results" / "FT" / "FT_stress_10rounds_20260319" / "drift_metrics.json",
    "ft_sample_r2_risk_fdr": ROOT / "results" / "FT" / "FT_stress_10rounds_20260319_r2" / "drift_metrics.json",
    "rome_sample_r1_risk_fdr": ROOT / "results" / "ROME" / "ROME_gpt2_ft_compare_10rounds_20260325" / "drift_metrics.json",
    "rome_sample_r2_risk_fdr": ROOT / "results" / "ROME" / "ROME_gpt2_ft_compare_10rounds_20260325_r2" / "drift_metrics.json",
    "memit_sample_r1_risk_fdr": ROOT / "results" / "MEMIT" / "MEMIT_gpt2_ft_compare_10rounds_20260320" / "drift_metrics.json",
    "memit_sample_r2_risk_fdr": ROOT / "results" / "MEMIT" / "MEMIT_gpt2_ft_compare_10rounds_20260320_r2" / "drift_metrics.json",
}


def plot_one(metrics_json: Path, out_stem: str):
    data = json.loads(metrics_json.read_text(encoding="utf-8"))
    rounds = data["rounds"]
    xs = [r["round"] for r in rounds]
    risk = [r["fairness_risk"] for r in rounds]
    fdr = [r["fdr"] for r in rounds]

    # This intentionally follows scripts/plot_drift.py, which produced the
    # original MEMIT-full risk/FDR joint curve.
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))

    ax[0].plot(xs, risk, marker="o")
    ax[0].set_title("Fairness Risk vs Round")
    ax[0].set_xlabel("Edit Round")
    ax[0].set_ylabel("Fairness Risk (higher=worse)")
    ax[0].grid(alpha=0.3)

    ax[1].plot(xs, fdr, marker="o")
    ax[1].axhline(0, linestyle="--", linewidth=1)
    ax[1].set_title("FDR vs Round")
    ax[1].set_xlabel("Edit Round")
    ax[1].set_ylabel("FDR (risk_t - risk_t-1)")
    ax[1].grid(alpha=0.3)

    fig.suptitle(f"CDA={data.get('cda'):.4f}")
    fig.tight_layout()

    png = OUT / f"{out_stem}.png"
    svg = OUT / f"{out_stem}.svg"
    fig.savefig(png, dpi=180)
    fig.savefig(svg)
    plt.close(fig)
    return png


def main():
    written = []
    for name, metrics_json in RUNS.items():
        if metrics_json.exists():
            written.append(plot_one(metrics_json, name))
        else:
            print(f"missing: {metrics_json}")
    print(f"saved {len(written)} figures to {OUT}")


if __name__ == "__main__":
    main()
