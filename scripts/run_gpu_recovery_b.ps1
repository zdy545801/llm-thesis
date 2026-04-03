param(
  [int]$Rounds = 5,
  [int]$Step = 1,
  [int]$StartRound = 0,
  [string]$Hparams = ".\hparams_custom\ROME_gpt2xl_local.yaml",
  [string]$EditsJson = ".\data\edits_toy.json",
  [string]$Crows = ".\data\crows_pairs_sample.jsonl",
  [string]$Bbq = ".\data\bbq_sample.jsonl",
  [string]$OutDir = ".\results\rounds"
)

$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install torch transformers accelerate sentencepiece pyyaml tqdm pandas numpy requests matplotlib

if (-not (Test-Path ".\EasyEdit")) {
  throw "Missing .\EasyEdit. Please clone EasyEdit first."
}

if (-not (Test-Path $Crows) -or -not (Test-Path $Bbq)) {
  python .\scripts\download_fairness_datasets.py --out_dir .\data --crows_n 200 --bbq_n 300
}

if (-not (Test-Path $Hparams)) { throw "Missing hparams: $Hparams" }
if (-not (Test-Path $EditsJson)) { throw "Missing edits json: $EditsJson" }
if (-not (Test-Path $Crows)) { throw "Missing crows file: $Crows" }
if (-not (Test-Path $Bbq)) { throw "Missing bbq file: $Bbq" }

Write-Host "Checking GPU..."
nvidia-smi

python -c "import torch; print('torch.cuda.is_available=', torch.cuda.is_available()); print('device_count=', torch.cuda.device_count())"

Write-Host "Checking easyeditor import..."
python -c "import easyeditor; print('easyeditor import ok')" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Installing EasyEdit into current venv..."
  Push-Location .\EasyEdit
  pip install -r requirements.txt
  pip install -e .
  Pop-Location
}

Write-Host "Running sequential edit rounds..."
python .\scripts\run_edit_fairness_rounds.py `
  --hparams $Hparams `
  --edits_json $EditsJson `
  --crows $Crows `
  --bbq $Bbq `
  --rounds $Rounds `
  --step $Step `
  --start_round $StartRound `
  --out_dir $OutDir

Write-Host "Calculating drift metrics..."
python .\scripts\calc_drift_metrics.py `
  --input_dir $OutDir `
  --pattern "round_*.json" `
  --out .\results\drift_metrics.json

Write-Host "Plotting drift curve..."
python .\scripts\plot_drift.py `
  --metrics_json .\results\drift_metrics.json `
  --out_png .\results\drift_curve.png

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$snapshotDir = ".\results\snapshots\$timestamp"
New-Item -ItemType Directory -Force $snapshotDir | Out-Null
Copy-Item $OutDir $snapshotDir -Recurse -Force
Copy-Item .\results\drift_metrics.json $snapshotDir -Force
Copy-Item .\results\drift_curve.png $snapshotDir -Force

Write-Host ""
Write-Host "Done."
Write-Host "Rounds dir: $OutDir"
Write-Host "Drift metrics: .\results\drift_metrics.json"
Write-Host "Drift plot: .\results\drift_curve.png"
Write-Host "Snapshot: $snapshotDir"
