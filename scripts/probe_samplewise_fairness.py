import argparse
import json
from pathlib import Path

import torch
import yaml
from transformers import AutoTokenizer

from run_edit_fairness_rounds import load_edits, load_hparams_class
from run_fairness_eval import read_jsonl


def ppl_score(model, tok, text: str, device: str):
    enc = tok(text, return_tensors="pt", truncation=True, max_length=256).to(device)
    with torch.no_grad():
        out = model(**enc, labels=enc["input_ids"])
    return torch.exp(out.loss).item()


def eval_crows_samplewise(model, tok, rows, device: str, limit=None):
    out = []
    use_rows = rows[:limit] if limit else rows
    for idx, r in enumerate(use_rows):
        s_more = r.get("sent_more")
        s_less = r.get("sent_less")
        if not s_more or not s_less:
            continue
        try:
            p_more = ppl_score(model, tok, s_more, device)
            p_less = ppl_score(model, tok, s_less, device)
            out.append(
                {
                    "sample_id": idx,
                    "bias_type": r.get("bias_type"),
                    "stereo_antistereo": r.get("stereo_antistereo"),
                    "p_more": p_more,
                    "p_less": p_less,
                    "prefer_stereo": p_more < p_less,
                    "ppl_gap": p_less - p_more,
                }
            )
        except Exception:
            continue
    return out


def eval_bbq_samplewise(model, tok, rows, device: str, limit=None):
    out = []
    use_rows = rows[:limit] if limit else rows
    for idx, r in enumerate(use_rows):
        ctx = r.get("context", "")
        q = r.get("question", "")
        opts = [r.get("ans0", ""), r.get("ans1", ""), r.get("ans2", "")]
        label = r.get("label")
        if label is None or not q:
            continue
        prompt = f"Context: {ctx}\nQuestion: {q}\nAnswer:"
        try:
            scores = []
            for i, op in enumerate(opts):
                if not op:
                    continue
                scores.append((i, ppl_score(model, tok, f"{prompt} {op}", device)))
            if not scores:
                continue
            pred = min(scores, key=lambda x: x[1])[0]
            out.append(
                {
                    "sample_id": idx,
                    "category": r.get("category"),
                    "label": label,
                    "pred": pred,
                    "correct": pred == label,
                    "scores": {f"ans{i}": s for i, s in scores},
                }
            )
        except Exception:
            continue
    return out


def summarize_crows(rows):
    if not rows:
        return {}
    prefer = sum(1 for x in rows if x["prefer_stereo"])
    mean_gap = sum(x["ppl_gap"] for x in rows) / len(rows)
    return {
        "valid_samples": len(rows),
        "prefer_stereo_rate": prefer / len(rows),
        "mean_ppl_gap": mean_gap,
    }


def summarize_bbq(rows):
    if not rows:
        return {}
    acc = sum(1 for x in rows if x["correct"]) / len(rows)
    return {
        "valid_samples": len(rows),
        "accuracy_proxy": acc,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hparams", type=str, required=True)
    parser.add_argument("--edits_json", type=str, required=True)
    parser.add_argument("--crows", type=str, required=True)
    parser.add_argument("--bbq", type=str, required=True)
    parser.add_argument("--rounds", type=int, nargs="+", required=True)
    parser.add_argument("--step", type=int, default=12)
    parser.add_argument("--crows_limit", type=int, default=300)
    parser.add_argument("--bbq_limit", type=int, default=300)
    parser.add_argument("--out_dir", type=str, required=True)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for EasyEdit probing.")

    from easyeditor import BaseEditor  # type: ignore

    hparams_path = Path(args.hparams)
    cfg = yaml.safe_load(hparams_path.read_text(encoding="utf-8"))
    alg_name = cfg["alg_name"]
    HParamsCls = load_hparams_class(alg_name)
    hparams = HParamsCls.from_hparams(str(hparams_path))

    model_name = cfg.get("model_name")
    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    prompts, rephrase_prompts, target_new, subjects, locality_prompts, locality_ans = load_edits(
        Path(args.edits_json)
    )
    crows_rows = read_jsonl(Path(args.crows))
    bbq_rows = read_jsonl(Path(args.bbq))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    total_edits = len(prompts)

    for r in args.rounds:
        k = min(r * args.step, total_edits)
        print(f"[probe_samplewise_fairness] round={r} cumulative_edits={k}")
        editor = BaseEditor.from_hparams(hparams)

        loc_inputs = {
            "neighborhood": {
                "prompt": locality_prompts[:k],
                "ground_truth": locality_ans[:k],
            }
        }

        _, edited_model, _ = editor.edit(
            prompts=prompts[:k],
            rephrase_prompts=rephrase_prompts[:k],
            target_new=target_new[:k],
            subject=subjects[:k],
            locality_inputs=loc_inputs,
            sequential_edit=True,
        )
        edited_model.eval()
        device = str(edited_model.device)

        crows_detail = eval_crows_samplewise(edited_model, tok, crows_rows, device, args.crows_limit)
        bbq_detail = eval_bbq_samplewise(edited_model, tok, bbq_rows, device, args.bbq_limit)

        out = {
            "round": r,
            "edited_items": k,
            "crows_summary": summarize_crows(crows_detail),
            "bbq_summary": summarize_bbq(bbq_detail),
            "crows_detail": crows_detail,
            "bbq_detail": bbq_detail,
        }
        out_path = out_dir / f"round_{r}_samplewise.json"
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print("saved:", out_path)

        del editor
        del edited_model
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
