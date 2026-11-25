# Demo xem lại (tầng A) — CountGD++ trên ảnh nhiều class

**Kết quả đã lưu; không chạy model trực tiếp.** App chỉ đọc output của lần chạy test một lần ngày 11/11/2026 (Kaggle T4) và tính lại số đếm bằng cấu hình đã khóa. Chạy trên CPU, chỉ mở tại `127.0.0.1` (không có link public).

## Dữ liệu app đọc (chỉ đọc, không sửa)

| File | Vai trò |
|---|---|
| `results/countgdpp/p1_test_kaggle_t4_20261111_1430_offline/bundle.json` | box, điểm CountGD++, cosine CLIP của B0, B2, P(τ 0.20) |
| `results/countgdpp/freeze_v2_20261111.json` | bounds + threshold **riêng** của từng cấu hình: P+F θ = 0.604, C6 θ = 0.427 |
| `experiments/countgdpp/dev_test_v2/test/manifest.csv` | GT; 120 query, `t37_1` là `uncertain` nên bị loại → 119 query hợp lệ |
| `results/countgdpp/p1_test_kaggle_t4_20261111_1430_eval/result.json` | số chính thức để đối chiếu |
| `results/countgdpp/p1_test_kaggle_t4_20261111_1430_posthoc_20261111/summary.json` | shared box X/Y chính thức |
| `data_external/mucca_zenodo_19231375/MUCCA_1.0/images/` | ảnh MUCCA (nằm ở checkout gốc `D:\MINHTRIHOCCODE\HOCKI5\CS331`, app tự tìm ngược lên các thư mục cha) |

## Tự kiểm khi khởi động

App dừng ngay nếu một trong các điều sau sai:
- hash của freeze, bundle và manifest khớp `result.json`;
- 120 query, đúng 1 query `uncertain` (`t37_1`);
- số đếm 120/120 query của B0, B2, P+F, C6 bằng `result.json`;
- MAE, RMSE, MAE present và FPR_absent bằng `result.json`;
- MAE làm tròn ra B0 7.71, B2 9.61, P+F 5.82, C6 4.63;
- shared box X/Y (IoU ≥ 0.5, gộp trên 39 ảnh) bằng `summary.json`.

Chỉ chạy phần kiểm, không mở giao diện:

```powershell
.venv-demo\Scripts\python demo\app_replay.py --check-only
```

## Cài đặt (chỉ làm một lần)

```powershell
py -3.13 -m venv .venv-demo
```

```powershell
.venv-demo\Scripts\python -m pip install "gradio>=5,<6" pillow playwright
```

`playwright` chỉ cần cho `capture_screens.py` (chụp giao diện bằng Edge có sẵn trên máy). App không cần nó.

## Mở và dừng app

Mở ở nền, cửa sổ ẩn, rồi vào http://127.0.0.1:7860:

```powershell
powershell -ExecutionPolicy Bypass -File demo\start_demo.ps1
```

Dừng:

```powershell
powershell -ExecutionPolicy Bypass -File demo\stop_demo.ps1
```

Chạy trực tiếp, có cửa sổ, để xem log:

```powershell
.venv-demo\Scripts\python demo\app_replay.py --port 7860
```

Log của bản chạy nền nằm ở `demo/demo_server.log` và `demo/demo_server.log.err`.

## Ba tab

1. **So sánh phương pháp:** chọn ảnh test và query. App hiện box, số đếm, GT và sai số của B0, B2, P+F, C6.
2. **Lỗi X/Y:** hai present query trên cùng ảnh.
   - Màu: xanh dương là box chỉ có ở X, cam là chỉ có ở Y, đỏ là **box dùng chung**, tức có box ở query kia trùng IoU ≥ 0.5 (cùng định nghĩa với báo cáo).
   - Bảng bên phải là số chính thức trên 39 ảnh. Ảnh có query `uncertain` được ghi chú là không tính.
3. **Bộ lọc F:** chọn P+F hoặc C6. Mỗi cách dùng bounds và ngưỡng khóa riêng.
   - Kéo θ để xem box được giữ (nét liền) và box bị bỏ (nét đứt xám) trên **ảnh đang chọn**.
   - Nút "Khôi phục cấu hình khóa" trả θ về giá trị đã khóa.
   - App không tính lại MAE toàn test theo thanh trượt và không lưu ngưỡng mới.

## Kịch bản demo khoảng 90 giây (số thật, đã kiểm)

| Bước | Thao tác | Nói | Số |
|---|---|---|---|
| 0:00 | Mở http://127.0.0.1:7860, chỉ vào dòng in đậm | "Đây là kết quả đã lưu của lần chạy test, không chạy lại model." | — |
| 0:10 | Bấm **Ví dụ 1** (tab 1) | "Blueberries, GT 7. B0 đếm 36, B2 đếm 65 vì khoanh từng hạt mâm xôi đen; cấu hình của nhóm đếm 8." | GT 7 · B0 36 · B2 65 · P+F 8 · C6 9 |
| 0:30 | Bấm **Ví dụ 2**, sang **tab 2** (B0) | "Bowls, GT 3. Plates và bowls dùng chung gần hết box (đỏ). Đây là lỗi X/Y; sau lọc vẫn thừa." | B0 33 · B2 36 · P+F 17 · C6 20; box dùng chung B0 61/65 |
| 0:55 | Bấm **Ví dụ 3** (tab 1) | "Dogs, GT 4. Ảnh có 80 con cừu; mọi cách đều đếm cừu thành chó. CLIP trên ô cắt nhỏ cũng nhầm." | B0 92 · B2 101 · P+F 72 · C6 66 |
| 1:10 | **Tab 3**, ảnh mcac_12, query bowls, kéo θ từ 0.604 xuống 0.45, rồi bấm **Khôi phục** | "Hạ ngưỡng thì giữ nhiều box hơn, đếm thừa tăng; nâng ngưỡng thì bắt đầu bỏ cả vật đúng. Đây là đánh đổi của F." | P+F: θ 0.604 → 17; θ 0.45 → 20 |
| 1:30 | Quay về slide | — | — |

Nếu app không mở được, dùng ảnh chụp ở slide Demo (trang 31) và bảng ba ví dụ trên slide.

## File

- `replay_data.py`: nạp dữ liệu, tính số đếm và shared box, tự kiểm. Công thức sao y `apply_freeze_v2.py` và `evaluation/test_xy_overlap_analysis.py`; không import hai file đó vì chúng đã ghi hash trong audit.
- `app_replay.py`: giao diện Gradio.
- `start_demo.ps1`, `stop_demo.ps1`: mở và dừng ở nền. Script dừng chỉ tắt `app_replay.py` chạy đúng cổng được chỉ định.
- `capture_screens.py`: chụp `final/shared/figures/demo_tab{1,2,3}.png` từ app đang chạy.
