import argparse
import json
from pathlib import Path

# Requires: pip install -e EasyEdit
from easyeditor import BaseEditor, WISEHyperParams  # type: ignore


def load_edits(path: Path, k: int):
    data = json.loads(path.read_text(encoding="utf-8"))
    data = data[:k]
    prompts = [x["src"] for x in data]
    rephrase = [x["rephrase"] for x in data]
    target_new = [x["alt"] for x in data]
    locality_prompts = [x["loc"] for x in data]
    locality_ans = [x["loc_ans"] for x in data]
    return prompts, rephrase, target_new, locality_prompts, locality_ans


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hparams", type=str, required=True)
    parser.add_argument("--edit_json", type=str, required=True)
    parser.add_argument("--k", type=int, default=20)
    parser.add_argument("--out", type=str, default="results/easyedit_sequential_metrics.json")
    args = parser.parse_args()

    prompts, rephrase, target_new, locality_prompts, locality_ans = load_edits(Path(args.edit_json), args.k)
    locality_inputs = {
        "neighborhood": {
            "prompt": locality_prompts,
            "ground_truth": locality_ans,
        }
    }

    hparams = WISEHyperParams.from_hparams(args.hparams)
    editor = BaseEditor.from_hparams(hparams)
    metrics, edited_model, _ = editor.edit(
        prompts=prompts,
        rephrase_prompts=rephrase,
        target_new=target_new,
        locality_inputs=locality_inputs,
        sequential_edit=True,
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved:", out)


if __name__ == "__main__":
    main()

