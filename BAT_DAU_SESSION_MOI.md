# Bắt đầu phiên mới — trạng thái CS331

**Cập nhật 10/11/2026; 11/11: Triệu ghi duyệt pilot (W3), pilot đã đóng; Triệu kiểm xong 40 ảnh test (W4).**

> **t37_1 đã chốt 11/11:** Trí chọn đánh `uncertain`, loại khỏi chấm (3 bút chì bị MUCCA gán `pens`); đã áp trước khi Triệu khóa. Trí cũng đã khóa ở máy mình nhưng chưa push: **khi pull sẽ xung đột `selection_meta.json`/`test/manifest.csv`; bản trên GitHub đã có quyết định này**. Xem [TRIEU_W4_KIEM_TEST_20261111.md](reports/TRIEU_W4_KIEM_TEST_20261111.md) mục 3.
- Kế hoạch đầy đủ: [roadmap/KE_HOACH_HOAN_THANH_20261110.md](roadmap/KE_HOACH_HOAN_THANH_20261110.md).
- Nhật ký: [WORKLOG.md](WORKLOG.md). Bản đồ thư mục: [README.md](README.md).
- Bản cũ của file này (nhiều lớp cập nhật chồng nhau): `quá khứ/2026-11-10_don_dep/BAT_DAU_SESSION_MOI_cu.md`.

**Đồng bộ Git 11/11:** đã gộp cc5510b với c572c04, giữ cả hai đóng góp. Pilot đã đóng; dev đã kiểm xong. Triệu tiếp W4/W5 và W6; hướng dẫn kiểm test: [HUONG_DAN_KIEM_V2](experiments/countgdpp/dev_test_v2/HUONG_DAN_KIEM_V2.md).

## Đang ở đâu

```
✅ [1] Chạy CountGD++    ✅ [2] Pilot tìm lỗi    ✅ [3] Cải tiến v1 (lọc + freeze)
✅ [4] Kiểm 10 ảnh mới    ✅ [5] N4 review khung   ✅ [6] Chốt nhánh P + T, D1–D10 (05/11)
⏳ [7] Dữ liệu v2: đã rút dev 20 + test 40 (05/11), dev đã kiểm 20/20; test chờ kiểm, CHƯA KHÓA   ◀── ĐANG Ở ĐÂY
   [8] Chạy dev trên T4: P (lưới tau), T, P+T, C6 → [9] chọn 1 cách theo luật D9, khóa cấu hình
   [10] Test 1 lần trên 40 ảnh → [11] Báo cáo + slide + nộp 02/12
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

## Việc ngay tiếp theo

| Ai | Việc | Hạn |
|---|---|---|
| **Trí** | ✅ Đã xong kiểm 20 ảnh dev (11/11). Tiếp: chờ bảng dev từ W6 để chọn cấu hình theo D9 (khoảng 1 giờ); bắt đầu dàn ý báo cáo | 16/11 |
| **Triệu** | W3, W4 đã xong 11/11 (test 40 ảnh: 13 `needs_review`, t37_3 đổi sang cups; [báo cáo](reports/TRIEU_W4_KIEM_TEST_20261111.md)). **W5 đã khóa 11/11** (`selection_meta.json` LOCKED, có hash 6 file) | 12–13/11 |
| **Triệu** | ✅ **W6 xong 11/11** (Kaggle T4, stamp 20261111_1203: Kiểm A, Kiểm C 60/60 đạt; output nhỏ ở `results/countgdpp/p1_dev_kaggle_t4_20261111_1203_*`, raw trên Kaggle). Trước đó: **W6 chạy trên Kaggle T4** bằng `experiments/countgdpp/kaggle_p1_dev.ipynb` (11/11, thay Colab; test sau này cũng phải chạy Kaggle T4). Nội dung cũ: **W6 chạy dev trên T4: được bắt đầu ngay** (dev đã chốt nội dung), song song với W4. Nhớ chạy `p1_controls.py` (để có C6) và giữ raw `.npz` trên Drive | 12–15/11 |
| **Assistant** | Đã xong: công cụ T/S/F/D9 (10/10 kiểm đạt, 10/11); chẩn đoán T + C6 trên p4_unseen_v1 (11/11, [kết quả](reports/ASSISTANT_CHAN_DOAN_T_C6_20261111.md)). Tiếp: chấm W6 bằng `select_offline_v2.py` khi dev đã khóa và có output (cần raw P1 trên Drive để tính P+T) | sau W6 |


**Giải thích thao tác (10/11):** kiểm absent/GT là xem ảnh gốc để xác nhận nhãn đầu vào dùng chấm, không review output model. Đã đọc bảng: dev vẫn 20 PENDING; có thể bắt đầu mcac_9 (plates=12, cups=4, forks dự kiến vắng mặt). Chưa có xác nhận nhãn mới.

## Quy tắc cần nhớ

- Assistant hỏi Trí trước khi chạy evaluator/model/thực nghiệm. Đọc file, viết code/tài liệu thì làm luôn.
- **Không sửa** dữ liệu đã khóa (`p4_unseen_v1`), freeze (`results/countgdpp/p4_candidate_freeze_20261021.json`), prediction gốc, hay file `.py` đã ghi hash trong audit.
- Test chỉ chạy **một lần**, sau khi khóa cấu hình. Không chỉnh tham số theo kết quả test.
- Sau mỗi lượt làm việc: cập nhật WORKLOG + file này.

## Câu mở phiên mới

> Tiếp tục CS331 tại D:\MINHTRIHOCCODE\HOCKI5\CS331. Đọc AGENTS.md, BAT_DAU_SESSION_MOI.md và mục mới nhất của WORKLOG.md; kiểm Git (remote zero-shot-counting) rồi làm tiếp việc đầu tiên chưa xong.
