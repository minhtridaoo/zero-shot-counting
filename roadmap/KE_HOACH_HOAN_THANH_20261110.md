# Kế hoạch đến khi hoàn thành — cập nhật 10/11/2026

**Repo đã đổi tên:** `github.com/minhtridaoo/zero-shot-counting` (remote local đã trỏ lại). HEAD `e7fb20c`.
**Còn 22 ngày đến hạn 02/12.** Lịch 05/11 đã trễ khoảng 4 ngày ở bước kiểm/khóa dữ liệu. Kế hoạch dưới đây đã dời lịch và vẫn còn 2 ngày đệm.

## 1. Đang ở đâu

```
✅ [1] Chạy CountGD++    ✅ [2] Pilot tìm lỗi    ✅ [3] Cải tiến v1 (lọc + freeze)
✅ [4] Kiểm 10 ảnh mới    ✅ [5] N4 review khung   ✅ [6] Chốt biến thể D1–D10 (05/11)
⏳ [7] Dữ liệu v2: ĐÃ RÚT (05/11, dev 20 + test 40), CHƯA KIỂM 0/60 ảnh, CHƯA KHÓA  ◀── ĐANG Ở ĐÂY
   [8] Chạy dev trên T4 + chấm   [9] Khóa cấu hình v2   [10] Test 1 lần   [11] Báo cáo + slide + nộp
```

Việc đã xong từ 05/11 đến nay:
- Triệu W1: rút dữ liệu.
- Triệu W2: đưa output P1 lên repo. **Assistant đã kiểm độc lập:** Kiểm C trùng tuyệt đối, bảng MAE theo tau khớp từng số, 5 query lệch ở lượt 1 đúng như báo cáo.
- Assistant: `evaluate_research.py` nhận GT `uncertain`; đã kiểm hồi quy CPU. Đã thêm công cụ T / fit S/F riêng nguồn / chọn D9, **10/10 kiểm đạt**, replay raw B2 30 query khớp nguồn. [Kết quả và giới hạn](../reports/ASSISTANT_OFFLINE_V2_20261110.md).

## 1b. Nhánh P / R nằm ở đâu (thêm 10/11 theo câu hỏi của Trí)

| Nhánh | Ý tưởng | Trạng thái |
|---|---|---|
| **P (chính)** | CLIP kiểm mẫu tự chọn trước lượt 2, bỏ mẫu sai loại | Chọn 05/11; code có (Triệu, 03/11); chạy thử pilot chỉ để kiểm code; **chưa thử trên dev** |
| **T (bổ sung)** | Lượt 2 chấm khung chỉ bằng điểm chữ, bỏ điểm mẫu ảnh | Đã có code ngoại tuyến và kiểm CPU 10/11; chưa có kết quả dev v2; P+T thật chờ raw P1 trên Drive |
| **R (dự phòng)** | Sửa bộ lọc cuối để không xóa vật đúng | Không làm; chỉ quay lại nếu P và T đều thua trên dev và còn thời gian (khó kịp trước 02/12) |
| **C6 (đối chứng)** | B0 + bộ lọc, không có lượt 2 | Chạy cùng ở bước [8] |

Vị trí trong pipeline:
- [7] chuẩn bị dữ liệu để thử P;
- [8] chạy P (lưới tau) / T / P+T / C6 trên dev;
- [9] chọn đúng một cách theo luật D9; không cách nào thắng thì là kết quả âm;
- [10] test một lần;
- [11] chương Phương pháp = P (+T); R ghi ở Hướng phát triển.

**Việc kiểm 60 ảnh ở bước [7] đang chặn việc thử nhánh P.**

> **Cập nhật 11/11 (chẩn đoán trên tập đã xem, [chi tiết](../reports/ASSISTANT_CHAN_DOAN_T_C6_20261111.md)):** T giảm thiệt hại của B2 nhưng chưa bằng B0. **C6 (B0 + lọc, chọn lại ngưỡng) là ứng viên duy nhất thắng B0 theo D9** (ngưỡng ≈ 0.34). Khả năng cao luật D9 trên dev sẽ chọn C6, trừ khi P vượt C6. Báo cáo cần định vị đóng góp đúng: lượt 2 gây hại + cơ chế lỗi + hiệu chỉnh 1 lượt / CLIP xác minh, không trình bày như phương pháp mới lớn.

## 2. "Hoàn thành" nghĩa là đủ 6 thứ này

| # | Sản phẩm | Trạng thái |
|---|---|---|
| H1 | **Báo cáo cuối** đủ mục: bài toán X/Y → CountGD++ B0/B2 → pilot + lỗi → cải tiến v1 + kết quả 10 ảnh → N4 + cơ chế lỗi → cải tiến v2 (P/T) trên dev → **kết quả test 40 ảnh** → hạn chế → kết luận | Có khoảng 60% tư liệu; **chưa viết** |
| H2 | **Bảng kết quả test cuối**: chạy một lần, có CI theo ảnh, đủ chỉ số có mặt / vắng mặt | Chưa |
| H3 | **Slide + demo** (ví dụ "hỏi people ra chó", trước/sau cải tiến) | Chưa |
| H4 | **Repo tái lập được**: README chỉ đường từ dữ liệu → lệnh → kết quả; tập dữ liệu và cấu hình đã khóa | Phần lớn đã có |
| H5 | **Pilot đóng**: Trí và Triệu cùng xác nhận (V7) | Trí đã xác nhận 05/11; **Triệu chưa ghi** (W3) |
| H6 | Kết luận trung thực: nếu v2 không thắng B0 theo luật D9 thì báo kết quả âm, kèm phân tích | Luật đã chốt |

## 3. Lịch mới (đường găng in đậm)

| Ngày | Trí | Triệu | Assistant |
|---|---|---|---|
| **10–12/11** | **Kiểm absent/GT dev 20 ảnh** (khoảng 1 giờ) | **Kiểm absent/GT test 40 ảnh** (khoảng 2 giờ); W3 ghi duyệt pilot (10 phút) | Viết công cụ ngoại tuyến: biến thể T + chọn lại ngưỡng S/F riêng từng nguồn + chấm theo luật D9; thử trên raw p4_unseen_v1 có sẵn ở local |
| **12/11** | — | **Khóa dữ liệu** (W5) | Kiểm hash, trạng thái khóa |
| **13–15/11** | — | **Chạy dev trên T4** (W6, khoảng 2–3 giờ GPU) | Chấm theo luật D9, viết báo cáo dev |
| **16/11** | Đọc bảng dev, **khóa cấu hình v2** (khoảng 1 giờ) | — | Viết freeze v2 + audit |
| 16–22/11 | **Viết báo cáo phần 1–5** (khoảng 4 giờ) | Related Work (W7, khoảng 2 giờ) | Dựng bảng/hình từ kết quả có sẵn |
| **23–24/11** | — | **Chạy test một lần** | Chấm + CI |
| 25–29/11 | Viết kết quả + hạn chế, slide, demo (khoảng 5 giờ) | Góp slide; review N4 nhỏ trên test (tùy chọn) | Kiểm số trong báo cáo |
| 30/11–01/12 | Đệm + tập thuyết trình | | |
| **02/12** | **Nộp** | | |

**Thời gian tập trung của Trí còn lại: khoảng 11 giờ.** Cụ thể: 1 giờ (kiểm dev) + 1 giờ (khóa cấu hình) + 4 giờ + 5 giờ (viết) + tập thuyết trình.

## 4. Nếu tiếp tục trễ (chọn sớm, không đợi sát hạn)

| Nếu | Thì |
|---|---|
| 13/11 dữ liệu vẫn chưa khóa | Thu nhỏ còn **dev 15 + test 30**: bỏ ngẫu nhiên có seed (331) 5 ảnh dev và 10 ảnh test **chưa kiểm**, **giữ tỉ lệ loại cặp**, ghi lý do **trước** khi chạy. Kiểm nhanh hơn khoảng 40% |
| 18/11 chưa có bảng dev | Bỏ phần tối ưu tham số, chạy P1 với tau mặc định 0.22 và T, **không chọn tham số** (vẫn công bằng), đi thẳng tới test |
| 24/11 chưa chạy được test | Báo cáo theo hướng **phân tích lỗi** dùng pilot + p4_unseen_v1 + N4 (đã có đủ số liệu), cải tiến v2 ghi là hướng phát triển. **Vẫn nộp được (H1, H3–H6)** |

## 5. Ba việc cần làm ngay

1. **Trí:** nhắn Triệu 3 việc đang trễ:
   - kiểm test 40 ảnh (W4);
   - ghi duyệt pilot (W3);
   - mốc khóa dữ liệu mới là 12/11.
2. **Trí:** kiểm dev 20 ảnh. File `experiments/countgdpp/dev_test_v2/absent_candidates.csv`, lọc cột `split = dev` (20 dòng; 40 dòng `test` là của Triệu). Cách làm như lần p4_unseen_v1 (HUONG_DAN_KIEM_DU_LIEU.md). Nếu lớp absent nhìn thấy trong ảnh thì đổi sang lớp dự phòng, đừng ghi `uncertain`.
3. **Assistant (cập nhật cuối phiên 10/11):** Trí đã cho phép CPU; đã kiểm hồi quy evaluator và chuẩn bị công cụ T / S/F / D9. Tiếp: kiểm P+T thật tại nơi có raw P1; khi W6 có output thì chấm dev. [Hướng dẫn](../experiments/countgdpp/OFFLINE_V2_HUONG_DAN.md). Chưa chọn hoặc khóa cấu hình từ kết quả chẩn đoán.
