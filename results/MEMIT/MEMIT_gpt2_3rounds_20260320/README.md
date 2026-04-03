# MEMIT 结果索引

## 目录用途
用于存放 MEMIT 方法的所有实验结果，避免和 FT/MEND 混放。

## 推荐执行入口
- Colab 统一入口：`COLAB_MEMIT_GPT2_FT_COMPARE_R1.ipynb`（当前保留版本）

## 推荐归档命名
- `MEMIT_stress_10rounds_YYYYMMDD`
- `MEMIT_minimal_2rounds_YYYYMMDD`

每个实验目录建议至少包含：
- `round_0.json` ~ `round_N.json`
- `drift_metrics.json`
- `drift_curve.png`
- `run_note.md`（记录当次参数与异常）
