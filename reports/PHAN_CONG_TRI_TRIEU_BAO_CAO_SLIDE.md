---
title: "Phân công Trí – Triệu: báo cáo cuối, slide và thuyết trình"
subtitle: "Assistant soạn 23/11/2026 theo yêu cầu của Trí · ĐỀ XUẤT, hai bạn chốt với nhau (assistant không chốt thay Triệu)"
---

> **Nguyên tắc chia:** ai làm phần nào trong đồ án thì người đó trình bày và trả lời câu hỏi về phần đó. Hai người nói gần bằng nhau (khoảng 8 / 7 phút). Đổi người nói ít lần (4 lần) để không mất nhịp.
>
> Nguồn của cột "đã làm": `WORKLOG.md`, `reports/CAM_NANG_DO_AN_CS331.md` (mục 1), `reports/KE_HOACH_SLIDE_THUYET_TRINH.md` (mục 6). Giả định thời lượng **15 phút + hỏi đáp** (chưa có quy định của thầy trong repo; nếu khác, xem mục 5).

# 1. Mỗi người đã làm gì trong đồ án (theo nhật ký)

| Mảng | Trí | Triệu |
|---|---|---|
| Môi trường | Dựng CountGD++ trên Kaggle T4, benchmark FSCD-147 (8.34) | Kiểm chéo evaluator, tính tay, self-test (21–24/10) |
| Pilot, v1 | Pilot 5 ảnh, xem bằng mắt 15/15 câu; cải tiến v1 (lọc + freeze) | Tự kiểm phần 2 (27/10) |
| Chẩn đoán | Chẩn đoán điểm token (15/10); quyết định đưa biến thể T vào trước khi khóa | **N4: gán nhãn mù 117 khung** (mẫu giả 1/21 đúng loại; 21/21 khung trùng); rà soát N4, nơi phát hiện cơ chế max (cùng assistant, `RA_SOAT_TRIEU_N4_20261029.md`) |
| Hướng v2 | Chốt D1–D10, chọn nhánh P + T | Đề xuất nhánh P (29/10), quy tắc dữ liệu v2 (04/11) |
| Dữ liệu v2 | Kiểm 20 ảnh dev | Rút dev/test (W1), **kiểm 40 ảnh test (W4), khóa dữ liệu (W5)** |
| Thực nghiệm | Chọn và **khóa cấu hình** (freeze v2) | **Chạy dev (W6), test một lần (W8)**, khảo sát FSC-147 trên Kaggle |
| Bổ sung 22/11 | Đồng ý thiết kế khảo sát và thử nghiệm gán khung | Kiểm A khảo sát; đề nghị thử hướng 1 (gán khung theo CLIP) |
| Viết | Bản chi tiết 22 trang, bản tóm tắt gửi thầy | **Related Work**, so sánh với nhóm khác, điểm yếu và hướng giải quyết |

Assistant (Claude) đã: viết phần lớn code chấm/hậu kiểm, tính lại độc lập các kết quả, soạn nháp tài liệu. Phải khai báo trong báo cáo (mục 4 dưới).

# 2. Báo cáo cuối (LaTeX, `final/report/main.tex`)

Assistant đã dựng **bản nháp đầy đủ**. Việc của hai bạn là: mỗi người **rà, sửa câu chữ và chịu trách nhiệm** phần của mình, rồi đọc chéo phần người kia.

| Chương | Phụ trách rà chính | Đọc chéo | Ghi chú |
|---|---|---|---|
| Tóm tắt, 1 Giới thiệu | Trí | Triệu | |
| 2 Công trình liên quan | **Triệu** | Trí | Từ nháp W7; Triệu kiểm lại trích dẫn PseCo, DAVE, VA-Count |
| 3 Kiến thức nền (CountGD++, CLIP) | Trí | Triệu | |
| 4 Bài toán và chỉ số | Trí | Triệu | |
| 5 Phương pháp (chẩn đoán, P, F, T) | Trí | Triệu | |
| 6 Dữ liệu và giao thức | **Triệu** | Trí | Triệu khóa dữ liệu và chạy test |
| 7 Kết quả (FSCD-147, pilot, v1, N4, dev, test) | Trí (7.1–7.3, 7.5–7.6), **Triệu (7.4 N4)** | chéo | |
| 8 Phân tích, FSC-147, thử nghiệm gán khung | **Triệu** | Trí | Triệu chạy FSC-147 |
| 9 Hạn chế, 10 Kết luận | Trí | Triệu | |
| Khai báo đóng góp + dùng AI | **cả hai cùng ký** | | Không ai ghi thay người kia |

# 3. Slide và lời nói (bản 2, 23/11: 30 slide nội dung, 5 phần, khoảng 24 phút)

> **Cập nhật 25/11 — sắp lại theo phiếu chấm (thứ tự 1 → 7). Bảng này thay cho bảng bản 2 bên dưới.**
> Số trang là số in trên slide (x/46). Người nói đã ghi ở đầu mỗi `\note`. Tổng 25:00: Trí 13:50, Triệu 11:10. Đây vẫn là **đề xuất**, hai bạn chốt.
>
> | Mục phiếu | Trang | Slide | Người nói | Thời gian |
> |---|---|---|---|---|
> | — | 1–2 | Bìa, Nội dung | Trí | 0:35 |
> | 1 Lý do | 3–6 | (chia mục), Bối cảnh, Khoảng trống, Related work | Trí | 2:10 |
> | 2.1 Bài toán | 7–9 | (chia mục), Định nghĩa, Câu hỏi nghiên cứu | Trí | 1:30 |
> | 2.2 Minh họa | 10 | mcac\_12 plates/bowls/spoons | Trí | 0:50 |
> | 3 Phương pháp | 11–12 | (chia mục), Baseline | Trí | 1:00 |
> | | 13–16 | Chẩn đoán, VĐ1, VĐ2, VĐ3 | **Triệu** | 3:30 |
> | | 17–20 | Cải tiến P, F, Tổng thể, **Điểm khác biệt (mới)** | Trí | 3:15 |
> | 4.1–4.2 | 21–25 | (chia mục), Dữ liệu MUCCA, **Tổng hợp dữ liệu (mới)**, **Độ đo (mới)**, Giao thức | **Triệu** | 3:10 |
> | 4.3 | 26 | Kết quả test | Trí | 1:10 |
> | | 27–28 | Phân rã, F và shared box | **Triệu** | 1:45 |
> | 4.4 | 29–30 | FSC-147, các hướng thử thêm | **Triệu** | 1:55 |
> | | 31 | **Demo (mới)**: slide + mở app | Trí | 1:30 |
> | 5 Kết luận | 32–33 | (chia mục), Những điều chưa trả lời được | **Triệu** | 0:50 |
> | | 34–35 | Kết luận, Hướng phát triển | Trí | 1:30 |
> | — | 36 | Phân công công việc (chuyển từ đầu xuống cuối) | Trí | 0:20 |
> | 7 Hỏi đáp | 37 | Cảm ơn, mời câu hỏi | cả hai | — |
> | dự phòng | 38–46 | Kết quả đầy đủ, v1, chi phí, thứ hạng dev, kết quả dev, ví dụ thất bại, ví dụ thành công/lỗi X/Y, theo loại cặp | người phụ trách phần đó | — |
>
> Đổi người nói 8 lần, nhiều hơn mức 4 lần của bản 1. Muốn ít lần đổi hơn thì Trí có thể nói luôn trang 27–28 (phần phân tích kết quả); khi đó Trí khoảng 15:35, Triệu khoảng 9:25.

> **Cập nhật 24/11:**
> - Slide đã thêm **slide 3 "Phân công công việc"** (bảng ai làm gì, lấy từ mục 1 file này) và bỏ nhãn "Trình bày" ở chân trang. Từ slide 3 trở đi, **số slide trong bảng dưới tăng thêm 1**.
> - Ai nói slide nào không đưa lên slide. Theo số mới: Trí 4–10, 15–17, 20–21, 30–31; Triệu 11–14, 18–19, 22–29.
> - Thuật ngữ trên slide đổi sang tiếng Anh: box, pseudo-exemplar, query, class, GT…
> - Mục 6 bên dưới còn dùng số slide của bản 1.

Bản 2 làm lại theo yêu cầu Trí: bố cục 5 phần (giống cách nhóm Hoàng Anh – Duy chia, nhưng nội dung và giao diện của nhóm mình), có mục lục, trang chia phần, định nghĩa hình thức, mỗi vấn đề có ảnh bằng chứng thật, tiêu đề slide nói kết luận, chân slide ghi "Trình bày: …" và nguồn số liệu.

| # | Phần | Slide | Người nói | Thời gian |
|---|---|---|---|---|
| 1–2 | | Bìa, Nội dung | Trí | 0:35 |
| 3 | 1. Lý do | Bối cảnh: đếm bằng tên lớp; kiểm môi trường 8.34 / 8.39 | Trí | 0:50 |
| 4 | | Khoảng trống: FSC-147 một loại; MUCCA; bài X/Y | Trí | 0:50 |
| 5 | | Công trình liên quan và vị trí đồ án (nội dung từ Related Work của Triệu) | Trí | 0:45 |
| 6 | 2. Bài toán | Định nghĩa input/output, Y1–Y3 | Trí | 0:50 |
| 7 | | **Minh họa mcac_12:** plates 36 / bowls 36 / spoons 34 (đáp án 16 / 3 / 0), 36/36 khung trùng | Trí | 0:50 |
| 8 | | RQ1–RQ3 và 4 đóng góp | Trí | 0:40 |
| 9 | 3. Phương pháp | Baseline CountGD++ B0/B2, cách chấm điểm | Trí | 1:00 |
| 10 | | **Bảng 3 vấn đề → hướng xử lý** | **Triệu** | 0:45 |
| 11 | | VĐ1: khung không đổi theo câu hỏi (mcac_88, 21/21; test 64%) | **Triệu** | 0:55 |
| 12 | | VĐ2: mẫu giả sai loại (N4 1/21; pilot 23/42) | **Triệu** | 0:50 |
| 13 | | VĐ3: cách chấm max, phép thử T (21%), H2 | **Triệu** | 1:00 |
| 14 | | Cải tiến P (thuật toán) | Trí | 0:50 |
| 15 | | Cải tiến F (công thức + ví dụ 4 khung) | Trí | 0:55 |
| 16 | | Tổng thể các biến thể | Trí | 0:40 |
| 17 | 4. Thực nghiệm | Dữ liệu MUCCA (6 ảnh mẫu, 4 tập, luật rút mẫu) | **Triệu** | 0:55 |
| 18 | | Giao thức "chọn trước, xem sau", D9, chỉ số, bootstrap theo ảnh | **Triệu** | 1:00 |
| 19 | | Kết quả dev (D9 chọn P+F) | Trí | 0:40 |
| 20 | | **Kết quả test chính** (−24%, CI không chứa 0) | Trí | 1:10 |
| 21 | | Phân rã: F giúp, P không (108/120) | **Triệu** | 0:55 |
| 22 | | Khung đúng/sai loại, dùng chung X/Y | **Triệu** | 0:50 |
| 23 | | Theo loại cặp | **Triệu** | 0:50 |
| 24–25 | | Ví dụ thành công / lỗi X/Y còn lại / thất bại / lọc quá tay | **Triệu** | 1:30 |
| 26 | | Tổng quát hóa FSC-147 (phạm vi áp dụng) | **Triệu** | 0:55 |
| 27 | | Các hướng thử thêm: gán khung CLIP; bài học C6 | **Triệu** | 1:00 |
| 28 | 5. Kết luận | Những điều kết quả chưa nói được | **Triệu** | 0:50 |
| 29 | | **Bảng kết luận vấn đề → cải tiến → kết quả** | Trí | 1:00 |
| 30–31 | | Hướng phát triển; Cảm ơn | Trí | 0:30 |

- **Trí khoảng 12 phút, Triệu khoảng 12 phút** (tính từ thời gian ghi trong kịch bản nói).
- **Vì sao chia vậy:** Triệu nói phần mình trực tiếp làm (review N4, khóa dữ liệu test, chạy test và FSC-147 trên Kaggle, các phân tích); Trí nói khung bài toán, phương pháp, cấu hình đã khóa, kết quả chính và kết luận.
- **6 lần đổi người**, có câu chuyển ở cuối lời nói mỗi khối (xem `notes.pdf`): S9→S10, S13→S14, S16→S17, S18→S19, S20→S21, S28→S29.
- **Slide dự phòng** (sau Cảm ơn): test đầy đủ (có RMSE), v1 trên 10 ảnh, chi phí + tái lập, thứ hạng dev.
- File: `final/slides/main.pdf`; kịch bản nói `final/slides/notes.pdf`. Hình mới sinh từ dự đoán đã lưu bằng `final/shared/figures/make_slide_figures.py` (không chạy mô hình; 21/21 và 36/36 khung trùng được tính lại khớp).

# 4. Hỏi đáp: ai trả lời

| Chủ đề câu hỏi | Người trả lời chính |
|---|---|
| Vì sao không huấn luyện lại; vì sao CLIP ViT-B/32; θ ở đâu ra; P không giúp sao vẫn là chính; X/Y giải xong chưa; dùng AI | **Trí** |
| Cỡ mẫu, CI theo ảnh, GT đúng không, "có ý nghĩa thống kê"; vì sao không chọn C6; câu vắng mặt; FSC-147; DAVE; thời gian chạy; tái lập; thử nghiệm dev tin được không | **Triệu** |
| Đóng góp từng người | mỗi người tự nói phần mình (bảng mục 1) |

Người kia **bổ sung tối đa một câu**, không nói chồng.

# 5. Nếu thầy cho thời lượng khác

**Trí xác nhận 23/11: thời lượng khoảng 20–25 phút** → giữ nguyên bản 2 (khoảng 24 phút). Nếu tập thử thấy quá 25 phút thì bỏ trước S5, S16, S22 (khoảng −2:15).

- **20 phút:** bỏ S5 (liên quan, để trả lời khi hỏi), S16, S19, S22; gộp S24–S25 thành một slide. Còn khoảng 20 phút.
- **15 phút:** thêm bỏ S8, S12 (nói một câu ở S10), S18 (nói D9 ở S20), S27, S30. Còn khoảng 15–16 phút.
- Muốn bỏ slide trong Beamer: chuyển frame xuống sau `\appendix`.

# 6. Việc còn lại đến 02/12

| Ngày | Trí | Triệu |
|---|---|---|
| 23–25/11 | Rà chương 1, 3–5, 7, 9–10 của báo cáo LaTeX; điền tên đầy đủ, MSSV, giảng viên | Rà chương 2, 6, 7.4, 8; kiểm trích dẫn |
| 26–27/11 | Sửa slide phần mình; tập lời S1–S5, S8–S10, S16 | Sửa slide phần mình; tập S6–S7, S11–S15 |
| 28/11 | Cùng chốt câu khai báo AI và đóng góp; biên dịch bản cuối | |
| 29–30/11 | Tập chung 2 lần, bấm giờ; hỏi nhau các câu ở mục 4 | |
| 01/12 | Rà bản nộp (PDF báo cáo, PDF slide, repo) | |
| **02/12** | **Nộp** | |

# 7. Cần hai bạn chốt (assistant không tự quyết)

1. Bảng phân công này (đặc biệt: Triệu có đồng ý nói S6–S7, S11–S15 không).
2. ~~Thời lượng~~ (đã chốt 20–25 phút, 23/11); mẫu báo cáo/slide nếu thầy có quy định.
3. Tên đầy đủ của Triệu, MSSV, tên giảng viên, tên trường/khoa (báo cáo để `[TODO]`).
4. Câu khai báo dùng AI (bản nháp ở cuối báo cáo).
