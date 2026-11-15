# Phân tích hậu kiểm trên test — khung trùng X/Y, khung trúng đúng loại, thời gian chạy (11/11/2026)

> **Hậu kiểm (post-hoc), chỉ để giải thích.** Mọi số dưới đây tính bằng CPU trên output đã lưu của lần chạy test duy nhất (`p1_test_kaggle_t4_20261111_1430`). Không chạy lại model, không chọn lại cấu hình hay ngưỡng. Bộ lọc F dùng đúng min/max và ngưỡng đã khóa trong `results/countgdpp/freeze_v2_20261111.json`. Kết quả chính vẫn là [KET_QUA_TEST_CUOI_20261111.md](KET_QUA_TEST_CUOI_20261111.md).

- Script: `evaluation/test_xy_overlap_analysis.py` (số liệu), `evaluation/make_report_figures.py` (hình).
- Output: `results/countgdpp/p1_test_kaggle_t4_20261111_1430_posthoc_20261111/` (`summary.json`, `xy_overlap_per_image.csv`); hình ở `reports/figures/`.

## 1. Đổi truy vấn X → Y, khung có đổi không?

Mỗi ảnh test có 2 lớp có mặt X, Y và 1 lớp vắng mặt Z. Với mỗi cách, lấy các khung được giữ lại, rồi tính:
- **Khung dùng chung X/Y:** tỉ lệ khung của X (và của Y) có khung trùng trong câu trả lời của query kia, với IoU ≥ 0.5.
- Tính trên 39 ảnh. Bỏ mcac_204 vì t37_1 là `uncertain` (D12).

| Cách | Khung X+Y | **Dùng chung X/Y** (IoU ≥ 0.5) [CI 95% theo ảnh] | IoU ≥ 0.8 | Trung bình theo ảnh | Ảnh có ≥ 50% khung dùng chung |
|---|---:|---:|---:|---:|---:|
| B0 | 1476 | **64%** [51, 75] | 60% | 52% | 22/39 |
| B2 | 1668 | **71%** [58, 81] | 66% | 63% | 29/39 |
| P+F (chính) | 921 | **59%** [40, 74] | 58% | 39% | 17/39 |
| B2+F | 887 | 59% [41, 73] | 58% | 40% | 17/39 |
| C6 = B0+F | 746 | **24%** [11, 37] | 23% | 18% | 8/37 |

Hai ảnh của C6 không còn khung nào ở cả X lẫn Y, nên mẫu số chỉ là 37.

**Đọc bảng:**
- **CountGD++ phần lớn trả về cùng một nhóm vật dù hỏi X hay Y**: B0 64%, B2 71%. Lượt 2 làm hiện tượng này nặng thêm. Cơ chế điểm lượt 2 = max(chữ, mẫu) chỉ giải thích một phần (biến thể T gỡ khoảng 1/5 tác hại trên dev, xem bản chi tiết mục 4.1).
- **Bộ lọc F sau lượt 2** (P+F, B2+F) chỉ giảm nhẹ tỉ lệ dùng chung (64–71% → 59%), dù số khung giảm gần một nửa. Tức là F chủ yếu cắt bớt khung, nhưng **chưa tách được X với Y**.
- **C6 (F áp ngay sau lượt 1) giảm tỉ lệ dùng chung xuống 24%**. Đây là cách duy nhất làm câu trả lời thật sự phụ thuộc vào truy vấn. Điều này giải thích vì sao C6 tốt nhất trên test.

## 2. Khung giữ lại có trúng đúng loại được hỏi không? (dùng điểm GT MUCCA)

MUCCA có điểm GT theo từng lớp, cùng hệ tọa độ pixel với khung. Mỗi khung được giữ lại của một query có mặt được xếp vào một trong ba nhóm:
- **đúng loại:** chứa ít nhất một điểm của lớp được hỏi;
- **chỉ loại khác:** chỉ chứa điểm của lớp khác có gán nhãn;
- **không trúng:** không chứa điểm nào.

Cách xếp này dễ dãi: khung to phủ cả hai loại vẫn tính là đúng.

| Cách | Khung (query có mặt) | Đúng loại | **Chỉ loại khác** | Không trúng | Khung ở query vắng mặt | trong đó nằm trên vật có nhãn |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 1481 | 60.4% | **34.6%** | 5.1% | 260 | 95.8% |
| B2 | 1671 | 56.6% | **34.6%** | 8.8% | 334 | 91.9% |
| P+F (chính) | 924 | 66.3% | **32.7%** | 1.0% | 153 | 98.0% |
| B2+F | 890 | 66.5% | 32.6% | 0.9% | 140 | 97.9% |
| C6 = B0+F | 746 | **76.9%** | **21.3%** | 1.7% | **39** | 100% |

**Đọc bảng:**
1. **Khoảng 1/3 khung CountGD++ đếm là vật loại khác** có trong ảnh. Đây là nguồn lỗi chính khi ảnh có nhiều loại vật.
2. **Lượt 2 (B2) thêm chủ yếu khung rác**: "không trúng" tăng từ 5.1% lên 8.8%, cộng thêm khung sai loại. Ví dụ blueberries bên dưới có 50 khung xám.
3. **F sau lượt 2 dọn gần hết khung rác** (còn 1%), nhưng **gần như không giảm khung sai loại** (32.7%). C6 giảm được khung sai loại xuống 21%.
4. **Với lớp vắng mặt, gần như mọi khung đếm nhầm đều là vật khác có trong ảnh** (92–100%), không phải nền. Mô hình "trỏ lại" vào vật có sẵn. C6 chỉ còn 39 khung như vậy (B0: 260).

**Hạn chế của phép đo:**
- MUCCA đánh **một điểm ở tâm** mỗi vật. Khung "không trúng" thường là **mảnh nhỏ của một vật** không chứa điểm tâm, ví dụ từng hạt của quả mâm xôi đen ở mcac_25 (ảnh này có nhãn đủ 5 loại quả). Khung loại này cũng có thể là nền, hoặc vật thuộc lớp không được gán nhãn.
- Quy tắc xếp nhóm dễ dãi (khung to phủ cả hai loại vẫn tính là đúng), nên tỉ lệ "chỉ loại khác" nghiêng về phía **thấp hơn** thực tế.
- *(Sửa 12/11: bản 11/11 ghi nhầm là dâu tây trong mcac_25 không có nhãn.)*

## 3. Ảnh minh họa (`reports/figures/`)

Màu khung: xanh = đúng loại, đỏ = chỉ loại khác, xám = không trúng điểm GT. Chấm trắng = điểm GT của lớp được hỏi.

| File | Query | Ý nghĩa |
|---|---|---|
| `fig_example_t05_1_mcac_25.png` | "blueberries", GT 7 | **Thành công.** B0 36, B2 65 (50 khung rác), P+F 8, C6 9 |
| `fig_example_t01_2_mcac_12.png` | "bowls", GT 3 | **Lỗi X/Y còn lại.** Mọi cách vẫn đếm chồng đĩa (plates) là bát. P+F 17, C6 20 |
| `fig_example_t33_1_mcac_171.png` | "dogs", GT 4 | **Thất bại.** Đàn dê bị đếm là chó ở mọi cách (66–101) |
| `fig_example_t40_1_mcac_224.png` | "people", GT 31 | **Lọc quá tay.** Không có khung sai loại, nhưng F bỏ cả người thật: P+F 13, C6 3 |

Hình khác:
- `fig_pipeline.png`: sơ đồ pipeline, đánh dấu chỗ sinh lỗi và chỗ sửa.
- `fig_results_test.png`: MAE test kèm Δ so với B0 và CI.

## 4. Thời gian chạy (Kaggle T4, ms mỗi query, bỏ query đầu vì khởi động 3.3 s)

| Cách | Lượt 1 | Lượt 2 (khi chạy) | Số query chạy lượt 2 | Trung bình cả pipeline |
|---|---:|---:|---:|---:|
| B0 | 890 | — | — | **≈ 0.89 s** |
| B2 | 890 | 880 | 85/119 | **≈ 1.52 s** |
| P (tau 0.20, M 5) | 890 | 879 | 83/119 | **≈ 1.50 s** + CLIP kiểm mẫu |

- Runner **không ghi thời gian CLIP**: cả CLIP kiểm mẫu giả của P lẫn CLIP chấm từng khung của bộ lọc F, chạy ở bước `p1_controls.py`.
- Vì vậy C6 = B0 + thời gian CLIP chấm khung, P+F = khoảng 1.5 s + CLIP.
- Nếu thầy hỏi chi phí: bỏ lượt 2 (C6) tiết kiệm khoảng 40% thời gian CountGD++. Muốn có số CLIP chính xác thì phải đo lại trên GPU; việc này không bắt buộc và chưa làm.

## 5. Dùng trong báo cáo thế nào

- Mục **Phân tích lỗi / Thảo luận**: dùng bảng 1 + bảng 2 + 4 ảnh để giải thích vì sao F giúp, vì sao C6 tốt hơn và lỗi nào còn lại (nhầm loại cùng nhóm, lọc quá tay ở ảnh đông).
- Ghi rõ đây là **phân tích hậu kiểm**, không dùng để chọn phương pháp. Kết quả chính vẫn là P+F.
- **Hướng tiếp theo gợi ý** (chỉ viết trong báo cáo, không chạy trên test này):
  - áp bộ lọc ngay sau lượt 1;
  - so sánh tương phản giữa các lớp trong ảnh (CLIP chấm khung với X so với Y);
  - ngưỡng thích ứng cho ảnh đông vật.
