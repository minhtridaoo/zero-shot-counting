"""Post-hoc breakdown of the LOCKED test result (no model run, no refitting): reads per-query counts from the
single frozen evaluation (`_eval/result.json`) and reports, per configuration,
  (1) MAE by pair type: "distinct" (X, Y from different super-categories, the teacher's X/Y question) vs
      "confusable" (same super-category), using the strata recorded in selection_meta.json;
  (2) present-query error decomposition: over-count vs under-count (sum of signed errors, number of queries);
  (3) exact-count rate.
Descriptive only; the main result stays the frozen P+F.  Run from the CS331 root:
  python evaluation/test_stratified_posthoc.py
"""
import csv, json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/countgdpp/p1_test_kaggle_t4_20261111_1430"
MAN = ROOT / "experiments/countgdpp/dev_test_v2/test/manifest.csv"
META = ROOT / "experiments/countgdpp/dev_test_v2/selection_meta.json"
OUT = Path(str(RUN) + "_posthoc_20261111") / "stratified.json"


def main():
    pq = json.loads((Path(str(RUN) + "_eval") / "result.json").read_text(encoding="utf-8"))["per_query_counts"]
    man = [r for r in csv.DictReader(open(MAN, encoding="utf-8", newline="")) if r["presence_status"] != "uncertain"]
    strata = json.loads(META.read_text(encoding="utf-8"))["strata"]
    kind = {img: k.split(":")[0] for k, imgs in strata.items() for img in imgs}
    res = {}
    for name, c in pq.items():
        d = {}
        for pt in ("distinct", "confusable"):
            rows = [r for r in man if kind[r["image_id"]] == pt]
            pres = [r for r in rows if r["presence_status"] == "present"]; ab = [r for r in rows if r["presence_status"] == "absent"]
            d[pt] = dict(n_images=len({r["image_id"] for r in rows}), n=len(rows),
                         MAE=sum(abs(c[r["query_id"]] - int(r["gt_count"])) for r in rows) / len(rows),
                         MAE_present=sum(abs(c[r["query_id"]] - int(r["gt_count"])) for r in pres) / len(pres),
                         FPR_absent=sum(c[r["query_id"]] > 0 for r in ab) / len(ab))
        pres = [r for r in man if r["presence_status"] == "present"]
        e = [c[r["query_id"]] - int(r["gt_count"]) for r in pres]
        d["present_errors"] = dict(n=len(e), over_n=sum(x > 0 for x in e), over_sum=sum(x for x in e if x > 0),
                                   under_n=sum(x < 0 for x in e), under_sum=-sum(x for x in e if x < 0),
                                   exact_n=sum(x == 0 for x in e), within_10pct=sum(abs(x) <= .1 * int(r["gt_count"]) for x, r in zip(e, pres)))
        res[name] = d
    # image-level bootstrap (5000, seed 331) of MAE difference vs B0 inside each pair type
    for pt in ("distinct", "confusable"):
        rows = [r for r in man if kind[r["image_id"]] == pt]
        imgs = sorted({r["image_id"] for r in rows})
        by = {i: [r for r in rows if r["image_id"] == i] for i in imgs}
        for name, c in pq.items():
            if name == "B0":
                continue
            def diff(sample):
                rr = [r for i in sample for r in by[i]]
                return sum(abs(c[r["query_id"]] - int(r["gt_count"])) - abs(pq["B0"][r["query_id"]] - int(r["gt_count"])) for r in rr) / len(rr)
            rnd = random.Random(331); v = sorted(diff([rnd.choice(imgs) for _ in imgs]) for _ in range(5000))
            res[name][pt]["vs_B0"] = dict(diff=diff(imgs), ci95=[v[124], v[4874]])
    OUT.write_text(json.dumps(dict(status="POST_HOC_ANALYSIS", source="_eval/result.json per_query_counts", result=res),
                              ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    for name, d in res.items():
        print(name, {k: {a: round(b, 3) if isinstance(b, float) else b for a, b in v.items()} for k, v in d.items()})


if __name__ == "__main__":
    main()
