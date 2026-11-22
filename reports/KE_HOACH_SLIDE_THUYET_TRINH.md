---
title: "Kế hoạch slide và thuyết trình đồ án CS331"
subtitle: "Dàn slide, ai nói gì, kịch bản, câu hỏi phản biện, hành trang · assistant soạn 22/11/2026 cho buổi họp tối của Trí và Triệu"
---

> Nội dung chi tiết và mọi con số: [CAM_NANG_DO_AN_CS331.md](CAM_NANG_DO_AN_CS331.md).
> **Giả định cần Trí và Triệu xác nhận tối nay:** thời lượng trình bày **15 phút + 5–10 phút hỏi đáp**, hai người cùng nói. Nếu thầy cho 10 phút thì bỏ các slide đánh dấu *(rút được)*. Nếu cho 20 phút thì thêm slide dự phòng.

# 1. Mạch kể (một câu cho mỗi phần)

1. **Vấn đề:** mô hình đếm theo chữ có thật sự đếm đúng loại được hỏi không, khi ảnh có nhiều loại?
2. **Chẩn đoán:** không. CountGD++ trả về cùng một nhóm khung dù đổi câu hỏi, và lượt 2 tự chọn mẫu còn làm tệ hơn.
3. **Cải tiến:** thêm CLIP làm người kiểm thứ hai: kiểm mẫu (P) và lọc khung (F). Không cần huấn luyện.
4. **Kiểm chứng trung thực:** chọn trên dev, khóa, test chạy một lần. Kết quả: giảm 24% MAE so với một lượt, CI không chứa 0.
5. **Hiểu sâu:** cái giúp là F, không phải P. Giúp ở cặp dễ nhầm, chưa giúp ở cặp khác hẳn. Bài học về chọn mô hình.

> **Nguyên tắc trình bày:** mỗi slide một ý, có một con số hoặc một hình. Chữ trên slide ít, phần giải thích nằm ở lời nói. Mọi con số đọc kèm đơn vị và ý nghĩa ("MAE 5.82, tức trung bình sai khoảng 6 vật mỗi câu").

# 2. Dàn slide (15 phút)

| # | Tiêu đề slide | Nội dung trên slide | Hình / bảng | Người nói | Thời gian |
|---|---|---|---|---|---|
| S1 | Tên đề tài | "Đếm đúng loại vật trong ảnh nhiều loại: chẩn đoán và giảm lỗi đếm nhầm loại của CountGD++"; tên nhóm, môn, ngày | — | Trí | 0:20 |
| S2 | Bài toán X/Y | Một ảnh có bát và đĩa; hỏi "bowls" phải ra bát, hỏi "plates" phải ra đĩa, hỏi "forks" (không có) phải ra 0 | Ảnh mcac_12 với 3 câu hỏi | Trí | 1:00 |
| S3 | Vì sao khó, vì sao quan trọng | Benchmark FSC-147 phần lớn chỉ có 1 loại mỗi ảnh, nên mô hình "đếm thứ nổi bật" vẫn được điểm cao. MUCCA: ảnh thật, nhiều loại có nhãn | 2 ảnh: FSC-147 và MUCCA cạnh nhau | Trí | 1:00 |
| S4 | CountGD++ đếm thế nào | Lượt 1: chữ → khung > 0.23. Lượt 2: lấy 3 khung chắc nhất làm mẫu giả → chạy lại. Ví von "người đếm chỉ vào 3 vật" | `fig_pipeline.png` (nửa trái) | Trí | 1:15 |
| S5 | Câu hỏi nghiên cứu | RQ1 chẩn đoán, RQ2 sửa không huấn luyện, RQ3 kiểm trên ảnh chưa thấy | 3 ô chữ | Trí | 0:30 |
| S6 | Chẩn đoán: lỗi ở đâu | N4: mẫu giả chỉ **1/21** đúng loại; "people" và "cars" trùng **21/21 khung**. Test: B0 dùng chung **64%** khung giữa X và Y; khoảng 1/3 khung là vật loại khác | Ảnh minh họa khung trùng + 2 con số lớn | Triệu | 1:30 |
| S7 | Cơ chế lượt 2 | Điểm lượt 2 = max(giống chữ, giống mẫu). Biến thể T bỏ max: chỉ gỡ khoảng **1/5** tác hại (dev). Giả thuyết H2: mẫu giả làm lệch cả điểm theo chữ (chưa kiểm) | Công thức max + bảng T nhỏ | Triệu | 1:15 |
| S8 | Cải tiến P và F | P: CLIP kiểm mẫu trước lượt 2. F: 0.5·CountGD++ + 0.5·CLIP ≥ θ. Không huấn luyện | `fig_pipeline.png` (nửa phải) + bảng ví dụ 4 khung blueberries | Trí | 1:30 |
| S9 | Giao thức "chọn trước, xem sau" | Dữ liệu người kiểm + khóa hash → luật D9 chốt trước → chọn trên dev → khóa → test **một lần** → người thứ hai tính lại | `fig_protocol.png` | Triệu | 1:15 |
| S10 | Kết quả test | B0 7.71 → **P+F 5.82** (−24%, CI [−3.66, −0.44]); B2 9.61 (lượt 2 gây hại, có ý nghĩa) | `fig_results_test.png` | Trí | 1:30 |
| S11 | Cái gì thật sự giúp | P = B2 ở **108/120** câu, nên P không giúp; B2+F ≈ P+F, nên **F** là thứ có tác dụng. F đổi đếm thừa thành đếm thiếu (+580/−77 → +243/−297) | Bảng 3 dòng + mũi tên | Triệu | 1:15 |
| S12 | Giúp ở đâu, chưa giúp ở đâu | Cặp dễ nhầm: −3.05 (chắc). Cặp khác hẳn: +0.51 (chưa chắc, 13 ảnh) | `fig_strata_errors.png` | Triệu | 1:00 |
| S13 | Ví dụ thành công / thất bại | blueberries (thành công) · dogs–dê (thất bại) · people (lọc quá tay) | 3 hình `fig_example_*` | Trí + Triệu | 1:15 |
| S14 | *(rút được)* Bài học chọn mô hình + khảo sát FSC-147 | C6 hạng 7/15 họ trên dev nhưng tốt nhất trên test; không đổi kết quả chính sau khi xem test. Khảo sát FSC-147 (300 ảnh một loại): B0 − B2 +0,55 [−3,00; +4,30], chưa khác rõ; P+F kém hơn B2 (+4,69 [+2,25; +7,50]), do đếm thiếu ở ảnh > 40 vật | Bảng dev → test | Triệu | 1:00 |
| S15 | Hạn chế và hướng phát triển | 4 hạn chế chính (thêm: X/Y chưa giải xong, sai khoảng nửa số vật; phạm vi: ảnh nhiều loại, ít đến vừa vật). **Thử nghiệm sơ bộ trên dev:** gán khung theo CLIP, khung dùng chung X/Y 62% → 3% nhưng MAE có mặt 5,05 → 6,92 (bỏ nhầm 30% vật đúng). Hướng tiếp: chỉ phân xử khung bị tranh chấp; ngưỡng theo mật độ; kiểm H2 | 2 cột + bảng nhỏ 2×2 (dùng chung / MAE có mặt) | Trí | 1:00 |
| S16 | Kết luận | 3 câu trả lời RQ1–RQ3 + "cảm ơn, mời thầy và các bạn hỏi" | — | Trí | 0:30 |

**Tổng khoảng 16 phút.** Rút S14 (−1:00) và nói gọn S3, S5 (−0:30) để về 15 phút.

**Slide dự phòng (để sau S16, chỉ mở khi được hỏi):**

- D1: bảng đầy đủ 5 cách trên test (MAE, MAE có mặt, FPR).
- D2: bảng dev (D9) và lưới τ/M.
- D3: bảng khung đúng loại / loại khác / không trúng.
- D4: thứ hạng dev theo họ phương pháp.
- D5: v1 trên p4_unseen_v1.
- D6: ví dụ "bowls" (lỗi X/Y còn lại).
- D7: kết quả khảo sát FSC-147 đầy đủ.
- D8: D1–D12.
- D9: chi phí thời gian.

# 3. Kịch bản nói (gợi ý, nói theo ý mình, không đọc)

**S1.** "Chào thầy và các bạn. Nhóm em gồm Trí và Triệu. Đề tài của nhóm là kiểm tra xem một mô hình đếm vật hiện đại có thật sự đếm đúng loại vật được hỏi không, khi trong ảnh có nhiều loại."

**S2.** "Ví dụ ảnh này có bát và đĩa. Hỏi 'bowls' thì đáp án là 3 cái bát. Đổi sang hỏi 'plates' thì mô hình phải đếm đĩa, không được đếm lại bát. Hỏi 'forks', thứ không có trong ảnh, thì phải trả 0. Thầy gọi đây là bài toán X/Y, và đó là câu hỏi xuyên suốt đồ án."

**S3.** "Vì sao cần hỏi vậy? Bộ dữ liệu chuẩn FSC-147 gần như ảnh nào cũng chỉ có một loại nổi bật. Một mô hình chỉ cần 'đếm thứ nổi bật nhất' cũng được điểm cao. Nhóm dùng MUCCA, bộ ảnh thật năm 2026 có nhãn điểm cho nhiều loại trong cùng một ảnh, nên kiểm được đúng câu hỏi này."

**S4.** "Mô hình nhóm chọn là CountGD++, công bố ở CVPR 2026. Lượt 1, mô hình đọc câu chữ và khoanh những thứ trông giống. Lượt 2, nó lấy 3 khung nó chắc nhất làm mẫu rồi chạy lại. Hình dung một người đếm chỉ vào 3 vật và nói 'đếm hết những thứ trông như thế này'. Nếu 3 vật đó sai loại thì lượt 2 sai rất tự tin. Nhóm không huấn luyện lại, chỉ dùng checkpoint công khai."

**S5.** "Nhóm đặt ba câu hỏi: mô hình sai ở đâu; sửa được mà không huấn luyện lại không; và mức sửa có còn đúng trên ảnh chưa từng dùng không."

**S6 (Triệu).** "Để chẩn đoán, em gán nhãn mù 117 khung. Kết quả: mẫu giả chỉ đúng loại 1 trên 21 lần. Ở một ảnh, hỏi 'people' và hỏi 'cars' cho ra 21 trên 21 khung giống hệt nhau. Trên tập test, đổi câu hỏi từ X sang Y thì 64% khung vẫn được dùng lại, và khoảng một phần ba khung rơi vào vật loại khác."

**S7 (Triệu).** "Đọc mã, nhóm thấy ở lượt 2, điểm của khung là max giữa 'giống chữ' và 'giống mẫu'. Vậy khung chỉ cần giống mẫu sai là được tính. Nhóm thử biến thể T bỏ max: nó chỉ gỡ được khoảng một phần năm tác hại trên dev. Vì vậy nhóm kết luận max chỉ là một phần nguyên nhân. Phần còn lại, nhóm đặt giả thuyết là mẫu giả làm lệch luôn cách mô hình hiểu câu chữ. Giả thuyết này chưa kiểm."

**S8.** "Cải tiến dùng CLIP làm người kiểm thứ hai. CLIP không đếm, chỉ chấm xem một ô ảnh có giống 'a photo of bowls' không. P là kiểm mẫu bằng CLIP trước lượt 2. F là lọc từng khung bằng điểm kết hợp: một nửa điểm CountGD++, một nửa điểm CLIP, giữ khung vượt ngưỡng. Ví dụ ở bảng này: khung rác bị bỏ, nhưng cũng có khung đúng bị bỏ nhầm."

**S9 (Triệu).** "Vì dữ liệu ít mà tham số nhiều, nhóm làm theo kiểu 'chọn trước, xem sau'. Dữ liệu được người kiểm rồi khóa bằng hash. Luật chọn cấu hình được viết ra trước khi chạy dev. Chọn trên dev xong thì khóa lại, rồi chạy test đúng một lần. Kết quả được người thứ hai tính lại và khớp tuyệt đối. Kết quả xấu cũng không chạy lại."

**S10.** "Trên 40 ảnh test, 119 câu hỏi: CountGD++ một lượt có MAE 7.71, tức trung bình sai gần 8 vật mỗi câu. Cấu hình đã khóa còn 5.82, giảm 24%. Khoảng tin cậy 95% của mức giảm không chứa 0. Lượt 2 gốc thì tệ hơn một lượt, 9.61, và cũng có ý nghĩa thống kê."

**S11 (Triệu).** "Phân tích sau đó cho thấy P gần như luôn chọn lại đúng bộ mẫu cũ, 108 trên 120 câu, và B2 cộng F cho kết quả gần bằng P cộng F. Vậy thành phần có tác dụng là bộ lọc F. F đổi lỗi đếm thừa thành đếm thiếu: thừa giảm từ 580 xuống 243, nhưng thiếu tăng từ 77 lên 297."

**S12 (Triệu).** "Chia theo loại cặp: với cặp dễ nhầm như bát–đĩa hay các loại quả, cải thiện rõ, khoảng 3 vật mỗi câu. Với cặp khác hẳn như người–xe, chưa thấy khác biệt chắc chắn, và chỉ có 13 ảnh. Nhóm nói thẳng điều này: phương pháp chưa giải quyết xong mọi dạng X/Y."

**S13.** "Ba ví dụ. Blueberries: B2 đếm 65, P+F đếm 8, đáp án 7. Dogs: đàn dê bị đếm là chó ở mọi cách, vì CLIP cũng không phân biệt được dê và chó ở ô ảnh nhỏ. People: F bỏ cả người thật, còn 13 trên 31."

**S14 (Triệu).** "Một bài học: trên dev, cách đơn giản C6 chỉ xếp thứ 7, nhưng trên test lại tốt nhất. Chênh lệch nằm trong khoảng nhiễu, nên nhóm không đổi kết quả chính sau khi đã xem test. Nhóm ghi C6 là giả thuyết cho lần kiểm sau." "Nhóm cũng kiểm thêm 300 ảnh FSC-147, mỗi ảnh một loại. Ở đó giữ hay bỏ lượt 2 chưa khác nhau rõ. Còn cấu hình của nhóm thì kém hơn, vì bộ lọc chọn trên ảnh 3–40 vật đã lọc quá tay ở ảnh dày. Nên nhóm ghi rõ: cải tiến dành cho ảnh nhiều loại, ít đến vừa vật."

**S15.** "Hạn chế: mẫu nhỏ, ngưỡng toàn cục, CLIP yếu với vật gần nghĩa. Bài X/Y cũng chưa giải xong: sau cải tiến, sai số vẫn khoảng nửa số vật. Nhóm đã thử sơ bộ trên dev một hướng nhắm thẳng vào chỗ này: gán mỗi khung cho loại mà CLIP thấy giống nhất. Tỉ lệ khung dùng chung giữa X và Y giảm từ khoảng 60% xuống 3%, nhưng CLIP trên ô cắt nhỏ bỏ nhầm khoảng 30% vật đúng, nên số đếm chưa tốt hơn. Bước tiếp là chỉ phân xử những khung bị hai câu hỏi tranh nhau, và dùng ngưỡng theo mật độ vật."

**S16.** "Tóm lại: CountGD++ đếm lẫn loại khi ảnh có nhiều loại, và lượt 2 làm nặng thêm. Một bộ lọc dùng CLIP, không cần huấn luyện, giảm 24% sai số trên tập test khóa trước. Cải thiện tập trung ở cặp dễ nhầm, và dành cho ảnh nhiều loại, ít đến vừa vật; trên ảnh một loại, ảnh dày thì nên giữ CountGD++ gốc. Em cảm ơn thầy và các bạn đã lắng nghe."

# 4. Câu hỏi phản biện có thể gặp (chia người trả lời)

| # | Câu hỏi | Ý trả lời ngắn | Người trả lời | Slide dự phòng |
|---|---|---|---|---|
| 1 | Sao không huấn luyện lại / fine-tune? | Câu hỏi là về mô hình công khai; MUCCA chỉ 200 ảnh, không đủ để vừa huấn luyện vừa có tập kiểm độc lập; sửa ở đầu ra dễ tái lập | Trí | — |
| 2 | 40 ảnh có quá ít không? | Có, đó là hạn chế số 1. Vì vậy nhóm dùng bootstrap theo ảnh và khóa trước test. Kết quả chính vẫn có CI không chứa 0 | Triệu | D1 |
| 3 | Sao C6 tốt hơn mà không chọn C6? | Luật chọn D9 chốt trước, dev chọn P+F. Đổi sau khi xem test là thiên lệch. C6 − P+F có CI chứa 0, nên chưa chắc C6 tốt hơn | Triệu | D4 |
| 4 | P không giúp thì sao vẫn gọi là cải tiến chính? | Kết quả chính là cấu hình đã khóa P+F, đúng giao thức. Nhóm báo trung thực rằng phần có tác dụng là F; P quá nhẹ tay (108/120 câu giống B2) | Trí | — |
| 5 | Sao dùng CLIP ViT-B/32 mà không dùng ViT-L/14? | Chốt từ giai đoạn v1 (pilot), sau đó khóa để không đổi biến giữa các giai đoạn; nhẹ hơn trên T4. Thử ViT-L là hướng phát triển. *(Trí xác nhận lý do thật tối nay)* | Trí | — |
| 6 | CI tính thế nào, sao theo ảnh? | 3 câu trong một ảnh không độc lập; lấy lại 40 ảnh 5.000 lần, lấy phân vị 2.5% và 97.5% | Triệu | — |
| 7 | GT có đúng không? | GT là số điểm MUCCA; người kiểm cả dev và test; 15/120 câu có ghi chú; độ nhạy dùng số người đếm: MAE đổi dưới 0.06 | Triệu | — |
| 8 | "Có ý nghĩa thống kê" nghĩa là gì ở đây? | CI 95% của chênh lệch MAE không chứa 0 | Triệu | — |
| 9 | Khác nhóm Hoàng Anh – Duy thế nào? | Câu trả lời mẫu ở mục 12b của cẩm nang (CLIP từng khung so với cả ảnh; ảnh nhiều loại; chẩn đoán cơ chế) | Trí | — |
| 10 | Có làm hỏng ảnh một loại (FSC-147) không? | Có, ở ảnh dày. Trên 300 ảnh FSC-147: P+F MAE 18,01 so với B2 13,32 (kém hơn, CI [+2,25; +7,50]), chủ yếu ở ảnh > 40 vật do bộ lọc gây đếm thiếu. Ảnh ≤ 40 vật thì ngang nhau (3,50 so với 3,44). Bỏ lượt 2 (B0 − B2) chưa khác rõ. Không so với 8,34 / 10,29 vì khác điều kiện (không cắt ảnh, không mẫu GPT-5) | Triệu | D7 |
| 11 | Tại sao lượt 2 hại? | max(chữ, mẫu) + mẫu giả sai loại; T chỉ gỡ khoảng 1/5; giả thuyết H2 | Triệu | — |
| 12 | Câu vắng mặt xử lý thế nào? | Z khó, cùng nhóm nghĩa, người kiểm; khung đếm nhầm 92–100% nằm trên vật thật khác; C6 FPR 0.10 | Triệu | D1 |
| 13 | Cặp khác hẳn chưa cải thiện, vậy X/Y giải được chưa? | Chưa hoàn toàn. Đó là phát hiện trung thực; B0 vốn đã tốt ở nhóm này; chỉ 13 ảnh. Hướng "CLIP tương phản" đã thử sơ bộ trên dev: khung dùng chung 62% → 3% nhưng MAE có mặt chưa tốt hơn (5,05 → 6,92), vì CLIP bỏ nhầm 30% vật đúng | Trí | — |
| 14 | Thời gian chạy? | B0 khoảng 0.89 s/câu, B2/P khoảng 1.5 s/câu trên T4; CLIP khoảng 1,3 s/câu (đo ở khảo sát FSC-147, ảnh nhiều khung hơn MUCCA); C6 tiết kiệm khoảng 40% thời gian CountGD++ | Triệu | D9 |
| 15 | Ngưỡng θ 0.604 ở đâu ra? | Chọn trên dev theo D9, cùng min/max, khóa trong freeze v2 (hash) | Trí | D2 |
| 16 | Tái lập thế nào? | Repo public; dữ liệu và cấu hình có hash; notebook Kaggle; Kiểm A + Kiểm C | Triệu | — |
| 17 | Đóng góp của từng thành viên? | Xem mục 6 | cả hai | — |
| 18 | Có dùng AI hỗ trợ không? | Có, dùng assistant (Claude) để viết code, kiểm số và soạn tài liệu. Mọi số liệu được tính lại độc lập; các quyết định do nhóm chốt. *(Thống nhất câu này tối nay)* | Trí | — |
| 19 | DAVE (CVPR 2024) đã dùng CLIP để lọc, nhóm em mới ở đâu? | DAVE quyết định theo cụm khung và huấn luyện bộ phát hiện riêng. F quyết định cho từng khung, gắn vào CountGD++ có sẵn, không huấn luyện, kết hợp điểm CLIP với điểm CountGD++. Đóng góp chính của nhóm là chẩn đoán lỗi lượt 2 trên ảnh nhiều loại và kiểm chứng bằng giao thức khóa trước | Triệu | — |
| 20 | Thử nghiệm gán khung theo CLIP chỉ trên dev, có tin được không? | Chỉ là sơ bộ. Khai báo trước, không có tham số nào phải chỉnh, không chạy trên test, không đổi kết quả chính. Dev đã dùng để chọn F nên số lạc quan; muốn kết luận cần một tập mới | Triệu | — |

**Mẹo trả lời:**

1. Nhắc lại câu hỏi bằng lời mình.
2. Trả lời trong 1–2 câu, kèm 1 con số.
3. Nói giới hạn nếu có.
4. Không biết thì nói "nhóm chưa kiểm điều đó; nếu làm, nhóm sẽ…". Đừng đoán.

# 5. Demo tĩnh (khuyên dùng thay demo trực tiếp)

- Dùng 4 hình `reports/figures/fig_example_*.png`. Mỗi hình đặt 4 cách cạnh nhau, khung tô màu theo đúng / sai loại.
- **Thứ tự kể:**
  1. thành công (blueberries);
  2. lỗi X/Y còn lại (bowls–đĩa);
  3. thất bại (dogs–dê);
  4. lọc quá tay (people).
- Lý do không demo trực tiếp: cần GPU + mạng, dễ hỏng lúc trình bày. Nhóm khác demo Gradio. Nếu nhóm muốn làm, xem mục 8.

# 6. Phân công nói và đóng góp (đề xuất, chốt tối nay)

| Phần | Trí | Triệu |
|---|---|---|
| Mở đầu, bài toán, mô hình, cải tiến, kết quả chính, kết luận | S1–S5, S8, S10, S15–S16 | |
| Chẩn đoán, giao thức, phân tích, bài học | | S6, S7, S9, S11, S12, S14 |
| Ví dụ | S13 (một nửa) | S13 (một nửa) |
| Đóng góp thực tế | Pilot, review bằng mắt, kiểm dev, khóa cấu hình, báo cáo chi tiết | Kiểm chéo evaluator, N4 (117 khung), kiểm test, chạy dev + test + khảo sát trên Kaggle, so sánh nhóm khác, Related Work |

# 7. Hành trang ngày báo cáo (checklist)

- [ ] File slide (`.pptx` + bản `.pdf` dự phòng), chép vào USB và lưu trên Drive.
- [ ] Báo cáo cuối `.pdf`.
- [ ] Mở sẵn repo GitHub trên trình duyệt.
- [ ] Bản in hoặc trên điện thoại: [bảng số tra nhanh](CAM_NANG_DO_AN_CS331.md#10-bảng-số-tra-nhanh-thuộc-lòng-các-số-in-đậm) và bảng câu hỏi phản biện (mục 4).
- [ ] Hình ví dụ ở độ phân giải gốc, phòng khi máy chiếu mờ.
- [ ] Laptop sạc đầy, bộ chuyển HDMI.
- [ ] Đã tập ít nhất 2 lần, bấm giờ.

# 8. Lịch từ nay đến 02/12

| Ngày | Việc | Ai |
|---|---|---|
| 22/11 | Triệu: khảo sát, Related Work, đọc cẩm nang. **Tối: họp chốt** (mục 9) | Triệu; cả hai buổi tối |
| 23–25/11 | Báo cáo cuối: chuyển bản chi tiết thành bản nộp, thêm Related Work + khảo sát | Trí chính, Triệu rà |
| 24/11 | Đóng khảo sát FSC-147 | Triệu + assistant |
| 25–28/11 | Làm slide theo mục 2, chèn hình | chia theo mục 6 |
| 29–30/11 | Tập 2 lần, bấm giờ; luyện câu hỏi mục 4 | cả hai |
| 01/12 | Rà bản nộp (báo cáo, slide, repo), đẩy bản cuối | cả hai |
| **02/12** | **Nộp** | |

# 9. Chương trình buổi họp tối 22/11 (khoảng 60–75 phút)

1. (10 phút) Triệu báo kết quả ngày hôm nay: khảo sát, Related Work, chỗ chưa hiểu.
2. (10 phút) Chốt thời lượng trình bày thầy yêu cầu và mẫu slide / mẫu báo cáo (nếu thầy có quy định).
3. (15 phút) Đi qua dàn slide mục 2; sửa nếu cần; chốt ai nói slide nào.
4. (15 phút) Hỏi nhau 10 câu ở mục 4; ghi câu nào chưa trả lời được.
5. (10 phút) Quyết các việc ở mục 10.
6. (5 phút) Chốt lịch mục 8 và ghi vào `BAT_DAU_SESSION_MOI.md`.

# 10. Việc chờ Trí quyết (assistant đề xuất, Trí chưa giao)

| # | Đề xuất | Lợi | Chi phí | Assistant khuyên |
|---|---|---|---|---|
| Q1 | Assistant dựng **bản nháp slide `.pptx`** theo dàn mục 2, chèn hình có sẵn | Tiết kiệm 3–4 giờ | Nhóm vẫn phải chỉnh lời, giao diện | **Nên** |
| Q2 | Assistant chuyển bản chi tiết 22 trang thành **bản nháp báo cáo cuối** (chèn Related Work + khảo sát khi có) | Đỡ việc 23–25/11 | Trí phải rà | **Nên** |
| Q3 | Demo Gradio trực tiếp (ảnh X/Y, so B0 và P+F) | Gây ấn tượng, nhóm khác có | Cần GPU và mạng lúc trình bày, rủi ro hỏng; khoảng nửa ngày làm | Không, trừ khi thầy yêu cầu demo trực tiếp |
| Q4 | Kiểm giả thuyết H2 (so điểm token chữ lượt 1 và lượt 2) | Trả lời trọn RQ1 | Cần raw `.npz` trên Kaggle + chạy; trái tinh thần "không mở rộng thử nghiệm" | Không, để hướng phát triển |
| Q5 | Thêm slide 1 phút "nhóm dùng AI hỗ trợ ra sao" | Minh bạch, tránh bị hỏi bất ngờ | Không đáng kể | Tùy quy định của thầy |
| Q6 | Gộp các ghi chú chưa commit trên máy Trí (BAT_DAU/WORKLOG) vào `main` | Repo thống nhất | 10 phút | **Nên**, khi Trí rảnh |
