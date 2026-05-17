# 结果与分析章节草稿（方向B）

## 1. 研究问题
在统一口径下比较 FT、MEMIT、ROME 的连续编辑公平性漂移，并验证重复实验与扩展实验下结论是否稳定。

## 2. 统一设置
### 2.1 Sample 口径
- 模型：`gpt2`
- 评测：CrowS 300 + BBQ 300
- 编辑集：`edits_bias_stress_60.json`
- 轮次：`rounds=10, step=6`
- 模式：`sequential_edit=True`

### 2.2 Full 口径（新增）
- 模型：`gpt2`
- 评测：`crows_pairs_full.jsonl + bbq_full.jsonl`
- 编辑集：`edits_bias_stress_120.json`
- 轮次：`rounds=10, step=12`

## 3. 公平性漂移结果（Risk / CDA）
### 3.1 Sample
- FT-R1：`0.6850 -> 0.6683`，`CDA=0.0`
- FT-R2：`0.6850 -> 0.6683`，`CDA=0.0`
- MEMIT-R1：`0.6850 -> 0.6767`，`CDA=0.0200`
- MEMIT-R2：`0.6850 -> 0.6717`，`CDA=0.0050`
- MEMIT-R3（shuffle）：`results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260325_r3_shuffle`
- ROME-R1：`0.6850 -> 0.6067`，`CDA=0.0`
- ROME-R2：`0.6850 -> 0.6067`，`CDA=0.0`

### 3.2 Full（已完成部分）
- FT-full：`0.6697 -> 0.6174`，`delta=-0.0523`，`CDA=0.0`
- ROME-full：`0.6705 -> 0.5747`，`delta=-0.0958`，`CDA=0.0`
- MEMIT-full：进行中

## 4. 编辑成功率（ESR）
定义：每轮 ESR = 该轮 `post.rewrite_acc` 的均值。

汇总入口：
- `results/edit_success_summary.md`
- `results/edit_success_summary.csv`
- `results/method_run_stats.md`

## 5. 综合解读
1. 三方法都出现轮次动态漂移（`FDR` 非单调）。
2. 在 sample 与 full 两种口径下，ROME 均显示更大的风险下降幅度。
3. FT/ROME 重复一致性较高；MEMIT 方向一致但幅度波动更明显。
4. ESR 显示方法在“编辑注入能力”上有差异，需与公平性指标联合解读。

## 6. 小结
通过 sample + full 的双口径设计，实验部分形成“可复现 + 可扩展”的证据链，为后续论文结论与应用化流程提供支持。
