"""Thử nghiệm sơ bộ hướng 1 — gán khung theo CLIP giữa các loại, CHỈ TRÊN DEV (khai báo: KHAI_BAO_TRUOC_XY_CLIP_20261122.md).

Bước A (không tham số): giữ khung b của câu q khi cosine CLIP(b, "a photo of q") >= cosine với mọi loại khác trong K(q).
  A_Q: K(q) = các câu hỏi trên cùng ảnh (X, Y, Z). A_V: K(q) = 45 lớp MUCCA ∪ {q}.
Áp trên khung đã lưu của P+F (đã khóa), B0, C6 (F lấy nguyên từ freeze v2). Không chạy CountGD++, không dùng GT để quyết định.
Dừng (không báo số) nếu: hash đầu vào sai; MAE dev của cấu hình gốc không tái lập; cosine CLIP tính lại lệch bundle >= 1e-3.
Không bao giờ đọc tập test.

  python experiments/xy_clip_assign/xy_clip_assign_dev.py --mucca <MUCCA_1.0> --check-only
  python experiments/xy_clip_assign/xy_clip_assign_dev.py --mucca <MUCCA_1.0> --out results/countgdpp/xy_clip_assign_dev_<stamp>
"""
import argparse, csv, hashlib, json, math, random, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/countgdpp"))
from p4_clip_score import crop_box, MODEL_ID, REVISION, TEMPLATE  # noqa: E402 (chỉ import, không sửa)

MANIFEST = ROOT / "experiments/countgdpp/dev_test_v2/dev/manifest.csv"
BUNDLE = ROOT / "results/countgdpp/p1_dev_kaggle_t4_20261111_1203_m5_offline_T/bundle.json"
FREEZE = ROOT / "results/countgdpp/freeze_v2_20261111.json"
SHA = {MANIFEST: "52d3f667bcd1b8bd8a7537504e9d8b45d5df50faac98a62b3b051cb5abaf6854",
       BUNDLE: "651a01c140c96cb0eef2b079727d00155f7e49d48e0f2aa7de4c46f3ada34aa9",
       FREEZE: "64e89ef53eab306fdbb33cfc39797749ff17cc8635f46ae381d96e45c4f6736d"}
SHA_ANN = "95d9908c367d43184fb1bda392b173107793f90b4595ba74e7e61c3cdbf2eb3f"
SHA_CLASSES = "4a9daeaef21b27e13db42c986a397fb97035f886d0094ea55bc409be1a9b355d"
DEV_MAE = {"P+F": 3.533333333333333, "B0": 6.283333333333333, "C6": 4.016666666666667}
BATCH, N_BOOT, SEED, IOU_T, CLIP_TOL = 2, 5000, 331, 0.5, 1e-3
# Sửa đổi kỹ thuật 22/11 (ghi trong khai báo §8): torch 2.2 không nạp được pytorch_model.bin qua transformers mới,
# nên trọng số nạp từ model.safetensors (bản safetensors của cùng model trên Hub); config/processor giữ revision đã ghim.
# Bước tái lập CLIP (< 1e-3 so với bundle tính trên Kaggle) xác nhận đầu ra giống bản cũ.
SAFETENSORS_REV = "c237dc49a33fc61debc9276459120b7eac67e7ef"
SHA_SAFETENSORS = "99d28a652e6ec46629ab7047a0ac82c69b1fe11e0ce672c43af65d3a9a3fc05d"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def keep_idx(cfg, row):
    """Chỉ số các khung cấu hình gốc giữ lại (F đúng như freeze/apply_freeze_v2)."""
    if cfg["filter"] is None:
        return list(range(len(row["boxes"])))
    (alo, ahi), (clo, chi) = cfg["bounds"]["countgd"], cfg["bounds"]["clip"]
    out = []
    for i, (a, c) in enumerate(zip(row["scores"], row["clip"])):
        na = .5 if ahi == alo else clamp01((a - alo) / (ahi - alo))
        nc = .5 if chi == clo else clamp01((c - clo) / (chi - clo))
        if .5 * na + .5 * nc >= cfg["threshold"]:
            out.append(i)
    return out


def iou(a, b):
    ix = max(0., min(a[2], b[2]) - max(a[0], b[0])); iy = max(0., min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy; ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.


def inside(b, p):
    return b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3]


def load_inputs(mucca):
    for p, h in SHA.items():
        if sha(p) != h:
            raise SystemExit(f"Sai hash: {p}")
    if sha(mucca / "annotations.json") != SHA_ANN or sha(mucca / "class_mapping.json") != SHA_CLASSES:
        raise SystemExit("Sai hash annotations/class_mapping MUCCA")
    man = list(csv.DictReader(MANIFEST.open(encoding="utf-8", newline="")))
    if any(r["split"] != "dev_v2" for r in man) or len(man) != 60:
        raise SystemExit("Manifest không phải dev 60 câu")
    fz = json.loads(FREEZE.read_text(encoding="utf-8"))
    cfgs = {"P+F": fz["main"], "B0": fz["companions_report_only"]["B0"], "C6": fz["companions_report_only"]["C6 = B0+F"]}
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    src = {n: {r["query_id"]: r for r in rows} for n, rows in bundle["sources"].items()}
    ann = json.loads((mucca / "annotations.json").read_text(encoding="utf-8"))
    classes = sorted(set(json.loads((mucca / "class_mapping.json").read_text(encoding="utf-8")).values()))
    for r in man:
        if not (mucca / "images" / f"{r['image_id']}.jpg").exists():
            raise SystemExit(f"Thiếu ảnh {r['image_id']}")
    return man, cfgs, src, ann, classes


def mae_of(counts, rows):
    return sum(abs(counts[r["query_id"]] - int(r["gt_count"])) for r in rows) / len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mucca", required=True, help="Thư mục MUCCA_1.0 (có images/, annotations.json, class_mapping.json)")
    ap.add_argument("--out", help="Thư mục kết quả mới, tương đối với CS331")
    ap.add_argument("--check-only", action="store_true", help="Chỉ kiểm đầu vào và tái lập cấu hình gốc; không tải CLIP")
    a = ap.parse_args()
    mucca = Path(a.mucca)
    man, cfgs, src, ann, classes = load_inputs(mucca)
    base_keep = {n: {r["query_id"]: keep_idx(cfg, src[cfg["source"]][r["query_id"]]) for r in man} for n, cfg in cfgs.items()}
    for n, K in base_keep.items():
        got = mae_of({q: len(v) for q, v in K.items()}, man)
        if abs(got - DEV_MAE[n]) > 1e-9:
            raise SystemExit(f"Không tái lập MAE dev của {n}: {got} != {DEV_MAE[n]}")
    print("Đầu vào khớp hash; tái lập MAE dev:", {n: round(DEV_MAE[n], 4) for n in DEV_MAE})
    if a.check_only:
        print("CHECK-ONLY: dừng trước khi tải CLIP."); return
    if not a.out:
        raise SystemExit("Cần --out")
    out = ROOT / a.out
    if out.exists():
        raise SystemExit("Đã có thư mục kết quả. Thử nghiệm chạy một lần; không ghi đè.")

    import os
    os.environ["USE_TF"] = "0"  # env ai_new có TensorFlow hỏng; transformers chỉ cần PyTorch (sửa đổi kỹ thuật, khai báo §8)
    import torch, transformers
    from PIL import Image
    from transformers import CLIPConfig, CLIPModel, CLIPProcessor
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file
    torch.manual_seed(0)
    t0 = time.time()
    processor = CLIPProcessor.from_pretrained(MODEL_ID, revision=REVISION, use_fast=False)
    model = CLIPModel(CLIPConfig.from_pretrained(MODEL_ID, revision=REVISION))
    wpath = hf_hub_download(MODEL_ID, "model.safetensors", revision=SAFETENSORS_REV)
    if sha(wpath) != SHA_SAFETENSORS:
        raise SystemExit("Sai hash model.safetensors")
    missing, unexpected = model.load_state_dict(load_file(wpath), strict=False)
    if [k for k in missing + unexpected if not k.endswith("position_ids")]:
        raise SystemExit(f"Trọng số không khớp kiến trúc: missing={missing}, unexpected={unexpected}")
    model.eval()

    by_img = {}
    for r in man:
        by_img.setdefault(r["image_id"], []).append(r)
    texts = sorted({r["prompt"] for r in man} | set(classes))
    with torch.inference_mode():  # từng câu một, đúng như p4_clip_score.py (tránh khác biệt do padding)
        tfeat = torch.cat([torch.nn.functional.normalize(model.get_text_features(
            **processor(text=[TEMPLATE.format(prompt=t)], return_tensors="pt", padding=True)), dim=-1) for t in texts])
    tidx = {t: i for i, t in enumerate(texts)}

    # cosine của mọi khung (nguồn B0 và tau0.200) với mọi tên
    cos = {}  # (source, query_id) -> list[list[float]] theo texts
    max_dev = 0.
    for img_id, rows in by_img.items():
        image = Image.open(mucca / "images" / f"{img_id}.jpg").convert("RGB")
        W, H = image.size
        for source in ("B0", "tau0.200"):
            for r in rows:
                row = src[source][r["query_id"]]
                crops = [image.crop(tuple(crop_box(b, W, H))) for b in row["boxes"]]
                feats = []
                with torch.inference_mode():
                    for s in range(0, len(crops), BATCH):
                        px = processor(images=crops[s:s + BATCH], return_tensors="pt")["pixel_values"]
                        feats.append(torch.nn.functional.normalize(model.get_image_features(pixel_values=px), dim=-1))
                if not feats:
                    cos[(source, r["query_id"])] = []; continue
                sims = (torch.cat(feats) @ tfeat.T).tolist()
                cos[(source, r["query_id"])] = sims
                own = [s[tidx[r["prompt"]]] for s in sims]
                max_dev = max([max_dev] + [abs(x - y) for x, y in zip(own, row["clip"])])
    clip_seconds = time.time() - t0
    if max_dev >= CLIP_TOL:
        raise SystemExit(f"KHONG DAT tái lập CLIP: lệch lớn nhất {max_dev:.2e} >= {CLIP_TOL}. Không báo số.")
    print(f"Tái lập CLIP đạt: lệch lớn nhất {max_dev:.2e}; {clip_seconds:.1f} s")

    def assign(source, r, idxs, kind):
        sims = cos[(source, r["query_id"])]
        K = [x["prompt"] for x in by_img[r["image_id"]]] if kind == "Q" else sorted(set(classes) | {r["prompt"]})
        q, others = tidx[r["prompt"]], [tidx[k] for k in K if k != r["prompt"]]
        return [i for i in idxs if all(sims[i][q] >= sims[i][o] for o in others)]

    keep = dict(base_keep)
    for n, cfg in cfgs.items():
        for kind in ("Q", "V"):
            keep[f"{n}+A_{kind}"] = {r["query_id"]: assign(cfg["source"], r, base_keep[n][r["query_id"]], kind) for r in man}
    boxes = {n: {q: [src[cfgs[n.split('+A_')[0]]["source"]][q]["boxes"][i] for i in idx] for q, idx in K.items()}
             for n, K in keep.items()}
    counts = {n: {q: len(v) for q, v in K.items()} for n, K in keep.items()}

    pres = [r for r in man if r["presence_status"] == "present"]
    absn = [r for r in man if r["presence_status"] == "absent"]
    imgs = sorted(by_img)

    def per_image(n):
        """Theo ảnh: (khung dùng chung s, tổng khung X+Y n, tổng |lỗi| câu có mặt, số câu có mặt)."""
        out = {}
        for i in imgs:
            P = [r for r in by_img[i] if r["presence_status"] == "present"]
            s = nn = 0
            if len(P) == 2:
                X, Y = (boxes[n][r["query_id"]] for r in P)
                s = sum(any(iou(b, o) >= IOU_T for o in Y) for b in X) + sum(any(iou(b, o) >= IOU_T for o in X) for b in Y)
                nn = len(X) + len(Y)
            e = sum(abs(counts[n][r["query_id"]] - int(r["gt_count"])) for r in P)
            out[i] = (s, nn, e, len(P))
        return out

    def point_check(n):
        c = dict(correct=0, other_class_only=0, no_point=0)
        for r in pres:
            pa = ann[r["image_id"] + ".jpg"]; cls = int(r["class_id"])
            own = [p for p, k in zip(pa["points"], pa["classes"]) if k == cls]
            oth = [p for p, k in zip(pa["points"], pa["classes"]) if k != cls]
            for b in boxes[n][r["query_id"]]:
                if any(inside(b, p) for p in own): c["correct"] += 1
                elif any(inside(b, p) for p in oth): c["other_class_only"] += 1
                else: c["no_point"] += 1
        tot = sum(c.values()); c["kept_boxes_present"] = tot
        c.update({k + "_rate": (c[k] / tot if tot else None) for k in ("correct", "other_class_only", "no_point")})
        return c

    PI = {n: per_image(n) for n in keep}
    summary = {}
    for n in keep:
        s = sum(v[0] for v in PI[n].values()); nn = sum(v[1] for v in PI[n].values())
        e = [counts[n][r["query_id"]] - int(r["gt_count"]) for r in pres]
        summary[n] = dict(MAE_all=mae_of(counts[n], man), MAE_present=mae_of(counts[n], pres),
                          FPR_absent=sum(counts[n][r["query_id"]] > 0 for r in absn) / len(absn),
                          overcount_present=sum(x for x in e if x > 0), undercount_present=-sum(x for x in e if x < 0),
                          shared_xy=(s / nn if nn else None), shared_boxes=s, xy_boxes=nn, point_check=point_check(n))

    def boot(A, B):
        def stat(sample):
            sa = sum(PI[A][i][0] for i in sample); na = sum(PI[A][i][1] for i in sample)
            sb = sum(PI[B][i][0] for i in sample); nb = sum(PI[B][i][1] for i in sample)
            ea = sum(PI[A][i][2] for i in sample); eb = sum(PI[B][i][2] for i in sample); k = sum(PI[A][i][3] for i in sample)
            return ((sa / na if na else 0.) - (sb / nb if nb else 0.), (ea - eb) / k if k else 0.)
        rng = random.Random(SEED)
        bs = [stat([rng.choice(imgs) for _ in imgs]) for _ in range(N_BOOT)]
        d = stat(imgs)
        ci = lambda j: sorted(x[j] for x in bs)
        c0, c1 = ci(0), ci(1)
        return dict(A=A, B=B, d_shared_xy=d[0], ci_shared_xy=[c0[124], c0[4874]],
                    d_MAE_present=d[1], ci_MAE_present=[c1[124], c1[4874]])

    pairs = [("primary", "P+F+A_Q", "P+F"), ("secondary", "B0+A_Q", "B0"), ("secondary", "C6+A_Q", "C6"), ("secondary", "P+F+A_V", "P+F")]
    comps = []
    for role, A, B in pairs:
        c = boot(A, B); c["role"] = role
        ds, dm = c["d_shared_xy"], c["d_MAE_present"]
        c["reading"] = ("có dấu hiệu giúp trên dev (cả hai giảm)" if ds < 0 and dm < 0 else
                        "không thấy giúp trên dev" if ds >= 0 and dm >= 0 else "đánh đổi (một chỉ số giảm, một tăng)")
        comps.append(c)

    out.mkdir(parents=True)
    res = dict(status="XY_CLIP_ASSIGN_DEV_PRELIMINARY", scope="chỉ dev (20 ảnh, đã dùng để chọn F); sơ bộ; không thay kết quả chính; không chạy test",
               declaration="experiments/xy_clip_assign/KHAI_BAO_TRUOC_XY_CLIP_20261122.md",
               inputs={str(p.relative_to(ROOT)): h for p, h in SHA.items()}, annotations_sha256=SHA_ANN, class_mapping_sha256=SHA_CLASSES,
               clip=dict(model=MODEL_ID, revision=REVISION, weights="model.safetensors", weights_revision=SAFETENSORS_REV,
                         weights_sha256=SHA_SAFETENSORS, template=TEMPLATE, batch=BATCH, device="cpu",
                         torch=torch.__version__, transformers=transformers.__version__),
               clip_replay_max_abs_diff=max_dev, clip_seconds=clip_seconds, base_mae_reproduced=DEV_MAE,
               summary=summary, comparisons=comps, per_query_counts=counts, tool_sha256=sha(__file__))
    (out / "result.json").write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    with (out / "per_query.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["query_id", "image_id", "prompt", "presence_status", "gt_count", *keep])
        for r in man:
            w.writerow([r["query_id"], r["image_id"], r["prompt"], r["presence_status"], r["gt_count"], *(counts[n][r["query_id"]] for n in keep)])
    (out / "clip_cosines.json").write_text(json.dumps(dict(texts=texts, cos={f"{s}|{q}": v for (s, q), v in cos.items()}), ensure_ascii=False) + "\n",
                                           encoding="utf-8", newline="\n")

    print(f"\n{'cách':<12}{'MAE':>7}{'MAE có mặt':>12}{'FPR':>6}{'dùng chung X/Y':>16}{'đúng loại':>11}")
    for n, m in summary.items():
        print(f"{n:<12}{m['MAE_all']:>7.2f}{m['MAE_present']:>12.2f}{m['FPR_absent']:>6.2f}{(m['shared_xy'] or 0):>16.1%}{(m['point_check']['correct_rate'] or 0):>11.1%}")
    for c in comps:
        print(f"{c['role']:<10} {c['A']} − {c['B']}: dùng chung {c['d_shared_xy']:+.3f} [{c['ci_shared_xy'][0]:+.3f}, {c['ci_shared_xy'][1]:+.3f}]"
              f" | MAE có mặt {c['d_MAE_present']:+.2f} [{c['ci_MAE_present'][0]:+.2f}, {c['ci_MAE_present'][1]:+.2f}] → {c['reading']}")
    print("Saved:", out)


if __name__ == "__main__":
    main()
