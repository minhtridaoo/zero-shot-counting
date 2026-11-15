"""Post-hoc analysis on the LOCKED test run (no model run, no refitting, no reselection).

Question: when a user switches the query from X to Y on the same image, do the kept boxes change?
For every test image (2 present queries X, Y + 1 absent query Z) and for each reported configuration
(B0, B2, main P+F, C6 = B0+F, B2+F), take the boxes that configuration keeps (F decisions use the FROZEN
bounds/thresholds from freeze_v2_20261111.json, via apply_freeze_v2.counts_for logic) and measure:

  * shared_xy  = share of X's and Y's kept boxes that have an IoU >= t match in the other query's kept boxes
                 (high = the model returns the same objects whatever you ask for)
  * absent_reuse = share of Z's kept boxes (absent class) that match a kept box of X or Y
                 (high = for an absent class the model just re-points at the other objects)

  * point check (MUCCA per-class GT points, same pixel frame as boxes): each kept box of a present query is
    "correct" if it contains a point of the queried class, "other_class_only" if it contains only points of
    other annotated classes, "no_point" otherwise; for absent queries, share of kept boxes on an annotated object.
    Lenient (a large box covering both classes counts as correct).

Thresholds t = 0.5 and 0.8. Images whose pair contains an `uncertain` query (D12, t37_1) are skipped for
shared_xy; absent_reuse uses every absent query.  Also writes a runtime table from predictions_*.jsonl.

Run from the CS331 root:
  python evaluation/test_xy_overlap_analysis.py
Outputs: results/countgdpp/p1_test_kaggle_t4_20261111_1430_posthoc_20261111/
"""
import csv, json, random, statistics as st, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/countgdpp"))
from apply_freeze_v2 import norm  # noqa: E402  (same normalisation as the frozen scorer)

RUN = ROOT / "results/countgdpp/p1_test_kaggle_t4_20261111_1430"
BUNDLE = Path(str(RUN) + "_offline") / "bundle.json"
MANIFEST = ROOT / "experiments/countgdpp/dev_test_v2/test/manifest.csv"
FREEZE = ROOT / "results/countgdpp/freeze_v2_20261111.json"
OUT = Path(str(RUN) + "_posthoc_20261111")
ANN = ROOT / "data_external/mucca_zenodo_19231375/MUCCA_1.0/annotations.json"


def inside(b, p):
    return b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3]


def point_check(keep, man):
    ann = json.loads(ANN.read_text(encoding="utf-8"))
    out = {}
    for name, K in keep.items():
        c = dict(correct=0, other_class_only=0, no_point=0, absent_boxes=0, absent_on_object=0)
        for r in man:
            a = ann[r["image_id"] + ".jpg"]; cls = int(r["class_id"])
            own = [p for p, k in zip(a["points"], a["classes"]) if k == cls]
            oth = [p for p, k in zip(a["points"], a["classes"]) if k != cls]
            for b in K[r["query_id"]]:
                if r["presence_status"] == "present":
                    if any(inside(b, p) for p in own): c["correct"] += 1
                    elif any(inside(b, p) for p in oth): c["other_class_only"] += 1
                    else: c["no_point"] += 1
                elif r["presence_status"] == "absent":
                    c["absent_boxes"] += 1; c["absent_on_object"] += any(inside(b, p) for p in a["points"])
        n = c["correct"] + c["other_class_only"] + c["no_point"]
        c.update(present_boxes=n, correct_rate=c["correct"] / n if n else None,
                 other_class_only_rate=c["other_class_only"] / n if n else None,
                 absent_on_object_rate=c["absent_on_object"] / c["absent_boxes"] if c["absent_boxes"] else None)
        out[name] = c
    return out


def iou(a, b):
    ix = max(0., min(a[2], b[2]) - max(a[0], b[0])); iy = max(0., min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.


def matched(boxes, others, t):
    return sum(any(iou(b, o) >= t for o in others) for b in boxes)


def configs():
    fz = json.loads(FREEZE.read_text(encoding="utf-8"))
    c = {"B0": fz["companions_report_only"]["B0"], "B2": fz["companions_report_only"]["B2"],
         "P+F (chính)": fz["main"], "C6 = B0+F": fz["companions_report_only"]["C6 = B0+F"],
         "B2+F": fz["companions_report_only"]["B2+F"]}
    return c


def kept(cfg, row):
    if cfg["filter"] is None:
        return list(row["boxes"])
    assert cfg["filter"] == "F"
    b = cfg["bounds"]
    return [bx for bx, a, c in zip(row["boxes"], row["scores"], row["clip"])
            if .5 * norm(a, b["countgd"]) + .5 * norm(c, b["clip"]) >= cfg["threshold"]]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    src = {n: {r["query_id"]: r for r in rows} for n, rows in bundle["sources"].items()}
    man = list(csv.DictReader(open(MANIFEST, encoding="utf-8", newline="")))
    byimg = {}
    for r in man:
        byimg.setdefault(r["image_id"], []).append(r)
    cfgs = configs()
    keep = {name: {q: kept(cfg, src[cfg["source"]][q]) for q in src[cfg["source"]]} for name, cfg in cfgs.items()}

    per_rows, summary = [], {}
    for name in cfgs:
        K = keep[name]
        agg = {t: dict(sx=0, nx=0, sz=0, nz=0, img_shared=[]) for t in (0.5, 0.8)}
        for img, rows in byimg.items():
            pres = [r for r in rows if r["presence_status"] == "present"]
            unc = [r for r in rows if r["presence_status"] == "uncertain"]
            absn = [r for r in rows if r["presence_status"] == "absent"]
            for t in (0.5, 0.8):
                rec = dict(config=name, iou=t, image_id=img)
                if len(pres) == 2 and not unc:
                    X, Y = (K[r["query_id"]] for r in pres)
                    s = matched(X, Y, t) + matched(Y, X, t); n = len(X) + len(Y)
                    agg[t]["sx"] += s; agg[t]["nx"] += n
                    if n:
                        agg[t]["img_shared"].append(s / n)
                    rec.update(x_query=pres[0]["query_id"], x_prompt=pres[0]["prompt"], y_query=pres[1]["query_id"],
                               y_prompt=pres[1]["prompt"], n_x=len(X), n_y=len(Y), shared=s, shared_rate=(s / n) if n else "")
                for z in absn:
                    Z = K[z["query_id"]]; others = [b for r in pres + unc for b in K[r["query_id"]]]
                    m = matched(Z, others, t); agg[t]["sz"] += m; agg[t]["nz"] += len(Z)
                    rec.update(z_query=z["query_id"], z_prompt=z["prompt"], n_z=len(Z), z_reuse=m)
                per_rows.append(rec)
        summary[name] = {}
        for t, a in agg.items():
            ish = a["img_shared"]
            summary[name][str(t)] = dict(
                shared_xy_pooled=a["sx"] / a["nx"] if a["nx"] else None, n_boxes_xy=a["nx"],
                shared_xy_mean_per_image=st.mean(ish) if ish else None,
                images_majority_shared=sum(v >= .5 for v in ish), n_images=len(ish),
                absent_kept_boxes=a["nz"], absent_reuse_pooled=a["sz"] / a["nz"] if a["nz"] else None)

    # image-level bootstrap CI for pooled shared_xy at IoU 0.5 (descriptive)
    rnd = random.Random(331)
    imgs = sorted({r["image_id"] for r in per_rows if "shared" in r})
    by = {(r["config"], r["image_id"]): r for r in per_rows if r["iou"] == 0.5 and "shared" in r}
    for name in cfgs:
        vals = []
        for _ in range(5000):
            smp = [rnd.choice(imgs) for _ in imgs]
            s = sum(by[(name, i)]["shared"] for i in smp); n = sum(by[(name, i)]["n_x"] + by[(name, i)]["n_y"] for i in smp)
            vals.append(s / n if n else 0.)
        vals.sort()
        summary[name]["0.5"]["shared_xy_pooled_ci95"] = [vals[124], vals[4874]]

    # runtime (ms, as logged on Kaggle T4); CLIP verification time is not logged by the runner
    rt = {}
    for label, f in [("B2", "predictions_B2.jsonl"), ("P (tau0.200)", "predictions_tau0.200.jsonl")]:
        rows = [json.loads(l) for l in open(RUN / f, encoding="utf-8")]
        s1 = [r["stage1_ms"] for r in rows[1:]]  # first query includes warm-up
        s2 = [r["stage2_ms"] for r in rows[1:] if r["stage2_executed"]]
        tot = [r["stage1_ms"] + (r["stage2_ms"] if r["stage2_executed"] else 0) for r in rows[1:]]
        rt[label] = dict(n=len(rows) - 1, stage2_executed=len(s2), stage1_ms_median=st.median(s1), stage1_ms_mean=st.mean(s1),
                         stage2_ms_median=st.median(s2), stage2_ms_mean=st.mean(s2), total_ms_mean=st.mean(tot),
                         warmup_first_query_stage1_ms=rows[0]["stage1_ms"])
    rt["B0"] = dict(n=rt["B2"]["n"], total_ms_mean=rt["B2"]["stage1_ms_mean"], note="B0 = lượt 1 (cùng lần chạy)")

    with open(OUT / "xy_overlap_per_image.csv", "w", encoding="utf-8", newline="") as f:
        cols = ["config", "iou", "image_id", "x_query", "x_prompt", "y_query", "y_prompt", "n_x", "n_y", "shared", "shared_rate",
                "z_query", "z_prompt", "n_z", "z_reuse"]
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(per_rows)
    res = dict(status="POST_HOC_ANALYSIS (không chọn lại cấu hình, không chạy model)", run=RUN.name, freeze=FREEZE.name,
               overlap=summary, point_check=point_check(keep, man), runtime_ms=rt)
    (OUT / "summary.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
