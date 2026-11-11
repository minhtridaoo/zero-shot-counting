"""Apply the FROZEN v2 configuration (results/countgdpp/freeze_v2_20261111.json) to a bundle — no refitting.

Use once on the locked test set. The bundle comes from the same run as the main source (B0 = stage 1, B2, tau0.200),
built by bundle_offline_v2.py from the p1_controls.py output of the test run. Bounds and thresholds are taken from
the freeze; F = 0.5*norm(CountGD) + 0.5*norm(CLIP), norm clamped to [0, 1], keep if F >= threshold (same as
select_offline_v2.py). Uncertain GT is excluded from every metric (D12). Reports the main configuration and the
report-only companions, plus an image-level bootstrap (5000 draws, seed 331) of the MAE difference vs B0.

--verify-dev re-applies the freeze to the dev bundle and requires the counts to equal the dev selection exactly
(implementation check, not a result).

Examples (from CS331 root):
  python experiments/countgdpp/apply_freeze_v2.py --bundle RUN_offline/bundle.json \
      --manifest experiments/countgdpp/dev_test_v2/test/manifest.csv --out results/countgdpp/RUN_test_eval
  python experiments/countgdpp/apply_freeze_v2.py --verify-dev
"""
import argparse, hashlib, json, math, random, csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "results/countgdpp/freeze_v2_20261111.json"
META = ROOT / "experiments/countgdpp/dev_test_v2/selection_meta.json"
DEV = "results/countgdpp/p1_dev_kaggle_t4_20261111_1203_m5"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def norm(v, b):
    lo, hi = b
    return .5 if lo == hi else max(0., min(1., (v - lo) / (hi - lo)))


def counts_for(cfg, src_rows):
    out = {}
    for q, r in src_rows.items():
        if cfg["filter"] is None:
            out[q] = len(r["scores"])
        elif cfg["filter"] == "F":
            b = cfg["bounds"]
            out[q] = sum(.5 * norm(a, b["countgd"]) + .5 * norm(c, b["clip"]) >= cfg["threshold"] for a, c in zip(r["scores"], r["clip"]))
        elif cfg["filter"] == "S":
            out[q] = sum(a >= cfg["threshold"] for a in r["scores"])
        else:
            raise ValueError("Unknown filter")
    return out


def load(bundle_path, manifest_path):
    bundle = json.loads(Path(bundle_path).read_text(encoding="utf-8"))
    man = list(csv.DictReader(open(manifest_path, encoding="utf-8", newline="")))
    ids = [r["query_id"] for r in man]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate manifest queries")
    src = {}
    for name, rows in bundle["sources"].items():
        byq = {r["query_id"]: r for r in rows}
        if set(byq) != set(ids):
            raise ValueError(f"Source coverage mismatch: {name}")
        for r in man:
            x = byq[r["query_id"]]
            if x["image_id"] != r["image_id"] or not (len(x["boxes"]) == len(x["scores"]) == len(x["clip"])):
                raise ValueError("Unaligned source")
        src[name] = byq
    return bundle, man, src


def metrics(c, man):
    valid = [r for r in man if r["presence_status"] != "uncertain"]
    def mae(rows):
        e = [abs(c[r["query_id"]] - int(r["gt_count"])) for r in rows]
        return dict(n=len(e), MAE=sum(e) / len(e), RMSE=math.sqrt(sum(x * x for x in e) / len(e))) if e else None
    pres = [r for r in valid if r["presence_status"] == "present"]; absn = [r for r in valid if r["presence_status"] == "absent"]
    return dict(all=mae(valid), present=mae(pres),
                absent=dict(n=len(absn), FPR_absent=sum(c[r["query_id"]] > 0 for r in absn) / len(absn),
                            MeanAbsentCount=sum(c[r["query_id"]] for r in absn) / len(absn)) if absn else None)


def bootstrap(ca, cb, man, n=5000, seed=331):
    valid = [r for r in man if r["presence_status"] != "uncertain"]
    imgs = sorted({r["image_id"] for r in valid}); by = {i: [r for r in valid if r["image_id"] == i] for i in imgs}
    d = lambda rows: sum(abs(cb[r["query_id"]] - int(r["gt_count"])) - abs(ca[r["query_id"]] - int(r["gt_count"])) for r in rows) / len(rows)
    rng = random.Random(seed); bs = sorted(d([r for i in (rng.choice(imgs) for _ in imgs) for r in by[i]]) for _ in range(n))
    e = lambda c: {r["query_id"]: abs(c[r["query_id"]] - int(r["gt_count"])) for r in valid}
    ea, eb = e(ca), e(cb)
    return dict(diff=d(valid), ci95=[bs[int(.025 * n) - 1], bs[int(.975 * n) - 1]], n_images=len(imgs),
                better=sum(eb[q] < ea[q] for q in ea), worse=sum(eb[q] > ea[q] for q in ea), same=sum(eb[q] == ea[q] for q in ea))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle"); ap.add_argument("--manifest"); ap.add_argument("--out")
    ap.add_argument("--verify-dev", action="store_true")
    a = ap.parse_args()
    fz = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert fz["status"] == "FROZEN_V2"
    configs = {fz["main"]["name"]: fz["main"], **fz["companions_report_only"]}
    if a.verify_dev:
        _, man, src = load(ROOT / f"{DEV}_offline_T/bundle.json", ROOT / "experiments/countgdpp/dev_test_v2/dev/manifest.csv")
        sel = json.loads((ROOT / f"{DEV}_dev_selection_T/selection.json").read_text(encoding="utf-8"))
        keymap = {fz["main"]["name"]: "tau0.200+F", "B0": "B0", "B2": "B2", "C6 = B0+F": "B0+F", "B2+F": "B2+F"}
        ok = True
        for name, cfg in configs.items():
            c = counts_for(cfg, src[cfg["source"]]); same = c == sel["per_query_counts"][keymap[name]]
            ok &= same; print(f"{name:<20} counts khớp dev selection: {same} | MAE {metrics(c, man)['all']['MAE']:.4f}")
        print("VERIFY-DEV:", "PASS" if ok else "FAIL"); raise SystemExit(0 if ok else 1)
    meta = json.loads(META.read_text(encoding="utf-8"))
    if meta["status"] != "LOCKED":
        raise ValueError("Data set is not LOCKED")
    locked = meta["locked_file_sha256"]
    mrel = Path(a.manifest).resolve().relative_to((ROOT / "experiments/countgdpp/dev_test_v2").resolve()).as_posix()
    if locked.get(mrel) != sha(a.manifest):
        raise ValueError(f"Manifest {mrel} differs from the locked hash")
    out = ROOT / a.out
    if out.exists():
        raise SystemExit("Output exists; the test is run once — do not overwrite")
    bundle, man, src = load(a.bundle, a.manifest)
    counts = {name: counts_for(cfg, src[cfg["source"]]) for name, cfg in configs.items()}
    table = {name: metrics(c, man) for name, c in counts.items()}
    comps = {name: bootstrap(counts["B0"], counts[name], man) for name in configs if name != "B0"}
    out.mkdir(parents=True)
    res = dict(status="TEST_RESULT_FROZEN_V2", freeze_sha256=sha(FREEZE), bundle_sha256=sha(a.bundle), manifest=mrel, manifest_sha256=sha(a.manifest),
               uncertain_excluded=[r["query_id"] for r in man if r["presence_status"] == "uncertain"], summary=table,
               vs_B0_image_bootstrap=comps, per_query_counts=counts, tool_sha256=sha(__file__))
    (out / "result.json").write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{'cách':<20}{'MAE':>7}{'MAE có mặt':>12}{'FPR_abs':>9}")
    for k, v in table.items():
        print(f"{k:<20}{v['all']['MAE']:>7.2f}{v['present']['MAE']:>12.2f}{v['absent']['FPR_absent']:>9.2f}")
    for k, v in comps.items():
        print(f"{k} vs B0: {v['diff']:+.2f} CI [{v['ci95'][0]:+.2f}, {v['ci95'][1]:+.2f}] tốt/kém/bằng {v['better']}/{v['worse']}/{v['same']}")
    print("Saved:", out)


if __name__ == "__main__":
    main()
