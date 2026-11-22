# Kết quả thử nghiệm sơ bộ hướng 1 — gán khung theo CLIP giữa các loại (chỉ dev), 22/11/2026

*Assistant (Claude) chạy và soạn theo yêu cầu của Triệu; Triệu báo Trí đã đồng ý chạy. Khai báo trước: `experiments/xy_clip_assign/KHAI_BAO_TRUOC_XY_CLIP_20261122.md`. Đây là **thử nghiệm sơ bộ trên dev**: không thay kết quả chính, không chạy trên test.*

## 1. Lần chạy

- **Run:** `results/countgdpp/xy_clip_assign_dev_20261122_1755/` (`result.json`, `per_query.csv`, `clip_cosines.json`). Chạy CPU máy Triệu.
- **Hai lần trước dừng vì lỗi kỹ thuật, chưa tính số nào** (ghi ở khai báo §8):
  - stamp `1745`: `torch` 2.2 không nạp được `.bin`, nên chuyển sang nạp `model.safetensors`;
  - stamp `1754`: TensorFlow hỏng, nên tắt bằng `USE_TF=0`.
- **Các bước kiểm (§4 khai báo):** đạt cả ba.
  - hash đầu vào khớp;
  - tái lập đúng MAE dev của P+F 3,5333, B0 6,2833, C6 4,0167;
  - **tái lập CLIP: lệch lớn nhất 1,37e-06** so với điểm tính trên Kaggle, tức bản safetensors cho cùng đầu ra.
- Thời gian tính CLIP: 234 s cho 1.798 khung × 45 tên, trên CPU.

## 2. Kết quả (dev: 20 ảnh, 40 câu có mặt, tổng GT 516 vật; 20 câu vắng mặt)

| Cách | MAE cả 60 | MAE có mặt | FPR vắng mặt | **Khung dùng chung X/Y** | Khung đúng loại | Đếm thừa / thiếu (câu có mặt) |
|---|---:|---:|---:|---:|---:|---|
| P+F (đã khóa) | **3,53** | **5,05** | 0,05 | 61,6% | 70,2% | 76 / 126 |
| P+F+A_Q | 4,62 | 6,92 | 0,00 | **2,9%** | 83,0% | 19 / 258 |
| P+F+A_V | 5,60 | 8,40 | 0,00 | 2,1% | 92,6% | 4 / 332 |
| B0 | 6,28 | 8,25 | 0,20 | 55,3% | 64,0% | 286 / 44 |
| B0+A_Q | 4,27 | 6,40 | 0,00 | 4,0% | 77,5% | 68 / 188 |
| B0+A_V | 4,93 | 7,40 | 0,00 | 1,6% | 88,1% | 12 / 284 |
| C6 | 4,02 | 5,80 | 0,05 | 24,4% | 80,1% | 59 / 173 |
| C6+A_Q | 4,70 | 7,05 | 0,00 | 2,9% | 87,3% | 21 / 261 |
| C6+A_V | 5,32 | 7,97 | 0,00 | 1,9% | 91,8% | 5 / 314 |

**So sánh khai báo trước** (Δ = A − B; CI 95% bootstrap ghép cặp theo 20 ảnh):

| Vai trò | So sánh | Δ khung dùng chung | Δ MAE có mặt | Cách đọc (theo khai báo) |
|---|---|---|---|---|
| **Chính** | **P+F+A_Q − P+F** | **−0,587** [−0,735; −0,404] | **+1,88** [−0,03; +3,73] | **Đánh đổi**: tách X/Y tốt hơn hẳn, nhưng đếm có mặt kém hơn |
| Phụ | B0+A_Q − B0 | −0,512 [−0,649; −0,358] | −1,85 [−4,25; +0,40] | Có dấu hiệu giúp trên dev (cả hai giảm; CI của MAE chứa 0) |
| Phụ | C6+A_Q − C6 | −0,215 [−0,403; −0,020] | +1,25 [−0,47; +3,15] | Đánh đổi |
| Phụ | P+F+A_V − P+F | −0,595 [−0,742; −0,412] | +3,35 [+1,43; +5,65] | Đánh đổi |

## 3. Đọc kết quả

1. **Bước A làm đúng việc nó nhắm tới.** Khung dùng chung giữa X và Y giảm từ khoảng 55–62% xuống **2–4%**, CI không chứa 0 ở mọi cặp. Câu vắng mặt không còn bị báo nhầm (FPR 0). Tỉ lệ khung đúng loại tăng (P+F: 70% → 83%).
2. **Nhưng nó bỏ nhầm cả vật đúng.** Với P+F, bước A bỏ 85 khung sai loại (127 → 42) nhưng cũng bỏ **97 khung đúng loại** (327 → 230). Đếm thiếu vì vậy tăng từ 126 lên 258. Kết quả là MAE câu có mặt **không tốt hơn** P+F.
   - Nguyên nhân thấy được: CLIP chấm trên **ô cắt nhỏ** và các loại **gần nghĩa** (chồng đĩa–bát, quả với quả), nên hay cho một vật đúng là "giống loại khác hơn". Luật "giữ khi giống loại được hỏi nhất" rất chặt: chỉ cần một loại khác nhỉnh hơn là khung bị bỏ.
3. **A_V (45 lớp) chặt hơn A_Q**, nên tách tốt hơn chút nhưng bỏ nhầm nhiều hơn.
4. **Áp A lên cấu hình đã có bộ lọc F thì lọc hai lần,** dẫn tới đếm thiếu. Áp lên B0 (chưa lọc gì) thì cả hai chỉ số đều giảm trên dev. Tuy vậy B0+A_Q (MAE có mặt 6,40) vẫn kém P+F (5,05) và C6 (5,80).
5. **Kết luận sơ bộ:** gán khung theo CLIP **giải được phần "khung dùng chung"** của bài X/Y, nhưng **chưa cải thiện số đếm**, vì CLIP trên ô cắt chưa đủ tin cậy để tách các loại gần nhau. Khớp với hạn chế 5 của báo cáo chính.

## 4. Giới hạn (theo khai báo §6)

- Dev 20 ảnh và đã dùng để chọn F, nên kết quả chỉ mang tính sơ bộ. CI rộng.
- A_Q giả định biết các loại khác được hỏi trên cùng ảnh. A_V dùng danh sách lớp của chính MUCCA.
- Không chạy trên test. Không chỉnh gì sau khi xem kết quả.

## 5. Gợi ý cho Hướng phát triển (chưa thử; chỉ ghi vào báo cáo)

- **Chỉ phân xử khung bị tranh chấp:** áp A **chỉ cho các khung xuất hiện ở cả X và Y**, còn khung không bị tranh chấp thì giữ nguyên. Như vậy vẫn giải được khung dùng chung mà không bỏ vật đúng ở chỗ không có tranh chấp.
- **Luật mềm hơn:** chỉ bỏ khung khi loại khác **vượt rõ** loại được hỏi. Cách này cần một ngưỡng, nên phải chọn trên một tập riêng và kiểm trên tập mới.
- **Bộ kiểm mạnh hơn:** CLIP lớn hơn, cắt có thêm ngữ cảnh.

## 6. Câu đưa vào báo cáo và slide (nháp)

> "Thử nghiệm sơ bộ trên dev: gán mỗi khung cho loại mà CLIP thấy giống nhất làm tỉ lệ khung dùng chung giữa X và Y giảm từ khoảng 60% xuống khoảng 3%. Nhưng CLIP trên ô cắt nhỏ bỏ nhầm cả vật đúng, nên số đếm không tốt hơn cấu hình đã khóa. Hướng tiếp theo là chỉ phân xử những khung bị hai câu hỏi tranh nhau."
