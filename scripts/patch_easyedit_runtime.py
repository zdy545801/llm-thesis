"""Patch a local EasyEdit checkout for the thesis reproduction workflow.

The notebooks used small compatibility patches for newer PyTorch / Transformers
and for reducing EasyEdit import chains. This script applies those patches to a
local EasyEdit checkout when needed.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_if_present(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        return False
    path.write_text(text.replace(old, new), encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--easyedit_dir", required=True, help="Path to local EasyEdit checkout")
    args = parser.parse_args()

    root = Path(args.easyedit_dir).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(root)

    easyeditor = root / "easyeditor"
    if not easyeditor.exists():
        raise FileNotFoundError(f"Cannot find easyeditor package under {root}")

    changed = []

    # nethook compatibility for PyTorch hook signature changes.
    nethook_py = easyeditor / "util" / "nethook.py"
    if nethook_py.exists():
        if replace_if_present(
            nethook_py,
            "def retain_hook(m, inputs, output, kwargs=None):",
            "def retain_hook(m, inputs, kwargs, output):",
        ):
            changed.append(str(nethook_py))
        if replace_if_present(
            nethook_py,
            """            def legacy_hook(m, inputs, output):\n                return retain_hook(m, inputs, output, kwargs=None)\n""",
            """            def legacy_hook(m, inputs, output):\n                return retain_hook(m, inputs, None, output)\n""",
        ):
            changed.append(str(nethook_py))

    # Keep imports focused on algorithms used in this thesis.
    init_py = easyeditor / "__init__.py"
    if init_py.exists():
        init_py.write_text(
            "from .editors.editor import BaseEditor\n"
            "from .models.ft.ft_hparams import FTHyperParams\n"
            "from .models.rome.rome_hparams import ROMEHyperParams\n"
            "from .models.memit.memit_hparams import MEMITHyperParams\n"
            "from .models.mend.mend_hparams import MENDHyperParams\n"
            "from .models.grace.grace_hparams import GraceHyperParams\n"
            "from .models.wise.wise_hparams import WISEHyperParams\n",
            encoding="utf-8",
        )
        changed.append(str(init_py))

    alg_dict_py = easyeditor / "util" / "alg_dict.py"
    if alg_dict_py.exists():
        alg_dict_py.write_text(
            "from ..models.rome import apply_rome_to_model\n"
            "from ..models.memit import apply_memit_to_model\n"
            "from ..models.mend import MendRewriteExecutor\n"
            "from ..models.ft import apply_ft_to_model\n"
            "from ..models.grace import apply_grace_to_model\n"
            "from ..models.wise import apply_wise_to_model\n\n"
            "ALG_DICT = {\n"
            "    'ROME': apply_rome_to_model,\n"
            "    'MEMIT': apply_memit_to_model,\n"
            "    'MEND': MendRewriteExecutor().apply_to_model,\n"
            "    'FT': apply_ft_to_model,\n"
            "    'GRACE': apply_grace_to_model,\n"
            "    'WISE': apply_wise_to_model,\n"
            "}\n\n"
            "ALG_MULTIMODAL_DICT = {}\n"
            "PER_ALG_DICT = {}\n"
            "DS_DICT = {}\n"
            "MULTIMODAL_DS_DICT = {}\n"
            "PER_DS_DICT = {}\n"
            "Safety_DS_DICT = {}\n",
            encoding="utf-8",
        )
        changed.append(str(alg_dict_py))

    models_init = easyeditor / "models" / "__init__.py"
    if models_init.exists():
        models_init.write_text(
            "from .ft import *\n"
            "from .rome import *\n"
            "from .memit import *\n"
            "from .mend import *\n"
            "from .grace import *\n"
            "from .wise import *\n",
            encoding="utf-8",
        )
        changed.append(str(models_init))

    editor_py = easyeditor / "editors" / "editor.py"
    if editor_py.exists():
        if replace_if_present(editor_py, "from ..models.melo.melo import LORA", "LORA = None  # patched: disable melo import"):
            changed.append(str(editor_py))
        if replace_if_present(editor_py, "if isinstance(edited_model, LORA):", "if (LORA is not None) and isinstance(edited_model, LORA):"):
            changed.append(str(editor_py))

    # MEMIT dict-output compatibility patch.
    compute_z_py = easyeditor / "models" / "memit" / "compute_z.py"
    if compute_z_py.exists():
        old = """        loss_layer_out = tr[hparams.layer_module_tmp.format(loss_layer)].output\n        if isinstance(loss_layer_out, (list, tuple)):\n            output = loss_layer_out[0]\n        else:\n            output = loss_layer_out\n"""
        new = """        loss_layer_out = tr[hparams.layer_module_tmp.format(loss_layer)].output\n        if isinstance(loss_layer_out, (list, tuple)):\n            output = loss_layer_out[0]\n        elif isinstance(loss_layer_out, dict):\n            output = None\n            for k in ('hidden_states', 'last_hidden_state', 'output'):\n                v = loss_layer_out.get(k, None)\n                if isinstance(v, torch.Tensor):\n                    output = v\n                    break\n                if isinstance(v, (list, tuple)) and len(v) > 0 and isinstance(v[0], torch.Tensor):\n                    output = v[0]\n                    break\n            if output is None:\n                for _, v in loss_layer_out.items():\n                    if isinstance(v, torch.Tensor):\n                        output = v\n                        break\n            if output is None:\n                raise TypeError(f'Unsupported dict output at loss layer: {list(loss_layer_out.keys())[:10]}')\n        else:\n            output = loss_layer_out\n"""
        if replace_if_present(compute_z_py, old, new):
            changed.append(str(compute_z_py))

    print("Patched EasyEdit files:")
    if changed:
        for item in sorted(set(changed)):
            print("-", item)
    else:
        print("- no changes needed")


if __name__ == "__main__":
    main()
