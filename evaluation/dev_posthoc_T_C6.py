"""Post-hoc on the LOCKED dev v2 selection outputs (no model run, no reselection; the freeze is unchanged).

Answers two review questions (feedback 15/11):
  (1) How much of the pass-2 harm (B2 - B0) does removing the max(text, exemplar) scoring (variant T) recover?
      share = (MAE_B2 - MAE_T) / (MAE_B2 - MAE_B0), with image-level bootstrap CIs (5000, seed 331) of
      T - B0, B2 - T, B2 - B0 and of the share itself.
  (2) Where did C6 (= B0+F) rank on dev among all configurations, and how far was it from the D9 winner
      (bootstrap CI of C6 - winner on dev)?  Also how far the winner was from the runner-ups.
Inputs: results/countgdpp/p1_dev_kaggle_t4_20261111_1203_{m5,m10}_dev_selection_T/selection.json
Output: results/countgdpp/p1_dev_kaggle_t4_20261111_1203_posthoc_20261115/summary.json
Run from the CS331 root:  python evaluation/dev_posthoc_T_C6.py
"""
import csv, json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = "results/countgdpp/p1_dev_kaggle_t4_20261111_1203"
MAN = ROOT / "experiments/countgdpp/dev_test_v2/dev/manifest.csv"
OUT = ROOT / f"{RUN}_posthoc_20261115"


def load(m):
    return json.loads((ROOT / f"{RUN}_{m}_dev_selection_T" / "selection.json").read_text(encoding="utf-8"))


def main():
    OUT.mkdir(exist_ok=True)
    man = [r for r in csv.DictReader(open(MAN, encoding="utf-8", newline="")) if r["presence_status"] != "uncertain"]
    imgs = sorted({r["image_id"] for r in man}); by = {i: [r for r in man if r["image_id"] == i] for i in imgs}
    gt = {r["query_id"]: int(r["gt_count"]) for r in man}
    sel = {m: load(m) for m in ("m5", "m10")}
    pq5 = sel["m5"]["per_query_counts"]

    def mae(c, sample=None):
        rows = [r for i in (sample or imgs) for r in by[i]]
        return sum(abs(c[r["query_id"]] - gt[r["query_id"]]) for r in rows) / len(rows)

    def boot(fn, n=5000, seed=331):
        rnd = random.Random(seed); v = []
        for _ in range(n):
            smp = [rnd.choice(imgs) for _ in imgs]
            x = fn(smp)
            if x is not None:
                v.append(x)
        v.sort(); return [v[int(.025 * len(v))], v[int(.975 * len(v)) - 1]], len(v)

    B0, B2, T = pq5["B0"], pq5["B2"], pq5["T"]
    part1 = dict(MAE=dict(B0=mae(B0), T=mae(T), B2=mae(B2)))
    for name, (a, b) in {"T-B0": (T, B0), "B2-T": (B2, T), "B2-B0": (B2, B0)}.items():
        ci, _ = boot(lambda smp: mae(a, smp) - mae(b, smp))
        part1[name] = dict(diff=mae(a) - mae(b), ci95=ci)

    def share(smp=None):
        d = mae(B2, smp) - mae(B0, smp)
        return None if abs(d) < 1e-9 else (mae(B2, smp) - mae(T, smp)) / d
    ci, nv = boot(share)
    part1["share_recovered_by_T"] = dict(value=share(), ci95=ci, valid_draws=nv,
                                         note="ratio of two noisy differences; unstable when B2-B0 is near 0")

    # (2) dev ranking over every configuration of both runs (M5, M10), main metric MAE_all
    table = []
    for m, s in sel.items():
        for name, c in s["per_query_counts"].items():
            table.append(dict(run=m, config=name, MAE=mae(c), source=name.split("+")[0]))
    table.sort(key=lambda r: r["MAE"])
    for i, r in enumerate(table, 1):
        r["rank"] = i
    winner = next(r for r in table if r["run"] == "m5" and r["config"] == "tau0.200+F")
    c6 = next(r for r in table if r["run"] == "m5" and r["config"] == "B0+F")
    W, C = sel["m5"]["per_query_counts"]["tau0.200+F"], pq5["B0+F"]
    ci, _ = boot(lambda smp: mae(C, smp) - mae(W, smp))
    # distinct rank among "families" (ignore duplicate B0/B2-derived rows repeated in both runs)
    fam = []
    seen = set()
    for r in table:
        key = r["config"] if not r["config"].startswith("tau") else f"{r['run']}:{r['config']}"
        if key in seen:
            continue
        seen.add(key); fam.append(r)
    part2 = dict(n_rows=len(table), winner=winner, C6=c6,
                 C6_rank_unique=next(i for i, r in enumerate(fam, 1) if r["config"] == "B0+F"), n_unique=len(fam),
                 C6_minus_winner=dict(diff=mae(C) - mae(W), ci95=ci),
                 top12_unique=[dict(rank=i, run=r["run"], config=r["config"], MAE=round(r["MAE"], 3)) for i, r in enumerate(fam[:12], 1)])
    # rank by method family = (pass-2 source, filter): best member of each family
    def family(cfg):
        base, _, filt = cfg.partition("+")
        b = "B0" if base == "B0" else "B2" if base == "B2" else "T" if base == "T" else "P+T" if base.endswith("_T") else "P"
        return f"{b}+{filt}" if filt else b
    best = {}
    for r in table:
        f = family(r["config"])
        if f not in best or r["MAE"] < best[f]["MAE"]:
            best[f] = dict(family=f, run=r["run"], config=r["config"], MAE=round(r["MAE"], 3))
    fam_rank = sorted(best.values(), key=lambda x: x["MAE"])
    part2["family_ranking"] = [dict(rank=i, **x) for i, x in enumerate(fam_rank, 1)]
    # dev -> test drift of the five reported configurations (test numbers from the single frozen evaluation)
    test = json.loads((ROOT / "results/countgdpp/p1_test_kaggle_t4_20261111_1430_eval/result.json").read_text(encoding="utf-8"))["summary"]
    pairs = {"B0": ("B0", "B0"), "B2": ("B2", "B2"), "P(tau 0.20, M 5)+F": ("tau0.200+F", "P(tau 0.20, M 5)+F"),
             "B2+F": ("B2+F", "B2+F"), "C6 = B0+F": ("B0+F", "C6 = B0+F")}
    part2["dev_to_test"] = {k: dict(dev=mae(pq5[d]), test=test[t]["all"]["MAE"], change=test[t]["all"]["MAE"] - mae(pq5[d]))
                            for k, (d, t) in pairs.items()}
    res = dict(status="POST_HOC_ANALYSIS (dev, không chọn lại cấu hình)", T_share=part1, C6_rank=part2)
    (OUT / "summary.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
