# Khai báo trước — khảo sát bổ sung FSC-147 (300 ảnh)

**Ngày soạn:** 20/11/2026. **Người soạn:** assistant (Claude), theo yêu cầu của Trí. Ý tưởng ban đầu từ bản so sánh nhóm khác của Triệu (19/11, đề xuất A).
**Người chạy:** Trí (phần FSC-147). Phần FSCD-147 là của Triệu, tách riêng (mục 9).
**Trạng thái:** CHỜ TRÍ DUYỆT. Chưa chạy gì trên GPU. Danh sách 300 ảnh đã cố định trong repo trước khi chạy.

---

## 1. Câu hỏi và phạm vi

**Câu hỏi:** bỏ lượt 2 có làm giảm chất lượng đếm trên ảnh thông thường, tức ảnh chỉ có một loại vật, không?

- Đây là **thử nghiệm bổ sung**. Nó không thay kết quả chính trên MUCCA và không dùng để chọn lại hay chỉnh cấu hình đã khóa.
- Ưu tiên chính vẫn là báo cáo cuối và demo tĩnh. Phần này không được làm chậm hai việc đó.
- MUCCA và FSC-147 **báo riêng**, không so trực tiếp điểm số giữa hai bộ.

## 2. Dữ liệu

| Mục | Giá trị |
|---|---|
| Split | FSCD-147 test, cũng là FSC-147 test: 1.190 ảnh. Các lớp test không có trong tập train của FSC-147 |
| Nhãn | `CountGDPlusPlus/data/fscd147/countgd_test_fscd147.json`, sha256 `e301c693…`, khớp lần kiểm benchmark 20/10 |
| Đã kiểm trên toàn bộ 1.190 ảnh | Mỗi ảnh có đúng 3 khung mẫu, đúng 1 lớp, GT > 0. GT từ 8 đến 3.701 (trung vị 36,5) |
| GT | Số chú thích điểm (`area == 4`). Bỏ 3 khung mẫu, giống loader CountGD++ |
| Câu truy vấn | Tên lớp FSC-147 nguyên văn, số ít (ví dụ "apple"), như benchmark gốc. Mọi câu đều là câu **có mặt** |
| Mẫu | `random.Random(331).sample(sorted(id ảnh), 300)`. Không chọn theo số vật, theo lớp hay theo kết quả |
| Kết quả lấy mẫu | 300 ảnh, 27/31 lớp; GT từ 8 đến 621 (trung vị 36); 163 ảnh ≤ 40, 137 ảnh > 40 |
| File cố định | `sample_300/inputs.jsonl` (sha256 `c1cfb321…`, không chứa GT), `sample_300/manifest.csv` (`30ea7987…`), `sample_300/sample_meta.json` |
| Ảnh | Chỉ có trên Kaggle (FSC147_384_V2, cùng nguồn với benchmark 15/10). Notebook ghi sha256 của từng ảnh trong 300 ảnh lúc chạy |

## 3. Cấu hình so sánh

Cả 5 cách lấy từ **một lần chạy** `run_b2_verified_pseudo.py` (tau 0.20, M = 5, `--replay-b2`), nên dùng chung ảnh, câu truy vấn, tiền xử lý và đúng một lượt 1.
Tiền xử lý: ảnh resize cạnh ngắn 800 (tối đa 1333). **`crop=False`** (không cắt ảnh thích ứng), **`synthetic=False`** (không mẫu GPT-5), seed 42, ngưỡng hộp 0.23.

| Cách | Gồm gì | Vai trò |
|---|---|---|
| **B0** | Chỉ lượt 1 (chữ), không lọc | Bỏ lượt 2 |
| **B2** | Lượt 1 → 3 mẫu tự chọn → lượt 2, không lọc | Cách CountGD++ thường dùng (nhưng không cắt ảnh, không mẫu GPT-5) |
| **P+F** | Lượt 1 → mẫu được CLIP kiểm (tau 0.20, M 5) → lượt 2 → bộ lọc F | Cấu hình đã khóa (freeze v2) |
| C6 = B0+F | B0 + bộ lọc F | Chỉ báo kèm |
| B2+F | B2 + bộ lọc F | Chỉ báo kèm |

**Cặp sạch để quy kết cho lượt 2: B0 với B2.** Hai cách này chung lượt 1, chung run, đều không lọc; khác nhau duy nhất là có chạy lượt 2 hay không.
Cặp C6 với B2+F **không sạch**, vì freeze v2 đặt cho mỗi nguồn một bộ lọc F riêng (C6 ngưỡng 0.427, B2+F ngưỡng 0.623, bounds khác nhau). Cặp này chỉ báo mô tả.

F dùng nguyên bounds và ngưỡng trong `results/countgdpp/freeze_v2_20261111.json` (sha256 `64e89ef5…`), qua hàm `counts_for` của `apply_freeze_v2.py` (chỉ import, không sửa).

## 4. So sánh, chỉ số và cách đọc

Ký hiệu: Δ = MAE(A) − MAE(B). CI 95% bằng bootstrap theo ảnh, 5.000 lần, seed 331 (mỗi ảnh có một câu).

| Vai trò | A − B | Ý nghĩa của Δ > 0 |
|---|---|---|
| **Chính** | **B0 − B2** | Bỏ lượt 2 làm sai số tăng |
| Phụ | P+F − B2 | Cấu hình đã khóa kém hơn CountGD++ hai lượt |
| Phụ | P+F − B0 | Cấu hình đã khóa kém hơn một lượt |
| Báo kèm (không sạch) | C6 − B2+F | Chỉ mô tả |

- **Chỉ số:** MAE, RMSE, Bias (trung bình dự đoán − GT), tổng đếm thừa, tổng đếm thiếu, số câu dự đoán 0. Tính trên toàn mẫu và theo hai nhóm khai báo trước: GT ≤ 40 (gần khoảng 3–40 vật của MUCCA) và GT > 40. Bootstrap của cặp chính tính cho cả từng nhóm.
- **Cách đọc:** CI nằm hoàn toàn trên 0 nghĩa là A kém hơn B. CI nằm hoàn toàn dưới 0 nghĩa là A tốt hơn B. CI chứa 0 nghĩa là không thấy khác biệt.
- Không có câu vắng mặt nên không có FPR. Script chấm mới không chia cho số câu vắng mặt.

## 5. Giới hạn diễn giải (ghi nguyên vào báo cáo)

- 300 ảnh là **khảo sát trên mẫu**, không đại diện cho kết quả trên toàn bộ FSC-147.
- Nếu B0 kém hơn B2, chỉ được viết "trên mẫu này, bỏ lượt 2 làm sai số tăng ở ảnh một loại". **Chưa đủ để kết luận** phương pháp chỉ phù hợp ảnh nhiều loại.
- Vì `crop=False` và `synthetic=False`, số này **không so được** với benchmark 8,34 của nhóm hay với 8,39 / 10,29 của bài báo. Không dùng 10,29 làm mốc, vì chưa xác minh điều kiện chạy tương đương.
- F và tau được chọn trên MUCCA (ảnh 3–40 vật mỗi loại). Ở ảnh dày, F có thể cắt quá tay. Đây là một phần của câu hỏi, không phải lỗi cần sửa.
- Mọi cách cùng bị đếm thiếu ở ảnh rất đông, vì không cắt ảnh.

## 6. Xử lý lỗi

- Runner dừng ngay ở câu lỗi đầu tiên. Khi có **lỗi kỹ thuật** (crash, thiếu file, hết phiên Kaggle), chạy lại **đúng notebook này** với run-id mới và ghi vào WORKLOG.
- Không chạy lại vì kết quả xấu. Không bỏ bớt ảnh khỏi mẫu.
- Nếu lỗi kỹ thuật lặp lại sau 2 lần, hoặc không tải được ảnh / checkpoint / GPU T4: báo sớm và bỏ phần này (xem mục 8).
- Thiếu ảnh trong thư mục tải về thì notebook dừng ở Ô 6. Không thay ảnh khác.

## 7. Thời gian

Thời gian chạy trên FSC-147 **chưa đo**. Mốc tham khảo duy nhất là lần chạy test MUCCA trên T4 (ảnh và số khung khác FSC-147): lượt 1 trung bình 0,91 s/câu, mỗi lượt 2 khoảng 0,88 s/câu. Lượt 2 của B2 và P chạy một lần nếu hai cách chọn cùng bộ mẫu.
Notebook in thời gian thật của runner và của phần chấm CLIP (`timing.json`). Cộng thêm thời gian cài môi trường như W8.

## 8. Lịch và tiêu chí dừng

| Ngày | Việc |
|---|---|
| 20–21/11 | Kiểm dữ liệu (đã xong), chốt thiết kế, chuẩn bị script (đã xong), **Trí duyệt** |
| 22–23/11 | Sau khi Trí đồng ý: push commit đã ghim lên GitHub (mục 10), **Trí chạy Kaggle**, assistant kiểm và tổng hợp |
| **24/11** | **Đóng phần này.** Chưa xong thì ghi vào phần hạn chế ("chưa kiểm trên ảnh một loại"), không để ảnh hưởng báo cáo |

## 9. Phân công

- **Trí — FSC-147 (khảo sát này):** duyệt bản này, rồi chạy notebook [kaggle_fsc147_survey.ipynb](kaggle_fsc147_survey.ipynb) trên Kaggle.
- **Triệu — FSCD-147:** phần riêng, không dùng notebook này. Chờ Triệu xác nhận phần của mình là **tổng hợp kết quả đã có** hay **chạy mới**:
  - Tổng hợp (assistant đề xuất): dùng benchmark FSCD-147 đã kiểm (MAE 8,34, [BENCHMARK_FSCD147.md](../../reports/BENCHMARK_FSCD147.md)), tự mở Bảng 1 bài báo CountGD++ để kiểm số 16,55 / 10,29 / 8,39. Không cần GPU.
  - Chạy mới: dùng notebook benchmark có sẵn [COUNTGDPP_FSCD147_KAGGLE.ipynb](../benchmark_fscd147/COUNTGDPP_FSCD147_KAGGLE.ipynb). Cần Trí duyệt riêng (AGENTS.md quy tắc 4).
  - **Tránh trùng:** FSC-147 test và FSCD-147 test là **cùng 1.190 ảnh**. Phần của Triệu không chạy lại cặp B0/B2/P+F trên các ảnh này, vì khảo sát của Trí đã làm.
- **Assistant:** đã viết script; sẽ kiểm output và soạn đoạn nhận xét.

## 10. Lệnh chạy (từ thư mục gốc CS331; trên Kaggle là các Ô 7–8 của notebook)

```bash
# 0. Tạo mẫu: ĐÃ CHẠY 20/11, không chạy lại (script từ chối ghi đè)
python experiments/fsc147_survey/make_fsc147_sample.py --out experiments/fsc147_survey/sample_300

# 1. Một lần chạy: B0 (lượt 1), B2, P(tau 0.20, M 5)
python experiments/countgdpp/run_b2_verified_pseudo.py --inputs experiments/fsc147_survey/sample_300/inputs.jsonl \
    --run-id RUN --tau-pseudo 0.20 --m 5 --replay-b2

# 2. Điểm CLIP từng khung, rồi gom bundle
python experiments/countgdpp/p1_controls.py --run results/countgdpp/RUN --run-id RUN_controls
python experiments/countgdpp/bundle_offline_v2.py --controls results/countgdpp/RUN_controls --out results/countgdpp/RUN_offline/bundle.json

# 3. Chấm duy nhất (chỉ câu có mặt, F từ freeze v2)
python experiments/fsc147_survey/score_fsc147_present_only.py --run results/countgdpp/RUN \
    --bundle results/countgdpp/RUN_offline/bundle.json --out results/countgdpp/RUN_eval
```

`RUN = fsc147_survey_kaggle_t4_<stamp>`. Notebook: [kaggle_fsc147_survey.ipynb](kaggle_fsc147_survey.ipynb). Môi trường (Ô 3) và Kiểm A (Ô 5) chép nguyên từ notebook test W8.

**Ghim commit:** notebook checkout đúng một commit cố định (`REPO_REF` ở Ô 1) và dừng nếu HEAD khác commit đó. Commit này phải có trên GitHub trước khi chạy. Khi đưa vào `main`, dùng merge hoặc fast-forward, không squash hay rebase, để SHA không đổi.

## 11. Đầu ra

- Trước khi chạy (đã có): bản này, `sample_300/`, `make_fsc147_sample.py`, `score_fsc147_present_only.py`, notebook.
- Sau khi chạy: `results/countgdpp/RUN*` (file nhỏ json/jsonl/csv theo D10; raw `.npz` để trên Kaggle), gồm `RUN_eval/result.json` và `per_query.csv` (dự đoán từng câu của 5 cách). Thêm bảng kết quả và đoạn nhận xét cho mục "Kiểm khả năng tổng quát" của báo cáo.
- Kết quả tốt hay xấu đều giữ nguyên.

## 12. Chưa kiểm được

- Script chấm mới **chưa chạy thử**: mới qua kiểm cú pháp. Có thể chạy thử trên dữ liệu giả trước khi chạy Kaggle, nếu Trí cho phép.
- Chưa tải ảnh FSC-147 về máy, nên hash ảnh chỉ có lúc chạy.
- `p1_controls.py` và `p4_clip_score.py` chưa từng chạy trên ảnh FSC-147. Đã đọc code: không có ràng buộc riêng cho MUCCA.
