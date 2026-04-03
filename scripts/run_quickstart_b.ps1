$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install torch transformers accelerate sentencepiece pyyaml tqdm pandas numpy requests

if (-not (Test-Path ".\\data\\crows_pairs_sample.jsonl")) {
  python .\scripts\download_fairness_datasets.py --out_dir .\data --crows_n 200 --bbq_n 300
}

python .\scripts\run_fairness_eval.py `
  --model_name gpt2 `
  --crows .\data\crows_pairs_sample.jsonl `
  --bbq .\data\bbq_sample.jsonl `
  --out .\results\baseline_gpt2.json

Write-Host "Done. Result -> .\\results\\baseline_gpt2.json"

