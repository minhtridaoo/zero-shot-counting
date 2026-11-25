# Rà slide theo phiếu chấm + kế hoạch dựng demo Gradio (25/11/2026)

> **Đã triển khai tối 25/11:**
> - slide sắp lại theo phiếu: [DOI_CHIEU_PHIEU_CHAM_SLIDE_20261125.md](DOI_CHIEU_PHIEU_CHAM_SLIDE_20261125.md);
> - demo tầng A: [demo/README.md](../demo/README.md).
>
> Khác plan ở một điểm: tab 3 **không** hiện MAE toàn test theo thanh trượt, tránh việc chọn lại ngưỡng trên test. Bản dưới đây là kế hoạch gốc.

Assistant soạn theo yêu cầu của Trí. **Chỉ là đề xuất.** Chưa sửa `final/slides/main.tex`, chưa viết code demo, chưa chạy gì.

Nguồn: phiếu chấm `PhieudanhgiaMonhoc.pdf` (Trí gửi), `final/slides/main.tex` tại commit `974048f`.

**Lưu ý của Trí:** thứ tự trình bày phải đi **đúng 1 → 7 theo phiếu**, nếu không sẽ bị trừ điểm.

---

## 1. Phiếu chấm (100 điểm)

| STT | Nội dung | Điểm |
|---|---|---|
| 1 | Lý do, cơ sở thực hiện đề tài | 5 |
| 2.1 | Phát biểu bài toán | 15 |
| 2.2 | Hình minh họa cho bài toán | 5 |
| 3 | Phương pháp: dễ hiểu, **làm nổi bật điểm khác biệt so với phương pháp khác** | **30** |
| 4.1 | Thực nghiệm: mô tả dataset | 10 |
| 4.2 | Thực nghiệm: độ đo | 10 |
| 4.3 | Thực nghiệm: kết quả các phương pháp | 5 |
| 4.4 | Thực nghiệm: **có chương trình demo**, có thực nghiệm khác tài liệu tham khảo | 5 |
| 5 | Nhận xét và kết luận | 5 |
| 6 | Slide đầy đủ, dễ hiểu, **có đánh số trang** | 5 |
| 7 | Hỏi đáp | 5 |

## 2. Slide hiện tại so với phiếu

| Phiếu | Slide hiện có (số trang theo bản 974048f) | Đánh giá | Cần sửa |
|---|---|---|---|
| — | 1 Bìa, 2 Nội dung, **3 Phân công** | Slide Phân công nằm **trước mục 1** | **Chuyển Phân công xuống cuối**, trước slide "Cảm ơn" (hoặc bỏ khỏi phần nói, để dự phòng). Như vậy sau mục lục là vào mục 1 ngay |
| 1 | Bối cảnh · Khoảng trống · Related work | Đủ | Giữ |
| 2.1 | Định nghĩa input/output · Câu hỏi nghiên cứu | Đủ nội dung, **nhưng slide RQ đứng sau slide Minh họa** (2.2), tức 2.1 bị tách làm hai | **Đổi thứ tự:** Định nghĩa → RQ + đóng góp → Minh họa mcac_12 |
| 2.2 | Minh họa mcac_12 (plates/bowls/spoons) | Tốt | Giữ, đặt làm slide cuối của mục 2 |
| 3 (30đ) | Baseline · 3 vấn đề · VĐ1–VĐ3 · P · F · Tổng thể | Phần trình bày dễ hiểu. **Phần so sánh với phương pháp khác lại nằm ở mục 1** (slide Related work), mục 3 không có slide nói rõ điểm khác biệt | **Thêm 1 slide cuối mục 3: "Điểm khác biệt so với các phương pháp khác"**: bảng PseCo / VA-Count / DAVE / CountGD++ gốc / Đồ án theo các cột: có huấn luyện không · kiểm exemplar · kiểm từng box hay từng cụm · cần dữ liệu nhãn không · dùng được cho mô hình có sẵn không. Slide Related work ở mục 1 rút lại chỉ còn "khoảng trống" |
| 4.1 (10đ) | 1 slide "Dữ liệu: MUCCA, bốn tập" | Chỉ có 1 slide cho 10 điểm. **FSC-147 (300 ảnh) và FSCD-147 (benchmark) chưa được mô tả ở đây**, chỉ nhắc ở chỗ khác | Tách thành 2 slide: (a) MUCCA: nguồn, 200 ảnh, số class, cách chia 4 tập, present/absent, phân bố số vật; (b) bảng tổng **mọi dataset đã dùng** (FSCD-147 kiểm môi trường, MUCCA, FSC-147 300 ảnh), ghi rõ dùng để làm gì. **Kiểm lại chú thích ảnh "chó–dê"** (mcac_171): 24/11 Triệu đã sửa "dê" thành **cừu** ở chỗ khác |
| 4.2 (10đ) | Khối "Chỉ số" trong slide "Giao thức" | Độ đo bị gộp chung với giao thức, nhìn như ý phụ | **Tách slide riêng "Độ đo đánh giá"**: MAE (chính), RMSE, MAE present, FPR_absent, tỉ lệ box dùng chung X/Y (IoU ≥ 0.5), CI bootstrap theo ảnh. Mỗi độ đo có công thức, 1 câu "vì sao cần", 1 ví dụ số nhỏ. Slide Giao thức giữ phần quy trình + D9. Thứ tự: Dataset → Độ đo → Giao thức → Kết quả |
| 4.3 | Dev · Test · Phân rã · Khung · Theo cặp · 2 ví dụ | Đủ | Giữ |
| 4.4 | FSC-147 300 ảnh · Hướng thử thêm (gán khung CLIP) | "Thực nghiệm khác tài liệu tham khảo" đã có. **Chưa có demo** | Thêm **slide "Demo"** (ảnh chụp giao diện + link/QR) và **demo trực tiếp** ngay sau slide này (mục 3 dưới). Thêm 1 dòng ở slide FSC-147: "thực nghiệm này không có trong bài báo CountGD++" |
| 5 | Chưa trả lời được · Kết luận · Hướng phát triển | Đủ | Đổi tên mục 5 thành **"Nhận xét và kết luận"** cho khớp phiếu |
| 6 | Footline có `số trang/tổng` | Đã có số trang | Sau khi chuyển slide, biên dịch lại và kiểm số trang hiện ở mọi slide (kể cả slide chia mục) |
| 7 | Slide "Cảm ơn" + 4 slide dự phòng + 20 câu hỏi trong `KE_HOACH_SLIDE_THUYET_TRINH.md` | Tốt | Thêm 1 slide dự phòng "Demo không chạy được thì xem video" |

**Đổi tên mục (mục lục) cho khớp phiếu:**

1. Lý do thực hiện đề tài
2. Phát biểu bài toán (đang là "Mô tả bài toán")
3. Phương pháp giải quyết
4. Thực nghiệm
5. Nhận xét và kết luận (đang là "Giới hạn và kết luận")

**Thời lượng:** thêm 3 slide (khác biệt, độ đo, demo) thì tăng khoảng 2,5 phút, cộng 1,5–2 phút demo trực tiếp. Để giữ trong 25 phút, gộp 2 slide ví dụ (24–25) thành 1 và rút slide "Theo loại cặp" xuống dự phòng.

**Phân công gợi ý:** Trí nói slide khác biệt (cuối mục 3, phần Trí) và demo (Trí dựng). Triệu nói 2 slide dataset + độ đo (phần Triệu).

---

## 3. Kế hoạch dựng demo Gradio

### 3.1 Điều kiện thực tế (đã kiểm 25/11)

- Máy Trí: RTX A2000 **4 GB**, Windows. CountGD++ cần detectron2 và extension biên dịch trên Linux, **chưa có checkpoint `.pth` ở local**. Ghi chú cài đặt cũ ghi "4 GB chưa kiểm chứng". → **Không chạy model trực tiếp trên laptop.**
- Đầu ra thật của lần chạy test có sẵn: `results/countgdpp/p1_test_kaggle_t4_20261111_1430_offline/bundle.json` (B0, B2, P τ0.20). Mỗi query có `boxes`, `scores` (CountGD++), `clip` (cosine). Dev cũng có bundle tương tự.
- Cấu hình F đã khóa: `results/countgdpp/freeze_v2_20261111.json` (bounds + threshold 0.604).
- Ảnh MUCCA có ở checkout gốc: `D:\MINHTRIHOCCODE\HOCKI5\CS331\data_external\...\images` (200 ảnh, không có trong worktree).
- Chưa cài `gradio`.

### 3.2 Hai tầng demo

| Tầng | Là gì | Chạy ở đâu | Rủi ro | Đề xuất |
|---|---|---|---|---|
| **A. Demo xem lại (bắt buộc)** | Chọn ảnh test + query → xem box và số đếm của **B0 / B2 / P+F / C6** cạnh nhau, so với GT. Bật "so 2 query cùng ảnh" để thấy box dùng chung X/Y. Kéo thanh threshold F để thấy đếm thừa → đếm thiếu | Laptop, **CPU**, không cần mạng | Rất thấp | **Làm** |
| **B. Demo chạy thật (tùy chọn)** | Tải ảnh bất kỳ + gõ 2 tên class → chạy CountGD++ B0 và P+F trực tiếp | Kaggle/Colab T4, `share=True` | Mạng, phiên GPU hết hạn, cài lâu | Làm nếu còn thời gian sau khi A xong; **quay video dự phòng** |

Tầng A dùng đúng output đã chấm, nên số trên demo **khớp bảng kết quả test** (P+F 5.82, B0 7.71). Đây là điểm mạnh khi bị hỏi. Phải nói rõ trên giao diện: "Kết quả lưu từ lần chạy test 11/11, không chạy lại model".

### 3.3 Tầng A: thiết kế

File mới (không sửa file có hash): `demo/app_replay.py`, `demo/README.md`.

```
python demo/app_replay.py --data-root D:\MINHTRIHOCCODE\HOCKI5\CS331
```

Giao diện gồm 3 tab:

1. **So sánh phương pháp**
   - Dropdown ảnh (40 ảnh test, tên kèm cặp class); radio chọn query (3 query/ảnh, ghi present/absent).
   - 4 ảnh lưới B0 · B2 · P+F · C6, vẽ box, tiêu đề "đếm = n (GT = m, sai = |n−m|)".
2. **Lỗi X/Y**
   - Chọn 2 query cùng ảnh. Vẽ box query X màu xanh, query Y màu cam, box trùng (IoU ≥ 0.5) màu đỏ.
   - In tỉ lệ box dùng chung cho B0 và P+F.
   - Ví dụ mặc định: mcac_12 plates/bowls.
3. **Bộ lọc F**
   - Thanh threshold (mặc định 0.604 đã khóa) và trọng số CountGD/CLIP (mặc định 0.5/0.5).
   - Đổi thì đếm lại ngay và hiện MAE toàn test.
   - Ghi rõ: "chỉ để minh họa, cấu hình báo cáo là giá trị khóa".

Logic:
- Đọc bundle + freeze + `test/manifest.csv`.
- `F = 0.5·norm(score, bounds.countgd) + 0.5·norm(clip, bounds.clip)`, giữ box khi F ≥ threshold.
- P+F = nguồn `tau0.200` + F; C6 = `B0` + F; B2 lấy thẳng.
- Kiểm khi khởi động: tính lại MAE test của P+F / B0 / C6 / B2 phải ra **5.82 / 7.71 / 4.63 / 9.61**. Sai thì dừng, báo lỗi.
- Đếm B0/B2 phải theo đúng ngưỡng của runner. Cần đọc `apply_freeze_v2.py` và `counts_for` để làm giống hệt.

### 3.4 Các bước (ước lượng)

| # | Việc | Ai | Thời gian |
|---|---|---|---|
| 1 | Trí đồng ý plan + cho phép cài `gradio` vào môi trường Python của máy | Trí | 5 phút |
| 2 | Viết `demo/app_replay.py` + README, phần tự kiểm MAE | Assistant | khoảng 1 giờ |
| 3 | Chạy app ở local, kiểm 4 số MAE khớp, chụp màn hình | Assistant (sau khi Trí cho chạy) | 15 phút |
| 4 | **Trí test:** thử 3 ví dụ đã chọn cho thuyết trình (mcac_12 bowls; 1 ví dụ thành công; 1 ví dụ thất bại), báo lỗi giao diện | Trí | 20 phút |
| 5 | Thêm slide "Demo" (ảnh chụp + cách chạy), slide dự phòng video | Assistant soạn, Trí duyệt | 20 phút |
| 6 | Quay video 60–90 giây (OBS hoặc Xbox Game Bar `Win+Alt+R`) làm dự phòng | Trí | 15 phút |
| 7 | (Tùy chọn) Tầng B trên Kaggle: notebook mới gọi `app.py` gốc + bước P/F; `share=True`; quay video | Assistant soạn, Trí chạy | nửa ngày |

**Kịch bản demo trực tiếp (khoảng 1:30):**
1. Mở mcac_12, query "bowls": B0 đếm khoảng 36, GT 3. P+F giảm mạnh.
2. Sang tab X/Y: plates và bowls dùng chung gần hết box → đây là VĐ1.
3. Tab F: kéo threshold lên thì đếm thừa giảm, nhưng bắt đầu đếm thiếu → đúng với kết luận "F đổi đếm thừa thành đếm thiếu".

### 3.5 Lịch đề xuất (hạn nộp 02/12)

| Ngày | Việc |
|---|---|
| 25/11 | Trí duyệt plan → assistant viết demo A |
| 26/11 | Trí test demo; assistant sửa slide theo mục 2 (thứ tự, 3 slide mới, đổi tên mục) |
| 27/11 | Trí + Triệu duyệt slide mới, biên dịch PDF; quay video demo |
| 28/11 | (Tùy chọn) demo B trên Kaggle |
| 29–30/11 | Tập 2 lượt **đúng thứ tự 1 → 7**, bấm giờ |
| 01/12 | Đệm |
| 02/12 | Nộp |
