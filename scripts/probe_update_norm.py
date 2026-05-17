import argparse
import json
from pathlib import Path

import torch
import yaml

from run_edit_fairness_rounds import load_edits, load_hparams_class


def _tensor_l2(x: torch.Tensor) -> float:
    return torch.norm(x.float()).item()


def _collect_layer_norms(base_state, edited_state):
    layer_norms = {}
    for name, base_tensor in base_state.items():
        if name not in edited_state:
            continue
        edited_tensor = edited_state[name]
        if not torch.is_tensor(base_tensor) or not torch.is_tensor(edited_tensor):
            continue
        if base_tensor.shape != edited_tensor.shape:
            continue
        delta = edited_tensor.float() - base_tensor.float()
        delta_norm = torch.norm(delta).item()
        if delta_norm == 0:
            continue
        layer_norms[name] = delta_norm
    return layer_norms


def _top_items(d, k=12):
    return [
        {"name": name, "delta_norm": val}
        for name, val in sorted(d.items(), key=lambda x: x[1], reverse=True)[:k]
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hparams", type=str, required=True)
    parser.add_argument("--edits_json", type=str, required=True)
    parser.add_argument("--rounds", type=int, nargs="+", required=True, help="Specific rounds to probe, e.g. 7 8 9")
    parser.add_argument("--step", type=int, default=12, help="New edits added per round")
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for EasyEdit probing.")

    from easyeditor import BaseEditor  # type: ignore

    hparams_path = Path(args.hparams)
    cfg = yaml.safe_load(hparams_path.read_text(encoding="utf-8"))
    alg_name = cfg["alg_name"]
    HParamsCls = load_hparams_class(alg_name)
    hparams = HParamsCls.from_hparams(str(hparams_path))

    prompts, rephrase_prompts, target_new, subjects, locality_prompts, locality_ans = load_edits(
        Path(args.edits_json)
    )

    total_edits = len(prompts)
    out_rows = []

    for r in args.rounds:
        k = min(r * args.step, total_edits)
        print(f"[probe_update_norm] round={r} cumulative_edits={k}")

        editor = BaseEditor.from_hparams(hparams)
        base_model = editor.model
        base_state = {name: tensor.detach().cpu().clone() for name, tensor in base_model.state_dict().items()}

        loc_inputs = {
            "neighborhood": {
                "prompt": locality_prompts[:k],
                "ground_truth": locality_ans[:k],
            }
        }

        metrics, edited_model, _ = editor.edit(
            prompts=prompts[:k],
            rephrase_prompts=rephrase_prompts[:k],
            target_new=target_new[:k],
            subject=subjects[:k],
            locality_inputs=loc_inputs,
            sequential_edit=True,
        )
        edited_state = {name: tensor.detach().cpu() for name, tensor in edited_model.state_dict().items()}
        layer_norms = _collect_layer_norms(base_state, edited_state)
        global_norm = sum(v * v for v in layer_norms.values()) ** 0.5

        rewrite_vals = []
        for item in metrics:
            post = item.get("post", {})
            val = post.get("rewrite_acc")
            if isinstance(val, list):
                vals = [float(x) for x in val if isinstance(x, (int, float))]
                if vals:
                    rewrite_vals.append(sum(vals) / len(vals))
            elif isinstance(val, (int, float)):
                rewrite_vals.append(float(val))

        out_rows.append(
            {
                "round": r,
                "edited_items": k,
                "global_update_norm": global_norm,
                "num_changed_tensors": len(layer_norms),
                "rewrite_mean": (sum(rewrite_vals) / len(rewrite_vals)) if rewrite_vals else None,
                "top_changed_tensors": _top_items(layer_norms),
            }
        )

        del editor
        del edited_model
        torch.cuda.empty_cache()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved:", out_path)


if __name__ == "__main__":
    main()
