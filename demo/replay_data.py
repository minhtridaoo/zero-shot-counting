"""Nạp kết quả ĐÃ LƯU của lần chạy test 11/11/2026 và tính lại số đếm theo cấu hình đã khóa.

Không chạy CountGD++ hay CLIP. Chỉ đọc:
  - results/countgdpp/p1_test_kaggle_t4_20261111_1430_offline/bundle.json   (box, điểm CountGD++, cosine CLIP)
  - results/countgdpp/freeze_v2_20261111.json                              (bounds + threshold riêng từng cấu hình)
  - experiments/countgdpp/dev_test_v2/test/manifest.csv                    (GT, present/absent/uncertain)
  - results/countgdpp/p1_test_kaggle_t4_20261111_1430_eval/result.json     (số chính thức để đối chiếu)
  - results/countgdpp/p1_test_kaggle_t4_20261111_1430_posthoc_20261111/summary.json (shared box chính thức)

Công thức giống hệt experiments/countgdpp/apply_freeze_v2.py (counts_for, metrics) và
evaluation/test_xy_overlap_analysis.py (iou, matched, shared box X/Y). Hai file đó có hash trong audit nên
không import trực tiếp ở đây; thay vào đó `self_check()` so từng số đếm với result.json và dừng nếu lệch.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = "results/countgdpp/p1_test_kaggle_t4_20261111_1430"
BUNDLE = ROOT / f"{RUN}_offline/bundle.json"
FREEZE = ROOT / "results/countgdpp/freeze_v2_20261111.json"
MANIFEST = ROOT / "experiments/countgdpp/dev_test_v2/test/manifest.csv"
RESULT = ROOT / f"{RUN}_eval/result.json"
POSTHOC = ROOT / f"{RUN}_posthoc_20261111/summary.json"

# Tên hiển thị -> khóa trong freeze / result.json / posthoc
CONFIGS = {
    "B0": dict(freeze=("companions_report_only", "B0"), result="B0", posthoc="B0",
               desc="CountGD++ một lượt"),
    "B2": dict(freeze=("companions_report_only", "B2"), result="B2", posthoc="B2",
               desc="CountGD++ hai lượt (pseudo-exemplar gốc)"),
    "P+F": dict(freeze=("main",), result="P(tau 0.20, M 5)+F", posthoc="P+F (chính)",
                desc="Cấu hình chính đã khóa: P(τ 0.20, M 5) rồi lọc F"),
    "C6": dict(freeze=("companions_report_only", "C6 = B0+F"), result="C6 = B0+F", posthoc="C6 = B0+F",
               desc="Đối chứng khai báo trước: B0 rồi lọc F (ngưỡng riêng)"),
}
EXPECTED_MAE = {"B0": 7.71, "B2": 9.61, "P+F": 5.82, "C6": 4.63}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm(v, b):
    lo, hi = b
    return .5 if lo == hi else max(0., min(1., (v - lo) / (hi - lo)))


def fusion(a, c, bounds):
    return .5 * norm(a, bounds["countgd"]) + .5 * norm(c, bounds["clip"])


def iou(a, b):
    ix = max(0., min(a[2], b[2]) - max(a[0], b[0])); iy = max(0., min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.


def shared_flags(boxes, others, t=0.5):
    """True với box có ít nhất một box ở query kia trùng IoU >= t (định nghĩa trong báo cáo)."""
    return [any(iou(b, o) >= t for o in others) for b in boxes]


@dataclass
class Query:
    query_id: str
    image_id: str
    image_path: str
    prompt: str
    status: str          # present / absent / uncertain
    gt: int
    pair_type: str = ""


@dataclass
class Replay:
    queries: dict = field(default_factory=dict)      # query_id -> Query
    images: dict = field(default_factory=dict)       # image_id -> [query_id,...]
    src: dict = field(default_factory=dict)          # source -> query_id -> row
    cfg: dict = field(default_factory=dict)          # display name -> freeze cfg
    result: dict = field(default_factory=dict)
    posthoc: dict = field(default_factory=dict)

    # ------------------------------------------------------------ cấu hình
    def kept_mask(self, name, qid, threshold=None):
        """Danh sách True/False: box nào được giữ. threshold=None nghĩa là ngưỡng đã khóa."""
        c = self.cfg[name]; r = self.src[c["source"]][qid]
        if c["filter"] is None:
            return [True] * len(r["boxes"])
        th = c["threshold"] if threshold is None else threshold
        return [fusion(a, s, c["bounds"]) >= th for a, s in zip(r["scores"], r["clip"])]

    def fusion_scores(self, name, qid):
        c = self.cfg[name]; r = self.src[c["source"]][qid]
        if c["filter"] is None:
            return None
        return [fusion(a, s, c["bounds"]) for a, s in zip(r["scores"], r["clip"])]

    def boxes(self, name, qid):
        return self.src[self.cfg[name]["source"]][qid]["boxes"]

    def kept_boxes(self, name, qid, threshold=None):
        return [b for b, k in zip(self.boxes(name, qid), self.kept_mask(name, qid, threshold)) if k]

    def count(self, name, qid, threshold=None):
        return sum(self.kept_mask(name, qid, threshold))

    # ------------------------------------------------------------ chỉ số (giống apply_freeze_v2.metrics)
    def metrics(self, name):
        valid = [q for q in self.queries.values() if q.status != "uncertain"]
        err = lambda rows: [abs(self.count(name, q.query_id) - q.gt) for q in rows]
        e = err(valid); ep = err([q for q in valid if q.status == "present"])
        absn = [q for q in valid if q.status == "absent"]
        return dict(n=len(e), MAE=sum(e) / len(e), RMSE=math.sqrt(sum(x * x for x in e) / len(e)),
                    MAE_present=sum(ep) / len(ep),
                    FPR_absent=sum(self.count(name, q.query_id) > 0 for q in absn) / len(absn))

    def xy_pair(self, image_id):
        qs = [self.queries[q] for q in self.images[image_id]]
        pres = [q for q in qs if q.status == "present"]
        unc = [q for q in qs if q.status == "uncertain"]
        return pres, unc

    def shared_image(self, name, image_id):
        """(số box dùng chung, tổng box X+Y) cho một ảnh; None nếu ảnh không đủ 2 present / có uncertain."""
        pres, unc = self.xy_pair(image_id)
        if len(pres) != 2 or unc:
            return None
        X = self.kept_boxes(name, pres[0].query_id); Y = self.kept_boxes(name, pres[1].query_id)
        return sum(shared_flags(X, Y)) + sum(shared_flags(Y, X)), len(X) + len(Y)

    def shared_pooled(self, name):
        s = n = 0
        for img in self.images:
            r = self.shared_image(name, img)
            if r:
                s += r[0]; n += r[1]
        return s / n if n else float("nan")


def load() -> Replay:
    rp = Replay()
    fz = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert fz["status"] == "FROZEN_V2", "freeze không phải FROZEN_V2"
    for name, c in CONFIGS.items():
        node = fz
        for k in c["freeze"]:
            node = node[k]
        rp.cfg[name] = node
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    rp.src = {n: {r["query_id"]: r for r in rows} for n, rows in bundle["sources"].items()}
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            q = Query(r["query_id"], r["image_id"], r["image_path"], r["prompt"], r["presence_status"],
                      int(r["gt_count"]))
            rp.queries[q.query_id] = q
            rp.images.setdefault(q.image_id, []).append(q.query_id)
    rp.result = json.loads(RESULT.read_text(encoding="utf-8"))
    rp.posthoc = json.loads(POSTHOC.read_text(encoding="utf-8"))
    return rp


def self_check(rp: Replay, verbose=True) -> list[str]:
    """So với artifact chính thức. Trả danh sách dòng báo cáo; raise AssertionError nếu lệch."""
    out = []
    res = rp.result
    for p, key in ((FREEZE, "freeze_sha256"), (BUNDLE, "bundle_sha256"), (MANIFEST, "manifest_sha256")):
        h = sha(p)
        assert h == res[key], f"Hash {p.name} khác result.json"
        out.append(f"hash {p.name}: {h[:12]}… khớp result.json")
    assert len(rp.queries) == 120, "manifest phải có 120 query"
    unc = [q for q in rp.queries.values() if q.status == "uncertain"]
    assert [q.query_id for q in unc] == res["uncertain_excluded"], "query uncertain khác lần chấm chính thức"
    out.append(f"120 query; loại {len(unc)} uncertain ({', '.join(q.query_id for q in unc)}) → 119 query hợp lệ")
    for name, c in CONFIGS.items():
        official = res["per_query_counts"][c["result"]]
        mine = {q: rp.count(name, q) for q in rp.queries}
        diff = [q for q in mine if mine[q] != official[q]]
        assert not diff, f"{name}: số đếm lệch result.json ở {diff[:5]}"
        m = rp.metrics(name); o = res["summary"][c["result"]]
        assert abs(m["MAE"] - o["all"]["MAE"]) < 1e-9 and abs(m["RMSE"] - o["all"]["RMSE"]) < 1e-9
        assert abs(m["MAE_present"] - o["present"]["MAE"]) < 1e-9
        assert abs(m["FPR_absent"] - o["absent"]["FPR_absent"]) < 1e-9
        assert round(m["MAE"], 2) == EXPECTED_MAE[name], f"{name}: MAE {m['MAE']:.4f} khác số trên slide"
        sh = rp.shared_pooled(name); sh_o = rp.posthoc["overlap"][c["posthoc"]]["0.5"]["shared_xy_pooled"]
        assert abs(sh - sh_o) < 1e-12, f"{name}: shared box {sh} khác posthoc {sh_o}"
        out.append(f"{name:<4} số đếm 120/120 khớp · MAE {m['MAE']:.2f} · RMSE {m['RMSE']:.2f} · "
                   f"MAE present {m['MAE_present']:.2f} · FPR_absent {m['FPR_absent']:.3f} · shared X/Y {sh:.1%}")
    if verbose:
        print("\n".join(out))
    return out


if __name__ == "__main__":
    self_check(load())
    print("SELF-CHECK: PASS")
