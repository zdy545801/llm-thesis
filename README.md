# LLM Thesis: Fairness Drift in Sequential Knowledge Editing

This repository contains the code, experiment notebooks, data files, and result artifacts for a graduation thesis on **fairness drift in sequential knowledge editing of large language models**.

## Project Focus

The thesis studies whether fairness risk changes when a language model is edited repeatedly. It compares three representative knowledge editing methods:

- **FT**: direct fine-tuning / global parameter update
- **ROME**: local rank-one model editing
- **MEMIT**: mass editing memory for multi-fact updates

The main analysis uses GPT-2, CrowS-Pairs, BBQ, and a bias-stress edit set to measure dynamic fairness risk across multiple edit rounds.

## Repository Layout

- `data/`: edit sets and fairness evaluation data used in the experiments
- `hparams_custom/`: local EasyEdit hparams used for FT, ROME, MEMIT, and MEND
- `ipynb/`: Colab notebooks for running sample/full experiments and mechanism probes
- `scripts/`: experiment, evaluation, plotting, drift metric, and probe scripts
- `results/`: experiment outputs, drift metrics, method summaries, and thesis figures
- `mechanism_probe_outputs/`: supplementary probe outputs for parameter update norms and output-distribution changes
- `paper_initial/`, `paper_final/`: literature/reference materials used during thesis writing
- `3.16/`, `3.18/`, `3.19/`, `3.20/`: experiment logs and writing notes

## Key Metrics

- `Risk_t`: combined fairness risk at edit round `t`
- `FDR_t = Risk_t - Risk_{t-1}`: round-to-round fairness drift rate
- `CDA`: cumulative drift area above the initial baseline
- `ESR`: edit success rate, based on `post.rewrite_acc`

## Notes

Large local runtime folders such as `.venv/` and temporary presentation/document assets are intentionally ignored. EasyEdit and RippleEdits are kept as repository links from the original working setup rather than vendoring their full source trees.

