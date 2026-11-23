"""Derived figures for the slides. Reads saved predictions only (no model run).

Usage:
  python final/shared/figures/make_slide_figures.py --data-root D:/MINHTRIHOCCODE/HOCKI5/CS331

--data-root must contain data_external/mucca_zenodo_19231375/MUCCA_1.0/images (gitignored data).
Prediction files are read from the repo (results/countgdpp/...). Outputs go next to this script.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

# (prediction file, image_id, [query_ids], output prefix)
PANELS = [
    ("results/countgdpp/p1_test_kaggle_t4_20261111_1430/predictions_B2.jsonl", "mcac_12",
     ["t01_1", "t01_2", "t01_3"], "xy_mcac12_B2"),
    ("results/countgdpp/p4_unseen_v1_b2_20261027/predictions.jsonl", "mcac_88",
     ["u07_1", "u07_2", "u07_3"], "xy_mcac88_B2"),
]
MONTAGE = ["mcac_12", "mcac_25", "mcac_171", "mcac_224", "mcac_88", "mcac_84"]


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def shared(boxes_a, boxes_b, thr):
    return sum(1 for a in boxes_a if any(iou(a, b) >= thr for b in boxes_b))


def load(pred_file, image_id):
    rows = {}
    for line in open(REPO / pred_file, encoding="utf-8"):
        d = json.loads(line)
        if d["image_id"] == image_id:
            rows[d["query_id"]] = d
    return rows


def draw(img_path, boxes, out, width=900):
    im = Image.open(img_path).convert("RGB")
    dr = ImageDraw.Draw(im)
    lw = max(2, im.width // 300)
    for b in boxes:
        dr.rectangle(b, outline=(230, 40, 40), width=lw)
    h = int(im.height * width / im.width)
    im.resize((width, h)).save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    args = ap.parse_args()
    img_dir = Path(args.data_root) / "data_external/mucca_zenodo_19231375/MUCCA_1.0/images"
    report = {}
    for pred_file, image_id, qids, prefix in PANELS:
        rows = load(pred_file, image_id)
        for q in qids:
            draw(img_dir / f"{image_id}.jpg", rows[q]["final_boxes"], OUT / f"{prefix}_{q}.png")
        a, b = rows[qids[0]]["final_boxes"], rows[qids[1]]["final_boxes"]
        report[prefix] = {
            "counts": {q: rows[q]["final_count"] for q in qids},
            "shared_iou0.5": f"{shared(a, b, 0.5)}/{len(a)}",
            "shared_iou0.8": f"{shared(a, b, 0.8)}/{len(a)}",
        }
    for image_id in MONTAGE:
        im = Image.open(img_dir / f"{image_id}.jpg").convert("RGB")
        w, h = 600, 420  # centre crop to a common aspect ratio
        s = max(w / im.width, h / im.height)
        im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1))
        l, t = (im.width - w) // 2, (im.height - h) // 2
        im.crop((l, t, l + w, t + h)).save(OUT / f"mucca_{image_id}.png")
    (OUT / "make_slide_figures_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
