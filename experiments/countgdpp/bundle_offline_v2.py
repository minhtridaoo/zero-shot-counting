"""Prepare aligned saved P1 controls and optional T exports; reuse CLIP, no inference."""
import argparse
import json
from pathlib import Path

import numpy as np

from offline_text_v2 import read_rows, sha


def build(controls, additions):
    cfg = json.loads((controls / "run_config.json").read_text(encoding="utf-8"))
    if cfg["runner"] != "p1_controls.py":
        raise ValueError("Expected saved P1 controls")
    kept = json.loads((controls / "kept_boxes.json").read_text(encoding="utf-8"))
    predictions = {r["query_id"]: r for r in read_rows(controls / "sources_predictions.jsonl")}
    sources = {}
    for name in cfg["sources"]:
        rows = []
        for q, boxes in kept[name].items():
            pred = predictions[name.replace('.', 'p') + "__" + q]
            if [b["box_xyxy"] for b in boxes] != pred["final_boxes"] or [b["countgd_score"] for b in boxes] != pred["final_scores"]:
                raise ValueError("Saved controls do not align with source predictions")
            rows.append(dict(query_id=q, image_id=pred["image_id"], boxes=pred["final_boxes"],
                             scores=pred["final_scores"], clip=[b["clip_cosine_target"] for b in boxes]))
        sources[name] = rows
    provenance = {str(controls / n): sha(controls / n) for n in ("run_config.json", "kept_boxes.json", "sources_predictions.jsonl")}
    for name, original, path in additions:
        if name in sources or original not in sources:
            raise ValueError("Duplicate new source or missing original source")
        tc = json.loads((path.parent / "run_config.json").read_text(encoding="utf-8"))
        expected = cfg["prediction_sha256"].get("predictions_" + original + ".jsonl")
        if tc.get("tool") != "offline_text_v2.py" or not tc.get("original_replay_verified") or tc["source_sha256"] != expected or tc.get("predictions_sha256") != sha(path):
            raise ValueError("T export is not from the same P1 prediction file")
        base = {r["query_id"]: r for r in sources[original]}
        rows = read_rows(path)
        if {r["query_id"] for r in rows} != set(base):
            raise ValueError("T query set differs")
        new = []
        for r in rows:
            b = base[r["query_id"]]
            indices = [i-1 for i in r["original_ranks"]]
            if len(set(indices)) != len(indices) or any(i < 0 or i >= len(b["boxes"]) for i in indices):
                raise ValueError("Invalid original box ranks")
            if r["image_id"] != b["image_id"] or len(indices) != r["final_count"] or len(indices) != len(r["final_scores"]):
                raise ValueError("T metadata mismatch")
            np.testing.assert_allclose(np.array(r["final_boxes"]).reshape(-1, 4), np.array([b["boxes"][i] for i in indices]).reshape(-1, 4), atol=.001, rtol=0)
            # Reuse the exact original coordinates, hence the exact same CLIP crop.
            new.append(dict(query_id=r["query_id"], image_id=r["image_id"], boxes=[b["boxes"][i] for i in indices],
                            scores=r["final_scores"], clip=[b["clip"][i] for i in indices]))
        sources[name] = new
        provenance[str(path)] = sha(path)
        provenance[str(path.parent / "run_config.json")] = sha(path.parent / "run_config.json")
    return dict(run_id=cfg["p1_run"], sources=sources, input_sha256=provenance, tool_sha256=sha(__file__))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--controls", type=Path, required=True)
    ap.add_argument("--text-source", nargs=3, action="append", default=[], metavar=("NAME", "ORIGINAL", "PREDICTIONS"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise ValueError("Output exists")
    result = build(args.controls, [(n, o, Path(p)) for n, o, p in args.text_source])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as f:
        json.dump(result, f, allow_nan=False)
        f.write("\n")


if __name__ == "__main__":
    main()
