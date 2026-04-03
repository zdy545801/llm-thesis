import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics_json", type=str, required=True)
    parser.add_argument("--out_png", type=str, default="results/drift_curve.png")
    args = parser.parse_args()

    data = json.loads(Path(args.metrics_json).read_text(encoding="utf-8"))
    rounds = data["rounds"]
    xs = [r["round"] for r in rounds]
    risk = [r["fairness_risk"] for r in rounds]
    fdr = [r["fdr"] for r in rounds]

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

    out = Path(args.out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180)
    try:
        print("saved:", out)
    except UnicodeEncodeError:
        print("saved: drift curve image written")


if __name__ == "__main__":
    main()
