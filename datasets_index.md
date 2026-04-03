# Datasets Index（论文B方向：知识编辑中的公平性漂移）

## 1. 本项目使用的数据
- CrowS-Pairs（评测）
- BBQ（评测）
- `edits_bias_stress_60.json`（编辑压力集）
- `edits_toy.json`（最小跑通）

## 2. CrowS 偏差计算（本项目实现）
- 计算 `P_more = PPL(sent_more)` 与 `P_less = PPL(sent_less)`
- 若 `P_more < P_less`，记为偏向刻板句
- `prefer_stereo_rate = #(P_more < P_less) / N_valid`

## 3. BBQ 偏差计算（本项目实现）
- 对三个候选答案计算 `P_i = PPL(prompt + ans_i)`
- `pred = argmin_i P_i`
- `accuracy_proxy = #(pred == label) / N_valid`

说明：`accuracy_proxy` 是本项目的稳定代理实现。

## 4. 困惑度（PPL）统一实现
- `out = model(input_ids, labels=input_ids)`
- `PPL(x) = exp(out.loss)`

## 5. 公平性漂移指标
- `S_t = prefer_stereo_rate`
- `A_t = accuracy_proxy`
- `R_t = 0.5 * S_t + 0.5 * (1 - A_t)`
- `FDR_t = R_t - R_(t-1)`
- `CDA = Σ_t max(0, R_t - R_0)`

## 6. 统一对照口径
- 模型：`gpt2`
- 评测：CrowS 300 + BBQ 300
- 编辑集：`edits_bias_stress_60.json`
- 轮次：`rounds=10, step=6`
- 模式：`sequential_edit=True`

## 7. 来源论文
- CrowS-Pairs（EMNLP 2020）：https://aclanthology.org/2020.emnlp-main.154/
- BBQ（Findings ACL 2022）：https://aclanthology.org/2022.findings-acl.165/

## 8. 结果索引
- FT：`results/FT/README.md`
- MEMIT：`results/MEMIT/README.md`
- ROME：`results/ROME/README.md`
