"""Kiểm độc lập kết quả khảo sát FSC-147 (300 ảnh) — assistant, 22/11/2026.

KHÔNG import code của repo. Tự cài lại: đếm từ bundle, bộ lọc F (theo mô tả trong freeze), chỉ số, Δ và bootstrap
ghép cặp theo ảnh (5000 lần, seed 331, cùng quy trình khai báo). So từng con số với result.json / per_query.csv.
Chỉ đọc file; không chạy model.

Dùng:
  python check_fsc147_independent.py --root <CS331> --run results/countgdpp/<RUN> [--kaggle-meta <dir>]
  python check_fsc147_independent.py --root <CS331> --selftest-w8   (thử bộ đếm F trên run test MUCCA 11/11)
"""
import argparse, csv, hashlib, json, math, random, sys
from pathlib import Path

FAILS = []


def check(ok, label, detail=""):
    print(("  OK   " if ok else "  FAIL ") + label + (f"  ({detail})" if detail else ""))
    if not ok:
        FAILS.append(label)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def f_count(rows_scores, rows_clip, cfg):
    (alo, ahi), (clo, chi) = cfg["bounds"]["countgd"], cfg["bounds"]["clip"]
    n = 0
    for a, c in zip(rows_scores, rows_clip):
        na = 0.5 if ahi == alo else clamp01((a - alo) / (ahi - alo))
        nc = 0.5 if chi == clo else clamp01((c - clo) / (chi - clo))
        n += (0.5 * na + 0.5 * nc) >= cfg["threshold"]
    return n


def my_counts(freeze, bundle):
    src = {name: {r["query_id"]: r for r in rows} for name, rows in bundle["sources"].items()}
    cfgs = {freeze["main"]["name"]: freeze["main"], **freeze["companions_report_only"]}
    out = {}
    for name, cfg in cfgs.items():
        s = src[cfg["source"]]
        if cfg["filter"] is None:
            out[name] = {q: len(r["scores"]) for q, r in s.items()}
        elif cfg["filter"] == "F":
            out[name] = {q: f_count(r["scores"], r["clip"], cfg) for q, r in s.items()}
        else:
            raise SystemExit(f"Bộ lọc lạ: {cfg['filter']}")
    return out, src


def mets(c, rows):
    e = [c[r["query_id"]] - int(r["gt_count"]) for r in rows]
    n = len(e)
    return dict(n=n, MAE=sum(abs(x) for x in e) / n, RMSE=math.sqrt(sum(x * x for x in e) / n), Bias=sum(e) / n,
                overcount_total=sum(x for x in e if x > 0), undercount_total=sum(-x for x in e if x < 0),
                zero_predictions=sum(c[r["query_id"]] == 0 for r in rows))


def boot(ca, cb, rows):
    by = {r["image_id"]: r for r in rows}
    imgs = sorted(by)
    d = {i: abs(ca[by[i]["query_id"]] - int(by[i]["gt_count"])) - abs(cb[by[i]["query_id"]] - int(by[i]["gt_count"])) for i in imgs}
    rng = random.Random(331)
    bs = sorted(sum(d[rng.choice(imgs)] for _ in imgs) / len(imgs) for _ in range(5000))
    return sum(d.values()) / len(imgs), [bs[124], bs[4874]]


def selftest_w8(root):
    print("== Self-test: bộ đếm F tự cài lại, trên run test MUCCA 11/11 ==")
    run = root / "results/countgdpp/p1_test_kaggle_t4_20261111_1430"
    freeze = json.loads((root / "results/countgdpp/freeze_v2_20261111.json").read_text(encoding="utf-8"))
    bundle = json.loads((run.parent / (run.name + "_offline") / "bundle.json").read_text(encoding="utf-8"))
    mine, _ = my_counts(freeze, bundle)
    res = json.loads((run.parent / (run.name + "_eval") / "result.json").read_text(encoding="utf-8"))
    ref = res.get("per_query_counts") or res.get("counts")
    if ref is None:
        print("  result.json W8 không có số đếm từng câu; khóa:", list(res)); return
    for name in mine:
        check(mine[name] == {q: int(v) for q, v in ref[name].items()}, f"W8 số đếm {name} khớp", f"{len(mine[name])} câu")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--run")
    ap.add_argument("--kaggle-meta")
    ap.add_argument("--selftest-w8", action="store_true")
    a = ap.parse_args()
    root = Path(a.root)
    if a.selftest_w8:
        selftest_w8(root)
        print("\nKẾT QUẢ:", "PASS" if not FAILS else f"FAIL {FAILS}")
        return
    run = root / a.run
    sample = root / "experiments/fsc147_survey/sample_300"
    meta = json.loads((sample / "sample_meta.json").read_text(encoding="utf-8"))
    man = list(csv.DictReader((sample / "manifest.csv").open(encoding="utf-8", newline="")))
    ids = [r["query_id"] for r in man]
    freeze_p = root / "results/countgdpp/freeze_v2_20261111.json"
    freeze = json.loads(freeze_p.read_text(encoding="utf-8"))

    print("== B. Đầy đủ và cấu hình ==")
    for n, d in meta["file_sha256"].items():
        check(sha(sample / n) == d, f"hash mẫu {n}")
    check(sha(freeze_p) == "64e89ef53eab306fdbb33cfc39797749ff17cc8635f46ae381d96e45c4f6736d", "hash freeze v2")
    cfg = json.loads((run / "run_config.json").read_text(encoding="utf-8"))
    check(cfg.get("status") == "complete", "B5 status complete", cfg.get("status"))
    check(cfg.get("completed_queries") == 300, "B5 completed_queries = 300", cfg.get("completed_queries"))
    check(cfg.get("tau_pseudo") == [0.2] and cfg.get("m") == 5, "B5 tau [0.2], m 5", f"{cfg.get('tau_pseudo')}, {cfg.get('m')}")
    check(set(cfg.get("outputs", {})) == {"B2", "tau0.200"}, "B5 outputs B2 + tau0.200", list(cfg.get("outputs", {})))
    for k in ("crop", "synthetic", "uses_ground_truth"):
        check(cfg.get(k) is False, f"B5 {k} = false", cfg.get(k))
    check("T4" in str(cfg.get("device")), "B5 device T4", cfg.get("device"))
    check(cfg.get("input_sha256") == meta["file_sha256"]["inputs.jsonl"], "B6 input_sha256 = mẫu")
    preds = {}
    for v, f in cfg["outputs"].items():
        rows = jl(run / f)
        preds[v] = {r["query_id"]: r for r in rows}
        check(len(rows) == 300 and [r["query_id"] for r in rows] == ids, f"B7 {f}: 300 dòng, đúng thứ tự mẫu", len(rows))
        check(all(r["execution_status"] == "ok" for r in rows), f"B7 {f}: mọi câu ok")
    check(all(preds["B2"][q]["stage1_count"] == preds["tau0.200"][q]["stage1_count"] for q in ids),
          "cùng lượt 1 cho B2 và P (stage1_count)")

    ev = run.parent / (run.name + "_eval")
    res = json.loads((ev / "result.json").read_text(encoding="utf-8"))
    check(res.get("status") == "FSC147_SURVEY_RESULT" and res.get("freeze_sha256", "").startswith("64e89ef5")
          and res.get("crop") is False, "B8 result.json: status, freeze, crop")
    if a.kaggle_meta:
        km = Path(a.kaggle_meta)
        h = json.loads((km / "fsc_image_sha256.json").read_text(encoding="utf-8"))
        names = set(h) if isinstance(h, dict) else {x.get("file_name") for x in h}
        if isinstance(h, dict) and "images" in h:
            names = set(h["images"])
        check(names == {r["file_name"] for r in man}, "B4 đủ 300 ảnh, khớp file_name", len(names))
        t = json.loads((km / "timing.json").read_text(encoding="utf-8"))
        check("runner_seconds" in t and "controls_clip_seconds" in t, "B9 timing có runner + CLIP", t)

    print("\n== C. Tính lại độc lập ==")
    bundle_p = run.parent / (run.name + "_offline") / "bundle.json"
    bundle = json.loads(bundle_p.read_text(encoding="utf-8"))
    mine, src = my_counts(freeze, bundle)
    for name, s in (("B0", "B0"), ("B2", "B2"), ("tau0.200", "tau0.200")):
        pv = {"B0": lambda q: preds["B2"][q]["stage1_count"], "B2": lambda q: preds["B2"][q]["final_count"],
              "tau0.200": lambda q: preds["tau0.200"][q]["final_count"]}[name]
        check(all(len(src[s][q]["scores"]) == pv(q) for q in ids), f"bundle {s} khớp số đếm trong predictions")
    pq = list(csv.DictReader((ev / "per_query.csv").open(encoding="utf-8", newline="")))
    check(len(pq) == 300 and [r["query_id"] for r in pq] == ids, "C1 per_query.csv 300 dòng, đúng thứ tự")
    for name in mine:
        col = [r[name] for r in pq]
        check(all(x.isdigit() for x in col), f"C1 cột {name} là số nguyên >= 0")
        check({r["query_id"]: int(r[name]) for r in pq} == mine[name], f"số đếm {name} tự tính = per_query.csv")
    groups = {"all": man, **{s: [r for r in man if r["stratum"] == s] for s in sorted({r["stratum"] for r in man})}}
    for g, rows in groups.items():
        for name in mine:
            m, r = mets(mine[name], rows), res["summary"][g][name]
            ok = all(abs(m[k] - r[k]) < 1e-9 for k in ("MAE", "RMSE", "Bias")) and all(m[k] == r[k] for k in ("n", "overcount_total", "undercount_total", "zero_predictions"))
            check(ok, f"C2 chỉ số [{g}] {name}", f"MAE {m['MAE']:.4f}")
    for c in res["comparisons"]:
        d, ci = boot(mine[c["A"]], mine[c["B"]], man)
        check(abs(d - c["diff"]) < 1e-9, f"C3 Δ {c['A']} − {c['B']}", f"{d:+.4f}")
        check(all(abs(x - y) < 1e-9 for x, y in zip(ci, c["ci95"])), f"CI {c['A']} − {c['B']}", f"[{ci[0]:+.3f}, {ci[1]:+.3f}]")
    for s, c in res["primary_by_stratum"].items():
        d, ci = boot(mine["B0"], mine["B2"], groups[s])
        check(abs(d - c["diff"]) < 1e-9 and all(abs(x - y) < 1e-9 for x, y in zip(ci, c["ci95"])), f"Δ chính nhóm {s}", f"{d:+.4f} [{ci[0]:+.3f}, {ci[1]:+.3f}]")

    print("\n== Bảng tóm tắt (tự tính) ==")
    for g, rows in groups.items():
        print(f"[{g}] n={len(rows)}")
        for name in mine:
            m = mets(mine[name], rows)
            print(f"  {name:<22} MAE {m['MAE']:7.2f}  RMSE {m['RMSE']:7.2f}  Bias {m['Bias']:+7.2f}  thừa {m['overcount_total']:6}  thiếu {m['undercount_total']:6}  =0 {m['zero_predictions']}")
    print("\nKẾT QUẢ:", "PASS" if not FAILS else f"FAIL ({len(FAILS)} mục): {FAILS}")


if __name__ == "__main__":
    main()
