# Bắt đầu phiên mới — trạng thái CS331

**Tiến độ 18/11/2026 (còn 14 ngày đến hạn nộp 02/12):**
- Thực nghiệm **đã xong hết** từ 11/11: dev, khóa cấu hình, test một lần (P+F MAE 5.82 so với B0 7.71). Không còn thí nghiệm bắt buộc nào.
- Đã có: bản chi tiết 22 trang (khung báo cáo cuối), bản tóm tắt gửi thầy 5 trang, 6 hình, các script hậu kiểm. Tất cả đã push lên GitHub (commit 406ba54, 15/11). Từ 15/11 đến 18/11 chưa có commit mới.
- **Còn thiếu:** (1) báo cáo cuối đúng mẫu nộp; (2) Related Work của Triệu (W7, hạn 20/11, chưa thấy trong repo); (3) slide; (4) demo trước/sau cải tiến.
- Chưa xác nhận được trong repo: Trí đã gửi bản tóm tắt cho thầy chưa, thầy góp ý gì.

**Cập nhật 20/11 — thêm hai phần kiểm tổng quát (chưa chạy model):**
- **FSC-147 — Trí chạy.** Câu hỏi: bỏ lượt 2 có làm giảm chất lượng đếm trên ảnh một loại không. Mẫu cố định 300 ảnh (seed 331).
  - Cặp chính B0 − B2 (chỉ khác lượt 2). Cặp phụ P+F − B2, P+F − B0. C6/B2+F chỉ báo kèm.
  - Đã có: [bản khai báo trước](experiments/fsc147_survey/KHAI_BAO_TRUOC_FSC147_20261120.md), `sample_300/`, 2 script mới, notebook [kaggle_fsc147_survey.ipynb](experiments/fsc147_survey/kaggle_fsc147_survey.ipynb) đã ghim commit.
- **FSCD-147 — Triệu.** Chờ Triệu xác nhận phần của mình là tổng hợp kết quả đã có (benchmark 8,34 + kiểm Bảng 1 bài báo) hay chạy mới (notebook `experiments/benchmark_fscd147/COUNTGDPP_FSCD147_KAGGLE.ipynb`, cần Trí duyệt).
  - FSC-147 test và FSCD-147 test là **cùng 1.190 ảnh**, nên Triệu không chạy lại cặp B0/B2/P+F.
- Các file đang ở worktree `.claude/worktrees/kind-chaplygin-249b83`, nhánh `claude/kind-chaplygin-249b83`, **chưa push**. Checkout chính chưa thấy cho tới khi push và gộp vào `main`.

**Việc tiếp theo, theo thứ tự:**
1. Trí: báo đã gửi bản tóm tắt cho thầy chưa; duyệt bản khai báo FSC-147.
2. Push nhánh có commit đã ghim lên GitHub, rồi gộp vào `main` (merge hoặc fast-forward, không squash).
3. Trí chạy notebook FSC-147 (22–23/11). Triệu xác nhận phần FSCD-147 và nộp Related Work (W7). **Hạn đóng hai phần này: 24/11.**
4. Trí + assistant: chuyển bản chi tiết thành báo cáo cuối (19–25/11).
5. Slide + demo tĩnh (25–29/11), dùng lại hình trong `reports/figures/`; tập thuyết trình 30/11–01/12.

**Đợt đồng bộ Git 15/11:** báo cáo và kết quả hậu kiểm được đưa vào commit của phiên này. Việc tiếp theo: Trí đọc mục 4.1/7.6 bản chi tiết rồi gửi thầy; chưa chạy kiểm giả thuyết H2 hoặc thí nghiệm mới.

**Cập nhật 10/11/2026; 11/11: Triệu ghi duyệt pilot (W3), pilot đã đóng; Triệu kiểm xong 40 ảnh test (W4), khóa dữ liệu (W5), chạy dev trên Kaggle (W6).**

> **Trí đọc trước 16/11:** [reports/TRIEU_W6_DEV_D9_20261111.md](reports/TRIEU_W6_DEV_D9_20261111.md). D9 trên dev, **đã có cả T và P+T** (11/11): M = 5 ứng viên tau0.200+F (MAE 3.533 so với B0 6.283); M = 10 hòa tau0.180+F và tau0.200+F. T/P+T không đổi lựa chọn (P+T+F 3.78). Trí chọn và khóa cấu hình.

> **t37_1 đã chốt 11/11:** Trí chọn đánh `uncertain`, loại khỏi chấm (3 bút chì bị MUCCA gán `pens`); đã áp trước khi Triệu khóa. Trí cũng đã khóa ở máy mình nhưng chưa push: **khi pull sẽ xung đột `selection_meta.json`/`test/manifest.csv`; bản trên GitHub đã có quyết định này**. Xem [TRIEU_W4_KIEM_TEST_20261111.md](reports/TRIEU_W4_KIEM_TEST_20261111.md) mục 3.
- Kế hoạch đầy đủ: [roadmap/KE_HOACH_HOAN_THANH_20261110.md](roadmap/KE_HOACH_HOAN_THANH_20261110.md).
- Nhật ký: [WORKLOG.md](WORKLOG.md). Bản đồ thư mục: [README.md](README.md).
- Bản cũ của file này (nhiều lớp cập nhật chồng nhau): `quá khứ/2026-11-10_don_dep/BAT_DAU_SESSION_MOI_cu.md`.

**Đồng bộ Git 11/11:** đã gộp cc5510b với c572c04, giữ cả hai đóng góp. Pilot đã đóng; dev đã kiểm xong. Triệu tiếp W4/W5 và W6; hướng dẫn kiểm test: [HUONG_DAN_KIEM_V2](experiments/countgdpp/dev_test_v2/HUONG_DAN_KIEM_V2.md).

## Đang ở đâu

```
✅ [1] Chạy CountGD++    ✅ [2] Pilot tìm lỗi    ✅ [3] Cải tiến v1 (lọc + freeze)
✅ [4] Kiểm 10 ảnh mới    ✅ [5] N4 review khung   ✅ [6] Chốt nhánh P + T, D1–D10 (05/11)
✅ [7] Dữ liệu v2: dev + test đã kiểm, LOCKED 11/11 (Triệu W5; D11 GT MUCCA, D12 t37_1 uncertain)
✅ [8] Chạy dev trên Kaggle T4 (Triệu W6, Kiểm A/C 60/60) + chấm D9 (assistant)
✅ [9] KHÓA CẤU HÌNH 11/11: P(tau 0.20, M = 5)+F → `results/countgdpp/freeze_v2_20261111.json` (dev 3.53 so với B0 6.28)
✅ [10] TEST một lần (Triệu W8, 11/11): **P+F MAE 5.82 so với B0 7.71 (−1.88, CI [−3.66, −0.44])**; C6 4.63; B2 9.61. Kiểm độc lập khớp ([kết quả](reports/KET_QUA_TEST_CUOI_20261111.md))
✅ [10b] Gói hậu kiểm + bản tiến độ gửi thầy (11/11, assistant, CPU): khung trùng X/Y, khung đúng loại, thời gian, 6 hình
✅ [10c] Bản trình bày CHI TIẾT 19 trang (12/11): nền tảng, định nghĩa, phương pháp, giao thức, kết quả, phân tích, hạn chế
✅ [10d] Sửa theo góp ý của bạn đọc (15/11): T chỉ gỡ khoảng 1/5 tác hại lượt 2; −39% so với B2 chỉ là mô tả; mục 7.6 giải thích thứ hạng C6
⏳ [11a] Kiểm tổng quát FSC-147, 300 ảnh (Trí): đã chuẩn bị + ghim commit 20/11; chờ duyệt, push, chạy 22–23/11; đóng 24/11
⏳ [11b] FSCD-147 (Triệu): chờ xác nhận tổng hợp hay chạy mới; đóng 24/11
⏳ [11] Báo cáo cuối + slide + demo → nộp 02/12   ◀── ĐANG Ở ĐÂY (18/11: có khung 22 trang; chưa có báo cáo cuối, Related Work, slide, demo)
```

**Nhánh P** (CLIP kiểm mẫu trước lượt 2) đã có code và đã kiểm trên pilot; chưa thử thật vì dữ liệu chưa khóa. **Nhánh R** chỉ để dự phòng. Chi tiết ở mục 1b của file kế hoạch.

**Chẩn đoán sớm 11/11 (assistant, CPU, trên p4_unseen_v1 đã xem — không phải kết quả độc lập):** [reports/ASSISTANT_CHAN_DOAN_T_C6_20261111.md](reports/ASSISTANT_CHAN_DOAN_T_C6_20261111.md).
- **T** cải thiện rõ so với B2: −4.20 MAE, CI [−7.30, −1.63], 12 tốt hơn / 0 kém hơn. Nhưng T **chưa bằng B0**.
- **C6 = B0 + lọc, chọn lại ngưỡng** (kiểm chéo giữ 1 ảnh) **thắng B0 theo D9**: B0+S MAE 3.70 / có mặt 4.85 (B0: 6.77 / 5.70), CI [−7.37, −0.20]; B0+F chặn vắng mặt tốt nhất (1/10).
- Ngưỡng B0+S ≈ **0.34** thay cho mặc định 0.23, tức là nâng ngưỡng 1 lượt.
- Mọi cách đi qua lượt 2 đều thua B0 ở query có mặt. Kế hoạch W6 **không đổi** (C6 đã có trong D8); dev_test_v2 sẽ xác nhận.

**✅ Dev đã chốt nội dung (11/11):** Trí kiểm xong 20 ảnh / 60 query (20/20 absent_ok, 40 GT present: 30 khớp, 10 `needs_review`). Assistant chuyển 2 CSV từ ANSI sang UTF-8, bỏ cột trống Excel thêm, sửa ngày; kiểm nhất quán **ĐẠT** (prompt/class/GT = MUCCA, hash ảnh khớp, chỉ cột người kiểm thay đổi). Hash: `dev/inputs.jsonl` e0b420fc7585…, `dev/manifest.csv` 52d3f667bcd1…. Bản Excel gốc lưu ở `quá khứ/snapshots/2026-11-11_bang_dev_ansi_truoc_chuyen_ma/`.
- **D11 (Trí chốt 11/11): GT = số điểm MUCCA gốc.** Chỗ người kiểm đếm khác thì vẫn giữ `gt_count` MUCCA, ghi `needs_review` + số người đếm vào `uncertainty_note`; báo cáo thêm một bảng độ nhạy "nếu dùng số người đếm". Lớp absent nhìn thấy trong ảnh thì đổi sang ứng viên kế tiếp đầu tiên. **Lưu CSV bằng "CSV UTF-8"**, ngày dạng `2026-11-11`.
- **Triệu chạy W6 (dev trên T4) được ngay**, vì W6 chỉ dùng `dev/inputs.jsonl` (không có GT, không đụng test). Khóa chính thức `LOCKED` (W5) sau khi test 40 ảnh kiểm xong.

**Cập nhật 11/11 — kiểm bảng absent dev:** đã có 19 `absent_ok`, riêng `mcac_99/key holders` là `visible`, chưa có lớp thay được xác nhận; người/ngày kiểm còn trống. Tiếp: Trí điền GT present trong dev/manifest.csv và hoàn thiện absent trước khóa. Chưa xác nhận hoàn thành cả 20 ảnh.

Ảnh hỗ trợ kiểm GT dev: [mở danh sách 40 ảnh có điểm và số thứ tự](experiments/countgdpp/dev_test_v2/dev/gt_review_images/index.html). Đây là nhãn nguồn, không phải dự đoán hay xác nhận người.

**✅ 11/11 (tối) — dev v2 đã chấm theo D9** ([kết quả](reports/DEV_V2_D9_KET_QUA_20261111.md)):
- B0: MAE 6.28 / có mặt 8.25 / FPR 0.20.
- **P(tau 0.20, M = 5)+F: 3.53 / 5.05 / 0.05**, ứng viên D9.
- P(tau 0.18–0.22, M = 10)+F ≈ 3.62; B2+F 3.73; C6 (B0+F) 4.02.
- Ngưỡng chọn trên chính dev nên số lạc quan; các cách đứng đầu sát nhau, test sẽ quyết.
- **T / P+T đã có** (Triệu tính từ raw Kaggle; assistant kiểm lại khớp): T 8.55, P+T 8.25, P+T+F 3.78. **D9 không đổi**: P(tau 0.20, M = 5)+F.

**✅ Thực nghiệm đã xong (11/11).** Kết luận chính ([reports/KET_QUA_TEST_CUOI_20261111.md](reports/KET_QUA_TEST_CUOI_20261111.md)):
- Cải tiến được kiểm chứng trên test: P+F 5.82 so với B0 7.71.
- Lượt 2 tự chọn mẫu gây hại: B2 kém B0 có ý nghĩa.
- Thành phần hiệu quả là bộ lọc Fusion CountGD++ + CLIP: B2+F ≈ P+F; C6 4.63 tốt nhất, nhưng so với P+F chưa có ý nghĩa thống kê.
- Kết quả chính vẫn là P+F như đã khóa.

**✅ 11/11 (khuya) — gói gửi thầy đã xong** (hậu kiểm, không chạy model, không chọn lại cấu hình):
- **Bản tiến độ gửi thầy:** [reports/BAO_CAO_TIEN_DO_GUI_THAY_20261111.md](reports/BAO_CAO_TIEN_DO_GUI_THAY_20261111.md) + `.docx` + `.pdf` (5 trang). **Trí đọc, sửa tên Triệu đầy đủ rồi gửi (14/11).**
- **Phân tích:** [reports/PHAN_TICH_HAU_KIEM_TEST_20261111.md](reports/PHAN_TICH_HAU_KIEM_TEST_20261111.md).
  - Đổi X → Y: B0 64%, B2 71%, P+F 59%, C6 24% khung dùng chung.
  - Khoảng 1/3 khung đếm là loại khác: B0 34.6%, P+F 32.7%, C6 21.3%.
  - Thời gian: B0 khoảng 0.89 s, B2/P khoảng 1.5 s + CLIP (CLIP không được ghi).
- **Hình** ở `reports/figures/`: pipeline, cột kết quả test, 4 ví dụ (blueberries thành công, bowls lỗi X/Y, dogs thất bại, people lọc quá tay).
- Script: `evaluation/test_xy_overlap_analysis.py`, `evaluation/make_report_figures.py`. Chưa commit/push.

**✅ 12/11 — bản trình bày chi tiết** ([reports/BAO_CAO_CHI_TIET_DO_AN_20261112.md](reports/BAO_CAO_CHI_TIET_DO_AN_20261112.md) + `.docx` + `.pdf`, 19 trang), theo yêu cầu "cặn kẽ, học thuật, dễ hiểu". Dùng làm **khung cho báo cáo cuối**.

Hậu kiểm mới:
- **Theo loại cặp:** cải thiện ở cặp dễ nhầm (P+F −3.05 [−5.43, −0.96]); cặp khác hẳn chưa khác B0 (+0.51 [−0.72, +1.82]).
- **F đổi lỗi đếm thừa thành đếm thiếu:** B0 +580/−77, P+F +243/−297.
- **P chọn lại đúng bộ mẫu B2 ở 108/120 câu.**
- Đã sửa lỗi ghi sai trong bản hậu kiểm 11/11: mcac_25 có nhãn dâu tây.

Bản tóm tắt gửi thầy đã thêm các ý trên. **Bản `.docx` đang mở trong Word nên chưa ghi đè được.** Bản cập nhật nằm ở `BAO_CAO_TIEN_DO_GUI_THAY_20261111_capnhat_1211.docx`; PDF đã cập nhật.

**✅ 15/11 — sửa bản chi tiết + bản tóm tắt theo góp ý** (bản chi tiết 22 trang, bản tóm tắt 5 trang, đã xuất lại docx/pdf).
Hậu kiểm dev: `evaluation/dev_posthoc_T_C6.py` → `results/countgdpp/p1_dev_kaggle_t4_20261111_1203_posthoc_20261115/`.
- T gỡ được 21% [5, 60] tác hại lượt 2 trên dev (67% trên p4_unseen_v1); T vẫn kém B0 (+2.27 [+0.52, +4.12]).
- C6 trên dev: thứ 7/15 họ phương pháp, thứ 25/90 cấu hình; C6 − P+F = +0.48 [−0.62, +1.63].
- Dev → test: P+F +2.29, C6 +0.61, B0 +1.42.

## Việc ngay tiếp theo

*Cập nhật 20/11. Các dòng đã xong trước đó (W6, W8, freeze v2) xem WORKLOG 11/11.*

| Ai | Việc | Hạn |
|---|---|---|
| **Trí** | (1) Báo đã gửi bản tóm tắt cho thầy chưa. (2) Duyệt [khai báo FSC-147](experiments/fsc147_survey/KHAI_BAO_TRUOC_FSC147_20261120.md). (3) Sau khi push: chạy `experiments/fsc147_survey/kaggle_fsc147_survey.ipynb` trên Kaggle T4, một lần | 21/11; chạy 22–23/11 |
| **Trí** | Viết báo cáo cuối từ bản chi tiết 22 trang | 19–25/11 |
| **Triệu** | (1) Xác nhận phần FSCD-147: tổng hợp kết quả đã có hay chạy mới (chạy mới cần Trí duyệt). (2) Related Work (W7) | W7: 20/11; FSCD-147: 24/11 |
| **Assistant** | Đã xong: script tạo mẫu, script chấm, notebook đã ghim commit. Tiếp: kiểm output FSC-147; soạn đoạn "Kiểm khả năng tổng quát"; hỗ trợ báo cáo cuối | 24/11 |
| **Cả nhóm** | Slide + demo tĩnh; tập thuyết trình | 25/11–01/12 |


**Giải thích thao tác (10/11):** kiểm absent/GT là xem ảnh gốc để xác nhận nhãn đầu vào dùng chấm, không review output model. Đã đọc bảng: dev vẫn 20 PENDING; có thể bắt đầu mcac_9 (plates=12, cups=4, forks dự kiến vắng mặt). Chưa có xác nhận nhãn mới.

## Quy tắc cần nhớ

- Assistant hỏi Trí trước khi chạy evaluator/model/thực nghiệm. Đọc file, viết code/tài liệu thì làm luôn.
- **Không sửa** dữ liệu đã khóa (`p4_unseen_v1`), freeze (`results/countgdpp/p4_candidate_freeze_20261021.json`), prediction gốc, hay file `.py` đã ghi hash trong audit.
- Test chỉ chạy **một lần**, sau khi khóa cấu hình. Không chỉnh tham số theo kết quả test.
- Sau mỗi lượt làm việc: cập nhật WORKLOG + file này.

## Câu mở phiên mới

> Tiếp tục CS331 tại D:\MINHTRIHOCCODE\HOCKI5\CS331. Đọc AGENTS.md, BAT_DAU_SESSION_MOI.md và mục mới nhất của WORKLOG.md; kiểm Git (remote zero-shot-counting) rồi làm tiếp việc đầu tiên chưa xong.
