# FT 实验日志（更新版）

## 归档目录
- R1：`results/FT/FT_stress_10rounds_20260319`
- R2：`results/FT/FT_stress_10rounds_20260319_r2`

## 配置
- 模型：`gpt2`
- 评测：CrowS 300 + BBQ 300
- 编辑集：`edits_bias_stress_60.json`
- 轮次：`rounds=10, step=6`
- 模式：`sequential_edit=True`

## 结果
- R1：`risk 0.685 -> 0.6683`，`CDA=0.0`
- R2：`risk 0.685 -> 0.6683`，`CDA=0.0`

## 备注
FT 在当前口径下重复实验一致性高。
