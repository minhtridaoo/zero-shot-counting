# Khai báo trước — thử nghiệm sơ bộ "gán khung theo CLIP giữa các loại" (hướng 1), chỉ trên dev

**Soạn:** assistant (Claude) theo yêu cầu của Triệu, 22/11/2026. Nguồn ý tưởng: `reports/TRIEU_DIEM_YEU_VA_HUONG_GIAI_QUYET_20261122.md` mục 3, hướng 1.

**Trạng thái:**
- Bản khai báo và script đã soạn xong. **Chưa chạy model, chưa có kết quả.**
- **22/11 (khuya): Triệu báo Trí đã đồng ý chạy** (AGENTS.md quy tắc 4). Assistant chỉ ghi lại lời Triệu chuyển; không ký thay Trí.
- Mốc cứng: chưa xong trước **tối 24/11** thì bỏ, chỉ ghi vào Hướng phát triển.

---

## 1. Câu hỏi

Với mỗi khung được giữ, nếu CLIP thấy khung đó **giống một loại khác hơn** loại được hỏi thì bỏ khung. Làm vậy có giảm được việc **hỏi X mà trả về khung của Y** không? Cụ thể: giảm tỉ lệ khung dùng chung giữa X và Y, và giảm MAE câu có mặt.

Đây là **thử nghiệm sơ bộ trên dev**:
- **Không thay kết quả chính** (test MUCCA 11/11) và không chạy trên test.
- Dev đã dùng để chọn cấu hình F, nên các số trên dev **lạc quan**.
- Kết quả chỉ đưa vào mục "Hướng phát triển — thử nghiệm sơ bộ".

## 2. Dữ liệu (chỉ đọc, đã khóa)

| Mục | Tệp | sha256 |
|---|---|---|
| Dev manifest (20 ảnh, 60 câu: 40 có mặt, 20 vắng mặt) | `experiments/countgdpp/dev_test_v2/dev/manifest.csv` | `52d3f667bcd1…` |
| Khung + điểm CountGD++ + CLIP theo đúng câu hỏi (B0, tau0.200) | `results/countgdpp/p1_dev_kaggle_t4_20261111_1203_m5_offline_T/bundle.json` | `651a01c140c9…` (trùng `provenance.bundle_sha256` của freeze) |
| Freeze v2 (cấu hình F đã khóa) | `results/countgdpp/freeze_v2_20261111.json` | `64e89ef53eab…` |
| Ảnh + điểm GT MUCCA (chỉ dùng cho chỉ số "khung sai loại") | `MUCCA_1.0/images/`, `annotations.json` | annotations `95d9908c367d…` |
| Danh sách 45 lớp MUCCA | `MUCCA_1.0/class_mapping.json` | `4a9daeaef21b…` |

**Không dùng GT để quyết định giữ hay bỏ khung.** GT chỉ dùng để chấm.

## 3. Cách làm (bước A, không có tham số nào để chỉnh)

1. Lấy các khung mà cấu hình gốc giữ lại, dùng đúng khung đã lưu, không chạy lại CountGD++.
2. Cắt từng khung từ ảnh gốc bằng `crop_box` của `p4_clip_score.py` (chỉ import, không sửa).
3. CLIP như cũ: `openai/clip-vit-base-patch32`, revision `3d74acf9a28c…`, mẫu câu "a photo of {loại}", cosine đã chuẩn hóa, batch 2, chạy CPU.
4. Với khung *b* của câu hỏi *q*, tính cosine của *b* với mọi tên trong **tập loại K(q)**.
5. **Giữ *b* khi và chỉ khi cosine với *q* ≥ cosine với mọi loại khác trong K(q)** (bằng nhau thì giữ). Không có ngưỡng nào phải chọn.

**Hai tập loại:**

| Ký hiệu | K(q) | Ý nghĩa |
|---|---|---|
| **A_Q** (chính) | Tên của **các câu hỏi trên cùng ảnh** (X, Y, Z: ba tên được hỏi, không dùng GT) | Tình huống người dùng hỏi nhiều loại trên một ảnh, đúng như bài X/Y |
| A_V (phụ) | **45 tên lớp MUCCA** ∪ {q} | Không cần biết người dùng hỏi gì khác; dùng một danh sách cố định |

**Cấu hình gốc được áp A:**
- P+F (cấu hình đã khóa);
- B0;
- C6 = B0+F.

F dùng nguyên bounds và ngưỡng trong freeze.

## 4. Kiểm trước khi tin kết quả (không đạt thì dừng, không báo số)

1. Hash của các tệp ở mục 2 khớp bảng trên.
2. **Tái lập cấu hình gốc:** MAE dev của P+F, B0, C6 tính từ bundle phải bằng số trong freeze (3,5333; 6,2833; 4,0167), sai khác < 1e-9.
3. **Tái lập điểm CLIP:** cosine với đúng câu hỏi, tính lại trên CPU, phải khớp cột `clip` trong bundle (tính trên Kaggle T4). Lệch lớn nhất < 1e-3, cùng ngưỡng với Kiểm A.

## 5. Chỉ số và so sánh (đặt trước)

**Chỉ số:**
- **Tỉ lệ khung dùng chung X/Y** (IoU ≥ 0,5, gộp theo cách của `evaluation/test_xy_overlap_analysis.py`);
- **MAE câu có mặt**;
- MAE cả 60 câu; FPR_absent; tổng đếm thừa / đếm thiếu ở câu có mặt;
- tỉ lệ khung đúng loại / chỉ loại khác / không trúng (phép kiểm điểm trong khung, vốn dễ dãi).

**So sánh** (Δ = A − B; CI 95% bootstrap ghép cặp theo ảnh, 5.000 lần, seed 331; dev chỉ có 20 ảnh nên CI sẽ rộng):

| Vai trò | So sánh | Chỉ số |
|---|---|---|
| **Chính** | **P+F+A_Q − P+F** | (a) tỉ lệ khung dùng chung X/Y; (b) MAE câu có mặt |
| Phụ | B0+A_Q − B0 | như trên |
| Phụ | C6+A_Q − C6 | như trên |
| Phụ | P+F+A_V − P+F | như trên |

**Cách đọc (đặt trước):**
- "Có dấu hiệu giúp" chỉ khi **cả hai** đều giảm: tỉ lệ khung dùng chung **và** MAE câu có mặt (so ước lượng điểm). Ghi kèm CI.
- Một chỉ số giảm, chỉ số kia tăng: báo "đánh đổi", nói rõ chiều nào.
- Không giảm: báo "không thấy giúp trên dev".
- Dù kết quả thế nào: **không** chuyển thành cấu hình chính, **không** chạy trên test, **không** chỉnh gì rồi chạy lại.

## 6. Giới hạn diễn giải (ghi nguyên vào báo cáo)

- Dev 20 ảnh và đã dùng để chọn F, nên kết quả lạc quan và chỉ mang tính sơ bộ.
- A_Q giả định biết các loại khác được hỏi trên cùng ảnh. A_V dùng danh sách lớp của chính MUCCA, nên dễ hơn so với thực tế mở.
- CLIP trên ô cắt nhỏ, loại gần nghĩa (dê–chó, chồng đĩa–bát) có thể vẫn nhầm.

## 7. Lệnh (từ thư mục gốc CS331; chỉ chạy sau khi Trí đồng ý)

```bash
# Kiểm đầu vào, không tải hay chạy CLIP
python experiments/xy_clip_assign/xy_clip_assign_dev.py --mucca <MUCCA_1.0> --check-only
# Chạy một lần (CPU, vài phút; lần đầu cần tải CLIP khoảng 600 MB)
python experiments/xy_clip_assign/xy_clip_assign_dev.py --mucca <MUCCA_1.0> --out results/countgdpp/xy_clip_assign_dev_<stamp>
```

Script từ chối ghi đè thư mục kết quả. Lỗi kỹ thuật (mạng, tải model) thì chạy lại và ghi WORKLOG; **không chạy lại vì kết quả xấu**.

## 8. Sửa đổi kỹ thuật trước khi có kết quả (22/11, khuya)

**Lần chạy 1 (stamp `20261122_1745`) dừng khi đang nạp CLIP:**
- Lỗi: `transformers` 4.57 không cho nạp `pytorch_model.bin` với `torch` 2.2.2 (yêu cầu torch ≥ 2.6, CVE-2025-32434).
- Script dừng trước khi tạo thư mục kết quả, **chưa tính số nào**.
- Không env conda nào trên máy có torch ≥ 2.6.

**Sửa:**
- Config và processor vẫn lấy ở revision đã ghim `3d74acf…`.
- Trọng số nạp từ `model.safetensors`, bản safetensors của cùng model trên Hub (revision `c237dc49a33f…`, sha256 `99d28a652e6e…`), script kiểm hash này trước khi nạp.
- `pytorch_model.bin` ở revision đã ghim trong cache máy Triệu có sha256 `a63082132ba4…`, **trùng** hash ghi trong `run_config` của lần chạy CLIP dev trên Kaggle. Đây đúng là bản đã dùng trước đây.
- Bước kiểm 3 của §4 (tái lập cosine < 1e-3 so với bundle) xác nhận bản safetensors cho cùng đầu ra. **Không đạt thì dừng, không báo số.**

**Lần chạy 2 (stamp `20261122_1754`) dừng ở bước xử lý ảnh đầu tiên:**
- Lỗi: `transformers` gọi vào TensorFlow, mà gói này trong env `ai_new` đã hỏng từ trước.
- Script dừng trước khi tạo thư mục kết quả, chưa tính số nào.

**Sửa:** đặt `USE_TF=0` trong script để `transformers` chỉ dùng PyTorch. Không đổi gì khác.

Không có thay đổi nào khác về thiết kế, chỉ số hay cách đọc.
