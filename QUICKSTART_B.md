# QUICKSTART B（当前执行版）

## 1. 目标
快速复现“连续知识编辑中的公平性漂移”主线实验，并输出：
- `round_*.json`
- `drift_metrics.json`
- `drift_curve.png`

## 2. Notebook 入口（已规整）
- FT：`ipynb/COLAB_FT_R1.ipynb`、`ipynb/COLAB_FT_R2.ipynb`
- MEMIT：`ipynb/COLAB_MEMIT_GPT2_FT_COMPARE_R1.ipynb`、`ipynb/COLAB_MEMIT_GPT2_FT_COMPARE_R2.ipynb`、`ipynb/COLAB_MEMIT_GPT2_FT_COMPARE_R3.ipynb`
- ROME：`ipynb/COLAB_ROME_GPT2_FT_COMPARE_R1.ipynb`、`ipynb/COLAB_ROME_GPT2_FT_COMPARE_R2.ipynb`

## 3. 统一对照口径
- 模型：`gpt2`
- 评测：CrowS 300 + BBQ 300
- 编辑集：`data/edits_bias_stress_60.json`
- 轮次：`rounds=10, step=6`
- 模式：`sequential_edit=True`

## 4. 已归档结果目录
- FT：`results/FT/FT_stress_10rounds_20260319`、`results/FT/FT_stress_10rounds_20260319_r2`
- MEMIT：
  - `results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260320`
  - `results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260320_r2`
  - `results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260325_r3_shuffle`
- ROME：
  - `results/ROME/ROME_gpt2_ft_compare_10rounds_20260325`
  - `results/ROME/ROME_gpt2_ft_compare_10rounds_20260325_r2`

## 5. 最短执行流程
1. 打开对应 notebook。
2. 从第一格顺序执行到最后一格。
3. 下载 zip 结果包。
4. 解压并归档到 `results/<method>/<run_name>/`。

## 6. 常见问题
- 看起来“卡住”：将运行单元改为 `python -u` 或 `Popen` 实时打印。
- OOM：保留 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:64`。
- R2/R3 重跑：务必使用新的 `OUT_DIR`，避免覆盖历史结果。
