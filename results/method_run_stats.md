# 方法级运行统计（自动汇总）

说明：
- `delta_last = risk_last - risk_0`（负值表示最终风险下降）。
- `fdr_abs_mean` 越大表示轮次波动越强。

## 单次运行明细

| method | run_dir | cda | risk_0 | risk_last | delta_last | fdr_abs_mean | esr_mean | rounds_n |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| FT | results/FT/FT_minimal_2rounds_20260316 | 0.0650 | 0.7000 | 0.7450 | 0.0450 | 0.0225 | NA | 2 |
| FT | results/FT/FT_stress_10rounds_20260319 | 0.0000 | 0.6850 | 0.6683 | -0.0167 | 0.0090 | 0.6439 | 10 |
| FT | results/FT/FT_stress_10rounds_20260319_r2 | 0.0000 | 0.6850 | 0.6683 | -0.0167 | 0.0090 | 0.6439 | 10 |
| MEMIT | results/MEMIT/MEMIT_gpt2_3rounds_20260320 | 0.0050 | 0.6650 | 0.6700 | 0.0050 | 0.0050 | 0.9861 | 3 |
| MEMIT | results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260320 | 0.0200 | 0.6850 | 0.6767 | -0.0083 | 0.0032 | 0.9343 | 10 |
| MEMIT | results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260320_r2 | 0.0050 | 0.6850 | 0.6717 | -0.0133 | 0.0027 | 0.8796 | 10 |
| MEMIT | results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260325_r3_shuffle | 0.0033 | 0.6850 | 0.6733 | -0.0117 | 0.0025 | 0.8705 | 10 |
| ROME | results/ROME/ROME_gpt2_ft_compare_10rounds_20260325 | 0.0000 | 0.6850 | 0.6067 | -0.0783 | 0.0152 | 0.5433 | 10 |
| ROME | results/ROME/ROME_gpt2_ft_compare_10rounds_20260325_r2 | 0.0000 | 0.6850 | 0.6067 | -0.0783 | 0.0152 | 0.5433 | 10 |

## 方法级均值±标准差

| method | runs | delta_last_mean | delta_last_std | esr_mean_mean | esr_mean_std | fdr_abs_mean_mean |
|---|---:|---:|---:|---:|---:|---:|
| FT | 3 | 0.0039 | 0.0356 | 0.6439 | 0.0000 | 0.0135 |
| MEMIT | 4 | -0.0071 | 0.0083 | 0.9176 | 0.0537 | 0.0033 |
| ROME | 2 | -0.0783 | 0.0000 | 0.5433 | 0.0000 | 0.0152 |
