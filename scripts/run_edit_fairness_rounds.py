import argparse
import json
from pathlib import Path

import torch
import yaml
from transformers import AutoTokenizer

from run_fairness_eval import eval_bbq, eval_crows, read_jsonl


def load_hparams_class(alg_name: str):
    # Lazy import to avoid requiring EasyEdit for unrelated scripts.
    from easyeditor import (  # type: ignore
        GraceHyperParams,
        MEMITHyperParams,
        MENDHyperParams,
        ROMEHyperParams,
        WISEHyperParams,
    )

    mapping = {
        "WISE": WISEHyperParams,
        "MEMIT": MEMITHyperParams,
        "ROME": ROMEHyperParams,
        "MEND": MENDHyperParams,
        "GRACE": GraceHyperParams,
    }
    if alg_name not in mapping:
        raise ValueError(f"Unsupported alg_name={alg_name}. Supported: {list(mapping.keys())}")
    return mapping[alg_name]


def load_edits(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    prompts = [x["src"] for x in data]
    rephrase_prompts = [x.get("rephrase", x["src"]) for x in data]
    target_new = [x["alt"] for x in data]
    subjects = []
    for x in data:
        s = x.get("subject")
        if s:
            subjects.append(s)
            continue
        # Heuristic fallback for toy prompts like "The capital of France is"
        src = x["src"].strip().rstrip("?")
        if " of " in src and " is" in src:
            tmp = src.split(" of ", 1)[1]
            s = tmp.split(" is", 1)[0].strip()
        else:
            s = src.split(" is", 1)[0].strip()
        subjects.append(s)
    locality_prompts = [x.get("loc", x["src"]) for x in data]
    locality_ans = [x.get("loc_ans", "") for x in data]
    return prompts, rephrase_prompts, target_new, subjects, locality_prompts, locality_ans


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hparams", type=str, required=True, help="EasyEdit YAML hparams path")
    parser.add_argument("--edits_json", type=str, required=True, help="Edit set JSON (e.g., zsre style)")
    parser.add_argument("--crows", type=str, required=True)
    parser.add_argument("--bbq", type=str, required=True)
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument("--step", type=int, default=1, help="New edits added per round")
    parser.add_argument("--start_round", type=int, default=0, help="For resuming runs")
    parser.add_argument("--out_dir", type=str, default="results/rounds")
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError(
            "EasyEdit in this repo requires CUDA for editing. No GPU detected. "
            "Use a CUDA machine, or run only fairness baseline scripts."
        )

    # Imports that require EasyEdit installed
    from easyeditor import BaseEditor  # type: ignore

    hparams_path = Path(args.hparams)
    with hparams_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    alg_name = cfg.get("alg_name")
    if alg_name is None:
        raise ValueError("hparams yaml must contain `alg_name`")

    HParamsCls = load_hparams_class(alg_name)
    hparams = HParamsCls.from_hparams(str(hparams_path))

    prompts, rephrase_prompts, target_new, subjects, locality_prompts, locality_ans = load_edits(Path(args.edits_json))
    crows_rows = read_jsonl(Path(args.crows))
    bbq_rows = read_jsonl(Path(args.bbq))

    model_name_for_tokenizer = getattr(hparams, "model_name", None) or getattr(
        hparams, "model_name_or_path", None
    )
    if not model_name_for_tokenizer:
        raise ValueError("Cannot find model_name in hparams.")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # round_0 = unedited baseline (keep format consistent with run_fairness_eval.py output)
    tok = AutoTokenizer.from_pretrained(model_name_for_tokenizer)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    if args.start_round <= 0:
        baseline_editor = BaseEditor.from_hparams(hparams)
        base_model = baseline_editor.model
        base_model.eval()
        result0 = {
            "model": model_name_for_tokenizer,
            "device": str(getattr(base_model, "device", "unknown")),
            "round": 0,
            "edited_items": 0,
            "crows": eval_crows(base_model, tok, crows_rows, str(base_model.device)),
            "bbq": eval_bbq(base_model, tok, bbq_rows, str(base_model.device)),
        }
        (out_dir / "round_0.json").write_text(
            json.dumps(result0, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("saved:", out_dir / "round_0.json")

    total_edits = len(prompts)
    for r in range(max(1, args.start_round), args.rounds + 1):
        k = min(r * args.step, total_edits)
        print(f"[Round {r}] cumulative edits={k}")

        loc_inputs = {
            "neighborhood": {
                "prompt": locality_prompts[:k],
                "ground_truth": locality_ans[:k],
            }
        }

        editor = BaseEditor.from_hparams(hparams)
        metrics, edited_model, _ = editor.edit(
            prompts=prompts[:k],
            rephrase_prompts=rephrase_prompts[:k],
            target_new=target_new[:k],
            subject=subjects[:k],
            locality_inputs=loc_inputs,
            sequential_edit=True,
        )
        edited_model.eval()

        result = {
            "model": model_name_for_tokenizer,
            "device": str(getattr(edited_model, "device", "unknown")),
            "round": r,
            "edited_items": k,
            "edit_metrics": metrics,
            "crows": eval_crows(edited_model, tok, crows_rows, str(edited_model.device)),
            "bbq": eval_bbq(edited_model, tok, bbq_rows, str(edited_model.device)),
        }

        out_file = out_dir / f"round_{r}.json"
        out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print("saved:", out_file)


if __name__ == "__main__":
    main()
