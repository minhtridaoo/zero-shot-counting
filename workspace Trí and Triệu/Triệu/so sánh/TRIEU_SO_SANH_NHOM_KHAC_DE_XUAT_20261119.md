# So sánh với nhóm Hoàng Anh – Duy + đề xuất cho nhóm mình — 19/11/2026

*Trợ lý AI (Claude) soạn theo yêu cầu của Triệu. Triệu đọc lại trước khi dùng; đoạn nào đưa vào báo cáo/slide cần ghi rõ là AI soạn.*

**Đã đối chiếu:**

- Slide nhóm Hoàng Anh – Duy: `C:\Users\diosodumb\Downloads\CountGDpp_slide_.pdf` (44 trang, trình bày 18/11). Đọc bằng văn bản trích từ PDF.
- Ảnh chụp slide "Cải tiến 3" và ảnh màn hình demo Gradio của nhóm đó.
- Phía nhóm mình: báo cáo chi tiết (bản Trí sửa 15/11), `reports/TRIEU_W8_TEST_20261111.md`, `reports/BENCHMARK_FSCD147.md`, runner `experiments/countgdpp/run_b2_verified_pseudo.py`.

---

## 1. Kết luận nhanh

- **Không trùng phương pháp chính.** Hai nhóm dùng cùng mô hình CountGD++ nhưng giải hai bài toán khác nhau:
  - **Nhóm kia:** sửa CountGD++ chạy chỉ bằng chữ trên **ảnh một loại (FSC-147)**. Ba lỗi họ sửa: đếm 0 dù có vật, đếm thừa, đếm ma (lớp vắng mặt). Sau đó mới kiểm trên MUCCA, ShanghaiTech và Blood Cell.
  - **Nhóm mình:** sửa lỗi **đếm nhầm loại khi X và Y cùng có trong ảnh** (bài X/Y), làm trực tiếp trên MUCCA.
- **Trùng ở mức ý tưởng chung:** cùng dùng CLIP làm "người kiểm thứ hai", cùng nâng ngưỡng để bớt đếm thừa, cùng nhận ra lượt 2 tin ảnh mẫu hơn chữ. Ai làm CountGD++ cũng dễ nghĩ ra những ý này, nên không phải chép.
- **Điểm khác quan trọng nhất:** nhóm kia hỏi CLIP **một lần cho cả ảnh** ("ảnh có X không?"). Nhóm mình hỏi CLIP **cho từng khung** ("khung này có phải X không?"). Kiểm theo cả ảnh không giải được bài X/Y: khi bát và đĩa cùng có mặt, hỏi "bowls" thì cổng vẫn mở và mô hình vẫn đếm lẫn đĩa.

---

## 2. Ba cải tiến của nhóm kia

| Cải tiến | Họ làm gì | Họ báo kết quả |
|---|---|---|
| **1. Mẫu giả dự phòng** | Lượt 1 không có khung nào > 0.23 thì lấy tối đa 3 khung có điểm > 0.05 làm mẫu, rồi vẫn chạy lượt 2. Sàn 0.05 chọn trên dev300 | FSC-147: ảnh đếm 0 giảm từ 33 xuống 1, MAE 10.20 → 7.73. MUCCA: **tệ hơn** (22.15 → 23.45, đếm ma 5.2% → 65.8%) |
| **2. Ngưỡng theo từng ảnh** | τ = clip(0.4 × trung bình 3 điểm cao nhất của ảnh, 0.15, 0.40); thực tế gần như cố định quanh 0.39 | FSC-147: 7.73 → 5.97. MUCCA: 22.15 → 16.81 (chỉ cải tiến 2). ShanghaiTech: **tệ hơn** (đếm thiếu đám đông) |
| **3. Cổng CLIP cả ảnh** | Hồi quy logistic trên (điểm cao nhất lượt 1, điểm CLIP ViT-L/14 của cả ảnh với "a photo of {class}"), học trên val; không qua cổng thì trả 0 | Đếm ma trên FSC-147 79.9% → 19.0%, MUCCA 65.8% → 22.5%. MAE FSC-147 tăng 5.97 → 6.35, không đạt tiêu chí họ đặt trước |
| Hướng thử thêm 1 | Cho các prompt trong cùng ảnh giành khung, so bằng điểm CountGD++ (3 vòng) | Không đạt: mất vật thật; "điểm các prompt không so trực tiếp được" |
| Hướng thử thêm 2 | Tinh chỉnh CountGD++ 1 epoch | Không đạt: đếm ma còn tăng |

---

## 3. Khác nhau về phương pháp

| # | Khía cạnh | Nhóm Hoàng Anh – Duy | Nhóm mình |
|---|---|---|---|
| 1 | Bài toán chính | Đếm 0 dù có vật, đếm thừa, đếm ma | Đếm nhầm loại khi X và Y cùng có mặt; trả 0 cho Z vắng mặt |
| 2 | Lượt 2 (mẫu giả) | **Tăng cường**: luôn cố có mẫu (cải tiến 1) | Coi là **nguồn lỗi**: P kiểm mẫu bằng CLIP, C6 bỏ hẳn lượt 2 |
| 3 | Lọc khung | Ngưỡng theo từng ảnh, **chỉ dùng điểm CountGD++** | F: một ngưỡng chung trên **điểm CountGD++ + CLIP của từng khung** |
| 4 | Dùng CLIP | **Cả ảnh**, ViT-L/14, quyết định đếm hay trả 0 | **Từng khung** (F) và **từng mẫu** (P), ViT-B/32 |
| 5 | Gộp tín hiệu | Hồi quy logistic học trên val | Trung bình 50/50 cố định; chỉ chọn min/max và ngưỡng trên dev |
| 6 | Dữ liệu chọn tham số | 300 ảnh val FSC-147 (một loại) | 20 ảnh dev MUCCA (nhiều loại) |
| 7 | Vai trò MUCCA | Bộ kiểm chuyển miền: 200 ảnh, 510 cặp có mặt, 2.400 cặp âm | Dữ liệu chính: pilot / p4 / dev / test 40 ảnh, 119 câu |
| 8 | Lớp vắng mặt | 12 lớp **ngẫu nhiên** mỗi ảnh; họ tự nhận dễ (AUROC 0.996) | Z **khó**: cùng nhóm nghĩa với Y, có người kiểm là thật sự vắng |
| 9 | Chỉ số | MAE chỉ trên cặp có mặt, Bias, tỉ lệ đếm ma | MAE cả câu có mặt và vắng mặt, FPR_absent, **tỉ lệ khung dùng chung X/Y**, phân loại khung theo điểm GT |
| 10 | Chẩn đoán | Qua ví dụ và phân bố điểm (10% ảnh có điểm lượt 1 ≤ 0.23 gây 44% sai số) | Đọc mã tìm cơ chế max; người xem lại khung (N4); đo khung trùng giữa X và Y; biến thể T |
| 11 | Giao thức | Chọn trên dev300, test một lần, tiêu chí đặt trước | Tương tự; thêm dữ liệu do người kiểm, khóa bằng mã băm, luật D9, bootstrap theo ảnh |
| 12 | Huấn luyện | Có thử tinh chỉnh 1 epoch | Không huấn luyện gì |
| 13 | Bộ dữ liệu | FSC-147, MUCCA, ShanghaiTech, Blood Cell | MUCCA (FSCD-147 chỉ để kiểm môi trường, chưa chạy cải tiến) |
| 14 | Demo | Gradio trực tiếp, ví dụ lớp vắng mặt (ảnh heo hỏi "dog") | Chưa có (kế hoạch 25–29/11) |

---

## 4. Chỗ gần nhau (cần chuẩn bị nếu bị hỏi)

1. **Cùng nâng ngưỡng để bớt đếm thừa.**
   - Ngưỡng của họ gần như cố định quanh 0.39, giống biến thể **S** của mình (ngưỡng CountGD++ cố định cao hơn 0.23).
   - Điểm khác của mình là F có thêm **CLIP cho từng khung**, không chỉ nâng ngưỡng.
   - Số của họ trên MUCCA (chỉ cải tiến 2: 22.15 → 16.81) cùng chiều với mình: lọc khung giúp trên ảnh nhiều loại.

2. **Cùng nhận xét "lượt 2 tin ảnh mẫu hơn chữ"** (slide 16 của họ). Điều này khớp với chẩn đoán cơ chế max của mình.
   - Số của họ trên MUCCA cũng cùng chiều với kết luận "lượt 2 gây hại trên ảnh nhiều loại" của mình: thêm mẫu dự phòng thì MAE tệ hơn và đếm ma tăng vọt.

3. **Hướng thử thêm 1 của họ gần với ý 2 trong Hướng phát triển của mình** (so mỗi khung với mọi tên loại rồi gán cho loại giống nhất).
   - Họ so bằng **điểm CountGD++** và thất bại vì điểm các prompt không cùng thang.
   - Ý của mình so điểm **CLIP của cùng một khung với nhiều tên loại**: cùng mô hình, cùng thang điểm, nên không vướng đúng lý do đó. Cần nói rõ khác biệt này nếu thầy hỏi.

4. **Ngưỡng theo từng ảnh trùng ý 3 trong Hướng phát triển của mình** ("ngưỡng thích ứng theo mật độ vật").
   - Cách của họ dựa trên độ tự tin (trung bình 3 điểm cao nhất), không dựa trên mật độ vật, và vẫn làm đếm thiếu ở đám đông (ShanghaiTech).
   - Giữ ý này trong Hướng phát triển, nhưng đừng trình bày như ý tưởng mới lạ.

5. **Số tái lập FSCD-147 giống hệt nhau** (8.34 / 24.64), vì hai nhóm chạy cùng checkpoint, cùng chế độ (chữ + mẫu GPT-5 + mẫu giả + cắt ảnh). Đây là bình thường, không phải vấn đề.

---

## 5. Không so con số trực tiếp giữa hai nhóm

| Khác biệt | Nhóm kia | Nhóm mình |
|---|---|---|
| Tập con MUCCA | Mọi cặp, có lớp tới 759 vật | Cặp có 3–40 vật mỗi loại |
| Lớp vắng mặt | Ngẫu nhiên (dễ) | Cùng nhóm nghĩa, có người kiểm (khó) |
| MAE | Chỉ trên cặp có mặt | Cả câu có mặt và vắng mặt (có báo riêng MAE có mặt) |
| "Code gốc" | Chữ + mẫu giả (tương đương B2 của mình) | Mốc chính là B0 (một lượt) |

Ví dụ: "đếm ma 5.2%" của họ và "FPR_absent 0.25" của mình **không cùng thước đo**.

---

## 6. Nhóm mình có gì mà họ chưa có, và ngược lại

**Điểm riêng của nhóm mình:**

- Đo trực tiếp bài X/Y: khung dùng chung giữa X và Y (B0 64%, C6 24%), khung trúng đúng loại theo điểm GT.
- Lớp vắng mặt khó, có người kiểm. Chính nhóm kia tự ghi hạn chế là "chưa có bộ negative khó".
- Chẩn đoán cơ chế lượt 2 (max, biến thể T) và người xem lại khung (N4).
- Kết quả tách theo loại cặp: cải thiện ở cặp dễ nhầm, chưa thấy ở cặp khác hẳn.

**Họ có, nhóm mình chưa có:**

- Kiểm trên nhiều bộ dữ liệu (FSC-147, ShanghaiTech, Blood Cell) → xem đề xuất A.
- Demo trực tiếp → xem đề xuất B.

**Câu trả lời mẫu khi thầy hỏi khác nhóm kia ở đâu:**

> "Nhóm bạn sửa CountGD++ cho ảnh một loại rồi kiểm trên ảnh nhiều loại. Nhóm em làm thẳng trên ảnh nhiều loại, chẩn đoán vì sao lượt 2 làm đếm lẫn loại, và dùng CLIP kiểm từng khung chứ không kiểm cả ảnh, nên xử lý được cả lúc X và Y cùng có mặt."

---

## 7. Đề xuất

### A. Kiểm "không làm hại" trên FSCD-147 (tùy chọn, cần Trí duyệt trước, AGENTS.md quy tắc 4)

**Vì sao:**

- Nhóm kia kiểm trên nhiều bộ dữ liệu; nhóm mình chưa từng chạy cải tiến trên ảnh một loại.
- Theo số nhóm kia trích từ Bảng 1 bài báo CountGD++, trên FSC-147 lượt 2 giảm MAE rất mạnh (16.55 → 10.29). **Triệu cần tự mở Bảng 1 bài báo để xác nhận số này.** Nếu đúng, C6 (bỏ lượt 2) có thể kém hẳn trên ảnh một loại.
- Thầy rất có thể hỏi "cải tiến có làm hỏng ảnh bình thường không?".
- Chi phí khoảng 1 giờ T4. Kết quả nào cũng dùng được: không hại là điểm cộng, có hại thì ghi rõ phạm vi áp dụng.

**Lưu ý kỹ thuật (đã kiểm trong repo):**

- Runner `run_b2_verified_pseudo.py` ghi `crop=False`, `synthetic=False`. Vì vậy số mới không so được với 8.34 hay với bài báo; chỉ so các cách với nhau trong cùng một lần chạy. Ảnh rất đông vật sẽ bị đếm thiếu ở mọi cách.
- `apply_freeze_v2.py` chia cho số câu vắng mặt, nên sẽ lỗi khi không có câu vắng mặt. File này đã ghi mã băm, **không sửa**; cần viết script chấm mới.
- Cần thêm script đổi FSC-147 test sang `inputs.jsonl` (đường dẫn ảnh + tên lớp).
- F được chỉnh trên ảnh 3–40 vật, nên có thể đếm thiếu ở ảnh dày.

**Bản nháp khai báo trước:**

> **Mục đích:** kiểm xem cấu hình đã khóa có làm kết quả tệ hơn trên ảnh chỉ có một loại vật hay không. Không dùng để chọn lại hay cải tiến.
>
> **Dữ liệu:** FSCD-147 test, 1.190 ảnh. Câu hỏi là tên lớp FSC-147. Mọi câu đều là câu có mặt.
>
> **Cách chạy:**
> - Kaggle T4, cùng cài đặt với lần chạy test MUCCA: `--tau-pseudo 0.20 --m 5 --replay-b2`, không cắt ảnh, không mẫu GPT-5. Lần chạy này ra B0, B2 và P.
> - Bộ lọc F áp offline với min/max và ngưỡng lấy nguyên từ `freeze_v2_20261111.json`. Ra thêm P+F, B2+F và C6.
>
> **So sánh chính:** P+F so với B2. Trên ảnh một loại, B2 là cách CountGD++ vốn được dùng.
> **So sánh phụ:** C6 so với B2, P+F so với B0.
>
> **Chỉ số:** MAE, RMSE, tổng đếm thừa và đếm thiếu. CI 95% của ΔMAE bằng bootstrap theo ảnh (5.000 lần, seed 331).
>
> **Báo theo nhóm (khai báo trước):** ảnh có GT ≤ 40 vật và ảnh có GT > 40.
>
> **Cách đọc kết quả:**
> - CI nằm hoàn toàn trên 0: "có hại trên ảnh một loại".
> - CI chứa 0: "không thấy khác biệt".
> - CI nằm hoàn toàn dưới 0: "có lợi".
>
> **Quy tắc:** chạy một lần, không đổi tham số. Kết quả nào cũng báo, đặt ở mục "Kiểm khả năng tổng quát", không thay kết quả chính. Nếu có hại, ghi phạm vi: "dùng cho ảnh nhiều loại; ảnh một loại nên giữ cách gốc".
>
> **Phân công:** Triệu chạy trên Kaggle, Trí duyệt, assistant viết hai script mới và kiểm kết quả.

**Lịch:** khai báo 20/11 → Trí duyệt 21/11 → chạy 22–23/11 → đưa số vào báo cáo 24/11.

**Nếu không chạy:** ghi trong phần hạn chế rằng kết luận chỉ áp dụng cho ảnh nhiều loại, kèm số 16.55 → 10.29 của bài báo (sau khi đã kiểm).

**Các bộ khác:**

| Bộ | Có nên? | Lý do |
|---|---|---|
| PrACo (mosaic) | Chỉ nếu dư thời gian | Kiểu X/Y trên nguồn ảnh thứ hai, nhưng hai nửa ảnh thường là cặp khác hẳn (nhóm cặp mình chưa thấy cải thiện), và phải tự dựng dữ liệu. Chưa kiểm chi tiết cách bộ này được tạo |
| ShanghaiTech, Blood Cell | Không | Ảnh một loại, rất dày, không liên quan bài X/Y |
| Tự dựng cặp X/Y từ COCO/LVIS | Không làm lúc này | Đúng bài toán nhất nhưng không kịp; ghi vào Hướng phát triển |

### B. Demo nhấn vào bài X/Y

- Nhóm kia demo ảnh heo hỏi "dog" (vật vắng mặt). Nhóm mình nên demo **X và Y cùng có mặt**, vì đây là điểm riêng.
- **Giao diện:** sửa từ `CountGDPlusPlus/app.py` (Gradio gốc có sẵn trong repo). Nhập ảnh + 2–3 tên loại → hiện khung B0 / B2 / P+F / C6 cạnh nhau cho từng câu hỏi, khung trùng giữa X và Y tô màu riêng. Người xem sẽ thấy ngay "hỏi bát mà khung y hệt lúc hỏi đĩa".
- **Phương án dự phòng (nên có):** ảnh trước/sau tĩnh từ `reports/figures/` (blueberries thành công, bowls lỗi X/Y, dogs thất bại, people lọc quá tay). Demo trực tiếp cần GPU và mạng, dễ hỏng lúc trình bày.
- **Thứ tự kể:** một ví dụ thành công, một ví dụ thất bại.

### C. Câu hỏi thầy có thể hỏi

| Câu hỏi | Ý trả lời |
|---|---|
| Khác nhóm Hoàng Anh – Duy ở đâu? | Câu trả lời mẫu ở mục 6 |
| Sao không dùng cổng CLIP cả ảnh như nhóm kia? | Cổng cả ảnh chỉ chặn lớp vắng mặt; khi X và Y cùng có mặt thì cổng vẫn mở và vẫn đếm lẫn. Nhóm em cần quyết định cho từng khung |
| Ngưỡng theo từng ảnh có tốt hơn ngưỡng chung của F không? | Chưa so trực tiếp. Ngưỡng của nhóm kia dựa trên độ tự tin và vẫn đếm thiếu ở đám đông. Nhóm em ghi ngưỡng thích ứng theo mật độ là hướng phát triển |
| Bỏ lượt 2 thì trên FSC-147 có tệ hơn không? | Có số từ đề xuất A thì trả lời bằng số. Chưa có thì: "chưa kiểm, kết luận chỉ áp dụng cho ảnh nhiều loại" |
| Lớp vắng mặt của nhóm em có dễ như nhóm kia không? | Không: Z cùng nhóm nghĩa với Y và có người kiểm là thật sự vắng, nên FPR của nhóm em khó hơn và không so trực tiếp được |

### D. Cách nhắc tới nhóm kia trong báo cáo

- **Không đưa** cổng CLIP cả ảnh hay ngưỡng theo từng ảnh vào phương pháp hoặc kết quả. Test đã khóa.
- **Không ghi tên nhóm** (không phải công trình đã công bố). Nếu cần, chỉ viết chung trong Hướng phát triển: "một hướng khác là kiểm theo cả ảnh trước khi đếm".

---

## 8. Chưa kiểm được

- Slide nhóm kia chỉ đọc qua văn bản trích từ PDF; hình và biểu đồ chưa xem, vài bảng bị lệch cột khi trích. Đã đối chiếu các con số lặp lại ở slide tổng hợp (28, 29, 31), nhưng từng ô có thể còn sai.
- Chưa tự đọc Bảng 1 bài báo CountGD++ (số 16.55 / 10.29 / 8.39 lấy từ slide nhóm kia).
- Chưa biết chi tiết cách dựng bộ PrACo.
