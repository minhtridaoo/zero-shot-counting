"""Fit per-source S/F on locked dev; D9 selection. Diagnostic mode never freezes.

Input bundle: {run_id, sources: {name: [{query_id,image_id,boxes,scores,clip}]}}.
clip contains aligned cosine scores; no CLIP/model is invoked by this tool.
"""
import argparse
import bisect
import csv
import hashlib
import json
import math
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def metrics(counts, manifest):
    result = {}
    for label, ids in (("all", list(manifest)), ("present", [q for q, r in manifest.items() if r["presence_status"] == "present"])):
        if not ids:
            raise ValueError("Need present queries")
        errors = [abs(counts[q] - int(manifest[q]["gt_count"])) for q in ids]
        result[label] = dict(n=len(ids), MAE=sum(errors) / len(ids), RMSE=math.sqrt(sum(e*e for e in errors) / len(ids)))
    absent = [q for q, r in manifest.items() if r["presence_status"] == "absent"]
    result["absent"] = dict(n=len(absent), FPR_absent=sum(counts[q] > 0 for q in absent) / len(absent)) if absent else None
    return result


def fit_threshold(scores, gt):
    """Historical rule: min MAE, RMSE, threshold; >= midpoint thresholds."""
    vals = sorted({v for s in scores.values() for v in s})
    if not vals:
        return 0.0  # All counts remain zero for any finite threshold.
    candidates = [vals[0] - 1e-6] + [(a + b)/2 for a, b in zip(vals, vals[1:])] + [vals[-1] + 1e-6]
    ordered = {q: sorted(s) for q, s in scores.items()}
    def criterion(t):
        errors = [abs(len(s) - bisect.bisect_left(s, t) - gt[q]) for q, s in ordered.items()]
        # Integer sums have the same ordering as MAE/RMSE, without round-off ties.
        return sum(errors), sum(e*e for e in errors), t
    return min(candidates, key=criterion)


def norm(v, bounds):
    lo, hi = bounds
    return .5 if lo == hi else max(0., min(1., (v - lo)/(hi - lo)))


def select_d9(table):
    base = table["B0"]
    if base["absent"] is None:
        return dict(status="NOT_EVALUABLE_NO_ABSENT", selected=None)
    eligible = [name for name, s in table.items() if s["present"]["MAE"] <= base["present"]["MAE"]
                and s["absent"]["FPR_absent"] <= base["absent"]["FPR_absent"]]
    best = min(table[n]["all"]["MAE"] for n in eligible)
    tied = sorted(n for n in eligible if table[n]["all"]["MAE"] == best)
    if best >= base["all"]["MAE"]:
        return dict(status="NO_STRICT_IMPROVEMENT", selected="B0", eligible=eligible, tied=tied)
    # D9 did not define a tie-break between distinct configurations; expose it.
    return dict(status="CANDIDATE" if len(tied) == 1 else "TIE_REQUIRES_DECISION",
                selected=tied[0] if len(tied) == 1 else None, eligible=eligible, tied=tied)


def evaluate(bundle, manifest):
    if "B0" not in bundle["sources"]:
        raise ValueError("D9 requires B0 from this same run")
    ids = {r["query_id"] for r in manifest}
    if len(ids) != len(manifest):
        raise ValueError("Duplicate manifest queries")
    valid = {}
    for r in manifest:
        state = r["presence_status"]
        if state not in {"present", "absent", "uncertain"}:
            raise ValueError("Unknown presence status")
        if state == "uncertain":
            continue
        gt = int(r["gt_count"])
        if gt < 0 or (state == "absent" and gt != 0):
            raise ValueError("Invalid GT")
        valid[r["query_id"]] = r
    counts, params = {}, {}
    for name, rows in bundle["sources"].items():
        if not name or name.endswith(("+S", "+F")):
            raise ValueError("Source name conflicts with generated filter name")
        byq = {r["query_id"]: r for r in rows}
        if len(byq) != len(rows) or set(byq) != ids:
            raise ValueError(f"Source coverage mismatch: {name}")
        for r in manifest:
            x = byq[r["query_id"]]
            if x["image_id"] != r["image_id"] or len(x["boxes"]) != len(x["scores"]) or len(x["clip"]) != len(x["scores"]):
                raise ValueError("Unaligned source")
            if not all(math.isfinite(v) for v in x["scores"] + x["clip"]):
                raise ValueError("Nonfinite score")
            if not all(0 <= v <= 1 for v in x["scores"]) or not all(-1.00001 <= v <= 1.00001 for v in x["clip"]):
                raise ValueError("Score range error")
        sc = {q: byq[q]["scores"] for q in valid}
        cs = {q: byq[q]["clip"] for q in valid}
        flat = [v for s in sc.values() for v in s]
        cf = [v for s in cs.values() for v in s]
        bounds = {"countgd": [min(flat), max(flat)] if flat else [0., 0.], "clip": [min(cf), max(cf)] if cf else [0., 0.]}
        fused = {q: [.5*norm(a, bounds["countgd"]) + .5*norm(b, bounds["clip"]) for a, b in zip(sc[q], cs[q])] for q in valid}
        counts[name] = {q: len(s) for q, s in sc.items()}
        params[name] = dict(bounds=bounds)
        for suffix, values in (("S", sc), ("F", fused)):
            threshold = fit_threshold(values, {q: int(valid[q]["gt_count"]) for q in valid})
            params[name][suffix] = threshold
            counts[name + "+" + suffix] = {q: sum(v >= threshold for v in s) for q, s in values.items()}
    table = {n: metrics(c, valid) for n, c in counts.items()}
    return dict(summary=table, parameters=params, per_query_counts=counts, d9=select_d9(table),
                uncertain_excluded=sorted(ids - set(valid)), interpretation="Fitted dev results, not holdout estimates")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--selection-meta", type=Path)
    ap.add_argument("--diagnostic", action="store_true", help="Historical/synthetic checks only; cannot select a production configuration")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise ValueError("Output exists")
    manifest = list(csv.DictReader(args.manifest.open(encoding="utf-8-sig", newline="")))
    if not args.diagnostic:
        if not args.selection_meta or json.loads(args.selection_meta.read_text(encoding="utf-8"))["status"] != "LOCKED":
            raise ValueError("Fit requires locked dev data")
        if not manifest or any(r.get("split") != "dev_v2" or not r.get("verified_by") or "PENDING" in r["verified_by"] for r in manifest):
            raise ValueError("Only human-checked dev_v2 may select configurations; never test")
        if not any(r["presence_status"] == "absent" for r in manifest):
            raise ValueError("D9 needs absent queries")
    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    if not bundle.get("run_id"):
        raise ValueError("Missing same-run provenance")
    result = evaluate(bundle, manifest)
    result.update(mode="DIAGNOSTIC_ONLY" if args.diagnostic else "DEV_SELECTION_REQUIRES_HUMAN_FREEZE",
                  bundle_sha256=sha(args.bundle), manifest_sha256=sha(args.manifest), tool_sha256=sha(__file__),
                  selection_meta_sha256=sha(args.selection_meta) if args.selection_meta else None,
                  run_id=bundle["run_id"])
    args.out.mkdir(parents=True)
    (args.out / "selection.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
