"""Self-test cho score_fsc147_present_only.py bằng dữ liệu GIẢ có đáp án tính tay. Không dùng GPU, ảnh hay model.

CHỈ CHẠY KHI TRÍ CHO PHÉP (AGENTS.md quy tắc 4). Ghi file tạm ngoài repo (thư mục tạm của hệ điều hành) rồi xóa.

Dữ liệu giả: 4 ảnh, GT 10, 20 (nhóm le40) và 50, 60 (nhóm gt40). Mỗi nguồn có khung "tốt" (điểm CountGD 0.99,
CLIP 0.40: F giữ với mọi bounds trong freeze v2) và khung "xấu" (0.24 / 0.13: F bỏ). Số đếm theo (tốt, xấu):
  B0       (0,0) (15,5) (40,0) (60,10)  -> B0  = 0, 20, 40, 70;  C6   = 0, 15, 40, 60
  B2       (10,2)(18,0) (45,5) (60,0)   -> B2  = 12, 18, 50, 60; B2+F = 10, 18, 45, 60
  tau0.200 (10,0)(20,5) (50,5) (58,0)   -> P   = 10, 25, 55, 58; P+F  = 10, 20, 50, 58
Đáp án tính tay ở EXPECTED bên dưới. Kiểm thêm: Δ = MAE(A) − MAE(B) của các cặp khai báo, nhóm gt40 có Δ hằng
nên CI phải đúng [10, 10], và 5 trường hợp phải bị từ chối: thư mục kết quả đã có, crop=True, synthetic=True,
query_id trùng trong một nguồn, manifest bị sửa (sai hash).

Example (from CS331 root):  python experiments/fsc147_survey/selftest_score_fsc147.py
"""
import csv
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCORER = HERE / "score_fsc147_present_only.py"
GOOD, BAD = (0.99, 0.40), (0.24, 0.13)
GT = {"q1": 10, "q2": 20, "q3": 50, "q4": 60}
SPEC = {"B0": [(0, 0), (15, 5), (40, 0), (60, 10)],
        "B2": [(10, 2), (18, 0), (45, 5), (60, 0)],
        "tau0.200": [(10, 0), (20, 5), (50, 5), (58, 0)]}
MAIN = "P(tau 0.20, M 5)+F"
EXPECTED = {  # name: (MAE, RMSE, Bias, thừa, thiếu, số câu = 0)
    "B0": (7.5, math.sqrt(75), -2.5, 10, 20, 1),
    "B2": (1.0, math.sqrt(2), 0.0, 2, 2, 0),
    MAIN: (0.5, 1.0, -0.5, 0, 2, 0),
    "C6 = B0+F": (6.25, 7.5, -6.25, 0, 25, 1),
    "B2+F": (1.75, math.sqrt(29 / 4), -1.75, 0, 7, 0),
}
EXPECTED_DIFF = {("B0", "B2"): 6.5, (MAIN, "B2"): -0.5, (MAIN, "B0"): -7.0, ("C6 = B0+F", "B2+F"): 4.5}
EXPECTED_STRATUM = {"le40": 3.0, "gt40": 10.0}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build(tmp):
    sample, run = tmp / "sample", tmp / "run"
    sample.mkdir(); run.mkdir()
    qids = sorted(GT)
    inputs = [dict(schema_version=1, image_id=f"img_{q}", query_id=q, image_path=f"fake/{q}.jpg", prompt="apple") for q in qids]
    (sample / "inputs.jsonl").write_bytes("".join(json.dumps(r) + "\n" for r in inputs).encode())
    with (sample / "manifest.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["query_id", "image_id", "prompt", "gt_count", "stratum", "presence_status"])
        for q in qids:
            w.writerow([q, f"img_{q}", "apple", GT[q], "le40" if GT[q] <= 40 else "gt40", "present"])
    meta = dict(status="SAMPLE_FIXED_BEFORE_RUN", file_sha256={n: sha(sample / n) for n in ("inputs.jsonl", "manifest.csv")})
    (sample / "sample_meta.json").write_text(json.dumps(meta), encoding="utf-8")
    cfg = dict(status="complete", input_sha256=meta["file_sha256"]["inputs.jsonl"], tau_pseudo=[0.2], m=5,
               outputs={"B2": "predictions_B2.jsonl", "tau0.200": "predictions_tau0.200.jsonl"}, crop=False, synthetic=False,
               uses_ground_truth=False, device="fake")
    (run / "run_config.json").write_text(json.dumps(cfg), encoding="utf-8")
    sources = {}
    for name, spec in SPEC.items():
        rows = []
        for q, (g, b) in zip(qids, spec):
            boxes = [GOOD] * g + [BAD] * b
            rows.append(dict(query_id=q, image_id=f"img_{q}", boxes=[[0, 0, 1, 1]] * len(boxes),
                             scores=[x[0] for x in boxes], clip=[x[1] for x in boxes]))
        sources[name] = rows
    (tmp / "bundle.json").write_text(json.dumps(dict(run_id=run.as_posix(), sources=sources)), encoding="utf-8")
    return sample, run


def score(tmp, sample, run, out):
    return subprocess.run([sys.executable, str(SCORER), "--run", run.as_posix(), "--bundle", (tmp / "bundle.json").as_posix(),
                           "--out", out.as_posix(), "--sample-dir", sample.as_posix()], capture_output=True, text=True, encoding="utf-8")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="fsc147_selftest_"))
    failures = []
    check = lambda ok, msg: None if ok else failures.append(msg)
    def rejects(p, expected, label):
        """Ca từ chối chỉ đạt khi script dừng VÀ báo đúng lý do mong đợi (không tính lỗi vì nguyên nhân khác)."""
        text = (p.stdout or "") + (p.stderr or "")
        check(p.returncode != 0 and expected in text, f"{label}: cần dừng với '{expected}', nhận mã {p.returncode}: {text[-400:]}")
    try:
        sample, run = build(tmp)
        out = tmp / "eval"
        p = score(tmp, sample, run, out)
        check(p.returncode == 0, f"chấm lỗi: {p.stderr[-800:]}")
        if p.returncode == 0:
            res = json.loads((out / "result.json").read_text(encoding="utf-8"))
            for name, (mae, rmse, bias, over, under, zero) in EXPECTED.items():
                m = res["summary"]["all"][name]
                got = (m["MAE"], m["RMSE"], m["Bias"], m["overcount_total"], m["undercount_total"], m["zero_predictions"])
                check(all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(got, (mae, rmse, bias, over, under, zero))), f"{name}: {got}")
            for c in res["comparisons"]:
                want = EXPECTED_DIFF[(c["A"], c["B"])]
                check(math.isclose(c["diff"], want, abs_tol=1e-9), f"Δ {c['A']} − {c['B']} = {c['diff']}, cần {want}")
                check(c["ci95"][0] <= c["ci95"][1], f"CI ngược: {c}")
            for s, want in EXPECTED_STRATUM.items():
                c = res["primary_by_stratum"][s]
                check(math.isclose(c["diff"], want, abs_tol=1e-9), f"nhóm {s}: Δ = {c['diff']}, cần {want}")
            check(res["primary_by_stratum"]["gt40"]["ci95"] == [10.0, 10.0], f"CI gt40 cần [10, 10]: {res['primary_by_stratum']['gt40']['ci95']}")
            check(sum(1 for _ in open(out / "per_query.csv", encoding="utf-8")) == 1 + len(GT), "per_query.csv sai số dòng")
            rejects(score(tmp, sample, run, out), "Đã có kết quả", "thư mục kết quả đã có")
        # run_config có crop=True -> phải từ chối
        cfg_path = run / "run_config.json"; good_cfg = cfg_path.read_text(encoding="utf-8")
        cfg_path.write_text(json.dumps(dict(json.loads(good_cfg), crop=True)), encoding="utf-8")
        rejects(score(tmp, sample, run, tmp / "eval_crop"), "run_config.crop phải là false", "crop=True")
        cfg_path.write_text(json.dumps(dict(json.loads(good_cfg), synthetic=True)), encoding="utf-8")
        rejects(score(tmp, sample, run, tmp / "eval_synth"), "run_config.synthetic phải là false", "synthetic=True")
        cfg_path.write_text(good_cfg, encoding="utf-8")
        # bundle có query trùng trong một nguồn -> phải từ chối
        bundle_path = tmp / "bundle.json"; good_bundle = bundle_path.read_text(encoding="utf-8")
        b = json.loads(good_bundle); b["sources"]["B2"].append(dict(b["sources"]["B2"][0]))
        bundle_path.write_text(json.dumps(b), encoding="utf-8")
        rejects(score(tmp, sample, run, tmp / "eval_dup"), "Nguồn B2 có query_id trùng", "query trùng")
        bundle_path.write_text(good_bundle, encoding="utf-8")
        with (sample / "manifest.csv").open("a", encoding="utf-8", newline="") as f:
            f.write("q5,img_q5,apple,7,le40,present\n")
        rejects(score(tmp, sample, run, tmp / "eval_tampered"), "manifest.csv khác hash lúc tạo mẫu", "manifest bị sửa")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if failures:
        print("SELF-TEST FAIL:"); [print(" -", f) for f in failures]; raise SystemExit(1)
    print("SELF-TEST PASS: số đếm, MAE/RMSE/Bias/thừa/thiếu/=0, Δ các cặp, nhóm, CI hằng, 5 trường hợp từ chối đúng lý do")


if __name__ == "__main__":
    main()
