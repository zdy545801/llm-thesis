# MEMIT GPT2 FT-Compare (2026-03-20)

## Goal
Method comparison against FT with aligned settings.

## Main Settings
- method: `MEMIT`
- model: `gpt2`
- eval set: `CrowS 300` + `BBQ 300`
- rounds: `10`
- step: `6`
- sequential edit: `True`

## Artifacts
- `rounds/round_0.json` ... `rounds/round_10.json`
- `drift_metrics.json`
- `drift_curve.png`

## Key Result
- `CDA = 0.02`
