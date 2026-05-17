# 结果与分析章节草稿（方向B）

## 1. 研究问题
在统一口径下比较 FT、MEMIT、ROME 的连续编辑公平性漂移，并验证结果是否偶然。

## 2. 实验设置（两套口径）
### 2.1 Sample 口径
- 模型：`gpt2`
- 评测：CrowS 300 + BBQ 300
- 编辑：`edits_bias_stress_60.json`
- 轮次：`rounds=10, step=6`
- 模式：`sequential_edit=True`

### 2.2 Full 口径
- 模型：`gpt2`
- 评测：`crows_pairs_full.jsonl + bbq_full.jsonl`
- 编辑：`edits_bias_stress_120.json`
- 轮次：`rounds=10, step=12`

指标：
- `R_t`：公平性风险
- `FDR_t = R_t - R_(t-1)`
- `CDA = Σ_t max(0, R_t - R_0)`

## 3. Sample 结果
### FT
- R1：`0.6850 -> 0.6683`，`CDA=0.0`
- R2：`0.6850 -> 0.6683`，`CDA=0.0`

### MEMIT
- R1：`0.6850 -> 0.6767`，`CDA=0.0200`
- R2：`0.6850 -> 0.6717`，`CDA=0.0050`
- R3（shuffle）：见 `results/MEMIT/MEMIT_gpt2_ft_compare_10rounds_20260325_r3_shuffle`

### ROME
- R1：`0.6850 -> 0.6067`，`CDA=0.0`
- R2：`0.6850 -> 0.6067`，`CDA=0.0`

## 4. Full 结果（新增）
- FT-full：`0.6697 -> 0.6174`，`delta=-0.0523`，`CDA=0.0`
- ROME-full：`0.6705 -> 0.5747`，`delta=-0.0958`，`CDA=0.0`
- MEMIT-full：进行中

## 5. 编辑成功率（ESR）
定义：每轮 ESR = 该轮 `post.rewrite_acc` 的均值。
- 自动汇总：`results/edit_success_summary.md`
- 方法汇总：`results/method_run_stats.md`

## 6. 综合解读
1. 三方法都存在轮次动态漂移（FDR 非单调）。
2. ROME 在 sample 与 full 口径下均表现出更大风险下降幅度。
3. FT/ROME 重复一致性较高；MEMIT 方向一致但幅度波动更明显。
4. ESR 需要和漂移指标联合解释，避免只看“编辑成功”而忽略“公平性变化”。
