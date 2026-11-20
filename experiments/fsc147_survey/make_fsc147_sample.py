"""Khảo sát bổ sung FSC-147 (khai báo trước 20/11): lấy mẫu ngẫu nhiên 300 ảnh FSCD-147 test, seed 331.

Đọc nhãn có sẵn trong repo (CountGDPlusPlus/data/fscd147/countgd_test_fscd147.json, sha256 đã ghi trong
reports/BENCHMARK_FSCD147.md), KHÔNG đọc ảnh và KHÔNG xem dự đoán nào. Mẫu chọn chỉ bằng random.Random(331).sample
trên danh sách id ảnh đã sắp xếp — không chọn theo số vật, loại hay kết quả.

Ghi ra (không ghi đè):
  <out>/inputs.jsonl     schema v1 cho run_b2_verified_pseudo.py (KHÔNG có GT)
  <out>/manifest.csv     GT để chấm: query_id, image_id, file_name, prompt, gt_count, stratum, presence_status=present
  <out>/sample_meta.json seed, hash nguồn, hash hai file trên, phân bố GT theo nhóm

GT = số chú thích điểm (area == 4) của ảnh; 3 khung mẫu (area != 4) bị loại, giống loader CountGD++
(CountGDPlusPlus/datasets/coco.py). Câu truy vấn = tên lớp FSC-147 nguyên văn (số ít, như benchmark gốc).
Nhóm khai báo trước: GT <= 40 ("le40", gần khoảng 3–40 vật của MUCCA) và GT > 40 ("gt40").

Example (from CS331 root):
  python experiments/fsc147_survey/make_fsc147_sample.py --out experiments/fsc147_survey/sample_300
"""
import argparse
import collections
import csv
import hashlib
import json
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANNO = ROOT / "CountGDPlusPlus/data/fscd147/countgd_test_fscd147.json"
ANNO_SHA256 = "e301c6933396b98040ff9b7d86e18d66c14cc8c2118ce0e4cae24f4f5807c35c"
IMAGE_DIR = "data_external/fsc147/images_384_VarV2"  # ảnh giải nén trên Kaggle vào đây (data_external/ bị .gitignore)
SEED, N = 331, 300
STRATA = (("le40", lambda g: g <= 40), ("gt40", lambda g: g > 40))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Thư mục mới, tương đối với CS331")
    a = ap.parse_args()
    out = ROOT / a.out
    if out.exists():
        raise SystemExit("Thư mục đã có. Mẫu chỉ tạo một lần; không ghi đè.")
    if sha(ANNO) != ANNO_SHA256:
        raise ValueError("Nhãn FSCD-147 test khác hash đã kiểm 20/10")
    d = json.loads(ANNO.read_text(encoding="utf-8"))
    cats = {c["id"]: c["name"] for c in d["categories"]}
    images = {im["id"]: im for im in d["images"]}
    if len(images) != 1190 or len({im["file_name"] for im in images.values()}) != 1190:
        raise ValueError("Cần đúng 1190 ảnh, tên không trùng")
    points, exemplars, classes = collections.Counter(), collections.Counter(), collections.defaultdict(set)
    for ann in d["annotations"]:
        (points if ann["area"] == 4 else exemplars)[ann["image_id"]] += 1
        classes[ann["image_id"]].add(ann["category_id"])
    for i in images:
        if exemplars[i] != 3 or len(classes[i]) != 1 or points[i] <= 0:
            raise ValueError(f"Ảnh {i}: cần 3 khung mẫu, 1 lớp, GT > 0")

    chosen = sorted(random.Random(SEED).sample(sorted(images), N))
    inputs, manifest = [], []
    for i in chosen:
        im, g = images[i], points[i]
        stem = Path(im["file_name"]).stem
        if not stem.isdigit():
            raise ValueError(f"Tên ảnh lạ: {im['file_name']}")
        prompt = cats[next(iter(classes[i]))]
        image_id, query_id = f"fsc_{stem}", f"fq_{stem}"
        stratum = next(name for name, test in STRATA if test(g))
        inputs.append(dict(schema_version=1, image_id=image_id, query_id=query_id, image_path=f"{IMAGE_DIR}/{im['file_name']}", prompt=prompt))
        manifest.append(dict(query_id=query_id, image_id=image_id, coco_image_id=i, file_name=im["file_name"], prompt=prompt,
                             gt_count=g, stratum=stratum, presence_status="present"))

    out.mkdir(parents=True)
    (out / "inputs.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in inputs), encoding="utf-8")
    with (out / "manifest.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(manifest)
    gts = [r["gt_count"] for r in manifest]
    meta = dict(status="SAMPLE_FIXED_BEFORE_RUN", purpose="Khảo sát bổ sung: bỏ lượt 2 có làm giảm chất lượng đếm trên ảnh một loại không",
                source=ANNO.relative_to(ROOT).as_posix(), source_sha256=ANNO_SHA256, split="FSCD-147 test (= FSC-147 test, 1190 ảnh)",
                seed=SEED, n=N, method="random.Random(331).sample(sorted(coco image ids), 300)", image_dir=IMAGE_DIR,
                prompt_rule="tên lớp FSC-147 nguyên văn", gt_rule="số chú thích điểm (area == 4); bỏ 3 khung mẫu",
                strata={name: sum(r["stratum"] == name for r in manifest) for name, _ in STRATA},
                gt_summary=dict(min=min(gts), median=statistics.median(gts), max=max(gts), total=sum(gts)),
                classes=dict(collections.Counter(r["prompt"] for r in manifest)),
                file_sha256={"inputs.jsonl": sha(out / "inputs.jsonl"), "manifest.csv": sha(out / "manifest.csv")},
                image_sha256="chưa có: ảnh chỉ có trên Kaggle; notebook ghi hash 300 ảnh lúc chạy", tool_sha256=sha(__file__))
    (out / "sample_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{N} ảnh | nhóm {meta['strata']} | GT {meta['gt_summary']} | {len(meta['classes'])} lớp")
    print("Saved:", out)


if __name__ == "__main__":
    main()
