# CS331 — Zero-shot counting: CountGD++ và lỗi đếm nhầm loại (X/Y)

**Nhóm:** Trí, Triệu · **Repo:** github.com/minhtridaoo/zero-shot-counting · **Hạn báo cáo:** 02/12/2026
**Trạng thái và việc tiếp theo:** đọc [BAT_DAU_SESSION_MOI.md](BAT_DAU_SESSION_MOI.md) trước tiên.

**Bài toán:** cùng một ảnh có hai loại X và Y. Hỏi X thì phải đếm X; đổi sang Y thì phải đếm Y, không đếm lại vật của X. Hỏi loại không có trong ảnh thì phải trả 0.
**Model:** CountGD++, không train lại. Cải tiến đang thử là nhánh **P**: CLIP kiểm mẫu tự chọn trước lượt 2, kèm biến thể **T**.

## Bản đồ thư mục

| Thư mục / file | Dùng để làm gì |
|---|---|
| `BAT_DAU_SESSION_MOI.md` | **Trạng thái hiện tại + việc tiếp theo** (một trang) |
| `roadmap/KE_HOACH_HOAN_THANH_20261110.md` | **Kế hoạch đến 02/12**, định nghĩa "hoàn thành", vị trí nhánh P/R |
| `WORKLOG.md` | Nhật ký mọi lượt làm việc (mục mới nhất ở trên cùng) |
| `AGENTS.md` | Quy tắc cho assistant khi mở phiên mới |
| `HANDOFF/` | Việc của Triệu: `GIAO_VIEC_TRIEU_20261106.md` (W1–W7), `HANDOFF_TRIEU.md` |
| `reports/` | **Báo cáo kết quả** dùng để viết báo cáo cuối (xem danh sách dưới) |
| `experiments/countgdpp/` | Code chạy model + **dữ liệu đã khóa** (`p4_unseen_v1/`, `dev_test_v2/`, `m4_inputs/`) |
| `experiments/benchmark_fscd147/` | Notebook Kaggle tái lập benchmark FSCD-147 |
| `evaluation/` | Code chấm điểm (evaluator, scorer, tạo gói review, app gán nhãn) |
| `results/countgdpp/` | Output các lần chạy; danh mục ở [results/README.md](results/README.md) |
| `workspace Trí and Triệu/` | Dữ liệu pilot MUCCA 10 ảnh và review gốc của Triệu. Manifest pilot trỏ vào đây, **không di chuyển** |
| `hướng cái tiển/` | Hai tài liệu đề xuất cải tiến / định hướng paper của Trí (27/10) |
| `CountGDPlusPlus/` | Code + checkpoint model (1,7 GB, không sửa) |
| `data_external/` | MUCCA 1.0 tải từ Zenodo (không đưa lên git) |
| `quá khứ/` | **Kho lưu trữ**: tài liệu cũ, snapshot, CLIP-Count. Xem [quá khứ/2026-11-10_don_dep/README.md](<quá khứ/2026-11-10_don_dep/README.md>) |

## Báo cáo kết quả (`reports/`), theo thứ tự câu chuyện

1. [BENCHMARK_FSCD147.md](reports/BENCHMARK_FSCD147.md): tái lập CountGD++ trên 1.190 ảnh (MAE 8.34).
2. [PILOT_SUMMARY.md](reports/PILOT_SUMMARY.md): pilot 5 ảnh, tìm ra lỗi đếm nhầm loại. [TRIEU_TU_KIEM_PHAN2_20261027.md](reports/TRIEU_TU_KIEM_PHAN2_20261027.md) là kiểm chéo của Triệu (V1–V6).
3. [P4_CLIP_EXPLORATORY_FINDINGS_20261021.md](reports/P4_CLIP_EXPLORATORY_FINDINGS_20261021.md) + [P4_AUDIT_20261022.md](reports/P4_AUDIT_20261022.md): cải tiến v1 (lọc điểm / Fusion CLIP) và freeze.
4. [P4_6_UNSEEN_RESULTS_20261027.md](reports/P4_6_UNSEEN_RESULTS_20261027.md): kiểm trên 10 ảnh mới.
5. [N4_KET_QUA_TANG_A_20261029.md](reports/N4_KET_QUA_TANG_A_20261029.md) + [RA_SOAT_TRIEU_N4_20261029.md](reports/RA_SOAT_TRIEU_N4_20261029.md): review khung bằng người, cơ chế lỗi (điểm mẫu ảnh lấn át điểm chữ).
6. [TRIEU_DE_XUAT_NHANH_P_20261029.md](reports/TRIEU_DE_XUAT_NHANH_P_20261029.md), [TRIEU_P1_COLAB_T4_20261103.md](reports/TRIEU_P1_COLAB_T4_20261103.md), [TRIEU_DE_XUAT_QUY_TAC_DU_LIEU_V2_20261104.md](reports/TRIEU_DE_XUAT_QUY_TAC_DU_LIEU_V2_20261104.md): nhánh P và dữ liệu v2.
7. [KE_HOACH_TIEP_THEO_20261105.md](reports/KE_HOACH_TIEP_THEO_20261105.md): **10 quyết định D1–D10 đã chốt** (máy chuẩn, dữ liệu, biến thể, luật chọn D9).
8. [TOM_TAT_DU_AN_20261027.md](reports/TOM_TAT_DU_AN_20261027.md): tóm tắt dự án cho demo (bản 27/10).

## Môi trường chạy

- CountGD++: WSL `Ubuntu-22.04`, venv `/root/.venvs/countgdpp` (máy Trí, RTX A2000). CLIP: WSL `Ubuntu`, venv `/root/.venvs/cs331-p4-clip`.
- **Máy chuẩn cho các so sánh mới (D1): Colab T4**, notebook `experiments/countgdpp/colab_p1_verified_pseudo.ipynb`, hướng dẫn `experiments/countgdpp/COLAB_P1_HUONG_DAN.md`.
