"""Kiểm wrapper suy luận: chạy LiveEngine trên vài query test đã có kết quả chính thức và so số đếm 4 cách.

KHÔNG phải chạy lại test, không dùng để báo cáo: chỉ xác nhận wrapper ghép đúng pipeline đã khóa
(lượt 1, B2, P τ 0.20 M 5, F theo freeze). Trên Kaggle T4 (cùng môi trường lần test) số đếm phải trùng;
trên CPU có thể lệch nhẹ do số học khác GPU, nên CPU chỉ báo lệch, không coi là lỗi.

Dùng: python demo/live/check_against_test.py --device cuda --data-root <thư mục có data_external> [--queries t01_1 t01_2 t05_1]
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_engine as le  # noqa: E402
from PIL import Image  # noqa: E402

RESULT = le.ROOT / "results/countgdpp/p1_test_kaggle_t4_20261111_1430_eval/result.json"
MANIFEST = le.ROOT / "experiments/countgdpp/dev_test_v2/test/manifest.csv"
KEYS = {"B0": "B0", "B2": "B2", "P+F": "P(tau 0.20, M 5)+F", "C6": "C6 = B0+F"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--data-root", default=str(le.ROOT))
    ap.add_argument("--queries", nargs="+", default=["t01_1", "t01_2", "t05_1"])
    ap.add_argument("--log-dir", default=None)
    a = ap.parse_args()
    res = json.loads(RESULT.read_text(encoding="utf-8"))["per_query_counts"]
    man = {r["query_id"]: r for r in csv.DictReader(open(MANIFEST, encoding="utf-8", newline=""))}
    eng = le.LiveEngine(a.device, Path(a.log_dir) if a.log_dir else le.ROOT / "demo/live/logs_check")
    print(f"Engine: {eng.env['device']} · nạp {eng.load_s}s", flush=True)
    ok_all = True
    for q in a.queries:
        r = man[q]
        image = Image.open(Path(a.data_root) / r["image_path"]).convert("RGB")
        out, shared = eng.run_query(image, r["prompt"])
        got = {m: out[m]["count"] for m in le.METHODS}
        want = {m: res[KEYS[m]][q] for m in le.METHODS}
        same = got == want
        ok_all &= same
        print(f"{q} '{r['prompt']}': mới {got} | chính thức {want} | {'KHỚP' if same else 'LỆCH'} · lượt 1 {shared['stage1_ms']:.0f} ms"
              + "".join(f" · {m}: {out[m]['error']}" for m in le.METHODS if out[m]["error"]), flush=True)
    print("CHECK:", "PASS (khớp hết)" if ok_all else ("LỆCH — trên GPU T4 là lỗi, phải xem lại" if a.device == "cuda"
                                                       else "LỆCH trên CPU — có thể do số học CPU khác GPU; kiểm lại trên Kaggle T4"))
    raise SystemExit(0 if ok_all or a.device == "cpu" else 1)


if __name__ == "__main__":
    main()
