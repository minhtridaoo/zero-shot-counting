# Hướng dẫn Triệu kiểm khảo sát FSC-147 (300 ảnh)

*Assistant soạn theo yêu cầu của Trí, 20/11/2026.* Trí chạy notebook; Triệu là người kiểm độc lập. Không cần GPU. Ghi kết quả kiểm vào WORKLOG, mục của Triệu.

## Trạng thái hiện tại (20/11)

- **Đã chuẩn bị:** bản khai báo, mẫu 300 ảnh, script tạo mẫu, script chấm, self-test, notebook cho Trí.
- **Self-test dữ liệu giả: PASS** (assistant chạy 20/11, Trí cho phép).
- **Khảo sát thật chưa chạy**, chưa có kết quả FSC-147 mới. **Không cần GPU** cho phần của Triệu.
- **Triệu chưa kiểm mục nào.** A1–A4: chờ Triệu, trước khi Trí chạy. B1–B10, C1–C5: chờ kết quả. Assistant không tự ghi "Đạt" thay Triệu.

**Xem trên GitHub:** [nhánh `claude/kind-chaplygin-249b83`](https://github.com/minhtridaoo/zero-shot-counting/tree/claude/kind-chaplygin-249b83). Notebook ghim commit `__PIN__`; các tệp của phần A nằm trong `experiments/fsc147_survey/` ở commit đó.

Mỗi mục có 3 trạng thái: **Đạt**, **Không đạt** (ghi lý do), **Chưa kiểm được** (ghi vì sao). Không đánh "Đạt" khi chưa tự xem.

## A. Trước khi Trí chạy (21/11): kiểm thiết kế và mẫu

1. Đọc [KHAI_BAO_TRUOC_FSC147_20261120.md](KHAI_BAO_TRUOC_FSC147_20261120.md). Kiểm các điểm:
   - So sánh chính là B0 − B2. P+F − B2 và P+F − B0 là phụ. C6 − B2+F chỉ mô tả.
   - Mục 9 ghi đúng những thay đổi so với đề xuất A của Triệu.
   Báo Trí nếu có điểm không đồng ý.
2. Kiểm mẫu bằng tay (chỉ đọc file):
   - `sample_300/manifest.csv` có đúng 300 dòng dữ liệu, `query_id` và `image_id` không trùng, `presence_status` đều là `present`.
   - `sample_300/inputs.jsonl` có đúng 300 dòng, cùng thứ tự `query_id` và `prompt` với manifest, **không có cột GT**.
   - sha256 của `inputs.jsonl`, `manifest.csv`, `sample_meta.json` khớp mục 3 bản khai báo:
     `certutil -hashfile <tệp> SHA256` (Windows) hoặc `sha256sum <tệp>`.
3. Tùy chọn: tự lấy lại mẫu vào **thư mục tạm khác** rồi so hash `inputs.jsonl` và `manifest.csv`. Script chỉ đọc tệp nhãn, không chạy model:
   `python experiments/fsc147_survey/make_fsc147_sample.py --out <thư_mục_tạm_mới>`
   Lưu ý: trên Windows, hash của `inputs.jsonl` chỉ khớp khi ghi ra cũng là CRLF.
4. Đọc nhanh `score_fsc147_present_only.py` và tự kiểm bằng mắt:
   - Δ = MAE(A) − MAE(B);
   - bootstrap lấy lại cùng bộ ảnh cho A và B;
   - F lấy từ freeze v2 qua `counts_for`;
   - không có chỗ nào chia cho số câu vắng mặt.

## B. Sau khi Trí chạy: kiểm độ đầy đủ và cấu hình

Trí gửi `for_repo_<stamp>.zip` và phần in ra của Ô 2, 5, 7, 8.

| # | Kiểm | Ở đâu | Đạt khi |
|---|---|---|---|
| 1 | Đúng commit đã ghim | Ô 2 in "commit (đã ghim)" | Trùng `REPO_REF` của notebook |
| 2 | Mẫu và freeze đúng | Ô 2 | Không có lỗi hash; in "tau 0.20, M 5" |
| 3 | CLIP trên Kaggle giống bản cũ | Ô 5 "KIEM A" | Lệch lớn nhất < 1e-3 |
| 4 | Đủ 300 ảnh, có hash | `fsc_image_sha256.json` | Đúng 300 tên file, khớp cột `file_name` của manifest |
| 5 | Run hoàn tất, đúng cấu hình | `RUN/run_config.json` | `status = complete`, `completed_queries = 300`, `tau_pseudo = [0.2]`, `m = 5`, `outputs` có `B2` và `tau0.200`, `crop = false`, `synthetic = false`, `uses_ground_truth = false`, `device` là T4 |
| 6 | Run dùng đúng mẫu | `RUN/run_config.json` | `input_sha256 = c1cfb321…` |
| 7 | Không câu nào lỗi | `RUN/predictions_B2.jsonl`, `predictions_tau0.200.jsonl` | Mỗi tệp 300 dòng, đều `execution_status = ok` |
| 8 | Chấm đúng freeze | `RUN_eval/result.json` | `freeze_sha256 = 64e89ef5…`, `status = FSC147_SURVEY_RESULT`, `crop = false` |
| 9 | Thời gian có ghi | `timing.json` | Có `runner_seconds` và `controls_clip_seconds` |
| 10 | Chỉ một lần chạy | WORKLOG + Output Kaggle | Không có run khảo sát nào khác. Nếu có chạy lại vì lỗi kỹ thuật thì WORKLOG ghi lý do |

## C. Kiểm bảng kết quả

1. `RUN_eval/per_query.csv` có 300 dòng. Các cột `B0`, `B2`, `P(tau 0.20, M 5)+F`, `C6 = B0+F`, `B2+F` đều là số nguyên ≥ 0.
2. Tự tính lại MAE của B0 và B2 trên toàn mẫu từ `per_query.csv` (Excel hoặc Python): trung bình của |dự đoán − `gt_count`|. Kết quả phải khớp `summary.all` trong `result.json` (sai khác < 1e-9).
3. Tự tính lại Δ chính = MAE(B0) − MAE(B2). Phải khớp `comparisons[0].diff`.
4. Đọc kết quả đúng cách khai báo:
   - CI nằm hoàn toàn trên 0: bỏ lượt 2 làm sai số tăng **trên mẫu này**.
   - CI nằm hoàn toàn dưới 0: bỏ lượt 2 làm sai số giảm trên mẫu này.
   - CI chứa 0: **chưa thấy khác biệt rõ**. Không viết là "không gây hại".
5. Kiểm đoạn nhận xét đưa vào báo cáo:
   - Không so với 8,34 / 10,29 / 8,39.
   - Không nói về lớp vắng mặt.
   - Không gọi đây là benchmark FSC-147 đầy đủ.
   - C6 − B2+F chỉ là mô tả.

## D. Báo lại

Gửi Trí một bảng gồm mục A1–A4, B1–B10, C1–C5 với trạng thái Đạt / Không đạt / Chưa kiểm được. Hạn: A trước khi Trí chạy (21/11); B và C trong ngày nhận kết quả, chậm nhất 24/11.
