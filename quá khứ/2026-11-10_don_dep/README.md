# Dọn workspace 10/11/2026 — đã chuyển gì vào đây và vì sao

Theo yêu cầu của Trí: giữ lại file cần thiết, gom phần không còn dùng. **Không xóa bằng chứng**: tài liệu cũ được chuyển vào đây bằng `git mv` (giữ lịch sử). Mọi link trong tài liệu đã được tự động sửa theo vị trí mới. Snapshot trước khi dọn: `../snapshots/2026-11-10_truoc_don_dep.zip` (tất cả file chữ/code/csv/json).

| Ở đây | Trước đây ở | Vì sao không còn dùng |
|---|---|---|
| `roadmap/CHECKLIST_3_GIO.md`, `P4_TIEP_THEO.md`, `PHAN_2_DANH_GIA.md`, `PHAN_3_TONG_KET.md`, `PIPELINE_COUNTGDPP.md`, `PIPELINE_PHAN_CONG.md`, `KE_HOACH_CAI_TIEN_20261027.md`, `VI_TRI_PIPELINE_20261028.md`, `ROADMAP.md` | `roadmap/` | Kế hoạch / checklist các giai đoạn đã qua; thay bằng `roadmap/KE_HOACH_HOAN_THANH_20261110.md` + `BAT_DAU_SESSION_MOI.md` |
| `reports/DANH_GIA_TRIEU_*`, `KE_HOACH_SUA_KIEM_CHEO_20261027.md`, `KIEM_LAI_TRUOC_DUYET_20261105.md`, `SYNC_TRIEU_20261027.md`, `TRIEU_EVALUATOR_CROSSCHECK_20261021.md`, `TRIEU_KET_QUA_KIEM_CHEO_20261024.md` | `reports/` | Giấy tờ kiểm chéo / giao nhận đã đóng; kết quả của chúng đã nằm trong các report còn lại ở `reports/` |
| `HANDOFF/HANDOFF.md`, `HANDOFF_MODEL.md`, `GIAO_VIEC_TRIEU_20261028.md` | `HANDOFF/` | Trạng thái nay ở `BAT_DAU_SESSION_MOI.md`; việc đợt 1 của Triệu (V1–V6) đã xong |
| `workspace/HANDOFF_CS331_PILOT_TO_P4_2026-10-22.md` | `workspace Trí and Triệu/Trí/` | Handoff cũ 22/10 |
| `CLIP-Count/` | gốc repo | Hướng model cũ đã bỏ (tháng 9–10); không code nào dùng |
| `README_cu.md`, `BAT_DAU_SESSION_MOI_cu.md`, `AGENTS_cu.md` | gốc repo | Bản trước khi viết lại cho gọn |

Benchmark FSCD-147 (`KAGGLE_PAPER_EVAL.md`, notebook, `build_kaggle_notebook.py`) **không** vào kho lưu trữ, mà chuyển sang `experiments/benchmark_fscd147/`.

**Đã xóa** (tạo lại được hoặc còn trong lịch sử git):
- `results/countgdpp.zip`, `results/countgdpp/b2_remaining3_20261015.zip`: bản sao của thư mục.
- `HANDOFF/TRIEU_GIAO_VIEC_20261028.zip`, `HANDOFF/TRIEU_T1_T4_20261027_v2.zip`: gói gửi Triệu, đã giao xong.
- `reports/PILOT_SUMMARY.md.bak*`, `experiments/countgdpp/__pycache__/`.
- Snapshot local 58,5 MB `2026-10-27_truoc_pull_36eaf96.zip`: nội dung đã có trong git từ commit e877541.

**Không động tới:** code `.py` (hash có trong audit), dữ liệu đã khóa, freeze, prediction, nhãn, `results/` (chỉ thêm `results/README.md`), dữ liệu pilot trong `workspace Trí and Triệu/`.
