"""Render MUCCA source points for the human check of dev_test_v2 (W4: Triệu checks test, Trí checks dev).

CPU only: reads the MUCCA labels and images, no model, never edits the dataset files. For one split it writes, OUTSIDE the
repo (review images are not committed, D10):
  <out>/<split>/<qid>_<image_id>_GT.jpg  left half = query _1 class, right half = query _2 class, numbered source points
  <out>/<split>/index.html               one block per image: counts, proposed absent + backups, GT image, original image
  <out>/<split>/SOURCE_MANIFEST.json     hashes of the inputs and of every rendered image
The points are the MUCCA annotation itself, so matching the drawn count with gt_count proves nothing about correctness:
the reviewer must look at the objects.

Example (from the CS331 root):
  python experiments/countgdpp/render_gt_review_v2.py --split test --mucca C:/Users/diosodumb/Downloads/MUCCA_1.0 --out C:/Users/diosodumb/Documents/CS331_review
"""
import argparse
import csv
import hashlib
import html
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SET = ROOT / "experiments/countgdpp/dev_test_v2"
REPO_MUCCA = "data_external/mucca_zenodo_19231375/MUCCA_1.0"
MIN_WIDTH = 1000  # small MUCCA images are upscaled so points and numbers stay readable
HEADER = 80


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def render_half(img, points, title, scale):
    w, h = img.size
    width, height = round(w * scale), round(h * scale)
    canvas = Image.new("RGB", (width, height + HEADER), (17, 22, 30))
    canvas.paste(img.resize((width, height), Image.LANCZOS) if scale != 1 else img, (0, HEADER))
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 8), title, fill="white", font=font(26))
    draw.text((10, 46), "SOURCE GT ONLY - NOT MODEL OUTPUT - NOT HUMAN VERIFIED", fill=(240, 200, 120), font=font(20))
    radius = max(5, round(width / 250))
    label_font = font(max(16, round(width / 70)))
    for k, (x, y) in enumerate(points, start=1):
        cx, cy = x * scale, y * scale + HEADER
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(230, 40, 60), outline="white", width=2)
        # odd numbers to the right of the point, even to the left, so dense stacks (plates, crowds) stay readable
        right_side = ((cx + radius + 4, cy), "lm")
        left_side = ((cx - radius - 4, cy), "rm")
        pos, anchor = right_side if k % 2 else left_side
        left, top, right, bottom = draw.textbbox(pos, str(k), font=label_font, anchor=anchor)
        if left < 0 or right > width:  # flip to the other side at the image edge
            pos, anchor = right_side if anchor == "rm" else left_side
            left, top, right, bottom = draw.textbbox(pos, str(k), font=label_font, anchor=anchor)
        draw.rectangle((left - 3, top - 2, right + 3, bottom + 2), fill=(10, 10, 10))
        draw.text(pos, str(k), fill=(255, 230, 90), font=label_font, anchor=anchor)
    return canvas


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--split", choices=("dev", "test"), required=True)
    p.add_argument("--mucca", default=REPO_MUCCA, help="MUCCA_1.0 folder (absolute, or relative to CS331)")
    p.add_argument("--out", required=True, help="Output folder OUTSIDE the repo; <out>/<split>/ is created")
    args = p.parse_args()

    mucca = Path(args.mucca) if Path(args.mucca).is_absolute() else ROOT / args.mucca
    out = Path(args.out).resolve() / args.split
    if out.is_relative_to(ROOT.resolve()):
        raise SystemExit("--out must be outside the repo: review images are not committed")
    meta = json.loads((SET / "selection_meta.json").read_text(encoding="utf-8"))
    for name, digest in meta["mucca_file_sha256"].items():
        if sha256(mucca / name) != digest:
            raise SystemExit(f"{name} differs from the MUCCA copy recorded in selection_meta.json")
    ann = json.loads((mucca / "annotations.json").read_text(encoding="utf-8"))
    by_id = {Path(f).stem: f for f in ann}

    manifest_path, absent_path = SET / args.split / "manifest.csv", SET / "absent_candidates.csv"
    with manifest_path.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f)]
    with absent_path.open(encoding="utf-8", newline="") as f:
        absent = {r["image_id"]: r for r in csv.DictReader(f) if r["split"] == args.split}
    per_image = defaultdict(list)
    for r in rows:
        per_image[r["image_id"]].append(r)
    if sorted(per_image) != sorted(meta[args.split]):
        raise SystemExit("manifest images differ from selection_meta.json")

    out.mkdir(parents=True, exist_ok=True)
    files, blocks = [], []
    for image_id, qrows in sorted(per_image.items(), key=lambda kv: kv[1][0]["query_id"]):
        image_path = mucca / "images" / by_id[image_id]
        if sha256(image_path) != meta["image_sha256"][image_id]:
            raise SystemExit(f"{image_id}: image hash differs from selection_meta.json")
        points, classes = ann[by_id[image_id]]["points"], ann[by_id[image_id]]["classes"]
        present = [r for r in qrows if r["presence_status"] == "present"]
        others = [r for r in qrows if r["presence_status"] != "present"]
        if len(present) != 2:
            raise SystemExit(f"{image_id}: expected 2 present queries")
        for r in others:
            if int(r["class_id"]) in classes:
                raise SystemExit(f"{r['query_id']}: absent class {r['target_class']} is annotated in the image")
        img = Image.open(image_path).convert("RGB")
        scale = max(1.0, MIN_WIDTH / img.size[0])
        halves, counts = [], []
        for r in present:
            pts = [pt for pt, c in zip(points, classes) if c == int(r["class_id"])]
            if len(pts) != int(r["gt_count"]):
                raise SystemExit(f"{r['query_id']}: {len(pts)} source points but gt_count {r['gt_count']}")
            counts.append(len(pts))
            halves.append(render_half(img, pts, f"{image_id} | {r['query_id']} | {r['target_class']} | source points: {len(pts)}", scale))
        sheet = Image.new("RGB", (halves[0].width * 2, halves[0].height))
        sheet.paste(halves[0], (0, 0))
        sheet.paste(halves[1], (halves[0].width, 0))
        name = f"{qrows[0]['query_id'].split('_')[0]}_{image_id}_GT.jpg"
        sheet.save(out / name, quality=90)
        files.append(dict(image_id=image_id, file=name, sha256=sha256(out / name), source_image_sha256=meta["image_sha256"][image_id],
                          source_point_counts=counts))

        a = absent[image_id]
        q = lambda r: f"<code>{html.escape(r['query_id'])}</code> {html.escape(r['target_class'])}"
        blocks.append(f"""<section id="{html.escape(qrows[0]['query_id'].split('_')[0])}">
<h2>{html.escape(qrows[0]['query_id'].split('_')[0])} · {html.escape(image_id)} · {html.escape(a['pair_type'])} · {html.escape(a['pair'])}</h2>
<table>
<tr><th>Có mặt (kiểm GT)</th><td>{q(present[0])}: <b>{present[0]['gt_count']}</b> điểm · {q(present[1])}: <b>{present[1]['gt_count']}</b> điểm</td></tr>
<tr><th>Vắng mặt (kiểm absent)</th><td>{' · '.join(q(r) for r in others)} <span class="muted">({html.escape(a['proposed_type'])})</span></td></tr>
<tr><th>Lớp dự phòng</th><td>{html.escape(a['next_candidates'])}</td></tr>
<tr><th>Mọi lớp có nhãn trong ảnh</th><td>{html.escape(a['annotated_classes'])}</td></tr>
<tr><th>Trạng thái lúc vẽ</th><td>{html.escape(a['human_check'])}</td></tr>
</table>
<p class="muted">Ảnh chấm GT (bấm để mở cỡ gốc):</p>
<a href="{html.escape(name)}"><img loading="lazy" src="{html.escape(name)}" alt="GT {html.escape(image_id)}"></a>
<p class="muted">Ảnh gốc, không có chấm (dùng để rà absent và vật bị chấm che):</p>
<a href="{html.escape(image_path.resolve().as_uri())}"><img loading="lazy" class="orig" src="{html.escape(image_path.resolve().as_uri())}" alt="{html.escape(image_id)}"></a>
</section>""")

    page = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><title>Kiểm GT {args.split}</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;margin:16px auto;max-width:1600px;padding:0 16px;background:#fafafa;color:#111}}
section{{border-top:3px solid #333;padding:8px 0 24px}} table{{border-collapse:collapse;margin:6px 0}}
th,td{{border:1px solid #ccc;padding:4px 8px;text-align:left;vertical-align:top}} th{{background:#eee;white-space:nowrap}}
img{{width:100%;height:auto;border:1px solid #999}} img.orig{{max-width:900px}} .muted{{color:#555;font-size:0.9em}}
</style></head><body>
<h1>Kiểm GT/absent — tập {args.split} dev_test_v2 ({len(blocks)} ảnh)</h1>
<p>Điểm vẽ ra là nhãn gốc MUCCA, <b>không phải output model và chưa ai xác nhận</b>. Số chấm khớp gt_count không chứng minh nhãn đúng: phải nhìn từng vật.
Trạng thái trong bảng là lúc chạy script; kết quả kiểm ghi vào <code>experiments/countgdpp/dev_test_v2/absent_candidates.csv</code> và <code>{args.split}/manifest.csv</code>.</p>
{chr(10).join(blocks)}
</body></html>
"""
    (out / "index.html").write_text(page, encoding="utf-8", newline="\n")
    source = dict(purpose="Render existing MUCCA source points for human review; no inference, no correctness judgment",
                  status="PREPARED_NOT_REVIEWED", split=args.split, script_sha256=sha256(Path(__file__)),
                  annotations_sha256=meta["mucca_file_sha256"]["annotations.json"], manifest_sha256=sha256(manifest_path),
                  absent_candidates_sha256=sha256(absent_path), files=files)
    (out / "SOURCE_MANIFEST.json").write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{args.split}: {len(files)} GT images + index.html written to {out}")


if __name__ == "__main__":
    main()
