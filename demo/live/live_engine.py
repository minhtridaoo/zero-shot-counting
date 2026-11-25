"""Suy luận THẬT trên ảnh mới cho demo: B0, B2, P+F, C6 với cấu hình đã khóa (freeze v2).

Không sửa file gốc. Ghép lại đúng các bước của pipeline đã chạy test 11/11:
  - nạp model như experiments/countgdpp/run_b2_verified_pseudo.py: lấy định nghĩa hàm từ CountGDPlusPlus/process_folder.py
    (bản pin, kiểm hash), checkpoint đã audit 14/10, seed 42 trước lượt 1, khôi phục RNG về cuối lượt 1 trước mỗi lượt 2;
  - B0 = lượt 1 (giữ box có điểm > 0.23);
  - B2 = lượt 2 với top-3 pseudo-exemplar gốc (run_b2_pilot.select_pseudo); lượt 1 không có box thì B2 = B0;
  - P(τ 0.20, M 5) = CLIP kiểm M ứng viên (pseudo_clip_verifier.top_candidates/choose/ClipVerifier), lượt 2 với các mẫu
    còn lại; không còn mẫu thì = B0; nếu bộ mẫu trùng B2 thì dùng lại đúng lượt 2 đó (runner cũng cache như vậy);
  - F = 0.5·norm(điểm CountGD++) + 0.5·norm(cosine CLIP của box cuối), bounds/threshold lấy từ freeze cho TỪNG cấu hình:
    P+F = nguồn P(τ 0.20) + F(main), C6 = nguồn B0 + F(C6). CLIP của box cuối dùng cùng crop/batch/mẫu câu với
    p4_clip_score.py (ClipVerifier.score, đã qua Kiểm A trên Kaggle).
Lượt 1 chạy MỘT lần cho mỗi query và dùng chung cho cả bốn cách. Model nạp một lần khi khởi động.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import platform
import random
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/countgdpp"))

from run_b0_batch import REPO, SOURCE_HASH, sha  # noqa: E402
from run_b2_pilot import select_pseudo  # noqa: E402
from run_b2_verified_pseudo import source_sha, MAX_PSEUDO, TAU  # noqa: E402
from pseudo_clip_verifier import MODEL_ID, REVISION, TEMPLATE, ClipVerifier, choose, top_candidates  # noqa: E402

FREEZE = ROOT / "results/countgdpp/freeze_v2_20261111.json"
FREEZE_SHA = "64e89ef53eab306fdbb33cfc39797749ff17cc8635f46ae381d96e45c4f6736d"
AUDIT = ROOT / "results/countgdpp/checkpoint_audit_2026-10-14.json"
METHODS = ("B0", "B2", "P+F", "C6")
TZ = timezone(timedelta(hours=7))


def norm(v, b):  # giống apply_freeze_v2.norm
    lo, hi = b
    return .5 if lo == hi else max(0., min(1., (v - lo) / (hi - lo)))


def iou(a, b):  # giống evaluation/test_xy_overlap_analysis.iou
    ix = max(0., min(a[2], b[2]) - max(a[0], b[0])); iy = max(0., min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.


def shared_flags(boxes, others, t=0.5):
    return [any(iou(b, o) >= t for o in others) for b in boxes]


def parse_queries(text: str, max_q: int = 3):
    raw = [q.strip() for part in (text or "").replace(";", ",").splitlines() for q in part.split(",")]
    qs = [q for q in raw if q]
    if not qs:
        raise ValueError("Chưa nhập tên vật cần đếm. Ví dụ: bowls, plates")
    bad = [q for q in qs if any(ch in q for ch in ".?!")]
    if bad:
        raise ValueError(f"Tên vật không được chứa dấu chấm/chấm hỏi/chấm than (CountGD++ dùng dấu chấm để tách câu): {bad}")
    if len(set(q.lower() for q in qs)) != len(qs):
        raise ValueError("Có tên vật bị lặp.")
    if len(qs) > max_q:
        raise ValueError(f"Tối đa {max_q} tên vật mỗi lần chạy (đang nhập {len(qs)}).")
    return qs


def parse_gt(text: str, n: int):
    """GT tùy chọn, cùng thứ tự với tên vật. Ô trống hoặc '-' = không có GT."""
    if not (text or "").strip():
        return [None] * n
    parts = [p.strip() for p in text.replace(";", ",").split(",")]
    if len(parts) != n:
        raise ValueError(f"GT phải có đúng {n} giá trị theo thứ tự tên vật (dùng '-' nếu không biết), đang có {len(parts)}.")
    out = []
    for p in parts:
        if p in ("", "-"):
            out.append(None)
        elif p.isdigit():
            out.append(int(p))
        else:
            raise ValueError(f"GT phải là số nguyên không âm hoặc '-': '{p}'")
    return out


class LiveEngine:
    def __init__(self, device: str = "cuda", log_dir: Path | None = None):
        import numpy as np
        import torch
        self.np, self.torch = np, torch
        t0 = time.perf_counter()
        # ---- kiểm checkpoint, code gốc, freeze (giống runner)
        audit = json.loads(AUDIT.read_text())
        ckpt = REPO / "checkpoints/countgd_plusplus.pth"
        if not ckpt.exists():
            raise FileNotFoundError(f"Thiếu checkpoint {ckpt}")
        self.ckpt_sha = sha(ckpt)
        if self.ckpt_sha != audit["checkpoint_sha256"] or audit.get("review_decision") != "compatible_with_pinned_B0_app":
            raise ValueError("Checkpoint khác bản đã audit 14/10")
        if source_sha(REPO / "process_folder.py") != SOURCE_HASH:
            raise ValueError("process_folder.py khác bản pin")
        for src, digest in audit["review_source_sha256"].items():
            if source_sha(REPO / src) != digest:
                raise ValueError(f"{src} khác bản đã audit")
        if sha(FREEZE) != FREEZE_SHA:
            raise ValueError("freeze_v2 khác sha256 đã khóa")
        fz = json.loads(FREEZE.read_text(encoding="utf-8"))
        assert fz["status"] == "FROZEN_V2"
        a = fz["runner"]["args"]
        assert a["tau_pseudo"] == [0.2] and a["m"] == 5 and fz["runner"]["tau_sample"] == TAU == .23 and fz["runner"]["max_pseudo"] == MAX_PSEUDO == 3
        assert fz["runner"]["clip_model"] == MODEL_ID and fz["runner"]["clip_revision"] == REVISION and fz["runner"]["clip_template"] == TEMPLATE
        self.tau_pseudo, self.m = a["tau_pseudo"][0], a["m"]
        self.f_main = fz["main"]; self.f_c6 = fz["companions_report_only"]["C6 = B0+F"]
        assert self.f_main["source"] == "tau0.200" and self.f_main["filter"] == "F"
        assert self.f_c6["source"] == "B0" and self.f_c6["filter"] == "F"
        # ---- nạp model một lần (giống run_b2_verified_pseudo.main)
        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("Không có CUDA. Demo chính cần GPU (Kaggle T4); --device cpu chỉ để kiểm chức năng.")
        self.cwd0 = os.getcwd()
        sys.path.insert(0, str(REPO)); os.chdir(REPO)
        tree = ast.parse((REPO / "process_folder.py").read_text())
        tree.body = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
        ns = {"__name__": "pinned_stock_definitions"}
        exec(compile(tree, str(REPO / "process_folder.py"), "exec"), ns)
        self.ns = ns
        self.device = torch.device(device)
        model, self.transform = ns["build_model_and_transforms"](ns["build_arg_parser"]().parse_args([]))
        self.model = model.to(self.device)
        self.clip = ClipVerifier(self.device)
        original = ns["get_boxes_from_prediction"]; self._cap = {}

        def observe(output, text, keywords="", conf_thresh=TAU):
            returned = original(output, text, keywords, conf_thresh)
            self._cap.update(scores=output["pred_logits"][0].sigmoid().detach().cpu(),
                             boxes=output["pred_boxes"][0].detach().cpu(),
                             ids=output["input_ids"][0].detach().cpu().tolist())
            return returned
        ns["get_boxes_from_prediction"] = observe
        self.load_s = round(time.perf_counter() - t0, 1)
        self.env = dict(device=torch.cuda.get_device_name() if self.device.type == "cuda" else f"CPU ({platform.processor() or platform.machine()})",
                        torch=torch.__version__, transformers=self.clip.transformers_version, python=sys.version.split()[0],
                        checkpoint_sha256=self.ckpt_sha, freeze_sha256=FREEZE_SHA, clip_model=MODEL_ID, clip_revision=self.clip.revision,
                        process_folder_sha256=SOURCE_HASH)
        self.config = dict(tau_sample=TAU, tau_final=TAU, max_pseudo=MAX_PSEUDO, tau_pseudo=self.tau_pseudo, m=self.m,
                           seed=42, resize=dict(short_side=800, max_size=1333), clip_template=TEMPLATE,
                           F_PplusF=dict(bounds=self.f_main["bounds"], threshold=self.f_main["threshold"]),
                           F_C6=dict(bounds=self.f_c6["bounds"], threshold=self.f_c6["threshold"]))
        self.log_dir = Path(log_dir) if log_dir else ROOT / "demo/live/logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / "requests.jsonl"

    # ------------------------------------------------------------ helpers
    def _sync(self):
        if self.device.type == "cuda":
            self.torch.cuda.synchronize()

    def _predict(self, image, prompt, exemplars):
        np = self.np; ns = self.ns
        prompts = {"image": image, "points": [[b[0], b[1], 2.0, b[2], b[3], 3.0] for b in exemplars]}
        b, s = ns["predict"](self.model, self.transform, image, prompt, prompts, [], [], self.device, TAU)
        x, y, w, h = ns["get_box_coords_from_boxes"](image, b)
        return np.stack((x, y, x + w, y + h), axis=1).reshape(-1, 4), np.asarray(s).reshape(-1), dict(self._cap)

    def _rng_state(self):
        t = self.torch
        return (t.get_rng_state(), t.cuda.get_rng_state_all() if self.device.type == "cuda" else None,
                self.np.random.get_state(), self.ns["random"].getstate(), random.getstate())

    def _set_rng(self, st):
        t = self.torch
        t.set_rng_state(st[0])
        if st[1] is not None:
            t.cuda.set_rng_state_all(st[1])
        self.np.random.set_state(st[2]); self.ns["random"].setstate(st[3]); random.setstate(st[4])

    def _f_keep(self, scores, clips, cfg):
        b = cfg["bounds"]
        fs = [.5 * norm(a, b["countgd"]) + .5 * norm(c, b["clip"]) for a, c in zip(scores, clips)]
        return fs, [f >= cfg["threshold"] for f in fs]

    # ------------------------------------------------------------ one query
    def run_query(self, image, prompt):
        """Trả dict theo phương pháp. Lỗi của một phương pháp được ghi riêng, không thay bằng phương pháp khác."""
        torch, np, ns = self.torch, self.np, self.ns
        out = {m: dict(ok=False, error=None, boxes=[], scores=[], count=None, timing={}, info={}) for m in METHODS}
        torch.manual_seed(42); np.random.seed(42); ns["random"].seed(42)
        self._sync(); t = time.perf_counter()
        b0, s0, cap0 = self._predict(image, prompt, [])
        self._sync(); stage1_ms = (time.perf_counter() - t) * 1000
        after = self._rng_state()
        shared = dict(stage1_ms=round(stage1_ms, 1))
        cache = {}

        def stage2(boxes):
            key = json.dumps(boxes)
            if key in cache:
                return cache[key] + (True,)
            self._set_rng(after)
            self._sync(); t2 = time.perf_counter()
            final, sf, _ = self._predict(image, prompt, boxes)
            self._sync()
            cache[key] = (final, sf, round((time.perf_counter() - t2) * 1000, 1))
            return cache[key] + (False,)

        # B0
        out["B0"].update(ok=True, boxes=b0.tolist(), scores=s0.tolist(), count=len(b0), timing=dict(stage1_ms=shared["stage1_ms"]))
        # B2
        try:
            pb, ps, _, _ = select_pseudo(cap0["scores"], cap0["boxes"], cap0["ids"], image.size, threshold=TAU, maximum=MAX_PSEUDO)
            chosen = pb.tolist()
            if chosen:
                final, sf, ms, reused = stage2(chosen)
                tim = dict(stage1_ms=shared["stage1_ms"], stage2_ms=ms)
            else:
                final, sf = b0, s0; tim = dict(stage1_ms=shared["stage1_ms"], stage2_ms=None)
            out["B2"].update(ok=True, boxes=final.tolist(), scores=sf.tolist(), count=len(final), timing=tim,
                             info=dict(n_pseudo=len(chosen), pseudo_boxes=chosen, stage2_executed=bool(chosen)))
        except Exception as e:  # noqa: BLE001
            out["B2"]["error"] = f"{type(e).__name__}: {e}"
        # P(τ 0.20, M 5) rồi F
        try:
            t = time.perf_counter()
            cands, _ = top_candidates(cap0["scores"], cap0["boxes"], cap0["ids"], image.size, TAU, self.m)
            for c, cos in zip(cands, self.clip.score(image, [c["box_xyxy"] if c["valid"] else [0, 0, 1, 1] for c in cands], prompt)):
                c["clip_cosine"] = cos if c["valid"] else None
            self._sync(); verify_ms = round((time.perf_counter() - t) * 1000, 1)
            picked = choose(cands, self.tau_pseudo, MAX_PSEUDO)
            pboxes = [c["box_xyxy"] for c in picked]
            if pboxes:
                pf, psf, ms, reused = stage2(pboxes)
            else:
                pf, psf, ms, reused = b0, s0, None, False
            t = time.perf_counter()
            clips = self.clip.score(image, pf.tolist(), prompt)
            self._sync(); clip_ms = round((time.perf_counter() - t) * 1000, 1)
            fs, keep = self._f_keep(psf.tolist(), clips, self.f_main)
            kb = [b for b, k in zip(pf.tolist(), keep) if k]; ks = [s for s, k in zip(psf.tolist(), keep) if k]
            out["P+F"].update(ok=True, boxes=kb, scores=ks, count=len(kb),
                              timing=dict(stage1_ms=shared["stage1_ms"], clip_verify_ms=verify_ms,
                                          stage2_ms=0.0 if reused else ms, stage2_reused_from_B2=reused, clip_final_ms=clip_ms),
                              info=dict(n_candidates=len(cands), n_pseudo=len(pboxes), stage2_executed=bool(pboxes),
                                        same_exemplars_as_B2=reused, source_boxes=pf.tolist(), source_count=len(pf),
                                        dropped_boxes=[b for b, k in zip(pf.tolist(), keep) if not k], f_scores=fs,
                                        candidate_clip=[c["clip_cosine"] for c in cands]))
        except Exception as e:  # noqa: BLE001
            out["P+F"]["error"] = f"{type(e).__name__}: {e}"
        # C6 = B0 rồi F (bounds/threshold riêng)
        try:
            t = time.perf_counter()
            clips0 = self.clip.score(image, b0.tolist(), prompt)
            self._sync(); clip_ms = round((time.perf_counter() - t) * 1000, 1)
            fs, keep = self._f_keep(s0.tolist(), clips0, self.f_c6)
            kb = [b for b, k in zip(b0.tolist(), keep) if k]; ks = [s for s, k in zip(s0.tolist(), keep) if k]
            out["C6"].update(ok=True, boxes=kb, scores=ks, count=len(kb), timing=dict(stage1_ms=shared["stage1_ms"], clip_final_ms=clip_ms),
                             info=dict(source_count=len(b0), dropped_boxes=[b for b, k in zip(b0.tolist(), keep) if not k], f_scores=fs))
        except Exception as e:  # noqa: BLE001
            out["C6"]["error"] = f"{type(e).__name__}: {e}"
        return out, shared

    # ------------------------------------------------------------ request
    def run_request(self, image, prompts, gts=None, client=None):
        image = image.convert("RGB")
        rid = datetime.now(TZ).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
        buf = __import__("io").BytesIO(); image.save(buf, format="PNG")
        img_sha = hashlib.sha256(buf.getvalue()).hexdigest()
        t = time.perf_counter()
        per_q = []
        for q, gt in zip(prompts, gts or [None] * len(prompts)):
            try:
                res, shared = self.run_query(image, q)
                per_q.append(dict(prompt=q, gt=gt, ok=True, results=res, shared=shared, error=None))
            except Exception as e:  # noqa: BLE001  lỗi lượt 1: cả bốn cách đều không có kết quả
                per_q.append(dict(prompt=q, gt=gt, ok=False, results=None, shared=None, error=f"{type(e).__name__}: {e}"))
        total_s = round(time.perf_counter() - t, 2)
        # box dùng chung giữa các cặp query, theo từng cách (cùng định nghĩa với báo cáo, IoU >= 0.5)
        xy = []
        for i in range(len(per_q)):
            for j in range(i + 1, len(per_q)):
                a, b = per_q[i], per_q[j]
                row = dict(x=a["prompt"], y=b["prompt"])
                for m in METHODS:
                    if a["ok"] and b["ok"] and a["results"][m]["ok"] and b["results"][m]["ok"]:
                        X, Y = a["results"][m]["boxes"], b["results"][m]["boxes"]
                        s = sum(shared_flags(X, Y)) + sum(shared_flags(Y, X))
                        row[m] = (s, len(X) + len(Y))
                    else:
                        row[m] = None
                xy.append(row)
        rec = dict(request_id=rid, time=datetime.now(TZ).isoformat(timespec="seconds"), inference=True,
                   image_sha256_png=img_sha, image_size=list(image.size), prompts=prompts, gt_user=gts,
                   env=self.env, config=self.config, total_s=total_s, client=client,
                   queries=[dict(prompt=p["prompt"], error=p["error"], stage1_ms=(p["shared"] or {}).get("stage1_ms"),
                                 methods={m: dict(ok=r["ok"], count=r["count"], error=r["error"], timing=r["timing"],
                                                  n_pseudo=r["info"].get("n_pseudo"), same_exemplars_as_B2=r["info"].get("same_exemplars_as_B2"))
                                          for m, r in (p["results"] or {}).items()}) for p in per_q],
                   xy_shared={f"{r['x']}|{r['y']}": {m: r[m] for m in METHODS} for r in xy})
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[inference] {rid} {image.size} {prompts} -> " +
              " | ".join(f"{p['prompt']}: " + (", ".join(f"{m}={p['results'][m]['count']}" for m in METHODS) if p["ok"] else p["error"]) for p in per_q)
              + f" ({total_s}s, {self.env['device']})", flush=True)
        return dict(request_id=rid, image_sha256=img_sha, image=image, queries=per_q, xy=xy, total_s=total_s, log=rec)
