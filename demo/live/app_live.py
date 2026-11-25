"""Demo suy luận THẬT — CS331: dán ảnh mới, nhập tên vật, chạy CountGD++ (B0, B2, P+F, C6) với cấu hình đã khóa.

Chạy trên GPU (Kaggle T4, xem kaggle_live_demo.ipynb):
    python demo/live/app_live.py --device cuda --share --password <mật khẩu>
Kiểm chức năng trên CPU (chậm, không dùng để trình bày):
    .venv-live\\Scripts\\python demo\\live\\app_live.py --device cpu --port 7870
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
sys.path.insert(0, str(Path(__file__).resolve().parent))

import live_engine as le  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

MAX_Q = 3
CAP = 900  # số box đề xuất tối đa mỗi ảnh của CountGD++ (num_queries trong cfg_app.py)
MAX_W = 760
COLORS = {"B0": (31, 119, 180), "B2": (214, 39, 40), "P+F": (44, 160, 44), "C6": (148, 103, 189)}
DESC = {"B0": "CountGD++ một lượt", "B2": "CountGD++ hai lượt (pseudo-exemplar gốc)",
        "P+F": "Cải tiến đã khóa: P(τ 0.20, M 5) rồi lọc F", "C6": "Một lượt rồi lọc F (ngưỡng khóa riêng)"}
ENGINE: le.LiveEngine | None = None

# Ctrl+V ở bất kỳ đâu trên trang (trừ khi đang gõ chữ) -> đưa ảnh trong clipboard vào ô ảnh.
PASTE_JS = r"""
<script>
(function () {
  async function putFile(file) {
    const root = document.querySelector('#live_image');
    if (!root) return;
    let input = root.querySelector('input[type=file]');
    if (!input) {                       // ô đang có ảnh cũ: bấm nút xóa của Gradio rồi chờ ô upload hiện lại
      const clear = [...root.querySelectorAll('button')].find(b => /clear|xóa|remove/i.test((b.getAttribute('aria-label') || '') + (b.title || '')));
      if (clear) clear.click();
      for (let i = 0; i < 30 && !input; i++) { await new Promise(r => setTimeout(r, 100)); input = root.querySelector('input[type=file]'); }
    }
    if (!input) { alert('Không tìm thấy ô ảnh để dán. Bấm "Xóa và bắt đầu lại" rồi thử Ctrl+V lần nữa.'); return; }
    const dt = new DataTransfer();
    dt.items.add(new File([file], file.name && file.name !== 'image.png' ? file.name : 'pasted.png', { type: file.type || 'image/png' }));
    input.files = dt.files;
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  window.addEventListener('paste', function (e) {
    const t = e.target;
    const typing = t && ((t.tagName === 'TEXTAREA') || (t.tagName === 'INPUT' && t.type !== 'file') || t.isContentEditable);
    const files = [...((e.clipboardData && e.clipboardData.files) || [])].filter(f => f.type.startsWith('image/'));
    if (!files.length || typing) return;      // dán chữ vào ô chữ vẫn bình thường
    e.preventDefault(); e.stopPropagation();
    putFile(files[0]);
  }, true);
})();
</script>
"""


def font(size):
    for f in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def render(image, kept, dropped, color, caption):
    s = MAX_W / image.width
    im = image.resize((MAX_W, max(1, round(image.height * s))), Image.LANCZOS) if s != 1 else image.copy()
    d = ImageDraw.Draw(im)
    for b in dropped or []:
        x0, y0, x1, y1 = (v * s for v in b)
        for xa in range(int(x0), int(x1), 8):
            d.line([(xa, y0), (min(xa + 4, x1), y0)], fill=(160, 160, 160), width=2)
            d.line([(xa, y1), (min(xa + 4, x1), y1)], fill=(160, 160, 160), width=2)
        for ya in range(int(y0), int(y1), 8):
            d.line([(x0, ya), (x0, min(ya + 4, y1))], fill=(160, 160, 160), width=2)
            d.line([(x1, ya), (x1, min(ya + 4, y1))], fill=(160, 160, 160), width=2)
    for b in kept:
        d.rectangle([v * s for v in b], outline=color, width=3)
    f = font(max(16, im.width // 30)); h = f.size + 12
    d.rectangle([0, im.height - h, im.width, im.height], fill=(255, 255, 255))
    d.text((8, im.height - h + 5), caption, fill=(20, 20, 20), font=f)
    return im


def fmt_ms(v):
    return "—" if v is None else (f"{v / 1000:.2f} s" if v >= 1000 else f"{v:.0f} ms")


def timing_text(m, r):
    t = r["timing"]
    if m == "B0":
        return f"lượt 1 {fmt_ms(t.get('stage1_ms'))} (dùng chung)"
    if m == "B2":
        return (f"lượt 1 (chung) + lượt 2 {fmt_ms(t.get('stage2_ms'))}" if t.get("stage2_ms") is not None
                else "lượt 1 (chung); không có pseudo-exemplar → bằng B0")
    if m == "P+F":
        s2 = ("lượt 2 dùng lại của B2 (cùng bộ exemplar)" if t.get("stage2_reused_from_B2")
              else (f"lượt 2 {fmt_ms(t.get('stage2_ms'))}" if t.get("stage2_ms") is not None else "không còn exemplar → nguồn = B0"))
        return f"lượt 1 (chung) + CLIP kiểm exemplar {fmt_ms(t.get('clip_verify_ms'))} + {s2} + CLIP chấm box {fmt_ms(t.get('clip_final_ms'))}"
    return f"lượt 1 (chung) + CLIP chấm box {fmt_ms(t.get('clip_final_ms'))}"


# ---------------------------------------------------------------- callbacks
def n_outputs():
    return MAX_Q * (1 + 1 + 4 + 1) + 3   # mỗi query: group, tiêu đề, 4 ảnh, bảng; + status, xy, log


def blank(status):
    import gradio as gr
    outs = []
    for _ in range(MAX_Q):
        outs += [gr.Group(visible=False), gr.Markdown(value="")] + [gr.Image(value=None, label=m) for m in le.METHODS] + [gr.Markdown(value="")]
    return outs + [gr.Markdown(value=status), gr.Markdown(value=""), gr.JSON(value=None)]


def on_input_change(image, queries, gts):
    msg = ("⚠ **Ảnh hoặc tên vật đã thay đổi — kết quả cũ đã được xóa.** Bấm **Chạy** để chạy model trên dữ liệu mới."
           if image is not None else "Dán ảnh (Ctrl+V), kéo thả hoặc bấm vào ô để chọn ảnh, nhập tên vật rồi bấm **Chạy**.")
    return blank(msg)


def start_run(image, queries, gts):
    return blank("⏳ **Đang chạy model…** Kết quả cũ đã được xóa. Trên GPU T4 mỗi tên vật mất vài giây.")


def run(image, queries, gts, request=None):
    import gradio as gr
    if image is None:
        return blank("❌ Chưa có ảnh. Dán ảnh bằng **Ctrl+V**, kéo thả, hoặc bấm vào ô ảnh để chọn file.")
    try:
        prompts = le.parse_queries(queries, MAX_Q)
        gt = le.parse_gt(gts, len(prompts))
    except ValueError as e:
        return blank(f"❌ {e}")
    try:
        res = ENGINE.run_request(image, prompts, gt, client=getattr(getattr(request, "client", None), "host", None))
    except Exception as e:  # noqa: BLE001
        return blank(f"❌ Lỗi khi chạy model: `{type(e).__name__}: {e}`. Kết quả không được hiển thị.")
    outs = []
    for qi in range(MAX_Q):
        if qi >= len(res["queries"]):
            outs += [gr.Group(visible=False), gr.Markdown(value="")] + [gr.Image(value=None) for _ in le.METHODS] + [gr.Markdown(value="")]
            continue
        q = res["queries"][qi]
        imgs, rows, capped = [], [], False
        for m in le.METHODS:
            if not q["ok"]:
                imgs.append(gr.Image(value=None, label=f"{m} — lỗi lượt 1")); continue
            r = q["results"][m]
            if not r["ok"]:
                imgs.append(gr.Image(value=None, label=f"{m} — LỖI: {r['error']}"))
                rows.append(f"| **{m}** | lỗi | — | `{r['error']}` |")
                continue
            dropped = r["info"].get("dropped_boxes")
            cap = f"{m} · \"{q['prompt']}\": {r['count']}" + ("" if q["gt"] is None else f" (GT {q['gt']})")
            imgs.append(gr.Image(value=render(res["image"], r["boxes"], dropped, COLORS[m], cap),
                                 label=f"{m} — {DESC[m]}"))
            err = "—" if q["gt"] is None else str(abs(r["count"] - q["gt"]))
            extra = ""
            if m in ("P+F", "C6"):
                extra = f" · F giữ {r['count']}/{r['info']['source_count']} box"
            if m in ("B2", "P+F") and r["info"].get("n_pseudo") is not None:
                extra += f" · {r['info']['n_pseudo']} pseudo-exemplar"
            if max(r["count"], r["info"].get("source_count") or 0) >= CAP:
                extra += f" · ⚠ chạm trần {CAP} box"
                capped = True
            rows.append(f"| **{m}** | **{r['count']}**{extra} | {err} | {timing_text(m, r)} |")
        head = f"### Tên vật {qi + 1}: `{q['prompt']}`" + ("" if q["gt"] is None else f" · GT bạn nhập: {q['gt']}")
        if capped:
            head += (f"\n\n⚠ **Có cách chạm trần {CAP} box**: CountGD++ chỉ có {CAP} box đề xuất mỗi ảnh, nên con số này là giới hạn "
                     "của mô hình, không phải số vật thật. Nên dùng ảnh ít vật hơn (dữ liệu của đồ án: 3–40 vật mỗi class).")
        if not q["ok"]:
            table = f"❌ Lỗi ở lượt 1, cả bốn cách đều không có kết quả: `{q['error']}`"
        else:
            table = (f"Lượt 1 (CountGD++ chỉ với tên vật) chạy **một lần** và dùng chung cho cả bốn cách: "
                     f"{fmt_ms(q['shared']['stage1_ms'])}.\n\n| Cách | Số đếm | Sai số so với GT bạn nhập | Thời gian |\n|---|---|---|---|\n"
                     + "\n".join(rows))
        outs += [gr.Group(visible=True), gr.Markdown(value=head)] + imgs + [gr.Markdown(value=table)]
    xy_md = ""
    if res["xy"]:
        lines = ["### Đếm lẫn giữa các tên vật (box dùng chung, IoU ≥ 0.5)",
                 "Tỉ lệ box của hai query có box trùng ở query kia. Cao nghĩa là đổi tên vật mà mô hình vẫn khoanh cùng những vật đó.",
                 "", "| Cặp | " + " | ".join(le.METHODS) + " |", "|---|" + "---|" * len(le.METHODS)]
        for r in res["xy"]:
            cells = [("lỗi" if r[m] is None else (f"{r[m][0]}/{r[m][1]} = {r[m][0] / r[m][1]:.0%}" if r[m][1] else "0 box")) for m in le.METHODS]
            lines.append(f"| `{r['x']}` / `{r['y']}` | " + " | ".join(cells) + " |")
        xy_md = "\n".join(lines)
    env = ENGINE.env
    status = (f"✅ **Đã chạy model thật** trên ảnh vừa nhập ({res['image'].width}×{res['image'].height}) · "
              f"request `{res['request_id']}` · {res['total_s']} s · {env['device']}. "
              + ("Không có GT nên không tính sai số." if all(q["gt"] is None for q in res["queries"]) else
                 "Sai số chỉ tính cho ví dụ này, theo GT bạn nhập; không phải kết quả nghiên cứu."))
    return outs + [gr.Markdown(value=status), gr.Markdown(value=xy_md), gr.JSON(value=res["log"])]


def signature(image, queries, gts):
    """Dấu vân tay của đầu vào: dùng để phát hiện ảnh/tên vật bị đổi trong lúc model đang chạy."""
    import hashlib
    if image is None:
        return None
    return hashlib.md5(image.convert("RGB").resize((64, 64)).tobytes()).hexdigest() + "|" + (queries or "") + "|" + (gts or "")


def stale_check(image, queries, gts, used):
    import gradio as gr
    if used is not None and signature(image, queries, gts) != used:
        return blank("⚠ **Ảnh hoặc tên vật đã đổi trong lúc model đang chạy — đã bỏ kết quả của dữ liệu cũ.** Bấm **Chạy** lại.")
    return [gr.skip()] * n_outputs()


def build():
    import gradio as gr
    e = ENGINE
    cpu_warn = ("\n\n⚠ **Đang chạy trên CPU — chỉ để kiểm chức năng, rất chậm (vài chục giây mỗi tên vật).** "
                "Demo trình bày chạy trên GPU Kaggle T4." if e.device.type == "cpu" else "")
    with gr.Blocks(title="CS331 · Demo đếm vật theo tên (CountGD++)", theme=gr.themes.Soft(), head=PASTE_JS,
                   analytics_enabled=False) as demo:
        gr.Markdown("# Đếm vật theo tên trên ảnh mới — CountGD++ và cải tiến của nhóm (CS331)")
        gr.Markdown(f"Model chạy **thật** trên ảnh bạn đưa vào: `{e.env['device']}` · checkpoint `{e.ckpt_sha[:12]}…` (đã audit) · "
                    f"freeze v2 `{le.FREEZE_SHA[:8]}…` · P(τ {e.tau_pseudo:.2f}, M {e.m}) · F: P+F θ = {e.f_main['threshold']:.3f}, "
                    f"C6 θ = {e.f_c6['threshold']:.3f} (bounds riêng). Ảnh mới không có GT, nên app **không** tính MAE hay khẳng định đếm đúng."
                    + cpu_warn)
        with gr.Row():
            with gr.Column(scale=3):
                img = gr.Image(label="Ảnh — Ctrl+V để dán, kéo thả, hoặc bấm để chọn file", type="pil",
                               sources=["upload", "clipboard"], elem_id="live_image", height=360)
            with gr.Column(scale=2):
                qbox = gr.Textbox(label="Tên vật cần đếm (tiếng Anh, số nhiều; tối đa 3, cách nhau bởi dấu phẩy)",
                                  placeholder="bowls, plates", lines=1, elem_id="live_queries")
                gr.Markdown("Ví dụ: `bowls, plates` · `people, cars` · `apples` · `dogs, sheep`")
                gtbox = gr.Textbox(label="GT (tùy chọn) — số vật thật theo cùng thứ tự, '-' nếu không biết",
                                   placeholder="3, 16", lines=1, elem_id="live_gt")
                with gr.Row():
                    run_btn = gr.Button("Chạy", variant="primary", elem_id="live_run")
                    clear_btn = gr.Button("Xóa và bắt đầu lại", elem_id="live_clear")
        status = gr.Markdown("Dán ảnh (Ctrl+V), kéo thả hoặc bấm vào ô để chọn ảnh, nhập tên vật rồi bấm **Chạy**.", elem_id="live_status")
        groups = []
        for qi in range(MAX_Q):
            with gr.Group(visible=False) as g:
                hd = gr.Markdown()
                with gr.Row():
                    ims = [gr.Image(label=m, type="pil", interactive=False, show_download_button=True) for m in le.METHODS[:2]]
                with gr.Row():
                    ims += [gr.Image(label=m, type="pil", interactive=False, show_download_button=True) for m in le.METHODS[2:]]
                tbl = gr.Markdown()
            groups += [g, hd] + ims + [tbl]
        xy = gr.Markdown()
        with gr.Accordion("Log của lần chạy này (xác nhận đã chạy inference + cấu hình dùng)", open=False):
            log = gr.JSON()
        outs = groups + [status, xy, log]
        ins = [img, qbox, gtbox]
        # ảnh: change (upload/dán/xóa); ô chữ: input (chỉ khi người dùng gõ), để không chen vào sau nút Chạy
        img.change(on_input_change, ins, outs, queue=False)
        qbox.input(on_input_change, ins, outs, queue=False)
        gtbox.input(on_input_change, ins, outs, queue=False)
        used = gr.State(None)
        remember = lambda i, q, g: signature(i, q, g)  # noqa: E731
        for trig in (run_btn.click, qbox.submit):
            (trig(start_run, ins, outs, queue=False)
             .then(remember, ins, used, queue=False)
             .then(run, ins, outs)
             .then(stale_check, ins + [used], outs, queue=False))

        def clear_all():
            return [gr.Image(value=None), gr.Textbox(value=""), gr.Textbox(value="")] + blank(
                "Đã xóa. Dán ảnh mới (Ctrl+V), nhập tên vật rồi bấm **Chạy**.")
        clear_btn.click(clear_all, None, ins + outs, queue=False)
    return demo


def main():
    global ENGINE
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--share", action="store_true", help="Tạo link https *.gradio.live (dùng khi model chạy trên Kaggle)")
    ap.add_argument("--password", default=os.environ.get("DEMO_PASSWORD"), help="Bật đăng nhập (user: cs331)")
    ap.add_argument("--log-dir", default=None)
    a = ap.parse_args()
    t = time.perf_counter()
    ENGINE = le.LiveEngine(a.device, a.log_dir)
    print(f"Model + CLIP đã nạp ({ENGINE.load_s}s) trên {ENGINE.env['device']}; log: {ENGINE.log_path}", flush=True)
    demo = build()
    demo.queue(default_concurrency_limit=1).launch(
        server_name=a.host, server_port=a.port, share=a.share, inbrowser=False, show_api=False,
        auth=("cs331", a.password) if a.password else None, max_file_size="20mb")
    print(f"Dừng sau {time.perf_counter() - t:.0f}s", flush=True)


if __name__ == "__main__":
    main()
