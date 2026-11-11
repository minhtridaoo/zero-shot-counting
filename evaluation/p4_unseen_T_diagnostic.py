"""DIAGNOSTIC ONLY (11/11/2026): score variant T (stage-2 boxes kept by text-token score only) on p4_unseen_v1.

T was designed after looking at errors on these same 10 images (RA_SOAT §3), so this is an early signal, NOT an
independent result; the real evaluation of T is dev_test_v2 (rule D9, test run once). T has no new parameter
(threshold 0.23 unchanged), and nothing here is tuned. Saved files only, CPU, no model.
Also reports T∩F: boxes kept by T AND by the frozen Fusion 50/50 (same CLIP scores, frozen 21/10 thresholds).

Example (from CS331 root): python evaluation/p4_unseen_T_diagnostic.py --run-id p4_unseen_v1_T_diagnostic_20261111
"""
import argparse, csv, json, math, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results/countgdpp"
ANN = ROOT / "data_external/mucca_zenodo_19231375/MUCCA_1.0/annotations.json"


def metrics(pairs):
    e = [abs(p - g) for p, g in pairs]
    return dict(n=len(e), MAE=sum(e) / len(e), RMSE=math.sqrt(sum(x * x for x in e) / len(e)), exact=sum(x == 0 for x in e))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run-id", required=True); args = ap.parse_args()
    out = R / args.run_id
    if out.exists():
        raise SystemExit("Output exists")
    man = {r["query_id"]: r for r in csv.DictReader(open(ROOT / "experiments/countgdpp/p4_unseen_v1/manifest.csv", encoding="utf-8", newline=""))}
    base = {r["query_id"]: r for r in csv.DictReader(open(R / "p4_unseen_v1_eval_20261027/per_query.csv", encoding="utf-8"))}
    T = {json.loads(l)["query_id"]: json.loads(l) for l in open(R / "offline_v2_cpu_20261110/text_replay_final/predictions.jsonl", encoding="utf-8")}
    kept = json.loads((R / "p4_unseen_v1_freeze_20261027/kept_boxes.json").read_text(encoding="utf-8"))
    b2 = {json.loads(l)["query_id"]: json.loads(l) for l in open(R / "p4_unseen_v1_b2_20261027/predictions.jsonl", encoding="utf-8")}
    ann = json.loads(ANN.read_text(encoding="utf-8"))
    assert set(man) == set(base) == set(T) == set(kept)
    inside = lambda p, b: b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3]
    rows = []
    for q in sorted(man):
        m, t = man[q], T[q]
        fus = {d["rank"] for d in kept[q] if d["keep_Fusion_50_50"]}
        if t["text_only_applied"]:
            t_ranks = t["original_ranks"]; tf = [r for r in t_ranks if r in fus]
        else:   # no pseudo -> B0 (no stage 2); T∩F undefined, use B0+frozen F? keep B0 count like T
            t_ranks = None; tf = None
        row = dict(query_id=q, image_id=m["image_id"], prompt=m["prompt"], presence=m["presence_status"], gt=int(m["gt_count"]),
                   B0=int(base[q]["pred_B0"]), B2=int(base[q]["pred_B2_original"]), S=int(base[q]["pred_B2_threshold"]),
                   F=int(base[q]["pred_Fusion_50_50"]), T=t["final_count"],
                   TF=len(tf) if tf is not None else int(base[q]["pred_Fusion_50_50"]))
        # point-in-box proxy for T boxes (present queries)
        a = ann[m["image_id"] + ".jpg"]; pts = list(zip(a["points"], a["classes"])); tgt = int(m["class_id"])
        tb = t["final_boxes"]
        row["T_boxes_with_target"] = sum(any(c == tgt and inside(p, b) for p, c in pts) for b in tb)
        row["T_boxes_other_only"] = sum((not any(c == tgt and inside(p, b) for p, c in pts)) and any(inside(p, b) for p, c in pts) for b in tb)
        row["T_target_pts_covered"] = sum(any(inside(p, b) for b in tb) for p, c in pts if c == tgt) if m["presence_status"] == "present" else ""
        rows.append(row)
    methods = ["B0", "B2", "S", "F", "T", "TF"]
    pres = [r for r in rows if r["presence"] == "present"]; absn = [r for r in rows if r["presence"] == "absent"]
    summ = {k: dict(all=metrics([(r[k], r["gt"]) for r in rows])["MAE"], present=metrics([(r[k], r["gt"]) for r in pres]),
                    absent_mean=sum(r[k] for r in absn) / len(absn), absent_nonzero=sum(r[k] > 0 for r in absn)) for k in methods}

    def paired(a, b):
        imgs = sorted({r["image_id"] for r in rows}); by = {i: [r for r in rows if r["image_id"] == i] for i in imgs}
        d = lambda rs: sum(abs(r[b] - r["gt"]) - abs(r[a] - r["gt"]) for r in rs) / len(rs)
        rng = random.Random(331); boots = sorted(d([r for i in (rng.choice(imgs) for _ in imgs) for r in by[i]]) for _ in range(5000))
        better = sum(abs(r[b] - r["gt"]) < abs(r[a] - r["gt"]) for r in rows); worse = sum(abs(r[b] - r["gt"]) > abs(r[a] - r["gt"]) for r in rows)
        return dict(comparison=f"{b} vs {a}", diff=d(rows), ci95=[boots[124], boots[4874]], better=better, worse=worse, same=len(rows) - better - worse)

    comps = [paired("B2", "T"), paired("B0", "T"), paired("F", "T"), paired("F", "TF"), paired("B0", "TF")]
    proxy = dict(T_kept=sum(r["T"] for r in pres), T_boxes_with_target=sum(r["T_boxes_with_target"] for r in pres),
                 T_boxes_other_only=sum(r["T_boxes_other_only"] for r in pres),
                 T_target_pts_covered=sum(r["T_target_pts_covered"] for r in pres), target_pts_total=sum(r["gt"] for r in pres))
    out.mkdir(parents=True)
    with open(out / "per_query.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    (out / "metrics.json").write_text(json.dumps(dict(status="DIAGNOSTIC_ONLY_SEEN_SET", summary=summ, comparisons=comps, proxy_present_T=proxy),
                                                  ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{'cách':<5}{'MAE_all':>8}{'MAE_pres':>9}{'abs_mean':>9}{'abs>0':>6}")
    for k in methods:
        s = summ[k]; print(f"{k:<5}{s['all']:>8.2f}{s['present']['MAE']:>9.2f}{s['absent_mean']:>9.2f}{s['absent_nonzero']:>6}")
    for c in comps:
        print(c["comparison"], f"diff {c['diff']:+.2f} CI [{c['ci95'][0]:+.2f}, {c['ci95'][1]:+.2f}]", f"{c['better']}/{c['worse']}/{c['same']}")
    print("proxy T (present):", proxy)
    for r in rows:
        print(r["query_id"], f"{r['prompt']:<16}", r["presence"][:3], "gt", r["gt"], "| B0", r["B0"], "B2", r["B2"], "F", r["F"], "T", r["T"], "TF", r["TF"])


if __name__ == "__main__":
    main()
