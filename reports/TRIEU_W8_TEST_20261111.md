# W8 — kết quả TEST (chạy một lần, cấu hình đã khóa) — 11/11/2026

*Assistant soạn theo yêu cầu của Triệu. Phần chạy: Triệu chạy `experiments/countgdpp/kaggle_p1_test.ipynb` bằng Save Version trên Kaggle T4. Phần kiểm: assistant tính lại từ output; không chạy model, không chọn lại gì.*

## 1. Lần chạy

- **Định danh:** run `p1_test_kaggle_t4_20261111_1430`, commit `13ac51f`, Tesla T4, chạy hết khoảng 14 phút, không lỗi. Đây là **lần chạy test duy nhất**.
- **Dữ liệu:** `dev_test_v2/test` (`LOCKED`), 40 ảnh, 120 query. t37_1 là `uncertain` (D12) nên bị loại; còn **119 query được chấm** (79 có mặt, 40 vắng mặt).
- **Cấu hình:** freeze v2 sha256 `64e89ef5…`, **P(tau 0.20, M = 5) + F**, ngưỡng F 0.6042, min/max lấy từ dev. Runner chạy tau 0.20, M = 5, `--replay-b2`, nên B0, B2 và P nằm trong cùng một run. Chấm duy nhất bằng `apply_freeze_v2.py`.
- **Kiểm trong notebook:** hash test inputs/manifest và 40 ảnh khớp bản khóa; freeze khớp; Kiểm A đạt (lệch 3.28e-07).
- **Assistant kiểm độc lập:**
  - 375 file trong `for_repo_20261111_1430.zip` khớp sha256 trong `FILES_*.json`.
  - `run_config`: `complete`, T4, `uses_ground_truth=false`, `input_sha256` = hash `test/inputs.jsonl` đã khóa.
  - `result.json`: `manifest_sha256` = bản khóa, `freeze_sha256` đúng, `bundle_sha256` đúng. `tool_sha256` = blob git của `apply_freeze_v2.py`; bản trên Windows khác hash chỉ vì xuống dòng CRLF.
  - **Tính lại từ bundle bằng hàm của chính tool: số đếm và MAE của cả 5 cách khớp tuyệt đối.**

## 2. Kết quả

| Cách | MAE | RMSE | MAE có mặt | FPR_absent | TB đếm ở query vắng mặt | So với B0: ΔMAE [CI 95% theo ảnh] | tốt/kém/bằng |
|---|---:|---:|---:|---:|---:|---|---|
| B0: CountGD++ chỉ dùng chữ | 7.706 | 16.632 | 8.316 | 0.250 | 6.50 | — | |
| B2: CountGD++ chữ + 3 mẫu tự chọn | 9.605 | 19.868 | 10.241 | 0.250 | 8.35 | **+1.90** [+0.81, +3.03] | 20/46/53 |
| **Chính: P(tau 0.20, M 5) + F** | **5.824** | **12.112** | **6.835** | **0.225** | **3.83** | **−1.88** [−3.66, −0.44] | 42/24/53 |
| C6 = B0+F (báo kèm) | 4.630 | 9.626 | 6.481 | 0.100 | 0.97 | −3.08 [−6.62, −0.51] | 48/24/47 |
| B2+F (báo kèm) | 5.697 | 11.846 | 6.810 | 0.250 | 3.50 | −2.01 [−3.94, −0.40] | 42/25/52 |

Bootstrap 5000 lần theo ảnh, seed 331, do `apply_freeze_v2.py` tính.

**Độ nhạy GT (D11):** nếu thay GT MUCCA bằng số Triệu đếm ở 12 query `needs_review` (t15_1 lấy 19 hoặc 21, t23_2 lấy 19 hoặc 20), MAE mọi cách đổi **dưới 0.06**. Ví dụ cách chính: 5.824 → 5.849–5.857; C6: 4.630 → 4.672–4.681. Thứ tự các cách không đổi.

## 3. Đọc kết quả

1. **Kết quả chính dương và có ý nghĩa:** cấu hình đã khóa giảm MAE so với CountGD++ chỉ dùng chữ từ 7.71 xuống 5.82 (−24%), CI không chứa 0. So với B2 (cơ chế mẫu tự chọn của paper): từ 9.61 xuống 5.82.
2. **Chẩn đoán được xác nhận trên test:** B2 kém B0 có ý nghĩa (+1.90, CI không chứa 0). Mẫu tự chọn làm CountGD++ đếm tệ hơn khi ảnh có nhiều loại.
3. **Thành phần hiệu quả là bộ lọc, không phải P:**
   - C6 (B0 + bộ lọc) tốt nhất trên test: MAE 4.63, FPR_absent 0.10, TB đếm ở query vắng mặt 0.97.
   - B2+F ≈ P+F (5.70 so với 5.82): kiểm mẫu bằng CLIP không giúp thêm.
   - Trên dev, P+F đứng đầu (3.53) và C6 đứng thứ 7 (4.02). Đây là dấu hiệu cấu hình nhiều tham số hơn bị lạc quan khi chọn trên 60 query dev.
4. **Câu hỏi vắng mặt:** cách chính gần như không giảm tỉ lệ đếm nhầm (0.25 → 0.225; dev là 0.05), dù số vật đếm nhầm trung bình giảm (6.50 → 3.83). C6 giảm rõ: 0.10 và 0.97.
5. **Theo giao thức** (freeze v2, `companions_note`): kết quả chính **vẫn là P+F**; C6 và B2+F là đối chứng đã khai báo trước, **không** được đổi thành "phương pháp chính" sau khi xem test. Báo cáo được phép kết luận rằng bộ lọc kết hợp CLIP là thành phần mang lại cải thiện, còn P không cải thiện thêm trên test, kèm lý do có thể là chọn quá khớp trên dev nhỏ.

## 4. File trong repo (D10, không `.npz`/ảnh)

`results/countgdpp/p1_test_kaggle_t4_20261111_1430{,_controls,_controls_clip,_offline,_eval,_kaggle_meta}/`. Raw (216 `.npz`, 360 ảnh) nằm trong Output của notebook Kaggle; danh sách hash có trong `_kaggle_meta/FILES_20261111_1430.json`.
