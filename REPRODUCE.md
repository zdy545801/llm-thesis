# Reproduction Guide

This guide explains how to reproduce the main workflow from a clean clone.

## 1. Clone This Repository

```bash
git clone https://github.com/zdy545801/llm-thesis.git
cd llm-thesis
```

## 2. Create Python Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
```

## 3. Install EasyEdit

The editing backend is EasyEdit. It is intentionally not vendored in this repository.

```bash
git clone https://github.com/zjunlp/EasyEdit.git
cd EasyEdit
git checkout 41937637c2171b9cf1f929c143231d45a79f7787
pip install -r requirements.txt
pip install -e .
cd ..
```

If EasyEdit import or MEMIT tracing fails under your installed package versions, apply the local compatibility patch:

```bash
python scripts/patch_easyedit_runtime.py --easyedit_dir ./EasyEdit
```

## 4. Verify Baseline Fairness Evaluation

This step does not edit the model. It checks that the evaluation scripts, data files, and Hugging Face model loading work.

```bash
python scripts/run_fairness_eval.py \
  --model_name gpt2 \
  --crows data/crows_pairs_sample.jsonl \
  --bbq data/bbq_sample.jsonl \
  --out results/reproduce_baseline_gpt2.json
```

Then compute nothing else yet: just check that `results/reproduce_baseline_gpt2.json` exists.

## 5. Minimal Sequential Editing Run

Use this to test the complete edit-evaluate-drift pipeline on a small toy setting.

```bash
PYTHONPATH=./EasyEdit:$PYTHONPATH python scripts/run_edit_fairness_rounds.py \
  --hparams hparams_custom/FT_gpt2_local.yaml \
  --edits_json data/edits_toy.json \
  --crows data/crows_pairs_sample.jsonl \
  --bbq data/bbq_sample.jsonl \
  --rounds 2 \
  --step 1 \
  --out_dir results/reproduce_minimal_ft/rounds
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH=".\EasyEdit;$env:PYTHONPATH"
python scripts/run_edit_fairness_rounds.py `
  --hparams hparams_custom/FT_gpt2_local.yaml `
  --edits_json data/edits_toy.json `
  --crows data/crows_pairs_sample.jsonl `
  --bbq data/bbq_sample.jsonl `
  --rounds 2 `
  --step 1 `
  --out_dir results/reproduce_minimal_ft/rounds
```

## 6. Compute Drift Metrics and Plot

```bash
python scripts/calc_drift_metrics.py \
  --input_dir results/reproduce_minimal_ft/rounds \
  --pattern "round_*.json" \
  --out results/reproduce_minimal_ft/drift_metrics.json

python scripts/plot_drift.py \
  --metrics_json results/reproduce_minimal_ft/drift_metrics.json \
  --out_png results/reproduce_minimal_ft/drift_curve.png
```

Expected outputs:

- `results/reproduce_minimal_ft/rounds/round_0.json`
- `results/reproduce_minimal_ft/rounds/round_1.json`
- `results/reproduce_minimal_ft/rounds/round_2.json`
- `results/reproduce_minimal_ft/drift_metrics.json`
- `results/reproduce_minimal_ft/drift_curve.png`

## 7. Recreate Thesis Figures from Existing Results

The repository already includes the result JSON files used for the thesis. To regenerate the paper figures:

```bash
python scripts/plot_ch4_thesis_figures.py
python scripts/plot_risk_fdr_drift_style_batch.py
```

Generated figures are written under:

- `results/thesis_figures_ch4/`
- `results/thesis_figures_ch4_drift_style/`

## 8. Recompute Method-Level Summaries

```bash
python scripts/calc_edit_success.py --results_root results
python scripts/summarize_method_runs.py --results_root results
```

## 9. Reproduce Full Experiments

For full experiments, use the Colab notebooks in `ipynb/`:

- `COLAB_FT_GPT2_FULL_EXPANDED.ipynb`
- `COLAB_ROME_GPT2_FULL_EXPANDED.ipynb`
- `COLAB_MEMIT_GPT2_FULL_EXPANDED.ipynb`
- `COLAB_MECHANISM_PROBES_GPT2.ipynb`

These notebooks include Colab-specific setup cells for cloning EasyEdit, patching compatibility issues, running round-by-round editing, computing drift metrics, and downloading outputs.

## Notes on Exact Reproduction

The checked-in `results/` directory contains the experiment outputs used by the thesis. New runs can differ slightly because of GPU type, package versions, EasyEdit version, and stochastic editing/evaluation details. For thesis verification, compare trends and output file structure first, then compare numeric values.
