"""DIAGNOSTIC ONLY (11/11/2026): leave-one-image-out (LOIO) refit of the S / F filters per source on p4_unseen_v1.

Question: is there a configuration that could beat B0 under rule D9 (MAE_present <= B0 and FPR_absent <= B0)?
Sources (same A2000 run 27/10): B0 (= stage 1), B2, T (stage-2 boxes kept by text score; box score = text score).
For each held-out image, thresholds are fitted on the other 9 images only, with the 21/10 rule
(candidate midpoints, minimise MAE, then RMSE, then smaller threshold; keep if score >= threshold; F = 0.5*minmax(CountGD)
+ 0.5*minmax(CLIP) with min/max from the 9 training images, clamped). p4_unseen_v1 was already used for error analysis,
so this is an early signal for the dev_test_v2 run, NOT a result to report as independent. CPU, saved files only.

Example: python evaluation/p4_unseen_loio_diagnostic.py --run-id p4_unseen_v1_loio_diagnostic_20261111
"""
import argparse, csv, json, math, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results/countgdpp"


def load_scores(folder):
    out = {}
    for p in (R / folder).glob("*_clip_scores.json"):
        o = json.loads(p.read_text(encoding="utf-8"))
        out[o["query_id"]] = [(float(r["b2_score"]), float(r["clip_cosine_target"])) for r in o["rows_original_order"]]
    return out


def mae_rmse(pairs):
    e = [abs(p - g) for p, g in pairs]
    return sum(e) / len(e), math.sqrt(sum(x * x for x in e) / len(e))


def fit(train, gt, key):
    vals = sorted({key(b) for q in train for b in boxes_of[q]})
    cands = [vals[0] - 1e-6] + [(a + b) / 2 for a, b in zip(vals, vals[1:])] + [vals[-1] + 1e-6] if vals else [0.0]
    best = None
    for th in cands:
        m, r = mae_rmse([(sum(key(b) >= th for b in boxes_of[q]), gt[q]) for q in train])
        if best is None or (m, r, th) < best[0]:
            best = ((m, r, th), th)
    return best[1]


def main():
    global boxes_of
    ap = argparse.ArgumentParser(); ap.add_argument("--run-id", required=True); args = ap.parse_args()
    out = R / args.run_id
    if out.exists():
        raise SystemExit("Output exists")
    man = {r["query_id"]: r for r in csv.DictReader(open(ROOT / "experiments/countgdpp/p4_unseen_v1/manifest.csv", encoding="utf-8", newline=""))}
    gt = {q: int(r["gt_count"]) for q, r in man.items()}
    img = {q: r["image_id"] for q, r in man.items()}
    b2s, b0s = load_scores("p4_unseen_v1_clip_20261027"), load_scores("p4_unseen_v1_B0_clip_20261111")
    T = {json.loads(l)["query_id"]: json.loads(l) for l in open(R / "offline_v2_cpu_20261110/text_replay_final/predictions.jsonl", encoding="utf-8")}
    srcs = {"B0": b0s, "B2": b2s, "T": {}}
    for q, t in T.items():
        if t["text_only_applied"]:
            srcs["T"][q] = [(float(s), b2s[q][rk - 1][1]) for s, rk in zip(t["final_scores"], t["original_ranks"])]
        else:
            srcs["T"][q] = b0s[q]          # no pseudo -> B0 boxes, exactly as T falls back
    assert all(set(s) == set(gt) for s in srcs.values())
    images = sorted(set(img.values()))
    pred = {}
    for name, sc in srcs.items():
        pred[name] = {q: len(sc[q]) for q in gt}
        pred[name + "+S"], pred[name + "+F"] = {}, {}
        for held in images:
            train = [q for q in gt if img[q] != held]; test = [q for q in gt if img[q] == held]
            boxes_of = sc
            ths = fit(train, gt, lambda b: b[0])
            allb = [b for q in train for b in sc[q]]
            lo0, hi0 = (min(b[0] for b in allb), max(b[0] for b in allb)) if allb else (0, 1)
            lo1, hi1 = (min(b[1] for b in allb), max(b[1] for b in allb)) if allb else (0, 1)
            nz = lambda v, lo, hi: 0.5 if hi == lo else max(0.0, min(1.0, (v - lo) / (hi - lo)))
            fz = lambda b: 0.5 * nz(b[0], lo0, hi0) + 0.5 * nz(b[1], lo1, hi1)
            thf = fit(train, gt, fz)
            for q in test:
                pred[name + "+S"][q] = sum(b[0] >= ths for b in sc[q])
                pred[name + "+F"][q] = sum(fz(b) >= thf for b in sc[q])
    pres = [q for q in gt if man[q]["presence_status"] == "present"]; absn = [q for q in gt if man[q]["presence_status"] == "absent"]
    res = {}
    for k, p in pred.items():
        res[k] = dict(MAE_all=mae_rmse([(p[q], gt[q]) for q in gt])[0], MAE_present=mae_rmse([(p[q], gt[q]) for q in pres])[0],
                      absent_mean=sum(p[q] for q in absn) / len(absn), FPR_absent=sum(p[q] > 0 for q in absn) / len(absn))
    b0 = res["B0"]
    for k, v in res.items():
        v["D9_eligible"] = v["MAE_present"] <= b0["MAE_present"] + 1e-12 and v["FPR_absent"] <= b0["FPR_absent"] + 1e-12
        v["D9_beats_B0"] = v["D9_eligible"] and v["MAE_all"] < b0["MAE_all"] - 1e-12

    def ci(a, b):
        by = {i: [q for q in gt if img[q] == i] for i in images}; rng = random.Random(331)
        d = lambda qs: sum(abs(pred[b][q] - gt[q]) - abs(pred[a][q] - gt[q]) for q in qs) / len(qs)
        bs = sorted(d([q for i in (rng.choice(images) for _ in images) for q in by[i]]) for _ in range(5000))
        return dict(comparison=f"{b} vs {a}", diff=d(list(gt)), ci95=[bs[124], bs[4874]])

    comps = [ci("B0", k) for k in ["B0+S", "B0+F", "B2+F", "T", "T+S", "T+F"]]
    out.mkdir(parents=True)
    (out / "metrics.json").write_text(json.dumps(dict(status="DIAGNOSTIC_ONLY_SEEN_SET_LOIO", results=res, comparisons_vs_B0=comps,
                                                      per_query={k: v for k, v in pred.items()}), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{'cách':<7}{'MAE_all':>8}{'MAE_pres':>9}{'abs_mean':>9}{'FPR_abs':>8}  D9")
    for k, v in res.items():
        print(f"{k:<7}{v['MAE_all']:>8.2f}{v['MAE_present']:>9.2f}{v['absent_mean']:>9.2f}{v['FPR_absent']:>8.2f}  "
              f"{'THẮNG B0' if v['D9_beats_B0'] else ('đạt điều kiện' if v['D9_eligible'] else '-')}")
    for c in comps:
        print(c["comparison"], f"{c['diff']:+.2f} CI [{c['ci95'][0]:+.2f}, {c['ci95'][1]:+.2f}]")


if __name__ == "__main__":
    main()
