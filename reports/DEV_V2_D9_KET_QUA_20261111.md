# Kết quả dev v2 và đề xuất chọn cấu hình theo D9 — 11/11/2026

**Nguồn:** W6 của Triệu (Kaggle T4, stamp `20261111_1203`, Kiểm A và Kiểm C 60/60 đạt, dev LOCKED). **Assistant chấm** bằng `bundle_offline_v2.py` + `select_offline_v2.py`, chạy CPU trên output đã có trong repo. Output: `results/countgdpp/p1_dev_kaggle_t4_20261111_1203_{m10,m5}_offline/`, `..._dev_selection/selection.json`.
**Cập nhật 11/11 (khuya):** Triệu đã tính T / P+T từ raw Kaggle và chạy lại D9 (`..._dev_selection_T/`); **D9 không đổi**. Assistant chạy lại độc lập trên bundle của Triệu, cho cùng lựa chọn, bảng điểm và ngưỡng; 7/7 run T có `original_replay_verified = True`. Báo cáo đầy đủ: [TRIEU_W6_DEV_D9_20261111.md](TRIEU_W6_DEV_D9_20261111.md).

## 1. Bảng dev (20 ảnh, 60 query; ngưỡng S/F chọn lại riêng từng nguồn trên dev, D2)

| Cách | M | MAE cả 60 | MAE có mặt (40) | FPR_absent (20) |
|---|---|---:|---:|---:|
| **B0** (mốc so sánh) | — | 6.28 | 8.25 | 0.20 |
| **P (tau 0.20) + F** | **5** | **3.53** | **5.05** | **0.05** |
| P (tau 0.18) + F | 10 | 3.62 | 5.03 | 0.20 |
| P (tau 0.20) + F | 10 | 3.62 | 5.08 | 0.15 |
| P (tau 0.22) + F | 10 | 3.63 | 5.22 | 0.05 |
| B2 + F | — | 3.73 | 5.15 | 0.20 |
| C6 = B0 + F | — | 4.02 | 5.80 | 0.05 |
| B0 + S | — | 4.10 | 5.92 | 0.05 |
| T / P+T (M = 5, đã có từ raw Kaggle, Triệu 11/11) | — | T 8.55 · P+T 8.25 · T+F 3.95 · P+T+F tốt nhất 3.78 | | |

B2 gốc (không lọc): 9.15 / 12.00 / 0.20 (theo bản chấm nhanh của Triệu).

**Luật D9:** chọn MAE cả tập nhỏ nhất, với điều kiện MAE có mặt ≤ B0 và FPR_absent ≤ B0. 17 cách đạt điều kiện.
- Lần chạy M = 5: ứng viên **P (tau 0.20) + F**, trạng thái `CANDIDATE`.
- Lần chạy M = 10: P (tau 0.18) + F và P (tau 0.20) + F **hòa** (`TIE_REQUIRES_DECISION`).
- Trên toàn lưới, MAE nhỏ nhất là **M = 5, tau 0.20, + F (3.53)**, và ứng viên này cũng có FPR thấp nhất (0.05).

## 2. Đọc kết quả

1. Trên dev, nhóm cách tốt nhất giảm MAE từ **6.28 xuống khoảng 3.5** và giảm MAE có mặt từ **8.25 xuống khoảng 5**. So với B0, đây là mức cải thiện lớn.
2. **Khoảng cách giữa các cách đứng đầu nhỏ** (3.53 / 3.62 / 3.73 / 4.02). Mọi ngưỡng đều được chọn ngay trên dev và có khoảng 40 cấu hình để so, nên con số dev **lạc quan**. Chỉ test mới cho biết chênh lệch giữa P+F, B2+F và C6 có thật hay không.
3. Khác với chẩn đoán trên p4_unseen_v1 (ở đó C6 tốt nhất), trên dev **P+F đứng đầu**: kiểm mẫu bằng CLIP trước lượt 2 rồi lọc Fusion. Đây đúng là nhánh P mà Trí đề xuất.

## 3. Cần Trí quyết (bước [9] khóa cấu hình)

1. **Khóa cấu hình:** đề xuất **M = 5, tau_pseudo = 0.20, lọc F** với min/max và ngưỡng đã chọn trên dev (`parameters["tau0.200+F"]` trong `m5_dev_selection/selection.json`).
2. ~~T / P+T~~: **đã tính, D9 không đổi.** Khi có bộ lọc, T không giúp thêm (P+T+F 3.78, kém P+F 3.53).
3. **Báo cáo trên test:** chạy test **một lần**, chấm cách đã khóa làm kết quả chính. Đồng thời đề xuất **báo kèm** B0, B2, C6 và B2+F với đúng ngưỡng đã khóa từ dev, để người đọc thấy bối cảnh. Các cách kèm này chỉ để tham khảo, không chọn lại.
