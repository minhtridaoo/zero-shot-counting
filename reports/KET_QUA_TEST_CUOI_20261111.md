# Kết quả cuối trên test — kiểm độc lập của assistant (11/11/2026)

**Nguồn:** W8 của Triệu ([báo cáo](TRIEU_W8_TEST_20261111.md)), run `p1_test_kaggle_t4_20261111_1430`, Kaggle T4, chạy **một lần**, chấm bằng `apply_freeze_v2.py` với freeze v2 (`results/countgdpp/freeze_v2_20261111.json`).

## 1. Assistant đã kiểm (chỉ đọc + tính lại bằng CPU)

- Freeze trong `result.json` khớp sha256 file freeze. Manifest test = bản khóa trong `selection_meta` = file trên đĩa.
- `run_config`: `complete`, Tesla T4, `input_sha256` = `test/inputs.jsonl` đã khóa, tau 0.20, M 5, `uses_ground_truth=false`.
- **Tính lại từ bundle** bằng hàm của `apply_freeze_v2.py`: số đếm từng query, MAE/RMSE/FPR và bootstrap của cả 5 cách **khớp tuyệt đối** `result.json`. t37_1 bị loại đúng (D12).
- **Test chỉ được chấm một lần:**
  - không có thư mục chấm test nào khác;
  - notebook `kaggle_p1_test.ipynb` không chạy `evaluate_research.py` (chỉ nhắc tới trong dòng cấm);
  - không có lần chọn lại ngưỡng.

## 2. Bảng kết quả cuối (119 query: 79 có mặt, 40 vắng mặt)

| Cách | MAE | MAE có mặt | FPR_absent | So với B0 [CI 95% theo ảnh] |
|---|---:|---:|---:|---|
| B0 | 7.71 | 8.32 | 0.250 | — |
| B2 | 9.61 | 10.24 | 0.250 | +1.90 [+0.81, +3.03] |
| **P(tau 0.20, M 5)+F (chính, đã khóa)** | **5.82** | **6.84** | **0.225** | **−1.88 [−3.66, −0.44]** |
| C6 = B0+F (báo kèm, khai báo trước) | 4.63 | 6.48 | 0.100 | −3.08 [−6.62, −0.51] |
| B2+F (báo kèm, khai báo trước) | 5.70 | 6.81 | 0.250 | −2.01 [−3.94, −0.40] |

Assistant tính thêm các so sánh cặp:
- C6 so với cách chính: −1.19, CI [−3.32, +0.24] → **chưa đủ chắc** là C6 tốt hơn.
- B2+F so với cách chính: −0.13, CI [−0.41, +0.18] → **P không đóng góp thêm**.

Độ nhạy D11 (số người đếm thay GT): MAE đổi dưới 0.06, thứ tự không đổi (Triệu tính).

## 3. Kết luận dùng cho báo cáo

1. **Có cải tiến được kiểm chứng trên tập test chưa từng xem:** cấu hình đã khóa giảm MAE so với CountGD++ một lượt từ 7.71 xuống 5.82 (−24%), CI không chứa 0. So với cơ chế hai lượt gốc (B2), mức giảm là 9.61 → 5.82.
2. **Lượt 2 tự chọn mẫu của CountGD++ gây hại khi ảnh có nhiều loại** (B2 kém B0, CI không chứa 0). Điều này xác nhận chẩn đoán từ pilot và N4.
3. **Thành phần tạo ra cải thiện là bộ lọc kết hợp điểm CountGD++ và CLIP (F)**, không phải bước kiểm mẫu P:
   - B2+F ≈ P+F;
   - B0+F (C6) cho số tốt nhất và giảm báo nhầm vật vắng mặt nhiều nhất (0.25 → 0.10). Tuy vậy, chênh lệch giữa C6 và cách chính chưa có ý nghĩa thống kê.
4. **Bài học về chọn mô hình:** trên dev, P+F đứng đầu (3.53) còn C6 xếp thứ 7 (4.02); trên test, thứ tự đảo lại. *(Làm rõ 15/11: thứ 7/15 khi gom theo họ phương pháp, tức thứ 25/90 cấu hình riêng lẻ. Trên dev, C6 − P+F = +0.48, CI [−0.62, +1.63], tức chưa phân biệt được ngay từ dev. Xem `reports/BAO_CAO_CHI_TIET_DO_AN_20261112.md` mục 7.6.)* Đây là dấu hiệu cấu hình nhiều tham số (tau, M, ngưỡng) bị lạc quan khi chọn trên 60 query. Nên ghi trong phần hạn chế, kèm gợi ý dùng dev lớn hơn hoặc kiểm chéo.
5. **Giữ đúng giao thức:** kết quả chính vẫn là P+F như đã khóa. C6 và B2+F là đối chứng khai báo trước, nên được phép thảo luận như phát hiện, nhưng không được đổi thành "phương pháp chính" sau khi xem test.
