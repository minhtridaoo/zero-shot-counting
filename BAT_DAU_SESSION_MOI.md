# Bắt đầu phiên mới — trạng thái CS331

**Cập nhật 10/11/2026; 11/11: Triệu ghi duyệt pilot (W3), pilot đã đóng.**
- Kế hoạch đầy đủ: [roadmap/KE_HOACH_HOAN_THANH_20261110.md](roadmap/KE_HOACH_HOAN_THANH_20261110.md).
- Nhật ký: [WORKLOG.md](WORKLOG.md). Bản đồ thư mục: [README.md](README.md).
- Bản cũ của file này (nhiều lớp cập nhật chồng nhau): `quá khứ/2026-11-10_don_dep/BAT_DAU_SESSION_MOI_cu.md`.

## Đang ở đâu

```
✅ [1] Chạy CountGD++    ✅ [2] Pilot tìm lỗi    ✅ [3] Cải tiến v1 (lọc + freeze)
✅ [4] Kiểm 10 ảnh mới    ✅ [5] N4 review khung   ✅ [6] Chốt nhánh P + T, D1–D10 (05/11)
⏳ [7] Dữ liệu v2: đã rút dev 20 + test 40 (05/11), KIỂM 0/60 ảnh, CHƯA KHÓA   ◀── ĐANG Ở ĐÂY
   [8] Chạy dev trên T4: P (lưới tau), T, P+T, C6 → [9] chọn 1 cách theo luật D9, khóa cấu hình
   [10] Test 1 lần trên 40 ảnh → [11] Báo cáo + slide + nộp 02/12
```

**Nhánh P** (CLIP kiểm mẫu trước lượt 2) đã có code và đã kiểm trên pilot; chưa thử thật vì dữ liệu chưa khóa. **Nhánh R** chỉ để dự phòng. Chi tiết ở mục 1b của file kế hoạch.

## Việc ngay tiếp theo

| Ai | Việc | Hạn |
|---|---|---|
| **Trí** | Kiểm absent/GT **20 ảnh dev**: `experiments/countgdpp/dev_test_v2/absent_candidates.csv`, lọc `split = dev`. Lớp absent mà nhìn thấy trong ảnh thì đổi sang lớp dự phòng, **không** ghi `uncertain`. Hướng dẫn: `experiments/countgdpp/dev_test_v2/HUONG_DAN_KIEM_V2.md`; ảnh chấm GT: `render_gt_review_v2.py --split dev` (11/11) | 12/11 |
| **Triệu** | Kiểm absent/GT **40 ảnh test** (W4, đang trễ), khóa dữ liệu (W5). W3 đã xong 11/11 | 12/11 |
| **Triệu** | Chạy dev trên T4 (W6), theo [HANDOFF/GIAO_VIEC_TRIEU_20261106.md](HANDOFF/GIAO_VIEC_TRIEU_20261106.md) | 13–15/11 |
| **Assistant** | Chờ Trí cho phép chạy thử CPU: (a) kiểm hồi quy `evaluation/evaluate_research.py` (đã sửa để nhận `uncertain`, chưa chạy thử); (b) viết công cụ ngoại tuyến cho biến thể T, chọn lại ngưỡng S/F riêng từng nguồn, chấm theo luật D9 | trước 13/11 |

## Quy tắc cần nhớ

- Assistant hỏi Trí trước khi chạy evaluator/model/thực nghiệm. Đọc file, viết code/tài liệu thì làm luôn.
- **Không sửa** dữ liệu đã khóa (`p4_unseen_v1`), freeze (`results/countgdpp/p4_candidate_freeze_20261021.json`), prediction gốc, hay file `.py` đã ghi hash trong audit.
- Test chỉ chạy **một lần**, sau khi khóa cấu hình. Không chỉnh tham số theo kết quả test.
- Sau mỗi lượt làm việc: cập nhật WORKLOG + file này.

## Câu mở phiên mới

> Tiếp tục CS331 tại D:\MINHTRIHOCCODE\HOCKI5\CS331. Đọc AGENTS.md, BAT_DAU_SESSION_MOI.md và mục mới nhất của WORKLOG.md; kiểm Git (remote zero-shot-counting) rồi làm tiếp việc đầu tiên chưa xong.
