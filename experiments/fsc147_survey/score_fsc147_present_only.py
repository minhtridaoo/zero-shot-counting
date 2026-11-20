"""Chấm khảo sát bổ sung FSC-147 test, 300 ảnh (chỉ câu có mặt) bằng cấu hình ĐÃ KHÓA freeze v2 — không chọn lại, không chỉnh ngưỡng.

Vì sao có file mới: apply_freeze_v2.py (đã ghi hash, không sửa) chia cho số câu vắng mặt và đòi manifest MUCCA đã khóa;
FSC-147 không có câu vắng mặt. File này chỉ IMPORT counts_for/norm từ apply_freeze_v2.py, nên cách tính số đếm
(gồm bộ lọc F với bounds/ngưỡng lấy nguyên từ freeze) giống hệt lần chấm test MUCCA.

Đầu vào: bundle.json từ bundle_offline_v2.py (sau p1_controls.py) của MỘT lần chạy run_b2_verified_pseudo.py
(tau 0.20, M 5, --replay-b2) trên experiments/fsc147_survey/sample_300/inputs.jsonl.

So sánh khai báo trước (Δ = MAE(A) − MAE(B); bootstrap theo ảnh, 5000 lần, seed 331, mỗi ảnh một câu):
  CHÍNH  B0 − B2         chỉ khác giữ/bỏ lượt 2 (cùng lượt 1, cùng run, không lọc). Δ > 0: bỏ lượt 2 làm sai số tăng.
  PHỤ    P+F − B2        cấu hình đã khóa so với CountGD++ hai lượt thông thường.
  PHỤ    P+F − B0
  BÁO KÈM (mô tả, không quy cho lượt 2): C6 = B0+F, B2+F, và C6 − B2+F (hai bộ lọc có ngưỡng khác nhau trong freeze).
Chỉ số: MAE, RMSE, Bias, tổng đếm thừa / đếm thiếu, số câu trả 0; toàn mẫu và theo nhóm GT <= 40 / > 40.

Example (from CS331 root):
  python experiments/fsc147_survey/score_fsc147_present_only.py --run results/countgdpp/RUN \
      --bundle results/countgdpp/RUN_offline/bundle.json --out results/countgdpp/RUN_fsc147_eval
"""
import argparse
import csv
import hashlib
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/countgdpp"))
from apply_freeze_v2 import FREEZE, counts_for  # noqa: E402  (chỉ import, không sửa file đã khóa)

FREEZE_SHA256 = "64e89ef53eab306fdbb33cfc39797749ff17cc8635f46ae381d96e45c4f6736d"
SAMPLE = ROOT / "experiments/fsc147_survey/sample_300"
N_BOOT, SEED = 5000, 331
MAIN = "P(tau 0.20, M 5)+F"
PAIRS = [("primary", "B0", "B2", True), ("secondary", MAIN, "B2", True), ("secondary", MAIN, "B0", True),
         ("report_only_not_clean", "C6 = B0+F", "B2+F", False)]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def metrics(c, rows):
    if not rows:
        return None
    e = [c[r["query_id"]] - int(r["gt_count"]) for r in rows]
    return dict(n=len(e), MAE=sum(map(abs, e)) / len(e), RMSE=math.sqrt(sum(x * x for x in e) / len(e)), Bias=sum(e) / len(e),
                overcount_total=sum(x for x in e if x > 0), undercount_total=-sum(x for x in e if x < 0),
                gt_total=sum(int(r["gt_count"]) for r in rows), zero_predictions=sum(c[r["query_id"]] == 0 for r in rows))


def bootstrap(ca, cb, rows):
    """Δ = MAE(A) − MAE(B), bootstrap GHÉP CẶP theo ảnh: mỗi lần lấy lại cùng một bộ ảnh (có hoàn lại) cho cả A và B.
    Mỗi ảnh có đúng một câu. CI lấy phân vị như apply_freeze_v2.py."""
    images = sorted({r["image_id"] for r in rows})
    if len(images) != len(rows):
        raise ValueError("Mỗi ảnh phải có đúng một câu")
    by_image = {r["image_id"]: r for r in rows}
    err = lambda c, r: abs(c[r["query_id"]] - int(r["gt_count"]))
    delta = lambda imgs: sum(err(ca, by_image[i]) - err(cb, by_image[i]) for i in imgs) / len(imgs)
    rng = random.Random(SEED)
    bs = sorted(delta([rng.choice(images) for _ in images]) for _ in range(N_BOOT))
    lo, hi = bs[int(.025 * N_BOOT) - 1], bs[int(.975 * N_BOOT) - 1]
    reading = ("A kém hơn B trên mẫu này (CI > 0)" if lo > 0 else "A tốt hơn B trên mẫu này (CI < 0)" if hi < 0
               else "chưa thấy khác biệt rõ (CI chứa 0; không chứng minh hai cách như nhau)")
    ea = {r["query_id"]: err(ca, r) for r in rows}; eb = {r["query_id"]: err(cb, r) for r in rows}
    return dict(diff=delta(images), ci95=[lo, hi], reading=reading, n_images=len(rows),
                A_better=sum(ea[q] < eb[q] for q in ea), A_worse=sum(ea[q] > eb[q] for q in ea), same=sum(ea[q] == eb[q] for q in ea))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="Thư mục run_b2_verified_pseudo.py, tương đối với CS331")
    ap.add_argument("--bundle", required=True, help="bundle.json từ bundle_offline_v2.py của cùng run")
    ap.add_argument("--out", required=True, help="Thư mục kết quả mới, tương đối với CS331; không ghi đè")
    ap.add_argument("--sample-dir", default=str(SAMPLE), help="Mặc định: mẫu cố định sample_300. Chỉ đổi khi chạy self-test dữ liệu giả")
    a = ap.parse_args()
    sample = Path(a.sample_dir) if Path(a.sample_dir).is_absolute() else ROOT / a.sample_dir
    out = ROOT / a.out
    if out.exists():
        raise SystemExit("Đã có kết quả. Khảo sát chạy một lần; không ghi đè.")

    meta = json.loads((sample / "sample_meta.json").read_text(encoding="utf-8"))
    if meta["status"] != "SAMPLE_FIXED_BEFORE_RUN":
        raise ValueError("Mẫu chưa cố định")
    for name, digest in meta["file_sha256"].items():
        if sha(sample / name) != digest:
            raise ValueError(f"{name} khác hash lúc tạo mẫu")
    if sha(FREEZE) != FREEZE_SHA256:
        raise ValueError("freeze v2 khác sha256 đã khóa")
    fz = json.loads(FREEZE.read_text(encoding="utf-8"))
    run_cfg = json.loads((ROOT / a.run / "run_config.json").read_text(encoding="utf-8"))
    args_fz = fz["runner"]["args"]
    if (run_cfg.get("status") != "complete" or run_cfg.get("input_sha256") != meta["file_sha256"]["inputs.jsonl"]
            or run_cfg.get("tau_pseudo") != args_fz["tau_pseudo"] or run_cfg.get("m") != args_fz["m"] or "B2" not in run_cfg.get("outputs", {})):
        raise ValueError("Run không hoàn tất, khác inputs của mẫu, hoặc khác tau/M/--replay-b2 của freeze")

    bundle = json.loads((ROOT / a.bundle).read_text(encoding="utf-8"))
    if Path(bundle["run_id"]).as_posix().rstrip("/") != Path(a.run).as_posix().rstrip("/"):
        raise ValueError(f"Bundle thuộc run khác: {bundle['run_id']}")
    man = list(csv.DictReader((sample / "manifest.csv").open(encoding="utf-8", newline="")))
    ids = {r["query_id"] for r in man}
    src = {}
    for name, rows in bundle["sources"].items():
        byq = {r["query_id"]: r for r in rows}
        if set(byq) != ids:
            raise ValueError(f"Nguồn {name} không phủ đúng {len(ids)} câu của mẫu")
        for r in man:
            x = byq[r["query_id"]]
            if x["image_id"] != r["image_id"] or not (len(x["boxes"]) == len(x["scores"]) == len(x["clip"])):
                raise ValueError(f"Nguồn {name} lệch ở {r['query_id']}")
        src[name] = byq

    configs = {fz["main"]["name"]: fz["main"], **fz["companions_report_only"]}
    if MAIN not in configs:
        raise ValueError("Tên cấu hình chính khác freeze")
    counts = {name: counts_for(cfg, src[cfg["source"]]) for name, cfg in configs.items()}
    strata = sorted({r["stratum"] for r in man})
    groups = {"all": man, **{s: [r for r in man if r["stratum"] == s] for s in strata}}
    table = {g: {name: metrics(c, rows) for name, c in counts.items()} for g, rows in groups.items()}
    comparisons = [dict(role=role, A=A, B=B, clean_pass2_pair=(role == "primary"), **bootstrap(counts[A], counts[B], man))
                   for role, A, B, _ in PAIRS]
    primary_by_stratum = {s: bootstrap(counts["B0"], counts["B2"], groups[s]) for s in strata}

    out.mkdir(parents=True)
    res = dict(status="FSC147_SURVEY_RESULT", scope="khảo sát bổ sung 300 ảnh FSC-147 test; chỉ câu có mặt; không phải benchmark đầy đủ, không nói gì về lớp vắng mặt; không thay kết quả chính MUCCA",
               crop=run_cfg.get("crop"), synthetic=run_cfg.get("synthetic"), device=run_cfg.get("device"),
               freeze_sha256=FREEZE_SHA256, run=a.run, run_config_sha256=sha(ROOT / a.run / "run_config.json"),
               bundle_sha256=sha(ROOT / a.bundle), sample_dir=str(a.sample_dir), sample_meta_sha256=sha(sample / "sample_meta.json"),
               delta_definition="Δ = MAE(A) − MAE(B)", bootstrap=dict(n=N_BOOT, seed=SEED, unit="ảnh"),
               summary=table, comparisons=comparisons, primary_by_stratum=primary_by_stratum,
               per_query_counts=counts, tool_sha256=sha(__file__))
    (out / "result.json").write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out / "per_query.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["query_id", "image_id", "prompt", "stratum", "gt_count", *counts])
        for r in man:
            w.writerow([r["query_id"], r["image_id"], r["prompt"], r["stratum"], r["gt_count"], *(counts[n][r["query_id"]] for n in counts)])

    for g, t in table.items():
        print(f"\n[{g}] n={t['B0']['n']}")
        print(f"{'cách':<22}{'MAE':>8}{'RMSE':>9}{'Bias':>8}{'thừa':>8}{'thiếu':>8}{'=0':>5}")
        for name, m in t.items():
            print(f"{name:<22}{m['MAE']:>8.2f}{m['RMSE']:>9.2f}{m['Bias']:>+8.2f}{m['overcount_total']:>8}{m['undercount_total']:>8}{m['zero_predictions']:>5}")
    print()
    for c in comparisons:
        print(f"{c['role']:<22} {c['A']} − {c['B']}: {c['diff']:+.2f} CI [{c['ci95'][0]:+.2f}, {c['ci95'][1]:+.2f}] → {c['reading']}")
    for s, c in primary_by_stratum.items():
        print(f"primary [{s}] B0 − B2: {c['diff']:+.2f} CI [{c['ci95'][0]:+.2f}, {c['ci95'][1]:+.2f}] (n={c['n_images']})")
    print("Saved:", out)


if __name__ == "__main__":
    main()
