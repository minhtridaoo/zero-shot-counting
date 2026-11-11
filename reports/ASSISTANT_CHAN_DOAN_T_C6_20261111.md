# Chẩn đoán sớm: T và C6 trên p4_unseen_v1 — 11/11/2026

**Người chạy:** assistant, theo phép của Trí ("việc gì chạy được thì làm luôn"). Chạy bằng CPU trên file đã lưu, cộng một lần chấm CLIP cho khung B0 (không chạy CountGD++).

**ĐÂY LÀ CHẨN ĐOÁN, KHÔNG PHẢI KẾT QUẢ ĐỘC LẬP.** p4_unseen_v1 đã được dùng để phân tích lỗi (N4), và ý tưởng T ra đời từ chính các ảnh này. Kết quả thật phải chờ dev_test_v2 (luật D9, test chạy một lần). Không ngưỡng nào ở đây được đem sang dev hay test.

## 1. Biến thể T (chỉ dùng điểm chữ ở lượt 2), không có tham số mới

Script: `evaluation/p4_unseen_T_diagnostic.py`. Output: `results/countgdpp/p4_unseen_v1_T_diagnostic_20261111/`.

| Cách | MAE cả 30 | MAE có mặt (20) | Vắng mặt: đếm TB | Vắng mặt > 0 |
|---|---:|---:|---:|---:|
| B0 | 6.77 | **5.70** | 8.9 | 3/10 |
| B2 | 13.00 | 12.95 | 13.1 | 3/10 |
| **T** | 8.80 | 7.55 | 11.3 | 3/10 |
| F (freeze cũ) | **5.53** | 7.80 | **1.0** | 3/10 |

- **T so với B2: −4.20 MAE, CI 95% [−7.30, −1.63], tốt hơn 12 / kém 0 / bằng 18 query.** T sửa được một phần thiệt hại do lượt 2 gây ra, xác nhận cơ chế "điểm mẫu ảnh lấn át điểm chữ".
- **T so với B0: +2.03** (CI [−0.37, +5.33]): T **chưa** bằng B0.
- T không giúp query vắng mặt: hỏi "sheep" vẫn đếm 31 con chó, vì bản thân chữ "sheep" đã chấm chó cao.

## 2. Chọn lại ngưỡng riêng từng nguồn (D2), kiểm chéo giữ 1 ảnh (LOIO)

Script: `evaluation/p4_unseen_loio_diagnostic.py`. Output: `results/countgdpp/p4_unseen_v1_loio_diagnostic_20261111/`. Điểm CLIP của khung B0: `results/countgdpp/p4_unseen_v1_B0_clip_20261111/` (458 khung, cùng CLIP đã khóa). Mỗi ảnh: chọn ngưỡng trên 9 ảnh còn lại theo đúng luật 21/10, rồi áp lên ảnh giữ lại.

| Cách | MAE cả 30 | MAE có mặt | Vắng mặt: đếm TB | FPR_absent | Theo D9 |
|---|---:|---:|---:|---:|---|
| B0 | 6.77 | 5.70 | 8.90 | 0.30 | mốc so sánh |
| **B0+S** | **3.70** | **4.85** | 1.40 | 0.20 | **thắng B0**, Δ −3.07, CI [−7.37, −0.20] |
| **B0+F (C6)** | 3.73 | 5.10 | **1.00** | **0.10** | **thắng B0**, Δ −3.03, CI [−7.37, +0.17] |
| B2+S / B2+F | 6.23 / 5.70 | 6.30 / 7.35 | 6.1 / 2.4 | 0.30 | không đạt (MAE có mặt kém B0) |
| T / T+S / T+F | 8.80 / 6.80 / 5.83 | 7.55 / 7.55 / 7.85 | | | không đạt |

**Ngưỡng B0+S chọn ở 10 lượt: 0,34 (9 lượt) và 0,385 (1 lượt)**, so với mặc định CountGD++ là 0,23. Vậy B0+S thực chất là **nâng ngưỡng tự tin của CountGD++ chạy 1 lượt**. B0+F cộng thêm CLIP xác minh, nên chặn query vắng mặt tốt nhất (1/10).

## 3. Đọc kết quả (sơ bộ, chờ dev_test_v2)

1. Mọi cách đi qua **lượt 2 tự chọn mẫu** (B2, T và các bản có lọc) đều **không thắng B0** ở query có mặt. Lượt 2 là nguồn gây hại chính.
2. Cách có triển vọng nhất là **giữ 1 lượt và hiệu chỉnh việc giữ khung** (nâng ngưỡng, hoặc dùng CLIP xác minh). C6 đã nằm sẵn trong danh sách D8 với ngưỡng chọn lại riêng từng nguồn (D2), nên **không cần đổi kế hoạch W6**: lần chạy dev sẽ kiểm đúng điều này.
3. Nhánh P (lọc mẫu bằng CLIP rồi mới chạy lượt 2) vẫn chưa đo được, vì raw P1 không có trên máy này. Nếu P không vượt được C6 trên dev thì luật D9 sẽ chọn C6.
4. Cách viết báo cáo phải trung thực. B0+S gần với "tinh chỉnh ngưỡng", một baseline đơn giản; đóng góp mới nằm ở chỗ khác:
   - chỉ ra lượt 2 (pseudo-exemplar) gây hại trong bài toán X/Y;
   - chỉ ra cơ chế: điểm mẫu ảnh lấn át điểm chữ;
   - cho thấy hiệu chỉnh 1 lượt cùng CLIP xác minh giảm mạnh lỗi vắng mặt mà không mất vật đúng.

**Giới hạn:** 10 ảnh, các query trong một ảnh không độc lập, tập đã xem trước. Kiểm chéo theo ảnh giảm được việc khớp quá mức nhưng không thay được tập test mới.
