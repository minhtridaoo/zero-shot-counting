# Triệu — việc ngày 22/11/2026: chạy thay Trí và chốt đồ án

*Assistant (Claude) soạn ngày 22/11 theo lời dặn của Trí. Triệu đọc hết file này trước khi bắt đầu.*

## 0. Lời dặn của Trí (ghi lại nguyên ý)

Trí nhắn ngày 22/11:
- Hôm nay Trí **không có thời gian** cho môn này. Trí **đã báo trước với Triệu**: hôm nay **Triệu chạy task của Trí thay Trí**.
- Trong ngày hôm nay, Triệu cố gắng làm hết những gì có thể, để **chốt xong đồ án**.
- **Tối nay** Trí và Triệu cùng lên kế hoạch: chuẩn bị gì, mang theo gì, trình bày gì với thầy trong buổi báo cáo.
- Cả hai cần **một cẩm nang đồ án** chứa toàn bộ nội dung. Từ cẩm nang đó lên kế hoạch slide và cách trình bày, sao cho thầy và các bạn dễ hiểu, nhóm trình bày trơn tru và tự tin, không có phần nào trong đồ án mà nhóm không nắm.

Về việc duyệt thiết kế khảo sát FSC-147, Trí đã nói trong trao đổi với assistant:
- 20/11: "Ổn về thiết kế và phân công rồi".
- 21/11: "Phần chuẩn bị ổn rồi".
- 22/11: giao Triệu chạy thay.

Assistant ghi lại đúng lời Trí. **Assistant không ký thay ai.** Nếu Triệu thấy cần Trí xác nhận thêm thì nhắn Trí một câu trước khi bấm chạy.

**Thay đổi vai trò so với kế hoạch 21/11:** Triệu vừa kiểm phần A, vừa chạy Kaggle (vai của Trí). Như vậy phần kiểm B/C không còn do một người độc lập làm. Cách bù:
- Assistant kiểm độc lập B/C khi có ZIP.
- Trí xem lại bảng kiểm khi có thời gian.
- Ghi rõ thay đổi này trong WORKLOG.

## 1. Thứ tự việc hôm nay (làm từ trên xuống; hết giờ thì dừng ở đâu ghi ở đó)

| # | Việc | Ưu tiên | Thời gian ước | File hướng dẫn |
|---|---|---|---|---|
| 1 | Pull `main` mới nhất | bắt buộc | 5 phút | mục 2 |
| 2 | Kiểm phần A của khảo sát (thiết kế + mẫu 300 ảnh) | bắt buộc trước khi chạy | 30–45 phút | [HUONG_DAN_KIEM_TRIEU.md](../experiments/fsc147_survey/HUONG_DAN_KIEM_TRIEU.md) phần A |
| 3 | **Chạy notebook khảo sát trên Kaggle, một lần** | cao | chưa đo; để chạy nền | mục 3 |
| 4 | Trong lúc Kaggle chạy: đọc [cẩm nang đồ án](../reports/CAM_NANG_DO_AN_CS331.md), đánh dấu chỗ chưa hiểu | cao | 1–2 giờ | cẩm nang |
| 5 | Viết Related Work (W7). Đây là phần còn thiếu của báo cáo cuối | cao | 2 giờ | mục 5 |
| 6 | Kaggle xong: tải ZIP + log, đưa vào repo, kiểm phần B/C | cao | 45 phút | mục 4 |
| 7 | Đọc [kế hoạch slide](../reports/KE_HOACH_SLIDE_THUYET_TRINH.md), chuẩn bị cho buổi họp tối với Trí | trung bình | 30 phút | mục 6 |
| 8 | Cập nhật WORKLOG + BAT_DAU, commit, push | bắt buộc cuối ngày | 15 phút | mục 7 |

**Không làm:**
- Không chạy lại test MUCCA. Không chạy evaluator khác.
- Không đổi tham số hay `REPO_REF`.
- Không chạy lại khảo sát vì kết quả xấu.
- Không sửa dữ liệu khóa, freeze hay dự đoán gốc.

## 2. Pull `main`

```bash
git checkout main
git pull --ff-only
```

- `main` đã có thư mục `experiments/fsc147_survey/` và notebook đúng (sau PR #1, #2).
- **Cẩm nang, kế hoạch slide và file này** được đẩy lên nhánh `claude/kind-chaplygin-249b83` ngày 22/11. Nếu `main` chưa có các file này (chưa merge PR), đọc trên nhánh:
  https://github.com/minhtridaoo/zero-shot-counting/tree/claude/kind-chaplygin-249b83
  Hoặc `git fetch origin && git checkout claude/kind-chaplygin-249b83` chỉ để đọc. **Notebook khảo sát vẫn tải từ `main`.**
- Nếu `pull --ff-only` báo lỗi vì có sửa đổi trên máy: **chép các file đang sửa ra chỗ khác trước**, rồi mới pull. Không dùng stash cũ.
- Máy Trí (`D:\MINHTRIHOCCODE\HOCKI5\CS331`) đang có ghi chú chưa commit trong `BAT_DAU_SESSION_MOI.md` và `WORKLOG.md`. Đó là việc của Trí, Triệu không cần đụng.

## 3. Chạy khảo sát FSC-147 trên Kaggle (thay Trí)

Làm đúng theo [HUONG_DAN_CHAY_KAGGLE_TRI.md](../experiments/fsc147_survey/HUONG_DAN_CHAY_KAGGLE_TRI.md). Hướng dẫn viết cho Trí, nhưng các bước y hệt. Tóm tắt:

1. Tải notebook `experiments/fsc147_survey/kaggle_fsc147_survey.ipynb` **từ `main`**.
   - Ô 1 phải có `REPO_REF = "4cd89092c5160dc0dc79455adba42ff096a44664"`.
   - Thấy SHA khác (ví dụ `d5339c2…`) là tải nhầm bản cũ.
2. Kaggle → Import Notebook → **GPU T4 x2**, **Internet On**.
3. **Add Input:** gắn Dataset checkpoint `countgd_plusplus.pth`. Đây là Dataset Triệu đã dùng cho W6/W8.
   - Ảnh FSC-147: không gắn thì Ô 6 tự tải bằng gdown.
   - Nếu gdown báo quá lượt tải: tạo Dataset chứa `images_384_VarV2` rồi gắn.
4. **Save Version → Save & Run All (Commit)**. Đặt tên version, ví dụ `fsc147_survey_run1`.
5. Xong thì tải **`for_repo_<stamp>.zip`** (tab Output) và **log** (tab Logs).
6. **Dừng và gửi log** khi gặp các trường hợp ở mục 5 của hướng dẫn chạy:
   - sai commit hoặc sai hash;
   - Kiểm A không đạt;
   - thiếu ảnh;
   - lỗi ở một ảnh;
   - script chấm từ chối.

   Lỗi kỹ thuật (hết giờ, crash cài đặt) thì chạy lại version mới, đủ 300 ảnh, **tối đa 2 lần**, và ghi WORKLOG.

Ghi lại: tên/số version Kaggle, giờ bắt đầu, giờ kết thúc.

## 4. Đưa kết quả vào repo và kiểm

1. Giải nén ZIP vào thư mục tạm. Chép các thư mục `fsc147_survey_kaggle_t4_<stamp>*` vào `results/countgdpp/`.
   - Chỉ file json/jsonl/csv/txt (D10). Không có `.npz`, không có ảnh.
   - Chép thêm `fsc_image_sha256.json`, `timing.json`, `FILES_<stamp>.json` vào `results/countgdpp/fsc147_survey_kaggle_t4_<stamp>_kaggle_meta/`. Cách này giống W8 có thư mục `_kaggle_meta`.
2. Làm **phần B và C** trong [HUONG_DAN_KIEM_TRIEU.md](../experiments/fsc147_survey/HUONG_DAN_KIEM_TRIEU.md). Điền từng mục: Đạt / Không đạt / Chưa kiểm được.
3. Viết `reports/TRIEU_FSC147_KHAO_SAT_20261122.md` (mẫu ngắn ở cuối file này).
4. Nếu Triệu có phiên Claude/assistant riêng: nhờ kiểm độc lập bằng câu
   > "Đọc HANDOFF/TRIEU_NGAY_22_11_CHOT_DO_AN.md mục 4, kiểm độc lập kết quả khảo sát FSC-147 trong results/countgdpp/fsc147_survey_kaggle_t4_<stamp>*: tính lại MAE và Δ của 5 cách từ per_query.csv và manifest, so với result.json; không chạy model."

   Nếu không có thì để Trí nhờ assistant kiểm khi Trí rảnh.
5. Điền số vào **mục 9 của cẩm nang** (chỗ "chờ kết quả") và slide dự phòng S14 trong kế hoạch slide. Giữ đúng cách đọc:
   - CI chứa 0 nghĩa là "chưa thấy khác biệt rõ";
   - không so với 8,34 / 10,29;
   - không nói về lớp vắng mặt.

**Nếu đến tối 23/11 chưa chạy xong:** khảo sát đóng ngày 24/11. Ghi vào phần hạn chế: "chưa kiểm trên ảnh một loại vật". Báo cáo và slide vẫn đủ mà không cần khảo sát này.

## 5. Related Work (W7)

Đây là mục duy nhất của báo cáo cuối mà repo chưa có. Gợi ý khung (khoảng 1–1,5 trang), mỗi ý 2–4 câu, và mỗi công trình nói rõ **khác đồ án ở đâu**:

1. **Đếm theo mẫu:** FSC-147 (Ranjan và cộng sự, 2021), bài toán class-agnostic counting.
2. **Đếm theo chữ / zero-shot:**
   - CountGD (Amini-Naieni, Han & Zisserman, NeurIPS 2024);
   - CountGD++ (Amini-Naieni & Zisserman, CVPR 2026), mô hình đồ án dùng;
   - nền GroundingDINO (Liu và cộng sự, ECCV 2024).
3. **Tự sinh mẫu từ chữ:** PseCo, DAVE, VA-Count. Ý chung: tạo mẫu rồi đếm theo mẫu. Đồ án cho thấy trong ảnh nhiều loại, mẫu tự sinh có thể sai loại và kéo theo lỗi. **Triệu tự mở bài gốc để ghi đúng tác giả, năm, hội nghị.** Assistant chưa kiểm trích dẫn của ba bài này.
4. **Đánh giá độ bám câu chữ:**
   - PrACo (Ciampi và cộng sự, WACV 2025);
   - MUCCA / PrACo++ (Pacini và cộng sự, 2026, arXiv 2605.02752).

   Đồ án dùng chung tinh thần (hỏi loại vắng mặt, có vật gây nhiễu) nhưng khác ở chỗ: *sửa* lỗi cho một mô hình cụ thể, kiểm bằng giao thức khóa trước.
5. **CLIP làm bộ kiểm** (Radford và cộng sự, ICML 2021).

Nguồn đã kiểm có trong "Tài liệu tham khảo" của `reports/BAO_CAO_CHI_TIET_DO_AN_20261112.md`. Lưu ở `reports/RELATED_WORK_TRIEU_20261122.md`.

## 6. Chuẩn bị cho buổi họp tối với Trí

- Đọc [CAM_NANG_DO_AN_CS331.md](../reports/CAM_NANG_DO_AN_CS331.md). Bản HTML có hình: `reports/CAM_NANG_DO_AN_CS331.html`.
- Đọc [KE_HOACH_SLIDE_THUYET_TRINH.md](../reports/KE_HOACH_SLIDE_THUYET_TRINH.md): dàn slide, ai nói phần nào, kịch bản, câu hỏi phản biện.
- Ghi ra **3–5 câu hỏi** về chỗ còn chưa chắc, để hỏi trong buổi họp.
- Mang theo mục "Việc chờ Trí quyết" ở cuối kế hoạch slide.

## 7. Cuối ngày: cập nhật và đẩy lên

1. `WORKLOG.md`: thêm mục mới **trên cùng**, ghi:
   - việc đã làm, version Kaggle, kết quả PASS/FAIL các mục kiểm;
   - việc chưa làm, lý do;
   - dòng: "Triệu chạy thay Trí theo lời dặn 22/11; kiểm B/C do Triệu tự làm, chờ kiểm độc lập".
2. `BAT_DAU_SESSION_MOI.md`: sửa khối "Cập nhật" trên cùng thành trạng thái mới và việc tiếp theo.
3. Commit rồi push lên `main`. Không force-push.

## Mẫu báo cáo ngắn `reports/TRIEU_FSC147_KHAO_SAT_20261122.md`

```markdown
# Khảo sát FSC-147 (300 ảnh) — Triệu chạy thay Trí, 22/11/2026
- Kaggle version: … ; run: fsc147_survey_kaggle_t4_<stamp> ; thời gian runner / CLIP: … s
- Commit đã ghim (Ô 2): 4cd8909… ; Kiểm A: lệch lớn nhất …
- Bảng kiểm A / B / C: (từng mục Đạt / Không đạt / Chưa kiểm được)
- Kết quả toàn mẫu: MAE B0 …, B2 …, P+F …, C6 …, B2+F …
- Chính B0 − B2: … CI [… , …] → (đọc theo khai báo)
- Nhóm ≤40 / >40: …
- Lỗi / chạy lại: …
- Chưa kiểm độc lập: (assistant sẽ kiểm)
```
