# Khảo sát FSC-147 (300 ảnh) — Triệu chạy thay Trí, 22/11/2026

*Khung do assistant (Claude) soạn ngày 22/11. Cột "Bằng chứng assistant" là những gì assistant đã tự kiểm. Cột "Triệu" do **Triệu tự điền** sau khi tự xem: Đạt / Không đạt / Chưa kiểm được. Assistant không đánh dấu thay.*

Triệu chạy thay Trí theo lời dặn 22/11 (xem `HANDOFF/TRIEU_NGAY_22_11_CHOT_DO_AN.md`). Vì Triệu vừa kiểm A vừa chạy Kaggle, kiểm B/C không còn do một người độc lập làm; assistant sẽ kiểm độc lập B/C khi có ZIP.

## Lần chạy

- Kaggle version: … (Triệu điền); run: `fsc147_survey_kaggle_t4_20261122_1618`
- Giờ bắt đầu / kết thúc: … / … (Triệu điền)
- Thời gian (`timing.json`): runner 571,5 s cho 300 câu (khoảng 1,9 s/câu, gồm lượt 1 + lượt 2 của B2 và P); điểm CLIP cho các khung 404,1 s (khoảng 1,3 s/câu)
- Lỗi / chạy lại: … (Triệu điền; theo ZIP thì run hoàn tất 300/300, mọi câu `ok`)
- ZIP: `for_repo_20261122_1618.zip`. Assistant giải nén, kiểm sha256 của **917/917** file có trong ZIP theo `FILES_20261122_1618.json` (khớp hết). 900 ảnh `.jpg` và 594 tệp `.npz` có trong danh sách nhưng không có trong ZIP, đúng quy ước D10. Đã chép vào `results/countgdpp/fsc147_survey_kaggle_t4_20261122_1618*` và `..._kaggle_meta/`.

## A. Kiểm thiết kế và mẫu (trước khi chạy)

Assistant đọc các file từ `origin/main` (`b7b9015`) và commit ghim `4cd89092c5160dc0dc79455adba42ff096a44664`. Hai bản giống hệt nhau ở `sample_300/`, `score_fsc147_present_only.py`, `experiments/countgdpp/` và freeze v2 (`git diff` rỗng).

| # | Mục kiểm | Bằng chứng assistant (22/11) | Triệu |
|---|---|---|---|
| A1 | Thiết kế: chính B0 − B2; phụ P+F − B2, P+F − B0; C6 − B2+F chỉ mô tả. Mục 9 ghi đúng các thay đổi so với đề xuất A | Bản khai báo §5 đúng như trên. §9 khớp đề xuất A ngày 19/11: 1.190 → 300 ảnh; chính P+F − B2 → B0 − B2; người chạy Triệu → Trí; thêm Bias và số câu trả 0 | |
| A2a | `manifest.csv`: 300 dòng, `query_id` và `image_id` không trùng, `presence_status` đều `present` | 300 dòng; 300 `query_id` và 300 `image_id` khác nhau; `present` = 300 | |
| A2b | `inputs.jsonl`: 300 dòng, cùng thứ tự `query_id` và `prompt` với manifest, không có cột GT | 300 dòng (CRLF); các khóa: `image_id`, `image_path`, `prompt`, `query_id`, `schema_version`; cùng thứ tự và cùng prompt với manifest | |
| A2c | sha256 khớp mục 3 bản khai báo | `inputs.jsonl` c1cfb321…211e, `manifest.csv` 30ea7987…2d33, `sample_meta.json` fc38c12c…92d2: cả ba khớp | |
| A3 | (Tùy chọn) Lấy lại mẫu vào thư mục tạm và so hash | Chạy `make_fsc147_sample.py` trong bản sao ở thư mục tạm (chỉ đọc tệp nhãn, không chạy model). Hash của cả 3 tệp mới **trùng** bản trong repo. Thông tin thêm: GT 8–621 (trung vị 36), nhóm ≤ 40 có 163 ảnh, > 40 có 137 ảnh, 27 lớp | |
| A4 | Script chấm: Δ = MAE(A) − MAE(B); bootstrap cùng bộ ảnh cho A và B; F lấy từ freeze qua `counts_for`; không chia cho số câu vắng mặt | Dòng 66: Δ là trung bình của (sai số A − sai số B), tức MAE(A) − MAE(B). Dòng 68: mỗi lần bootstrap bốc một danh sách ảnh dùng chung cho A và B. Dòng 130: `counts_for(cfg, …)` với cấu hình lấy từ freeze. Hàm `metrics` chỉ chia cho số câu có mặt; không có FPR | |

Tự kiểm lệnh sha256 trên máy (PowerShell, sau khi pull):

```powershell
certutil -hashfile experiments\fsc147_survey\sample_300\inputs.jsonl SHA256
```

## B. Kiểm độ đầy đủ và cấu hình (sau khi chạy)

Assistant kiểm bằng `evaluation/check_fsc147_survey_independent.py`. Script này không import code repo: tự cài lại bộ đếm F theo freeze, các chỉ số, Δ và bootstrap. Trước khi dùng, đã thử trên run test MUCCA 11/11 và ra khớp cả 5 cách. **Kết quả: PASS mọi mục chạy được.**

| # | Mục | Triệu | Assistant (kiểm độc lập, 22/11) |
|---|---|---|---|
| B1 | Đúng commit đã ghim (Ô 2) | | Đạt. Log dòng 15: "commit (đã ghim) 4cd89092c5160dc0dc79455adba42ff096a44664"; `FILES_*.json` ghi cùng commit |
| B2 | Mẫu và freeze đúng, in "tau 0.20, M 5" | | Đạt. Log dòng 16: "mẫu FSC-147 cố định: 300 ảnh … freeze v2 khớp: P(tau 0.20, M 5)+F"; hash mẫu và freeze khớp |
| B3 | Kiểm A của notebook (Ô 5): lệch lớn nhất < 1e-3 | | Đạt. Log dòng 431: "KIEM A: 663 khung, lech lon nhat 3.28e-07, trung binh 5.03e-08". Log cũng ghi "Checkpoint đúng bản đã audit 14/10" |
| B4 | Đủ 300 ảnh trong `fsc_image_sha256.json`, khớp `file_name` | | Đạt: 300 tên, khớp đúng manifest |
| B5 | `run_config.json`: complete, 300 câu, tau [0.2], m 5, có B2 và tau0.200, crop/synthetic/uses_ground_truth = false, T4 | | Đạt mọi trường; device Tesla T4; checkpoint `b89395d7…` (như W8) |
| B6 | `input_sha256 = c1cfb321…` | | Đạt |
| B7 | `predictions_B2.jsonl`, `predictions_tau0.200.jsonl`: mỗi tệp 300 dòng, đều `ok` | | Đạt: 300 dòng mỗi tệp, đúng thứ tự mẫu, đều `ok`; B2 và P cùng lượt 1 |
| B8 | `result.json`: freeze 64e89ef5…, `FSC147_SURVEY_RESULT`, crop false | | Đạt |
| B9 | `timing.json` có `runner_seconds` và `controls_clip_seconds` | | Đạt: 571,5 s và 404,1 s |
| B10 | Chỉ một lần chạy (hoặc WORKLOG ghi lý do chạy lại) | | ZIP và log chỉ có một run (`20261122_1618`). Log không có dòng lỗi nào (0 dòng Traceback/Error/KHONG DAT); tổng thời gian khoảng 26 phút. Triệu xác nhận trên Kaggle không có version khác |

## C. Kiểm bảng kết quả

| # | Mục | Triệu | Assistant |
|---|---|---|---|
| C1 | `per_query.csv` 300 dòng, 5 cột số nguyên ≥ 0 | | Đạt. Số đếm tự tính từ bundle của cả 5 cách = `per_query.csv`; số đếm trong bundle = `predictions_*.jsonl` |
| C2 | Tính lại MAE B0, B2, khớp `summary.all` (< 1e-9) | | Đạt cho cả 5 cách, cả 3 nhóm (toàn mẫu, ≤ 40, > 40), đủ MAE, RMSE, Bias, thừa, thiếu, số câu trả 0 |
| C3 | Tính lại Δ chính, khớp `comparisons[0].diff` | | Đạt cho cả 4 cặp, kèm CI và Δ chính theo nhóm |
| C4 | Đọc CI đúng cách khai báo | | Xem mục "Kết quả" bên dưới |
| C5 | Đoạn nhận xét không so với 8,34 / 10,29 / 8,39, không nói lớp vắng mặt, không gọi là benchmark đầy đủ | | Đoạn nhận xét bên dưới tuân theo; Triệu kiểm lại |

## Kết quả

*Assistant điền 22/11 từ `results/countgdpp/fsc147_survey_kaggle_t4_20261122_1618_eval/result.json`, đã tính lại độc lập.*

**Toàn mẫu (300 ảnh, mọi câu có mặt):**

| Cách | MAE | RMSE | Bias | Đếm thừa | Đếm thiếu | Số câu trả 0 |
|---|---:|---:|---:|---:|---:|---:|
| B0 (một lượt) | 13,88 | 49,00 | −1,54 | 1.851 | 2.312 | 12 |
| B2 (hai lượt) | **13,32** | 48,62 | −0,23 | 1.964 | 2.033 | 12 |
| P+F (đã khóa) | 18,01 | 55,21 | −14,68 | 500 | 4.904 | 12 |
| B2+F (báo kèm) | 17,98 | 53,18 | −14,79 | 478 | 4.915 | 12 |
| C6 = B0+F (báo kèm) | 25,11 | 71,55 | −20,93 | 627 | 6.907 | 36 |

**So sánh khai báo trước** (Δ = MAE(A) − MAE(B); CI 95% bootstrap ghép cặp theo ảnh):

| Vai trò | A − B | Δ | CI 95% | Cách đọc theo khai báo |
|---|---|---:|---|---|
| **Chính** | **B0 − B2** | +0,55 | [−3,00; +4,30] | **Chưa thấy khác biệt rõ** trên mẫu này (CI chứa 0). Không có nghĩa là "bỏ lượt 2 không hại" |
| Chính, nhóm ≤ 40 | B0 − B2 | +0,52 | [−0,13; +1,55] | Chưa thấy khác biệt rõ |
| Chính, nhóm > 40 | B0 − B2 | +0,60 | [−7,07; +8,47] | Chưa thấy khác biệt rõ |
| Phụ | P+F − B2 | +4,69 | [+2,25; +7,50] | **P+F kém hơn B2 trên mẫu này** (CI > 0) |
| Phụ | P+F − B0 | +4,14 | [+0,56; +8,09] | **P+F kém hơn B0 trên mẫu này** (CI > 0) |
| Chỉ mô tả | C6 − B2+F | +7,14 | [+2,37; +12,64] | Hai bộ lọc có ngưỡng khác nhau; không quy cho lượt 2 |

**Theo nhóm số vật (mô tả; CI theo nhóm chỉ khai báo cho cặp chính):**

| Cách | MAE nhóm ≤ 40 (163 ảnh) | MAE nhóm > 40 (137 ảnh) |
|---|---:|---:|
| B0 | 3,95 | 25,69 |
| B2 | 3,44 | 25,09 |
| P+F | 3,50 | 35,28 |
| B2+F | 3,65 | 35,02 |
| C6 | 5,34 | 48,64 |

**Nhận xét** (bản nháp do assistant soạn để đưa vào báo cáo; Triệu và Trí rà lại):

1. **Câu hỏi chính.** Trên mẫu 300 ảnh một loại vật này, với điều kiện không cắt ảnh và không mẫu GPT-5, **chưa thấy khác biệt rõ giữa giữ và bỏ lượt 2**: B2 13,32 so với B0 13,88; CI của chênh lệch chứa 0, ở cả hai nhóm.
2. **Cấu hình đã khóa (P+F) kém hơn trên mẫu này:** cao hơn B2 khoảng 4,7 và cao hơn B0 khoảng 4,1 MAE (CI đều > 0).
   - Theo bảng mô tả, phần kém hơn **tập trung ở ảnh nhiều vật (> 40)**: MAE 35,28 so với 25,09. Ở ảnh ≤ 40 vật, P+F ngang B2 (3,50 so với 3,44) và thấp hơn B0.
   - Nguyên nhân thấy được là **đếm thiếu**: P+F thiếu 4.904 vật so với 2.033 của B2, và Bias −14,68. Bộ lọc F được chọn trên MUCCA (3–40 vật mỗi loại), nên ở ảnh dày nó bỏ cả vật đúng. Bản khai báo §8 đã nêu trước rủi ro này.
3. **C6 kém nhất trên mẫu này** (MAE 25,11, thiếu 6.907 vật, 36 câu trả 0). Vì vậy hướng "C6 cần kiểm tiếp" trong báo cáo chính phải ghi kèm: trên ảnh một loại, dày, C6 lọc quá tay.
4. **Phạm vi áp dụng.** Cải tiến của đồ án (bộ lọc F với ngưỡng chọn trên MUCCA) phù hợp với ảnh nhiều loại, ít đến vừa vật. Với ảnh một loại, nhiều vật, nên giữ CountGD++ gốc, hoặc chọn lại ngưỡng F theo mật độ (hướng phát triển).

**Giới hạn khi nói** (theo khai báo §8):
- Chỉ áp dụng cho mẫu 300 ảnh và điều kiện này. Không phải benchmark đầy đủ của FSC-147.
- Mọi câu đều có mặt, nên khảo sát không nói gì về lớp vắng mặt.
- Không so với 8,34 / 10,29 / 8,39, vì các số đó chạy ở điều kiện khác.

**Log Kaggle:** `notebook258d8120dd.log`, Triệu tải về. Đã lưu vào `results/countgdpp/fsc147_survey_kaggle_t4_20261122_1618_kaggle_meta/kaggle_log_20261122_1618.txt`. Số in trong log (dòng 2017–2022) trùng `result.json`.

**Còn thiếu:**
- Tên version Kaggle.
- Cột "Triệu".
- Trí xem lại bảng kiểm khi rảnh.
