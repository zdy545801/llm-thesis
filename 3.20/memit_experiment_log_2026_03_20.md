# MEMIT 实验日志（更新版）

## 归档目录
- R1：`results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260320`
- R2：`results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260320_r2`
- R3（shuffle）：`results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260325_r3_shuffle`

## 配置
- 模型：`gpt2`
- 评测：CrowS 300 + BBQ 300
- 编辑集：`edits_bias_stress_60.json`（R3 使用打乱顺序版本）
- 轮次：`rounds=10, step=6`
- 模式：`sequential_edit=True`

## 结果摘要
- R1：`risk 0.685 -> 0.6767`，`CDA=0.0200`
- R2：`risk 0.685 -> 0.6717`，`CDA=0.0050`
- R3：见对应目录 `drift_metrics.json`

## 备注
MEMIT 重复实验方向一致，但幅度存在波动；R3 用于补充稳健性证据。
