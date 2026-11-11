"""CPU-only T/P+T export. No GT, model, or changes to source artifacts."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_rows(path):
    rows = [json.loads(s) for s in Path(path).read_text(encoding="utf-8-sig").splitlines() if s.strip()]
    if len({r["query_id"] for r in rows}) != len(rows) or not rows:
        raise ValueError("Empty or duplicate query IDs")
    return rows


def decode(raw, width, height, text_only=False, threshold=0.23):
    scores, boxes = raw["scores"], raw["normalized_cxcywh"]
    ids = raw["input_ids"].tolist()
    if scores.ndim != 2 or boxes.shape != (len(scores), 4) or not 0 < len(ids) <= scores.shape[1]:
        raise ValueError("Invalid raw shapes")
    if not np.isfinite(scores).all() or not np.isfinite(boxes).all() or np.any((scores < 0) | (scores > 1)):
        raise ValueError("Invalid raw values")
    dot = ids.index(1012)
    if dot + 1 >= scores.shape[1] or width <= 0 or height <= 0:
        raise ValueError("Invalid token span or image dimensions")
    # Exemplar '*' = 1008; exclude CLS, SEP, padding and punctuation as well.
    target = [i for i in range(dot) if ids[i] not in {0, 101, 102, 1008, 1012, 1029}]
    if not target:
        raise ValueError("No target text tokens")
    pos = scores[:, target].max(axis=1) if text_only else scores[:, :dot + 1].max(axis=1)
    neg = scores[:, dot + 1:].max(axis=1)
    keep = np.flatnonzero((pos > threshold) & (pos > neg))
    b = boxes[keep]
    scale = np.array([width, height], dtype=b.dtype)
    center, size = b[:, :2] * scale, b[:, 2:] * scale
    xyxy = np.concatenate([center - size / 2, center + size / 2], axis=1)
    values = pos[keep] if text_only else scores[keep].max(axis=1)
    return keep, xyxy, values, target


def transform(rows, run, threshold=0.23):
    out, hashes = [], {}
    run = Path(run).resolve()
    for row in rows:
        if row["execution_status"] != "ok" or row["box_format"] != "xyxy_pixels":
            raise ValueError("Source error cannot become a zero count")
        fallback = row["no_pseudo"]
        if bool(row["stage2_executed"]) == bool(fallback):
            raise ValueError("Inconsistent second-pass flags")
        filename = "stage1_raw.npz" if fallback else (row.get("stage2_raw") or "stage2_raw.npz")
        path = (run / row["query_id"] / filename).resolve()
        if not path.is_relative_to(run):
            raise ValueError("Raw path escapes run")
        with np.load(path, allow_pickle=False) as z:
            raw = {k: z[k] for k in z.files}
        hashes[str(path)] = sha(path)
        original, boxes, values, _ = decode(raw, row["image_width"], row["image_height"], threshold=threshold)
        if len(original) != row["final_count"]:
            raise ValueError(f"Original replay count differs: {row['query_id']}")
        np.testing.assert_allclose(boxes, np.array(row["final_boxes"]).reshape(-1, 4), atol=.001, rtol=0)
        np.testing.assert_allclose(values, row["final_scores"], atol=1e-5, rtol=0)
        if fallback:
            selected, result_boxes, result_scores, target = original, np.array(row["final_boxes"]).reshape(-1, 4), np.array(row["final_scores"]), []
        else:
            selected, result_boxes, result_scores, target = decode(raw, row["image_width"], row["image_height"], True, threshold)
        ranks = {int(pid): i + 1 for i, pid in enumerate(original)}
        rec = dict(row)
        rec.update(final_count=len(selected), final_boxes=result_boxes.tolist(), final_scores=result_scores.tolist(),
                   proposal_ids=selected.tolist(), original_ranks=[ranks[int(i)] for i in selected],
                   source_variant=row.get("variant", "B2"), variant="T" if row.get("variant", "B2") == "B2" else "P+T",
                   target_token_indices=target, text_only_applied=not fallback)
        out.append(rec)
    return out, hashes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--predictions", type=Path, required=True)
    ap.add_argument("--raw-run", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise ValueError("Output exists; choose a new directory")
    rows, hashes = transform(read_rows(args.predictions), args.raw_run)
    args.out.mkdir(parents=True)
    (args.out / "predictions.jsonl").write_text("".join(json.dumps(r, allow_nan=False) + "\n" for r in rows), encoding="utf-8")
    cfg = dict(tool="offline_text_v2.py", tool_sha256=sha(__file__), source_sha256=sha(args.predictions),
               predictions_sha256=sha(args.out / "predictions.jsonl"),
               raw_sha256=hashes, original_replay_verified=True, threshold=.23, uses_gt=False,
               rule="text max > .23 and > unchanged negative span; no pseudo keeps B0 exactly",
               note="T boxes are a subset of replayed source boxes; original_ranks permits exact CLIP reuse")
    (args.out / "run_config.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
