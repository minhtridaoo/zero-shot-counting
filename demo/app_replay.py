"""Demo xem lại (tầng A) — CS331, CountGD++ trên ảnh nhiều class.

Kết quả đã lưu từ lần chạy test 11/11/2026 (Kaggle T4); KHÔNG chạy model trực tiếp.
Chạy (từ thư mục gốc repo):
    .venv-demo\\Scripts\\python demo\\app_replay.py
Tùy chọn: --data-root <thư mục chứa data_external>  --port 7860  --check-only
"""
from __future__ import annotations

import argparse
import os
import sys
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
for _s in (sys.stdout, sys.stderr):  # console Windows mặc định cp1252, không in được tiếng Việt
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay_data as rd  # noqa: E402

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

BANNER = ("**Kết quả đã lưu; không chạy model trực tiếp.** Box, điểm CountGD++ và điểm CLIP lấy từ lần chạy "
          "test một lần ngày 11/11/2026 trên Kaggle T4; số đếm tính lại bằng cấu hình đã khóa "
          "(`freeze_v2_20261111.json`) và đã đối chiếu khớp `result.json` (119 query hợp lệ).")
COLORS = {"B0": (31, 119, 180), "B2": (214, 39, 40), "P+F": (44, 160, 44), "C6": (148, 103, 189)}
X_COL, Y_COL, SH_COL, DROP_COL = (31, 119, 180), (255, 140, 0), (220, 20, 60), (150, 150, 150)
MAX_W = 760
DEMO_EXAMPLES = [("mcac_25", "t05_1", "Thành công: blueberries"),
                 ("mcac_12", "t01_2", "Lỗi X/Y còn sót: bowls"),
                 ("mcac_171", "t33_1", "Thất bại: dogs (ảnh có 80 cừu)")]

RP: rd.Replay | None = None
DATA_ROOT: Path | None = None


def find_data_root(arg):
    cands = [Path(arg)] if arg else []
    here = rd.ROOT
    cands += [here] + list(here.parents)
    for c in cands:
        if (c / "data_external/mucca_zenodo_19231375/MUCCA_1.0/images").is_dir():
            return c
    raise SystemExit("Không tìm thấy ảnh MUCCA (data_external/...). Dùng --data-root <thư mục CS331 gốc>.")


@lru_cache(maxsize=64)
def base_image(image_id):
    q = RP.queries[RP.images[image_id][0]]
    im = Image.open(DATA_ROOT / q.image_path).convert("RGB")
    scale = MAX_W / im.width  # ảnh MUCCA nhiều tấm chỉ rộng 500 px: phóng lên cho box và chữ rõ khi chiếu
    if scale != 1:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    return im, scale


def font(size):
    for f in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def draw(image_id, layers, caption=None):
    """layers: list of (boxes, color, width, dashed)."""
    im, s = base_image(image_id)
    im = im.copy(); d = ImageDraw.Draw(im)
    for boxes, col, w, dashed in layers:
        for b in boxes:
            x0, y0, x1, y1 = (v * s for v in b)
            if dashed:
                for xa in range(int(x0), int(x1), 8):
                    d.line([(xa, y0), (min(xa + 4, x1), y0)], fill=col, width=w)
                    d.line([(xa, y1), (min(xa + 4, x1), y1)], fill=col, width=w)
                for ya in range(int(y0), int(y1), 8):
                    d.line([(x0, ya), (x0, min(ya + 4, y1))], fill=col, width=w)
                    d.line([(x1, ya), (x1, min(ya + 4, y1))], fill=col, width=w)
            else:
                d.rectangle([x0, y0, x1, y1], outline=col, width=w)
    if caption:
        # góc dưới bên trái: góc trên bị nhãn của khung Gradio che
        f = font(max(16, im.width // 30))
        tw = d.textlength(caption, font=f); h = f.size + 12
        d.rectangle([0, im.height - h, im.width, im.height], fill=(255, 255, 255))
        d.text((8, im.height - h + 5), caption, fill=(20, 20, 20), font=f)
    return im


# ---------------------------------------------------------------- nhãn chọn
def image_choices():
    out = []
    for img, qids in RP.images.items():
        qs = [RP.queries[q] for q in qids]
        out.append((f"{img} · " + " / ".join(q.prompt for q in qs), img))
    return out


def query_label(q):
    if q.status == "uncertain":
        return f"{q.query_id} · {q.prompt} (uncertain, không chấm)"
    return f"{q.query_id} · {q.prompt} ({'có mặt' if q.status == 'present' else 'vắng mặt'}, GT {q.gt})"


def query_choices(image_id):
    return [(query_label(RP.queries[q]), q) for q in RP.images[image_id]]


# ---------------------------------------------------------------- tab 1
def compare(image_id, qid):
    import gradio as gr
    q = RP.queries[qid]
    imgs, rows = [], []
    for name in rd.CONFIGS:
        n = RP.count(name, qid)
        err = "không chấm" if q.status == "uncertain" else str(abs(n - q.gt))
        cap = f"{name}: đếm {n} · GT {q.gt}" + ("" if q.status == "uncertain" else f" · sai {abs(n - q.gt)}")
        imgs.append(gr.Image(value=draw(image_id, [(RP.kept_boxes(name, qid), COLORS[name], 3, False)], cap),
                             label=f"{name} — {rd.CONFIGS[name]['desc']}"))
        rows.append([name, n, q.gt, err])
    note = f"**Query:** {query_label(q)}"
    if q.status == "absent":
        note += " — đúng là phải trả **0**."
    return [*imgs, rows, note]


def on_image_change(image_id, current_q=None):
    """Đổi ảnh: giữ query đang chọn nếu nó thuộc ảnh mới (vd khi bấm nút ví dụ), không thì lấy query đầu."""
    import gradio as gr
    ch = query_choices(image_id)
    keep = current_q if current_q in RP.images[image_id] else ch[0][1]
    return gr.Radio(choices=ch, value=keep)


# ---------------------------------------------------------------- tab 2
def xy_view(image_id, name):
    pres, unc = RP.xy_pair(image_id)
    X, Y = pres[0], pres[1]
    bx = RP.kept_boxes(name, X.query_id); by = RP.kept_boxes(name, Y.query_id)
    fx = rd.shared_flags(bx, by); fy = rd.shared_flags(by, bx)
    only_x = [b for b, f in zip(bx, fx) if not f]; only_y = [b for b, f in zip(by, fy) if not f]
    sh = [b for b, f in zip(bx, fx) if f] + [b for b, f in zip(by, fy) if f]
    n = len(bx) + len(by); s = sum(fx) + sum(fy)
    cap = f"{name}: {s}/{n} box dùng chung" if n else f"{name}: không giữ box nào"
    im = draw(image_id, [(only_x, X_COL, 3, False), (only_y, Y_COL, 3, False), (sh, SH_COL, 3, False)], cap)
    rows = []
    for nm in rd.CONFIGS:
        r = RP.shared_image(nm, image_id)
        cx = RP.count(nm, X.query_id); cy = RP.count(nm, Y.query_id)
        rate = "—" if not r or not r[1] else f"{r[0]}/{r[1]} = {r[0] / r[1]:.0%}"
        rows.append([nm, cx, cy, rate])
    md = (f"**X = \"{X.prompt}\"** (GT {X.gt}, xanh dương) · **Y = \"{Y.prompt}\"** (GT {Y.gt}, cam) · "
          f"**đỏ = box dùng chung**: có box ở query kia trùng IoU ≥ 0.5.")
    if unc:
        md += "\n\n⚠ Ảnh này có query `uncertain`, nên **không** nằm trong 39 ảnh tính shared box chính thức."
    import gradio as gr
    table = gr.Dataframe(value=rows, headers=["Cách", f"Đếm X (GT {X.gt})", f"Đếm Y (GT {Y.gt})", "Box dùng chung"])
    return gr.Image(value=im, label=f"{name}: xanh = chỉ X · cam = chỉ Y · đỏ = dùng chung"), table, md


def official_shared_table():
    rows = []
    for nm, c in rd.CONFIGS.items():
        o = RP.posthoc["overlap"][c["posthoc"]]["0.5"]
        lo, hi = o.get("shared_xy_pooled_ci95", [None, None])
        rows.append([nm, f"{o['shared_xy_pooled']:.0%}", f"[{lo:.0%}, {hi:.0%}]" if lo is not None else "—"])
    return rows


# ---------------------------------------------------------------- tab 3
def f_view(image_id, qid, name, th):
    q = RP.queries[qid]; c = RP.cfg[name]
    boxes = RP.boxes(name, qid); fs = RP.fusion_scores(name, qid)
    keep = [b for b, f in zip(boxes, fs) if f >= th]; drop = [b for b, f in zip(boxes, fs) if f < th]
    n_lock = RP.count(name, qid); n_now = len(keep)
    cap = f"{name} @ θ={th:.3f}: giữ {n_now}/{len(boxes)} · GT {q.gt}"
    im = draw(image_id, [(drop, DROP_COL, 2, True), (keep, COLORS[name], 3, False)], cap)
    locked = abs(th - c["threshold"]) < 1e-9
    md = (f"**{query_label(q)}** · nguồn box: `{c['source']}` ({len(boxes)} box trước khi lọc)\n\n"
          f"- Ngưỡng **đã khóa** của {name}: θ = {c['threshold']:.3f} → đếm **{n_lock}**"
          + ("" if q.status == "uncertain" else f" (sai {abs(n_lock - q.gt)})") + "\n"
          f"- Ngưỡng **đang kéo**: θ = {th:.3f} → đếm **{n_now}**"
          + ("" if q.status == "uncertain" else f" (sai {abs(n_now - q.gt)})")
          + (" — đang dùng cấu hình khóa." if locked else " — *chỉ minh họa trên ảnh này, không lưu, không đổi kết quả báo cáo.*")
          + "\n\nNét liền: box được giữ. Nét đứt xám: box bị F bỏ.")
    import gradio as gr
    return gr.Image(value=im, label=f"{name}: nét liền = giữ · nét đứt xám = F bỏ"), md


def f_reset(name):
    import gradio as gr
    return gr.Slider(value=RP.cfg[name]["threshold"])


def f_config_change(image_id, qid, name):
    import gradio as gr
    th = RP.cfg[name]["threshold"]
    im, md = f_view(image_id, qid, name, th)
    return gr.Slider(value=th), im, md


# ---------------------------------------------------------------- UI
def build():
    import gradio as gr
    imgs = image_choices()
    first = DEMO_EXAMPLES[0][0]
    with gr.Blocks(title="CS331 · Demo xem lại CountGD++ trên ảnh nhiều class", theme=gr.themes.Soft(),
                   analytics_enabled=False) as demo:
        gr.Markdown("# Đếm đúng class trong ảnh nhiều class — demo xem lại (CS331)")
        gr.Markdown(BANNER)
        with gr.Row():
            ex_btns = [gr.Button(f"Ví dụ {i + 1}: {lab}", size="sm") for i, (_, _, lab) in enumerate(DEMO_EXAMPLES)]
        with gr.Tabs():
            # ---- tab 1
            with gr.Tab("1 · So sánh phương pháp"):
                with gr.Row():
                    img1 = gr.Dropdown(choices=imgs, value=first, label="Ảnh test (40 ảnh)", scale=2)
                    q1 = gr.Radio(choices=query_choices(first), value=DEMO_EXAMPLES[0][1], label="Query", scale=3)
                note1 = gr.Markdown()
                with gr.Row():
                    o_b0 = gr.Image(type="pil", interactive=False); o_b2 = gr.Image(type="pil", interactive=False)
                with gr.Row():
                    o_pf = gr.Image(type="pil", interactive=False); o_c6 = gr.Image(type="pil", interactive=False)
                tab1 = gr.Dataframe(headers=["Cách", "Đếm", "GT", "Sai số |đếm − GT|"], interactive=False)
                outs1 = [o_b0, o_b2, o_pf, o_c6, tab1, note1]
                img1.change(on_image_change, [img1, q1], q1)
                q1.change(compare, [img1, q1], outs1)
            # ---- tab 2
            with gr.Tab("2 · Lỗi X/Y (box dùng chung)"):
                with gr.Row():
                    img2 = gr.Dropdown(choices=imgs, value="mcac_12", label="Ảnh test", scale=2)
                    cfg2 = gr.Radio(choices=list(rd.CONFIGS), value="B0", label="Cấu hình", scale=2)
                md2 = gr.Markdown()
                with gr.Row():
                    o2 = gr.Image(type="pil", interactive=False, scale=3)
                    with gr.Column(scale=2):
                        tab2 = gr.Dataframe(headers=["Cách", "Đếm X", "Đếm Y", "Box dùng chung (ảnh này)"],
                                            interactive=False, label="Ảnh đang chọn")
                        gr.Dataframe(value=official_shared_table(), headers=["Cách", "Shared box X/Y", "CI 95%"],
                                     interactive=False, label="Toàn test, 39 ảnh (phân tích 11/11, số trên slide)")
                for comp in (img2, cfg2):
                    comp.change(xy_view, [img2, cfg2], [o2, tab2, md2])
            # ---- tab 3
            with gr.Tab("3 · Bộ lọc F"):
                with gr.Row():
                    img3 = gr.Dropdown(choices=imgs, value=first, label="Ảnh test", scale=2)
                    q3 = gr.Radio(choices=query_choices(first), value=DEMO_EXAMPLES[0][1], label="Query", scale=3)
                with gr.Row():
                    cfg3 = gr.Radio(choices=["P+F", "C6"], value="P+F", label="Cấu hình có F (mỗi cách dùng bounds/ngưỡng khóa riêng)")
                    th3 = gr.Slider(0.0, 1.0, value=RP.cfg["P+F"]["threshold"], step=0.001, label="Ngưỡng F (θ)")
                    reset3 = gr.Button("Khôi phục cấu hình khóa", variant="primary")
                gr.Markdown("F = 0.5·norm(điểm CountGD++) + 0.5·norm(cosine CLIP); giữ box khi F ≥ θ. "
                            "Thanh trượt chỉ minh họa trên **ảnh đang chọn**; app không tính lại MAE toàn test và không lưu ngưỡng mới.")
                with gr.Row():
                    o3 = gr.Image(type="pil", interactive=False, scale=3)
                    md3 = gr.Markdown()
                img3.change(on_image_change, [img3, q3], q3)
                q3.change(f_view, [img3, q3, cfg3, th3], [o3, md3])
                th3.release(f_view, [img3, q3, cfg3, th3], [o3, md3])
                cfg3.change(f_config_change, [img3, q3, cfg3], [th3, o3, md3])
                reset3.click(f_reset, cfg3, th3).then(f_view, [img3, q3, cfg3, th3], [o3, md3])

        def goto(i):
            im, qid, _ = DEMO_EXAMPLES[i]
            ch = query_choices(im)
            return (gr.Dropdown(value=im), gr.Radio(choices=ch, value=qid),
                    gr.Dropdown(value=im), gr.Dropdown(value=im), gr.Radio(choices=ch, value=qid))
        for i, b in enumerate(ex_btns):
            b.click(lambda i=i: goto(i), None, [img1, q1, img2, img3, q3])
        demo.load(compare, [img1, q1], outs1)
        demo.load(xy_view, [img2, cfg2], [o2, tab2, md2])
        demo.load(f_view, [img3, q3, cfg3, th3], [o3, md3])
    return demo


def main():
    global RP, DATA_ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    RP = rd.load()
    rd.self_check(RP)
    DATA_ROOT = find_data_root(a.data_root)
    missing = [q.image_path for q in RP.queries.values() if not (DATA_ROOT / q.image_path).is_file()]
    if missing:
        raise SystemExit(f"Thiếu {len(missing)} ảnh, ví dụ {missing[0]}")
    print(f"Ảnh MUCCA: {DATA_ROOT} (40/40 ảnh có)")
    for im, qid, lab in DEMO_EXAMPLES:
        q = RP.queries[qid]
        print(f"  {lab}: {qid} GT {q.gt} · " + " · ".join(f"{n} {RP.count(n, qid)}" for n in rd.CONFIGS))
    if a.check_only:
        print("CHECK-ONLY: PASS"); return
    build().queue().launch(server_name="127.0.0.1", server_port=a.port, share=False, inbrowser=False,
                           show_api=False)


if __name__ == "__main__":
    main()
