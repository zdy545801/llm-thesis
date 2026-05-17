# External Dependencies

This repository keeps thesis-specific code, data, notebooks, and results only. It does not vendor large external editing frameworks.

## EasyEdit

The editing experiments use EasyEdit as the backend for FT, ROME, MEMIT, and MEND-style editing APIs.

Recommended setup:

```bash
git clone https://github.com/zjunlp/EasyEdit.git
cd EasyEdit
git checkout 41937637c2171b9cf1f929c143231d45a79f7787
pip install -r requirements.txt
pip install -e .
```

Then return to this repository and make EasyEdit importable:

```bash
export PYTHONPATH=/path/to/EasyEdit:$PYTHONPATH
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH="D:\path\to\EasyEdit;$env:PYTHONPATH"
```

For local reproduction with the provided PowerShell helper, clone EasyEdit into the repository root as `EasyEdit/`. The directory is ignored by Git.

## Compatibility Patch

Some Colab runs used small EasyEdit compatibility patches for newer PyTorch / Transformers versions. If EasyEdit import or MEMIT tracing fails, run:

```bash
python scripts/patch_easyedit_runtime.py --easyedit_dir /path/to/EasyEdit
```

This patch only adjusts local EasyEdit files in your environment. It does not modify this thesis repository.

## Model Downloads

The scripts download Hugging Face models such as `gpt2` or `gpt2-xl` on first use. Make sure your environment has internet access and enough disk space.

## Hardware

- Fairness baseline evaluation can run on CPU, but GPU is recommended.
- EasyEdit-based FT / ROME / MEMIT runs require CUDA in the provided scripts.
- Full runs are slower and may require Colab GPU or a local NVIDIA GPU.
