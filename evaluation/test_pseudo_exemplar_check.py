"""Post-hoc (no model run): did CLIP verification (P, tau 0.20, M 5) pick different / more correct pseudo-exemplars than
plain B2 on the LOCKED test run?  Reads predictions_*.jsonl (pseudo_boxes) + candidates.jsonl (chosen ids) and the
MUCCA GT points. An exemplar is "own" if it contains a point of the queried class, "other" if only other-class
points, "none" otherwise (lenient: a box covering several objects still counts as own). Uncertain GT is skipped.
Run from the CS331 root:  python evaluation/test_pseudo_exemplar_check.py
"""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evaluation"))
from test_xy_overlap_analysis import inside, ANN, MANIFEST, RUN  # noqa: E402

OUT = Path(str(RUN) + "_posthoc_20261111") / "pseudo_exemplars.json"


def main():
    ann = json.loads(ANN.read_text(encoding="utf-8"))
    man = {r["query_id"]: r for r in csv.DictReader(open(MANIFEST, encoding="utf-8", newline=""))}
    out = {}
    for name, f in [("B2", "predictions_B2.jsonl"), ("P", "predictions_tau0.200.jsonl")]:
        c = dict(q=0, q_with=0, ex=0, own=0, other=0, none=0, abs_q_with=0)
        for line in open(RUN / f, encoding="utf-8"):
            r = json.loads(line); m = man[r["query_id"]]
            if m["presence_status"] == "uncertain":
                continue
            a = ann[r["image_id"] + ".jpg"]; cls = int(m["class_id"]); c["q"] += 1
            if r["pseudo_boxes"]:
                c["q_with"] += 1; c["abs_q_with"] += m["presence_status"] == "absent"
            if m["presence_status"] != "present":
                continue
            for b in r["pseudo_boxes"] or []:
                c["ex"] += 1
                if any(inside(b, p) for p, k in zip(a["points"], a["classes"]) if k == cls): c["own"] += 1
                elif any(inside(b, p) for p in a["points"]): c["other"] += 1
                else: c["none"] += 1
        out[name] = c
    rows = [json.loads(l) for l in open(RUN / "candidates.jsonl", encoding="utf-8")]
    same = sum(r["chosen"]["B2"] == r["chosen"]["tau0.200"] for r in rows)
    res = dict(status="POST_HOC_ANALYSIS", pseudo_exemplar_check=out, same_exemplar_set_B2_vs_P=[same, len(rows)])
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
