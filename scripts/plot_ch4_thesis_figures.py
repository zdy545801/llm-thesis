import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.ticker import MaxNLocator


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "thesis_figures_ch4"
OUT.mkdir(parents=True, exist_ok=True)


def setup_fonts():
    font_candidates = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
    ]
    for fp in font_candidates:
        if Path(fp).exists():
            font_prop = fm.FontProperties(fname=fp)
            plt.rcParams["font.family"] = font_prop.get_name()
            plt.rcParams["axes.unicode_minus"] = False
            return font_prop
    plt.rcParams["axes.unicode_minus"] = False
    return None


FONT_PROP = setup_fonts()

COLORS = {
    "FT": "#6E86A6",
    "ROME": "#2F5FA7",
    "MEMIT": "#A9B8C9",
    "FDR": "#D88C5A",
    "GRID": "#E7ECF3",
    "AXIS": "#4A5568",
    "TEXT": "#22324A",
    "BASE": "#BFC7D5",
}


plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": COLORS["AXIS"],
        "axes.labelcolor": COLORS["TEXT"],
        "xtick.color": COLORS["TEXT"],
        "ytick.color": COLORS["TEXT"],
        "text.color": COLORS["TEXT"],
        "axes.spines.top": True,
        "axes.spines.right": True,
        "axes.linewidth": 1.0,
        "grid.color": COLORS["GRID"],
        "grid.linewidth": 0.8,
        "grid.alpha": 0.8,
        "legend.frameon": False,
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
    }
)


def load_metrics(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return pd.DataFrame(data["rounds"]), data


def savefig(fig, name: str, dpi: int = 300):
    png = OUT / f"{name}.png"
    svg = OUT / f"{name}.svg"
    fig.savefig(png, dpi=dpi)
    fig.savefig(svg)
    plt.close(fig)


def style_axis(ax, xlabel=None, ylabel=None):
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(True, axis="y", linestyle="-", alpha=0.7)
    ax.tick_params(labelsize=10)
    for side in ["top", "right", "bottom", "left"]:
        ax.spines[side].set_visible(True)
        ax.spines[side].set_color(COLORS["AXIS"])
        ax.spines[side].set_linewidth(1.0)


def plot_single_series(df, y, color, ylabel, name):
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.plot(df["round"], df[y], color=color, marker="o", linewidth=2.0, markersize=5)
    if y == "fairness_risk":
        ax.axhline(df[y].iloc[0], color=COLORS["BASE"], linestyle="--", linewidth=1.2)
    else:
        ax.axhline(0, color=COLORS["BASE"], linestyle="--", linewidth=1.2)
    style_axis(ax, xlabel="轮次", ylabel=ylabel)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    savefig(fig, name)


def plot_risk_fdr_pair(df, method_key, name):
    # Match the compact two-panel style used in the thesis draft:
    # closed axes, light grid, blue lines in both panels, and a small CDA title.
    pair_blue = "#1F77B4"
    fig, axes = plt.subplots(1, 2, figsize=(6.24, 2.4))

    axes[0].plot(
        df["round"],
        df["fairness_risk"],
        color=pair_blue,
        marker="o",
        linewidth=1.0,
        markersize=2.4,
    )
    axes[0].set_title("Fairness Risk vs Round", fontsize=6)
    axes[0].set_xlabel("Edit Round", fontsize=5.5)
    axes[0].set_ylabel("Fairness Risk (higher=worse)", fontsize=5.5)
    axes[0].grid(True, color="#D9D9D9", alpha=0.55, linewidth=0.45)
    axes[0].xaxis.set_major_locator(MaxNLocator(integer=True))
    axes[0].tick_params(labelsize=5.5, width=0.55)

    axes[1].plot(
        df["round"],
        df["fdr"],
        color=pair_blue,
        marker="o",
        linewidth=1.0,
        markersize=2.4,
    )
    axes[1].axhline(0, color=pair_blue, linestyle="--", linewidth=0.55, alpha=0.75)
    axes[1].set_title("FDR vs Round", fontsize=6)
    axes[1].set_xlabel("Edit Round", fontsize=5.5)
    axes[1].set_ylabel("FDR (risk_t - risk_t-1)", fontsize=5.5)
    axes[1].grid(True, color="#D9D9D9", alpha=0.55, linewidth=0.45)
    axes[1].xaxis.set_major_locator(MaxNLocator(integer=True))
    axes[1].tick_params(labelsize=5.5, width=0.55)

    for ax in axes:
        for side in ["top", "right", "bottom", "left"]:
            ax.spines[side].set_visible(True)
            ax.spines[side].set_color("#333333")
            ax.spines[side].set_linewidth(0.55)

    cda = 0.0
    if "delta_from_base" in df.columns:
        cda = sum(max(0.0, float(v)) for v in df["delta_from_base"])
    fig.suptitle(f"CDA={cda:.4f}", fontsize=6, y=0.985)
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.20, top=0.80, wspace=0.27)
    # The paired risk/FDR figures are intended to be inserted as compact
    # thesis subfigures, so the PNG is exported at reference-screen scale.
    savefig(fig, name, dpi=100)


def main():
    method_stats = pd.read_csv(ROOT / "results" / "method_run_stats.csv")

    sample_rows = method_stats[
        method_stats["run_dir"].isin(
            [
                "results/FT/FT_stress_10rounds_20260319",
                "results/FT/FT_stress_10rounds_20260319_r2",
                "results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260320",
                "results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260320_r2",
                "results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260325_r3_shuffle",
                "results/ROME/ROME_gpt2_ft_compare_10rounds_20260325",
                "results/ROME/ROME_gpt2_ft_compare_10rounds_20260325_r2",
            ]
        )
    ].copy()
    sample_rows["run_label"] = [
        "FT-R1",
        "FT-R2",
        "MEMIT-R1",
        "MEMIT-R2",
        "MEMIT-Shuffle",
        "ROME-R1",
        "ROME-R2",
    ]

    full_rows = method_stats[
        method_stats["run_dir"].isin(
            [
                "results/FT/FT_gpt2_full_e120_20260404",
                "results/ROME/ROME_gpt2_full_e120_20260404",
                "results/MEMIT/MEMIT_gpt2_full_e120_20260405",
            ]
        )
    ].copy()
    full_rows["method"] = pd.Categorical(
        full_rows["method"], categories=["FT", "ROME", "MEMIT"], ordered=True
    )
    full_rows = full_rows.sort_values("method")

    ft_full_df, _ = load_metrics(
        ROOT / "results" / "FT" / "FT_gpt2_full_e120_20260404" / "drift_metrics.json"
    )
    rome_full_df, _ = load_metrics(
        ROOT / "results" / "ROME" / "ROME_gpt2_full_e120_20260404" / "drift_metrics.json"
    )
    memit_full_df, _ = load_metrics(
        ROOT / "results" / "MEMIT" / "MEMIT_gpt2_full_e120_20260405" / "drift_metrics.json"
    )
    memit_shuffle_df, _ = load_metrics(
        ROOT
        / "results"
        / "MEMIT"
        / "MEMIT_gpt2_ft_compare_10rounds_20260325_r3_shuffle"
        / "drift_metrics.json"
    )

    # Fig 4.1
    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    bar_colors = [
        COLORS["FT"],
        COLORS["FT"],
        COLORS["MEMIT"],
        COLORS["MEMIT"],
        COLORS["MEMIT"],
        COLORS["ROME"],
        COLORS["ROME"],
    ]
    bars = ax.bar(
        sample_rows["run_label"],
        sample_rows["delta_last"],
        color=bar_colors,
        edgecolor="white",
        linewidth=0.8,
    )
    for i, b in enumerate(bars):
        if "Shuffle" in sample_rows.iloc[i]["run_label"]:
            b.set_hatch("//")
    ax.axhline(0, color=COLORS["BASE"], linewidth=1.2)
    style_axis(ax, ylabel="最终风险变化 Δrisk")
    ax.set_ylim(min(sample_rows["delta_last"]) - 0.01, max(sample_rows["delta_last"]) + 0.01)
    for b, v in zip(bars, sample_rows["delta_last"]):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + (0.002 if v >= 0 else -0.004),
            f"{v:.3f}",
            ha="center",
            va="bottom" if v >= 0 else "top",
            fontsize=9,
        )
    savefig(fig, "fig4_1_sample_final_delta_compare")

    # Fig 4.2
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    ax.plot(
        memit_shuffle_df["round"],
        memit_shuffle_df["fairness_risk"],
        color=COLORS["MEMIT"],
        marker="o",
        linewidth=2.0,
        markersize=5,
    )
    ax.axhline(
        memit_shuffle_df["fairness_risk"].iloc[0],
        color=COLORS["BASE"],
        linestyle="--",
        linewidth=1.2,
    )
    style_axis(ax, xlabel="轮次", ylabel="公平性风险 risk")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    savefig(fig, "fig4_2_memit_shuffle_risk")

    # Fig 4.3
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    ax.plot(
        memit_shuffle_df["round"],
        memit_shuffle_df["fdr"],
        color=COLORS["FDR"],
        marker="o",
        linewidth=2.0,
        markersize=5,
    )
    ax.axhline(0, color=COLORS["BASE"], linestyle="--", linewidth=1.2)
    style_axis(ax, xlabel="轮次", ylabel="轮间变化 FDR")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    savefig(fig, "fig4_3_memit_shuffle_fdr")

    # Fig 4.4
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    bars = ax.bar(
        full_rows["method"],
        full_rows["delta_last"],
        color=[COLORS[m] for m in full_rows["method"]],
        width=0.58,
    )
    ax.axhline(0, color=COLORS["BASE"], linewidth=1.2)
    style_axis(ax, ylabel="最终风险变化 Δrisk")
    ax.set_ylim(full_rows["delta_last"].min() - 0.018, 0)
    for b, v in zip(bars, full_rows["delta_last"]):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v - 0.006,
            f"{v:.3f}",
            ha="center",
            va="top",
            fontsize=9,
        )
    savefig(fig, "fig4_4_full_final_delta_compare")

    # Fig 4.5-4.8
    plot_single_series(ft_full_df, "fairness_risk", COLORS["FT"], "公平性风险 risk", "fig4_5_ft_full_risk")
    plot_single_series(ft_full_df, "fdr", COLORS["FDR"], "轮间变化 FDR", "fig4_6_ft_full_fdr")
    plot_single_series(
        rome_full_df, "fairness_risk", COLORS["ROME"], "公平性风险 risk", "fig4_7_rome_full_risk"
    )
    plot_single_series(rome_full_df, "fdr", COLORS["FDR"], "轮间变化 FDR", "fig4_8_rome_full_fdr")

    # Paired risk + FDR figures in original side-by-side academic style
    plot_risk_fdr_pair(ft_full_df, "FT", "fig4_pair_ft_full_risk_fdr")
    plot_risk_fdr_pair(rome_full_df, "ROME", "fig4_pair_rome_full_risk_fdr")
    plot_risk_fdr_pair(memit_full_df, "MEMIT", "fig4_pair_memit_full_risk_fdr")
    plot_risk_fdr_pair(memit_shuffle_df, "MEMIT", "fig4_pair_memit_shuffle_risk_fdr")

    # Fig 4.9
    fig, ax1 = plt.subplots(figsize=(8.6, 4.8))
    ax1.plot(
        memit_full_df["round"],
        memit_full_df["fairness_risk"],
        color=COLORS["MEMIT"],
        marker="o",
        linewidth=2.0,
        markersize=5,
        label="risk",
    )
    ax1.axhline(
        memit_full_df["fairness_risk"].iloc[0],
        color=COLORS["BASE"],
        linestyle="--",
        linewidth=1.0,
    )
    ax1.set_xlabel("轮次", fontsize=11)
    ax1.set_ylabel("公平性风险 risk", fontsize=11, color=COLORS["TEXT"])
    ax1.tick_params(axis="y", labelcolor=COLORS["TEXT"])
    ax1.grid(True, axis="y", linestyle="-", alpha=0.7)
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))

    ax2 = ax1.twinx()
    ax2.plot(
        memit_full_df["round"],
        memit_full_df["fdr"],
        color=COLORS["FDR"],
        marker="s",
        linewidth=1.8,
        markersize=4,
        label="FDR",
    )
    ax2.axhline(0, color=COLORS["BASE"], linestyle=":", linewidth=1.0)
    ax2.set_ylabel("轮间变化 FDR", fontsize=11, color=COLORS["TEXT"])
    ax2.tick_params(axis="y", labelcolor=COLORS["TEXT"])
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper right", prop=FONT_PROP)
    savefig(fig, "fig4_9_memit_full_joint")

    # Fig 4.10
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    bars = ax.bar(
        full_rows["method"],
        full_rows["esr_mean"],
        color=[COLORS[m] for m in full_rows["method"]],
        width=0.58,
    )
    style_axis(ax, ylabel="平均 ESR")
    ax.set_ylim(0, 1.05)
    for b, v in zip(bars, full_rows["esr_mean"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.3f}", ha="center", va="bottom", fontsize=9)
    savefig(fig, "fig4_10_mean_esr_compare")

    # Fig 4.11
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    bars = ax.bar(
        full_rows["method"],
        full_rows["fdr_abs_mean"],
        color=[COLORS[m] for m in full_rows["method"]],
        width=0.58,
    )
    style_axis(ax, ylabel="平均绝对 FDR")
    ax.set_ylim(0, full_rows["fdr_abs_mean"].max() + 0.005)
    for b, v in zip(bars, full_rows["fdr_abs_mean"]):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + 0.0012,
            f"{v:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    savefig(fig, "fig4_11_mean_abs_fdr_compare")

    print(f"saved to {OUT}")


if __name__ == "__main__":
    main()
