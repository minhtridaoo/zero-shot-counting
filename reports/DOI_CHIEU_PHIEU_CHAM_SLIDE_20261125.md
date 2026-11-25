# Đối chiếu phiếu chấm với slide (25/11/2026)

- **Nguồn phiếu chấm:** `C:\Users\ADMIN\Downloads\PhieudanhgiaMonhoc.pdf` (bản gốc Trí gửi; đã đọc cả 2 trang, hai trang giống nhau).
- **Slide:** `final/slides/main.pdf`, 46 trang: 37 trang trình bày + 9 trang dự phòng. Số trang dưới đây là số in ở góc phải mỗi slide (x/46).
- **Người đối chiếu:** assistant soạn. Mức điểm do thầy chấm. Bảng này chỉ ghi slide nào đáp ứng tiêu chí nào và còn thiếu gì, **không** tự chấm đạt.
- **Thứ tự:** các mục trên slide đi đúng 1 → 7 như phiếu. Tên năm mục trong mục lục (trang 2) trùng tên trên phiếu.

| Tiêu chí (điểm) | Slide đáp ứng | Còn thiếu / chờ duyệt |
|---|---|---|
| **1. Lý do, cơ sở thực hiện đề tài (5)** | Mục 1, trang 3–6: bối cảnh và kiểm môi trường FSCD-147 (4), khoảng trống của FSC-147 và bài X/Y (5), related work (6) | — |
| **2.1 Phát biểu bài toán (15)** | Mục 2, trang 7–9: định nghĩa input/output, ba yêu cầu Y1–Y3 (8); câu hỏi nghiên cứu RQ1–RQ3 và đóng góp (9) | Thứ tự đã sửa: Định nghĩa → RQ → Minh họa |
| **2.2 Hình minh họa (5)** | Trang 10: mcac_12, ba query, 36/36 box trùng | — |
| **3. Phương pháp: dễ hiểu, nổi bật điểm khác biệt (30)** | Mục 3, trang 11–20: baseline (12), chẩn đoán ba vấn đề (13–16), cải tiến P (17), F (18), tổng thể các biến thể (19), **bảng khác biệt với CountGD++ gốc, PseCo, VA-Count, DAVE (20)** | Trang 20 ghi rõ **chưa so trực tiếp**, nên không nói tốt hơn. Đặc điểm từng phương pháp lấy từ Related Work của Triệu, đã đối chiếu lại tóm tắt arXiv 25/11. Triệu nên đọc lại trang 20 |
| **4.1 Mô tả dataset (10)** | Trang 22: MUCCA (200 ảnh, 45 class, 2–7 class/ảnh, 12.265 điểm nhãn; bốn tập; 120 → 119 query). Trang 23: bảng mọi dữ liệu và lần đánh giá; ghi rõ FSCD-147 và FSC-147 **cùng nguồn ảnh**, không độc lập | Chú thích mcac_171 sửa thành "chó–dê (+80 cừu)". Kiểm theo nhãn gốc: chó 4, dê 7, cừu 80; cặp query trên test là dogs–goats |
| **4.2 Độ đo (10)** | Trang 24: MAE, RMSE, MAE present, FPR_absent, shared box X/Y, CI bootstrap theo ảnh, kèm ví dụ số. Ghi rõ CI chứa 0 nghĩa là chưa đủ bằng chứng, không phải bằng nhau. Trang 25: giao thức và luật D9 | — |
| **4.3 Kết quả các phương pháp (5)** | Trang 26: bảng test B0/B2/P+F/B2+F/C6 kèm CI. Trang 27–28: phân rã, box đúng/sai class, shared box. Dự phòng: kết quả đầy đủ (39), dev (43), theo loại cặp (46) | Kết quả dev chuyển xuống dự phòng cho đủ thời gian; trang 25 vẫn nêu D9 chọn P+F và MAE dev 3.53 |
| **4.4 Demo, thực nghiệm khác tài liệu tham khảo (5)** | Thực nghiệm khác bài báo: khảo sát FSC-147 (29), gán box theo CLIP (30), đo lỗi X/Y (28). **Demo (cập nhật 25/11 tối): trang 31**, chạy model thật trên ảnh mới (`demo/live/`); bản xem lại kết quả đã lưu chỉ còn là dự phòng | **Đang hoàn thiện:** luồng dán ảnh → chạy → hiện kết quả đã kiểm trên CPU (11/11 bước). **Bản GPU trên Kaggle chưa chạy**: chờ Trí mở phiên Kaggle. Chưa quay video dự phòng |
| **5. Nhận xét và kết luận (5)** | Mục 5, trang 32–35: những điều chưa trả lời được (33), bảng vấn đề → cải tiến → kết quả (34), hướng phát triển (35) | Câu "phạm vi" đã sửa thành "mới kiểm chứng trên ảnh nhiều class, ít đến vừa vật", không suy rộng |
| **6. Slide đầy đủ, dễ hiểu, có đánh số trang (5)** | Mọi trang, kể cả trang chia mục, trang "Cảm ơn" và dự phòng, đều có số x/46 (đã kiểm từng trang bằng `pdftotext`). Đã xem ảnh từng trang | Còn tràn nhẹ ở 2 trang dự phòng có sẵn từ trước (44: chú thích sát chân trang; 46: bảng lệch phải khoảng 0,7 mm). Không ảnh hưởng phần trình bày |
| **7. Hỏi đáp (5)** | Trang 37 "Cảm ơn, mời đặt câu hỏi"; 9 trang dự phòng (38–46); 20 câu hỏi phản biện trong `reports/KE_HOACH_SLIDE_THUYET_TRINH.md` | Do thầy chấm lúc hỏi đáp. Nên tập thêm câu hỏi về trang 20 ("sao không so với DAVE?") và về demo ("có chạy model không?") |

## Thời lượng (theo `[m:ss]` trong ghi chú)

Tổng **25:00**, gồm 1:30 demo. Trí nói 13:50, Triệu 11:10. Người nói từng slide ghi ở đầu mỗi `\note`. Bảng chi tiết: `python final/slides/_tools/timing.py final/slides/main.tex`.

Để giữ trong 25 phút, bốn slide được chuyển xuống dự phòng:
- kết quả dev;
- theo loại cặp;
- ví dụ thành công / lỗi X/Y (demo cho xem trực tiếp);
- ví dụ thất bại (demo cho xem ví dụ dogs).
