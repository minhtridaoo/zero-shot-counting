# Điểm yếu của kết quả và hướng giải quyết — 22/11/2026

*Trợ lý AI (Claude) soạn theo yêu cầu của Triệu, để Trí xem trước buổi họp tối 22/11. Mọi con số lấy từ kết quả đã kiểm trong repo (nguồn ở cuối file). Phần "Đề xuất" chỉ là gợi ý; Trí và Triệu quyết. **Chưa chạy thử nghiệm nào trong file này.***

---

## 1. Đánh giá chung

**Kết quả trung thực và vững, nhưng mức cải thiện khiêm tốn.** Giá trị lớn nhất của đồ án nằm ở **chẩn đoán lỗi và cách kiểm chứng chặt**, không nằm ở một phương pháp mới mạnh.

**Điểm mạnh (giữ khi trình bày):**
- **Kết quả chính là thật:** P+F giảm MAE 24% so với B0 trên test MUCCA (5,82 so với 7,71; CI [−3,66; −0,44]). Cấu hình khóa trước khi xem test, test chạy một lần, số liệu được tính lại độc lập.
- **Chẩn đoán lặp lại được:** lượt 2 tự chọn mẫu làm CountGD++ kém hơn trên ảnh nhiều loại, thấy ở cả pilot, p4 và test (B2 − B0 +1,90 [+0,81; +3,03]). Nhóm đo được 64% khung dùng chung giữa X và Y, khoảng 1/3 số khung sai loại.
- **Báo cả kết quả âm:** P không giúp gì; thứ hạng dev đảo trên test; T chỉ gỡ khoảng 1/5 tác hại; cấu hình kém hơn trên FSC-147, đúng rủi ro đã khai báo trước.

---

## 2. Năm điểm yếu (nên tự nêu trước khi thầy hỏi)

### Điểm yếu 1: Bài X/Y chưa giải quyết xong

| Chỉ số (test MUCCA, 79 câu có mặt) | B0 | P+F | C6 |
|---|---:|---:|---:|
| MAE câu có mặt | 8,32 | 6,84 | 6,48 |
| MAE / số vật thật trung bình (12,4 vật) | 67% | 55% | 52% |
| Khung dùng chung khi đổi X → Y (IoU ≥ 0,5) | 64% | 59% | 24% |
| Khung rơi vào vật loại khác | 34,6% | 32,7% | 21,3% |

Cải tiến giảm lỗi nhưng chưa xóa được lỗi. Sai số vẫn khoảng một nửa số vật thật. Với P+F, hơn một nửa số khung vẫn dùng chung giữa hai câu hỏi.

*Ghi chú: tỉ lệ MAE / số vật trung bình chỉ là thước đo thô để hình dung độ lớn lỗi.*

### Điểm yếu 2: Phần có tác dụng (F) không mới; ý chính ban đầu (P) không đóng góp

- **Bản theo câu chữ của DAVE** (Pelhan và cộng sự, CVPR 2024) đã dùng CLIP để loại cụm khung không giống câu chữ. Đã đọc mục 3.2–3.4 của bài.
- P chọn lại đúng bộ mẫu của B2 ở 108/120 câu, nên B2+F ≈ P+F (5,70 so với 5,82).
- Ba điểm F khác DAVE:
  1. DAVE quyết định theo cụm khung; F quyết định cho từng khung.
  2. DAVE huấn luyện bộ phát hiện và đặc trưng riêng; F gắn vào CountGD++ có sẵn, không huấn luyện.
  3. F kết hợp điểm CLIP với điểm của chính CountGD++.

### Điểm yếu 3: Cải thiện tập trung ở một số trường hợp

- **Cặp dễ nhầm** (27 ảnh): P+F so với B0 −3,05 [−5,43; −0,96], có cải thiện.
- **Cặp khác hẳn** như người–xe (13 ảnh, đúng ví dụ thầy nêu): +0,51 [−0,72; +1,82], **chưa thấy cải thiện rõ**.
- Khoảng **một nửa** mức giảm tổng sai số của P+F đến từ 40 câu vắng mặt (giảm khoảng 107, so với khoảng 117 ở câu có mặt).

### Điểm yếu 4: Khó dùng ngoài phạm vi (khảo sát FSC-147, 300 ảnh một loại)

| | MAE cả mẫu | Ảnh ≤ 40 vật | Ảnh > 40 vật |
|---|---:|---:|---:|
| B2 | **13,32** | 3,44 | 25,09 |
| P+F | 18,01 | 3,50 | 35,28 |
| C6 | 25,11 | 5,34 | 48,64 |

- P+F kém hơn B2: +4,69 [+2,25; +7,50]. Nguyên nhân là **đếm thiếu ở ảnh dày** (thiếu 4.904 vật so với 2.033), vì ngưỡng F chọn trên ảnh MUCCA 3–40 vật.
- C6 tốt nhất trên MUCCA nhưng kém nhất ở đây.
- Giữ hay bỏ lượt 2 (B0 − B2): +0,55 [−3,00; +4,30], chưa thấy khác biệt rõ.

### Điểm yếu 5: Mẫu nhỏ, cơ chế chưa giải thích hết

- Test chỉ có 40 ảnh; các phân tích theo nhóm cặp chỉ mang tính mô tả.
- Bỏ cách chấm max (T) chỉ gỡ khoảng 1/5 tác hại trên dev (T 8,55, B2 9,15, B0 6,28). Phần còn lại là giả thuyết H2, chưa kiểm.

---

## 3. Hướng giải quyết điểm yếu 1

**Ràng buộc:** tập test đã dùng. Không được chạy cách mới trên test rồi báo như kết quả chính, vì như vậy phá giao thức "chọn trước, xem sau".

| # | Hướng | Ý tưởng | Vì sao có thể giúp | Rủi ro | Chi phí |
|---|---|---|---|---|---|
| 1 | **Gán khung theo CLIP giữa các loại** (ý 2 trong Hướng phát triển) | Với mỗi khung, CLIP chấm điểm giống "a photo of X", "a photo of Y", … rồi gán khung cho loại giống nhất. Hỏi X thì chỉ đếm khung được gán cho X | Nhắm thẳng vào khung dùng chung và khung sai loại. Khác hướng nhóm Hoàng Anh – Duy đã thất bại (họ so điểm CountGD++ giữa các prompt, vốn không cùng thang); điểm CLIP của cùng một khung với nhiều câu thì cùng thang | Cặp quá giống (dê–chó, chồng đĩa–bát) thì CLIP cũng nhầm. Cần danh sách loại để so: các loại được hỏi trong cùng ảnh, hoặc một danh sách cố định | **Thấp:** chạy CPU trên khung đã lưu. Đã kiểm máy Triệu có khung dev, 200 ảnh MUCCA, `transformers` và `torch` |
| 2 | **Câu "không đếm Y"** (prompt âm có sẵn trong CountGD++) | Khi hỏi X, đưa Y vào làm câu chỉ định "không đếm cái này" | Dùng khả năng CountGD++ được thiết kế sẵn; tách X/Y ngay trong mô hình | Chưa biết hiệu quả; phải chạy lại GPU | Trung bình: Kaggle T4 |
| 3 | Bộ kiểm tốt hơn | CLIP bản lớn hơn (ViT-L/14), cắt khung có phần xung quanh, nhiều mẫu câu | CLIP hiện nhầm ở ô cắt nhỏ | Chỉ cải thiện từ từ | Thấp đến trung bình |
| 4 | Huấn luyện lại | Tinh chỉnh với ảnh nhiều loại | Sửa tận gốc | Ít dữ liệu; nhóm Hoàng Anh – Duy tinh chỉnh 1 epoch còn tệ hơn | **Cao, không kịp 02/12** |

**Liên quan điểm yếu 4:** ngưỡng F theo mật độ vật (ý 3 trong Hướng phát triển) sẽ giảm việc lọc quá tay ở ảnh dày. Hướng này để báo cáo, không làm trước 02/12.

### Nếu làm thì báo thế nào

| Cách | Được nói gì | Vấn đề |
|---|---|---|
| a. Chỉ thử trên **dev** | "Thử nghiệm sơ bộ trên dev cho thấy…" | Dev đã dùng để chọn cấu hình, nên số lạc quan. Chỉ đủ làm minh chứng cho Hướng phát triển |
| b. Dựng **tập test mới** từ khoảng 125 ảnh MUCCA chưa dùng | Kiểm chứng thật | Phải chọn cặp và người kiểm như W4/W5, khoảng 1–2 ngày công; ảnh có cặp khác hẳn còn rất ít |
| c. Chạy trên test cũ | "Hậu kiểm trên test đã xem" | Yếu, dễ bị coi là chọn theo kết quả. **Không nên** |

---

## 4. Đề xuất

1. **Không đổi kết quả chính.** Còn 10 ngày; báo cáo cuối và slide là ưu tiên.
2. **Tùy chọn, nếu Trí đồng ý** (AGENTS.md quy tắc 4): làm **hướng 1 theo cách a**:
   - thử nhỏ trên dev, chạy CPU, khoảng nửa ngày;
   - **khai báo trước** như khảo sát FSC-147: chỉ số chính là tỉ lệ khung dùng chung X/Y và MAE câu có mặt;
   - đưa vào mục "Hướng phát triển — thử nghiệm sơ bộ", ghi rõ là số trên dev.

   Giảm được khung dùng chung thì nhóm có câu trả lời cụ thể cho "bước tiếp theo là gì". Không giảm thì cũng biết CLIP chưa đủ, và ghi lại trung thực.
3. **Cách trình bày.** Không nói "nhóm đề xuất phương pháp mới giúp CountGD++ đếm đúng loại". Nên nói:
   > "Nhóm tìm ra và đo được vì sao CountGD++ đếm nhầm loại trên ảnh nhiều loại. Nhóm cho thấy một bước lọc đơn giản, không cần huấn luyện, giảm lỗi 24% trong đúng phạm vi đó, kiểm bằng giao thức khóa trước, và chỉ ra rõ nó chưa làm được gì."

## 4b. Cập nhật 22/11 (khuya): đã thử hướng 1 trên dev

Sau khi Triệu báo Trí đồng ý, assistant chạy thử nghiệm theo bản khai báo `experiments/xy_clip_assign/KHAI_BAO_TRUOC_XY_CLIP_20261122.md`. Kết quả chi tiết ở `reports/XY_CLIP_ASSIGN_DEV_KET_QUA_20261122.md`.
- **Khung dùng chung X/Y:** 61,6% → **2,9%**. Câu vắng mặt không còn bị báo nhầm.
- **MAE câu có mặt:** 5,05 → 6,92 (+1,88 [−0,03; +3,73]). Đọc theo khai báo: **đánh đổi**.
- Nguyên nhân: CLIP trên ô cắt nhỏ bỏ nhầm khoảng 30% khung đúng loại.
- Hướng tiếp (chưa thử): chỉ phân xử các khung bị X và Y tranh nhau.

## 5. Cần Trí quyết

| # | Câu hỏi | Lựa chọn |
|---|---|---|
| T1 | Có làm thử nghiệm sơ bộ hướng 1 trên dev không? | Làm (nửa ngày, CPU) / Chỉ ghi vào Hướng phát triển |
| T2 | Có nêu 5 điểm yếu trong slide "Hạn chế" (S15) như trên không? | Đồng ý / Rút gọn |
| T3 | Có đồng ý cách trình bày ở đề xuất 3 không? | Đồng ý / Sửa |

---

**Nguồn số liệu:**
- `reports/KET_QUA_TEST_CUOI_20261111.md`
- `reports/TRIEU_W8_TEST_20261111.md`
- `reports/PHAN_TICH_HAU_KIEM_TEST_20261111.md` (khung dùng chung, khung sai loại)
- `reports/BAO_CAO_CHI_TIET_DO_AN_20261112.md` mục 7.2–7.4 (theo loại cặp; P trùng B2 ở 108/120 câu)
- `reports/DEV_V2_D9_KET_QUA_20261111.md`
- `reports/TRIEU_FSC147_KHAO_SAT_20261122.md`
- `reports/RELATED_WORK_TRIEU_20261122.md` (DAVE)
- Tỉ lệ MAE / số vật trung bình và phần đóng góp của câu vắng mặt: assistant tính 22/11 từ manifest và `result.json` đã khóa.
