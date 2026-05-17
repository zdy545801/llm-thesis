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
- `thesis_final_clean.docx`: final thesis document snapshot
- `requirements.txt`: Python dependencies for local reproduction
- `REPRODUCE.md`: step-by-step reproduction commands
- `EXTERNAL_DEPENDENCIES.md`: EasyEdit setup and compatibility notes

## Key Metrics

- `Risk_t`: combined fairness risk at edit round `t`
- `FDR_t = Risk_t - Risk_{t-1}`: round-to-round fairness drift rate
- `CDA`: cumulative drift area above the initial baseline
- `ESR`: edit success rate, based on `post.rewrite_acc`

## Notes

Large local runtime folders, writing notes, temporary presentation/document assets, cached Python files, reference PDFs, and local external code checkouts are intentionally ignored.

This repository does not vendor the full EasyEdit or RippleEdits source trees. To rerun editing experiments, install or clone EasyEdit separately, then point the notebooks/scripts to that local EasyEdit checkout.

For a clean reproduction workflow, start with `REPRODUCE.md`.
