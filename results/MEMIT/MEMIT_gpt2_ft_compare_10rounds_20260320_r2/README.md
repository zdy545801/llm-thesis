# MEMIT GPT2 FT-Compare R2 (2026-03-20)

## Goal
Second run (R2) under FT-comparable settings for repeatability check.

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
- `CDA = 0.005`
- `risk(round0) = 0.685`
- `risk(round10) = 0.6717`
