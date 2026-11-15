"""Report figures from saved outputs only (no model run). Post-hoc illustration of the LOCKED test run.

  fig_pipeline.png         pipeline diagram (B0 -> pass 2 -> Fusion filter), with where errors arise / are fixed
  fig_example_<qid>.png    one test query, 4 panels: B0 | B2 | P+F (main) | C6; kept boxes coloured by MUCCA GT
                           points: green = contains a point of the queried class, red = only points of another
                           class, grey = no point. GT points of the queried class drawn as small white dots.
  fig_results_test.png     test MAE per configuration with 95% image-bootstrap CI of the difference vs B0

Run from the CS331 root:  python evaluation/make_report_figures.py
"""
import csv, json, sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evaluation"))
from test_xy_overlap_analysis import BUNDLE, MANIFEST, ANN, RUN, configs, kept, inside  # noqa: E402

FIG = ROOT / "reports/figures"
IMG = ROOT / "data_external/mucca_zenodo_19231375/MUCCA_1.0/images"
EXAMPLES = ["t05_1", "t01_2", "t33_1", "t40_1"]
PANELS = ["B0", "B2", "P+F (chính)", "C6 = B0+F"]
GREEN, RED, GREY = "#1a9850", "#d73027", "#9e9e9e"


def pipeline():
    fig, ax = plt.subplots(figsize=(13, 4.6)); ax.set_xlim(0, 13); ax.set_ylim(0, 4.6); ax.axis("off")

    def box(x, y, w, h, text, fc, ec="#333", fs=9.5, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05", fc=fc, ec=ec, lw=1.3))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, weight="bold" if bold else None, wrap=True)

    def arrow(x0, y0, x1, y1, color="#333", style="-|>"):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle=style, color=color, lw=1.5))

    box(0.1, 1.9, 1.6, 1.0, "Ảnh +\ntruy vấn chữ\n(vd: \"bowls\")", "#f5f5f5")
    box(2.1, 1.9, 1.9, 1.0, "CountGD++\nlượt 1\n(chỉ chữ)", "#dbe9f6", bold=True)
    box(2.1, 3.4, 1.9, 0.8, "B0: đếm = số khung\nđiểm ≥ 0.23", "#eeeeee", fs=8.5)
    arrow(1.7, 2.4, 2.1, 2.4); arrow(3.05, 2.9, 3.05, 3.4)
    box(4.5, 1.9, 2.1, 1.0, "Chọn mẫu giả\ntừ khung lượt 1\n(B2: top-3 điểm)", "#fde7d4")
    box(4.5, 0.5, 2.1, 1.0, "P: CLIP kiểm mẫu giả\n(cos ≥ τ = 0.20,\nxét M = 5 ứng viên)", "#fff3c4")
    arrow(4.0, 2.4, 4.5, 2.4); arrow(5.55, 1.9, 5.55, 1.5)
    box(7.1, 1.9, 1.9, 1.0, "CountGD++\nlượt 2\n(chữ + mẫu giả)", "#dbe9f6", bold=True)
    arrow(6.6, 2.4, 7.1, 2.4); arrow(6.6, 1.0, 7.5, 1.9)
    box(9.5, 1.9, 2.0, 1.0, "Bộ lọc Fusion F\n0.5·CountGD + 0.5·CLIP\n≥ ngưỡng (khóa từ dev)", "#d9f0d3", bold=True, fs=8.8)
    arrow(9.0, 2.4, 9.5, 2.4)
    box(11.85, 1.9, 1.05, 1.0, "Số\nđếm", "#f5f5f5", bold=True)
    arrow(11.5, 2.4, 11.85, 2.4)
    # C6 shortcut: B0 boxes straight into F
    ax.annotate("", xy=(10.5, 2.9), xytext=(4.0, 3.8),
                arrowprops=dict(arrowstyle="-|>", color="#1a9850", lw=1.4, ls="--", connectionstyle="arc3,rad=-0.15"))
    ax.text(7.3, 4.25, "C6 = B0 + F (bỏ lượt 2) — tốt nhất trên test, báo kèm", color="#1a9850", fontsize=9, ha="center")
    # error / fix notes
    ax.text(5.55, 3.25, "✗ lỗi: mẫu giả có thể là\nvật loại khác → lượt 2 đếm\nthêm vật sai (B2 kém B0)", color=RED, fontsize=8.3, ha="center")
    ax.text(8.6, 1.2, "✗ điểm lượt 2 = max(chữ, mẫu)\n→ điểm mẫu lấn át chữ", color=RED, fontsize=8.3, ha="center")
    ax.text(10.9, 1.2, "✓ sửa: CLIP chấm từng khung\ntheo đúng chữ được hỏi", color=GREEN, fontsize=8.3, ha="center")
    ax.text(0.1, 0.02, "Cấu hình chính (khóa trước test): P(τ 0.20, M 5) + F.  B0 = lượt 1;  B2 = lượt 2 gốc;  B2+F = B2 + bộ lọc.",
            fontsize=8.5, color="#333")
    fig.tight_layout(); fig.savefig(FIG / "fig_pipeline.png", dpi=170); plt.close(fig)


def examples():
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    src = {n: {r["query_id"]: r for r in rows} for n, rows in bundle["sources"].items()}
    man = {r["query_id"]: r for r in csv.DictReader(open(MANIFEST, encoding="utf-8", newline=""))}
    ann = json.loads(ANN.read_text(encoding="utf-8")); cfgs = configs()
    for qid in EXAMPLES:
        m = man[qid]; a = ann[m["image_id"] + ".jpg"]; cls = int(m["class_id"])
        own = [p for p, k in zip(a["points"], a["classes"]) if k == cls]
        oth = [p for p, k in zip(a["points"], a["classes"]) if k != cls]
        others = sorted({r["prompt"] for r in man.values() if r["image_id"] == m["image_id"] and r["query_id"] != qid
                         and r["presence_status"] != "absent"})
        im = Image.open(IMG / f"{m['image_id']}.jpg").convert("RGB")
        fig, axs = plt.subplots(1, 4, figsize=(17, 4.9 * im.height / im.width + 0.9))
        for ax, name in zip(axs, PANELS):
            K = kept(cfgs[name], src[cfgs[name]["source"]][qid])
            ax.imshow(im); ax.axis("off")
            ng = nr = 0
            for b in K:
                if any(inside(b, p) for p in own): col = GREEN; ng += 1
                elif any(inside(b, p) for p in oth): col = RED; nr += 1
                else: col = GREY
                ax.add_patch(Rectangle((b[0], b[1]), b[2] - b[0], b[3] - b[1], fill=False, ec=col, lw=1.6))
            for p in own:
                ax.plot(p[0], p[1], "o", ms=3.5, mfc="white", mec="black", mew=.6)
            ax.set_title(f"{name}: đếm {len(K)} (GT {m['gt_count']})\nđúng loại {ng} · loại khác {nr} · không trúng {len(K) - ng - nr}",
                         fontsize=10)
        fig.suptitle(f"Test {qid} — ảnh {m['image_id']}, hỏi \"{m['prompt']}\" (vật khác có mặt: {', '.join(others)})  "
                     f"[xanh = trúng đúng loại, đỏ = chỉ trúng loại khác, xám = không trúng điểm GT; chấm trắng = điểm GT]",
                     fontsize=10)
        fig.tight_layout(); fig.savefig(FIG / f"fig_example_{qid}_{m['image_id']}.png", dpi=130); plt.close(fig)


def results_bar():
    e = json.loads((Path(str(RUN) + "_eval") / "result.json").read_text(encoding="utf-8"))
    order = ["B0", "B2", "P(tau 0.20, M 5)+F", "B2+F", "C6 = B0+F"]
    label = {"B0": "B0\n(1 lượt)", "B2": "B2\n(2 lượt gốc)", "P(tau 0.20, M 5)+F": "P+F\n(CHÍNH, đã khóa)",
             "B2+F": "B2+F\n(báo kèm)", "C6 = B0+F": "C6 = B0+F\n(báo kèm)"}
    col = {"B0": "#9e9e9e", "B2": RED, "P(tau 0.20, M 5)+F": "#2166ac", "B2+F": "#92c5de", "C6 = B0+F": GREEN}
    s, bt = e["summary"], e["vs_B0_image_bootstrap"]
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    for k, name in enumerate(order):
        v = s[name]["all"]["MAE"]; ax.bar(k, v, color=col[name], width=.62)
        t = f"{v:.2f}"
        if name in bt:
            d, (lo, hi) = bt[name]["diff"], bt[name]["ci95"]; t += f"\nΔ {d:+.2f}\n[{lo:+.2f}, {hi:+.2f}]"
        ax.text(k, v + .15, t, ha="center", va="bottom", fontsize=8.6)
    ax.set_xticks(range(len(order))); ax.set_xticklabels([label[n] for n in order], fontsize=9)
    ax.set_ylabel("MAE trên test (119 query) — thấp hơn là tốt"); ax.set_ylim(0, 13.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Kết quả test (chạy một lần, Kaggle T4). Δ = chênh MAE so với B0, CI 95% bootstrap theo ảnh", fontsize=9.5)
    fig.tight_layout(); fig.savefig(FIG / "fig_results_test.png", dpi=170); plt.close(fig)


def strata_errors():
    """Post-hoc: MAE by pair type + over/under-count decomposition (from test_stratified_posthoc.py output)."""
    d = json.loads((Path(str(RUN) + "_posthoc_20261111") / "stratified.json").read_text(encoding="utf-8"))["result"]
    order = ["B0", "B2", "P(tau 0.20, M 5)+F", "B2+F", "C6 = B0+F"]
    short = {"B0": "B0", "B2": "B2", "P(tau 0.20, M 5)+F": "P+F\n(chính)", "B2+F": "B2+F", "C6 = B0+F": "C6"}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.4))
    x = range(len(order)); w = .38
    for off, pt, col, lab in ((-w / 2, "distinct", "#762a83", "cặp khác hẳn (13 ảnh, 39 query)"),
                              (w / 2, "confusable", "#e08214", "cặp dễ nhầm (27 ảnh, 80 query)")):
        vals = [d[n][pt]["MAE"] for n in order]
        a1.bar([i + off for i in x], vals, w, color=col, label=lab)
        for i, v in zip(x, vals):
            a1.text(i + off, v + .15, f"{v:.1f}", ha="center", fontsize=8.5)
    a1.set_xticks(list(x)); a1.set_xticklabels([short[n] for n in order]); a1.set_ylabel("MAE")
    a1.set_title("MAE theo loại cặp (hậu kiểm)", fontsize=10); a1.legend(fontsize=8.5, frameon=False)
    a1.spines[["top", "right"]].set_visible(False)
    over = [d[n]["present_errors"]["over_sum"] for n in order]; under = [-d[n]["present_errors"]["under_sum"] for n in order]
    a2.bar(list(x), over, .6, color=RED, label="đếm thừa (tổng số vật thừa)")
    a2.bar(list(x), under, .6, color="#4393c3", label="đếm thiếu (tổng số vật thiếu)")
    for i, (o, u) in enumerate(zip(over, under)):
        a2.text(i, o + 12, f"+{o}", ha="center", fontsize=8.5); a2.text(i, u - 40, f"{u}", ha="center", fontsize=8.5)
    a2.axhline(0, color="#333", lw=.8); a2.set_xticks(list(x)); a2.set_xticklabels([short[n] for n in order])
    a2.set_title("79 query có mặt: lỗi đếm thừa so với đếm thiếu", fontsize=10); a2.legend(fontsize=8.5, frameon=False, loc="upper right")
    a2.spines[["top", "right"]].set_visible(False); a2.set_ylim(-480, 860)
    fig.tight_layout(); fig.savefig(FIG / "fig_strata_errors.png", dpi=170); plt.close(fig)


def protocol():
    fig, ax = plt.subplots(figsize=(13, 3.3)); ax.set_xlim(0, 13); ax.set_ylim(0, 3.3); ax.axis("off")
    steps = [("MUCCA 1.0\n200 ảnh, 45 lớp\nnhãn điểm", "#f5f5f5"),
             ("Rút bằng quy tắc cố định\n(seed 331, 3–40 điểm/lớp)\nbỏ 15 ảnh đã dùng", "#eeeeee"),
             ("Người kiểm nhãn\nGT có mặt + lớp vắng mặt\n→ KHÓA (hash)", "#fde7d4"),
             ("DEV 20 ảnh / 60 query\nthử B0, B2, P(τ, M), T,\nS/F, C6 → luật D9", "#dbe9f6"),
             ("KHÓA cấu hình\nfreeze_v2 (sha256)\nP(0.20, 5)+F", "#fff3c4"),
             ("TEST 40 ảnh / 119 query\nchạy MỘT lần, T4\nkiểm độc lập", "#d9f0d3")]
    for i, (t, c) in enumerate(steps):
        x = .1 + i * 2.15
        ax.add_patch(FancyBboxPatch((x, 1.0), 1.85, 1.5, boxstyle="round,pad=0.05", fc=c, ec="#333", lw=1.2))
        ax.text(x + .925, 1.75, t, ha="center", va="center", fontsize=8.8)
        if i:
            ax.annotate("", xy=(x, 1.75), xytext=(x - .3, 1.75), arrowprops=dict(arrowstyle="-|>", lw=1.4))
    ax.text(6.5, .45, "Chọn trước, xem sau: luật D9 chốt trước khi chạy dev; ngưỡng chỉ học trên dev; đối chứng báo kèm chốt trong freeze trước khi chạy test; "
            "test không dùng để chỉnh.", ha="center", fontsize=9, color="#333")
    ax.text(6.5, 2.95, "Giao thức thực nghiệm (tránh \"chọn theo kết quả\")", ha="center", fontsize=10.5, weight="bold")
    fig.tight_layout(); fig.savefig(FIG / "fig_protocol.png", dpi=170); plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    pipeline(); examples(); results_bar(); strata_errors(); protocol()
    print("ok ->", FIG)
