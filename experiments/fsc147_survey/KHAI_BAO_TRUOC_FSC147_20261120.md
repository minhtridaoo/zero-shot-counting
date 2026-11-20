# Khai báo trước — khảo sát bổ sung FSC-147, 300 ảnh

**Soạn:** assistant (Claude) theo yêu cầu của Trí, 20/11/2026; rà soát và thống nhất lại cùng ngày. Ý tưởng gốc: đề xuất A trong bản so sánh nhóm khác của Triệu (19/11).
**Phân công:** **Trí chạy** notebook Kaggle. **Triệu kiểm** thiết kế, danh sách mẫu và kết quả theo [HUONG_DAN_KIEM_TRIEU.md](HUONG_DAN_KIEM_TRIEU.md), đồng thời tiếp tục phần báo cáo được giao.
**Trạng thái:** Trí đồng ý thiết kế và phân công (20/11). **Chưa chạy model, evaluator hay self-test.** Chưa sẵn sàng chạy: còn chờ self-test và push. Mẫu 300 ảnh đã cố định từ trước khi chạy.

Chỉ có **một** khảo sát, trên 300 ảnh. Không tách thành hai lượt FSC-147 và FSCD-147, và không chạy lại benchmark FSCD-147 cũ (8,34 / 24,64). Báo cáo cuối viết song song ngay từ bây giờ. Khảo sát đóng ngày 24/11; không kịp thì ghi vào phần hạn chế.

---

## 1. Câu hỏi

**Câu hỏi chính:** trên mẫu này, giữ lượt 2 hay bỏ lượt 2 cho kết quả đếm tốt hơn?
**Câu hỏi phụ:** cấu hình cải tiến đã khóa (P+F) đứng ở đâu trên dữ liệu bổ sung này?

Đây là kiểm tra bổ sung. Nó không thay kết quả chính trên MUCCA, không chọn lại hay chỉnh tham số. Kết quả báo riêng với MUCCA, không so trực tiếp điểm số giữa hai bộ.

## 2. Dữ liệu và cách gọi

**Cách gọi thống nhất trong mọi tài liệu khảo sát: "FSC-147 test".**

- **Quan hệ FSC-147 / FSCD-147:** FSCD-147 là FSC-147 có thêm khung hộp cho vật. Hai bộ dùng chung ảnh và chung chia split. Tệp nhãn khảo sát đọc là bản FSCD-147 đi kèm CountGD++, nhưng chỉ dùng phần **điểm** để đếm (giống nhãn FSC-147) và tên lớp. Khung hộp không được dùng.
- Tên tệp, tên thư mục và tên cũ có chữ "FSCD-147" (ví dụ `countgd_test_fscd147.json`, docstring của `make_fsc147_sample.py`, hay benchmark 15/10) là tên gốc, giữ nguyên để không phá hash.

| Mục | Đã xác nhận |
|---|---|
| Nguồn nhãn | `CountGDPlusPlus/data/fscd147/countgd_test_fscd147.json`, có trong repo từ commit đầu (19/10), sha256 `e301c693…`. Khớp hash trong metadata lần benchmark 15/10 ([BENCHMARK_FSCD147.md](../../reports/BENCHMARK_FSCD147.md)) |
| Nguồn ảnh | Link "Download FSCD-147" trong README CountGD++ (Google Drive `1m_v_hBwXH1NzcuUj_qa-ziKn-LYfUWA6`), thư mục `FSC147_384_V2/images_384_VarV2`. Ảnh có chiều cao 384. Chưa tải về máy; notebook ghi sha256 của 300 ảnh lúc chạy |
| Split | Test: 1.190 ảnh, khớp số ảnh test của FSC-147. Các lớp test không có trong train của FSC-147 |
| Annotation đếm | Mỗi ảnh có các điểm (`area == 4`) và đúng 3 khung mẫu (`area != 4`). GT = số điểm, bỏ 3 khung mẫu, giống loader CountGD++ (`datasets/coco.py`). Lần kiểm 20/10 xác nhận GT trong log CountGD++ khớp số điểm này ở cả 1.190 ảnh |
| Tên lớp | Trường `categories` của tệp nhãn (31 lớp, mỗi ảnh đúng 1 lớp). Câu truy vấn là tên lớp nguyên văn, số ít (ví dụ "apple"), như benchmark gốc |
| Chưa đối chiếu | Chưa so với tệp gốc `annotation_FSC147_384.json` / `ImageClasses_FSC147.txt`, vì máy này không có hai tệp đó |

## 3. Mẫu cố định

| Mục | Giá trị |
|---|---|
| Cách lấy | `random.Random(331).sample(sorted(id ảnh), 300)`. Không chọn theo số vật, theo lớp hay theo kết quả |
| Đã kiểm 20/11 | Chạy lại phép lấy mẫu ra **đúng 300 id** như đã lưu; GT, tên file, tên lớp khớp tệp nhãn; `inputs.jsonl` không chứa GT. **Giữ nguyên, không bốc lại** |
| Kết quả | 300 ảnh, 27/31 lớp, GT từ 8 đến 621 (trung vị 36). Nhóm ≤ 40 vật: 163 ảnh; > 40 vật: 137 ảnh |
| `sample_300/inputs.jsonl` | sha256 `c1cfb321119ae2c39c0ec229a20b2c5802a477b55bee2279a61ae2b42422211e` (300 dòng, xuống dòng CRLF, giữ nguyên byte bằng `.gitattributes`) |
| `sample_300/manifest.csv` | sha256 `30ea79874998dc32f6534842c72f102bf44d2e3b9b5a4bc65905284981072d33` (GT để chấm) |
| `sample_300/sample_meta.json` | sha256 `fc38c12c3a6cb37e64472724699545490b74e090b2d73a6a73b5dd677f1892d2` (seed, hash nguồn, hash hai tệp trên) |

## 4. Năm cách và vì sao so được

Cả năm cách lấy từ **một lần chạy** `run_b2_verified_pseudo.py --tau-pseudo 0.20 --m 5 --replay-b2`. Vì vậy chúng dùng chung ảnh, chung câu truy vấn và chung đúng một kết quả lượt 1.

Tiền xử lý giữ nguyên runner:
- ảnh resize cạnh ngắn 800 (tối đa 1333);
- **`crop=False`**, **`synthetic=False`**;
- seed 42, ngưỡng khung 0.23.

| Cách | Gồm gì |
|---|---|
| **B0** | Kết quả lượt 1 (`stage1_*`), không lọc |
| **B2** | Lượt 1 → tối đa 3 khung điểm > 0.23 làm mẫu (`select_pseudo`) → lượt 2, không lọc |
| **P+F** | Lượt 1 → mẫu được CLIP kiểm (tau 0.20, M 5) → lượt 2 → bộ lọc F. Cấu hình chính của freeze v2 |
| **B2+F** | B2 + bộ lọc F (bounds và ngưỡng riêng trong freeze) |
| **C6** | B0 + bộ lọc F (bounds và ngưỡng riêng trong freeze) |

**Đã kiểm trong code** rằng B0 và B2 chỉ khác nhau ở việc có chạy lượt 2:
- Cùng ảnh, cùng câu truy vấn, cùng model và ngưỡng 0.23.
- Trước lượt 2, trạng thái ngẫu nhiên được trả về đúng lúc vừa xong lượt 1.
- Mẫu của lượt 2 lấy từ chính lượt 1. Nếu lượt 1 không có khung nào > 0.23 thì không chạy lượt 2, và B2 = B0.

F dùng nguyên bounds và ngưỡng trong `results/countgdpp/freeze_v2_20261111.json` (sha256 `64e89ef5…`), qua hàm `counts_for` của `apply_freeze_v2.py` (chỉ import, không sửa). Điểm CLIP của từng khung tính bằng `p1_controls.py` như lần test MUCCA. Không chỉnh tham số nào theo kết quả.

## 5. So sánh khai báo trước

Ký hiệu: Δ = MAE(A) − MAE(B). Δ > 0 nghĩa là A sai nhiều hơn B.

| Vai trò | A − B | Dùng để |
|---|---|---|
| **Chính** | **B0 − B2** | Trả lời câu hỏi chính. Δ > 0: bỏ lượt 2 làm sai số tăng; Δ < 0: bỏ lượt 2 làm sai số giảm |
| Phụ | P+F − B2 | Cấu hình cải tiến so với CountGD++ hai lượt |
| Phụ | P+F − B0 | Cấu hình cải tiến so với một lượt |
| Chỉ mô tả | C6 − B2+F | Hai cách dùng ngưỡng F khác nhau, nên **không quy kết chênh lệch cho lượt 2** |

## 6. Chỉ số và thống kê

- **Chỉ số:** MAE, RMSE, độ lệch có dấu (Bias = trung bình dự đoán − GT), tổng đếm thừa, tổng đếm thiếu, số truy vấn trả 0.
- **Phạm vi báo:** toàn mẫu, nhóm ≤ 40 vật và nhóm > 40 vật (khai báo trước; 40 gần cận trên 3–40 vật của MUCCA).
- **CI 95% cho Δ:** bootstrap **ghép cặp theo ảnh**, 5.000 lần, seed 331. Mỗi lần lấy lại cùng một bộ ảnh (có hoàn lại) cho cả A và B. Mỗi ảnh có đúng một câu. Cặp chính có thêm CI riêng cho từng nhóm.
- Không có câu vắng mặt, nên không có FPR.

## 7. Quy tắc xử lý lỗi (không bỏ ảnh âm thầm, không thay ảnh)

- Notebook dừng nếu thiếu dù chỉ 1 trong 300 ảnh. Không thay bằng ảnh khác.
- Runner dừng ở câu lỗi đầu tiên và ghi lỗi.
- **Lỗi kỹ thuật** (crash môi trường, hết phiên Kaggle, tải thiếu): chạy lại **đúng notebook này, toàn bộ 300 ảnh**, với run-id mới, và ghi vào WORKLOG. Tối đa 2 lần chạy lại.
- **Lỗi lặp lại ở cùng một ảnh:** chạy lại không giúp được. Hai khả năng thấy được khi đọc code: `select_pseudo` báo khung mẫu suy biến, hoặc không tìm thấy token của câu truy vấn. **Đây là rủi ro đọc từ code, chưa xảy ra trên 300 ảnh này.** **Không loại ảnh đó để chạy tiếp.** Ghi khảo sát là **chưa hoàn tất**, kèm id ảnh và thông báo lỗi, rồi đưa vào phần hạn chế.
- Script chấm **từ chối** (không chấm) khi:
  - bundle không phủ đủ đúng 300 câu, hoặc có `query_id` / `image_id` trùng;
  - hash của mẫu đổi;
  - run khác tau/M/`--replay-b2` của freeze;
  - `run_config` có `crop`, `synthetic` hoặc `uses_ground_truth` khác false;
  - thư mục kết quả đã có.
- Không chạy lại vì kết quả xấu.

## 8. Giới hạn diễn giải (ghi nguyên vào báo cáo)

- Kết quả chỉ áp dụng cho **mẫu 300 ảnh và điều kiện này** (không cắt ảnh, không mẫu GPT-5, câu truy vấn là tên lớp số ít). Đây **không phải benchmark đầy đủ** của FSC-147.
- Mọi câu đều có mặt, nên khảo sát **không nói gì về lớp vắng mặt**.
- **CI chứa 0 nghĩa là chưa thấy khác biệt rõ.** Không có nghĩa là "không gây hại" hay "hai cách như nhau".
- Nếu B0 kém hơn B2, chỉ viết "trên mẫu này, bỏ lượt 2 làm sai số tăng". Chưa đủ để kết luận phương pháp chỉ hợp với ảnh nhiều loại.
- **Không so trực tiếp** với 10,29 / 8,39 của bài báo hay 8,34 của lần benchmark 15/10. Các số đó chạy ở điều kiện khác (có cắt ảnh, có mẫu GPT-5, trên đủ 1.190 ảnh).
- F và tau được chọn trên MUCCA (3–40 vật mỗi loại). Ảnh dày có thể bị lọc quá tay; ảnh rất đông bị mọi cách đếm thiếu vì không cắt ảnh.

## 9. Thay đổi so với đề xuất gốc của Triệu (19/11, đề xuất A)

| Mục | Đề xuất gốc | Bản này | Lý do |
|---|---|---|---|
| Số ảnh | 1.190 ảnh | 300 ảnh lấy ngẫu nhiên, seed 331 | Trí chốt khảo sát thu nhỏ, đóng trước 24/11 |
| So sánh chính | P+F − B2 | **B0 − B2** | Chỉ cặp này khác duy nhất ở lượt 2. P+F − B2 chuyển thành so sánh phụ |
| So sánh phụ | C6 − B2, P+F − B0 | P+F − B2, P+F − B0; C6 − B2+F chỉ mô tả | C6 và B2+F dùng ngưỡng F khác nhau |
| Người chạy | Triệu | **Trí chạy**, Triệu kiểm | Trí phân công 20/11 |
| Tách FSC-147 / FSCD-147 | — | Một khảo sát duy nhất, gọi là "FSC-147 test" | Cùng ảnh, cùng split |
| Benchmark cũ | — | Không chạy lại | Không cần lấy lại 8,34 / 24,64 |
| Chỉ số | MAE, RMSE, thừa/thiếu | Thêm Bias và số câu trả 0 | Thấy rõ chiều lệch |
| Bootstrap, seed, nhóm ≤ 40 / > 40, cách đọc CI | | Giữ nguyên; ghi rõ "ghép cặp theo ảnh"; CI chứa 0 không chứng minh không hại | |

## 10. Lịch và tiêu chí dừng

| Ngày | Việc |
|---|---|
| 20–21/11 | Kiểm dữ liệu (xong), Trí duyệt thiết kế (xong 20/11). Sau khi Trí cho phép: chạy self-test dữ liệu giả; lỗi thì sửa script, kiểm lại, ghim commit mới |
| 21/11 | Push nhánh chứa commit đã ghim lên GitHub, kiểm notebook lấy được đúng commit. Triệu kiểm phần A |
| 22–23/11 | Trí chạy Kaggle **một lần**. Assistant và Triệu kiểm |
| **24/11** | **Đóng.** Chưa xong hoặc chưa hoàn tất thì ghi vào hạn chế, không để ảnh hưởng báo cáo |

Thời gian chạy trên FSC-147 **chưa đo**. Mốc tham khảo duy nhất là lần test MUCCA trên T4 (ảnh khác): lượt 1 khoảng 0,91 s/câu, mỗi lượt 2 khoảng 0,88 s/câu. Notebook ghi thời gian thật vào `timing.json`. Nếu thiếu dữ liệu, GPU hoặc checkpoint thì báo sớm để thu gọn hoặc bỏ.

## 10b. Luồng khảo sát (Trí chốt 20/11)

1. Trí duyệt thiết kế.
2. Assistant chạy self-test dữ liệu giả **sau khi Trí cho phép**.
3. Nếu lỗi: sửa script → kiểm lại → ghim commit cuối.
4. Push nhánh chứa commit đã ghim lên GitHub. Kiểm notebook lấy được đúng commit đó.
5. Triệu kiểm phần A: thiết kế + danh sách 300 ảnh.
6. Trí gắn dữ liệu/checkpoint và chạy notebook Kaggle. Notebook chạy model → áp bộ lọc đã khóa → chấm 5 cách → xuất ZIP.
7. Trí tải ZIP, gửi assistant và Triệu.
8. Assistant tổng hợp. Triệu kiểm đủ ảnh, đúng cấu hình, tính lại điểm (phần B–C).
9. Đưa bảng kết quả, nhận xét và hạn chế vào báo cáo.
10. Đóng khảo sát ngày 24/11.

## 11. Lệnh chạy (từ thư mục gốc CS331; trên Kaggle là Ô 7–8 của notebook)

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

`RUN = fsc147_survey_kaggle_t4_<stamp>`. Notebook duy nhất: [kaggle_fsc147_survey.ipynb](kaggle_fsc147_survey.ipynb), dành cho Trí.

**Ghim commit:** notebook checkout đúng commit ghi ở `REPO_REF` (Ô 1) và dừng nếu HEAD khác.
- **Push nhánh** chứa commit đó lên GitHub là đủ để notebook lấy code. **Không bắt buộc gộp vào `main` trước.** Nếu sau này gộp, dùng merge hoặc fast-forward, không squash hay rebase, để SHA không đổi.
- **Nếu sửa code sau self-test, phải ghim lại commit mới** và push commit đó.
- **Chưa sẵn sàng chạy** cho tới khi self-test đạt và commit đã ghim có trên GitHub.

## 12. Đầu ra

- **Trước khi chạy (đã có):** bản này, `sample_300/`, `make_fsc147_sample.py`, `score_fsc147_present_only.py`, `selftest_score_fsc147.py` (5 ca từ chối; chưa chạy), notebook, `HUONG_DAN_KIEM_TRIEU.md`.
- **Sau khi chạy:** `results/countgdpp/RUN*` chỉ gồm file nhỏ json/jsonl/csv/txt (D10); raw `.npz` để trên Kaggle. Gồm:
  - `RUN_eval/result.json` và `per_query.csv` (số đếm từng câu của 5 cách);
  - `predictions_*.jsonl`;
  - `fsc_image_sha256.json`, `timing.json`.
  Assistant soạn bảng kết quả và đoạn nhận xét cho mục "Kiểm khả năng tổng quát". Kết quả tốt hay xấu đều giữ nguyên.
