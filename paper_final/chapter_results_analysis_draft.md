# 结果与分析章节草稿（方向B）

## 1. 研究问题
在统一口径下比较 FT、MEMIT、ROME 的连续编辑公平性漂移，并验证重复实验与扰动实验下结论是否稳定。

## 2. 统一设置
- 模型：`gpt2`
- 评测：CrowS 300 + BBQ 300
- 编辑集：`edits_bias_stress_60.json`
- 轮次：`rounds=10, step=6`
- 模式：`sequential_edit=True`

## 3. 公平性漂移结果（Risk / CDA）
- FT-R1：`0.685 -> 0.6683`，`CDA=0.0`
- FT-R2：`0.685 -> 0.6683`，`CDA=0.0`
- MEMIT-R1：`0.685 -> 0.6767`，`CDA=0.0200`
- MEMIT-R2：`0.685 -> 0.6717`，`CDA=0.0050`
- MEMIT-R3（shuffle）：见 `results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260325_r3_shuffle/drift_metrics.json`
- ROME-R1：`0.685 -> 0.6067`，`CDA=0.0`
- ROME-R2：`0.685 -> 0.6067`，`CDA=0.0`

## 4. 编辑成功率（ESR）
定义：每轮 ESR = 该轮 `post.rewrite_acc` 的均值。

汇总结果（`esr_first / esr_last / esr_mean`）：
- FT-R1：`0.7500 / 0.5639 / 0.6439`
- FT-R2：`0.7500 / 0.5639 / 0.6439`
- MEMIT-R1：`1.0000 / 0.9083 / 0.9343`
- MEMIT-R2：`0.9167 / 0.9056 / 0.8796`
- MEMIT-R3（shuffle）：`0.8889 / 0.8514 / 0.8705`
- ROME-R1：`0.8333 / 0.5722 / 0.5433`
- ROME-R2：`0.8333 / 0.5722 / 0.5433`

原始导出：
- `results/edit_success_summary.md`
- `results/edit_success_summary.csv`

## 5. 综合解读
1. 三方法都出现轮次动态漂移（`FDR` 非单调）。
2. 当前设置下 ROME 风险下降幅度最大。
3. FT/ROME 重复一致性较高；MEMIT 方向一致但幅度波动更明显。
4. ESR 显示 MEMIT 编辑注入能力较强，但公平性表现仍需结合漂移指标一起解读。

## 6. 小结
加入 ESR 后，实验部分形成“双指标闭环”：既能评估公平性漂移，也能证明编辑任务本身是否成功。
