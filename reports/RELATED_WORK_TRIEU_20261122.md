# Công trình liên quan (Related Work) — bản nháp W7, 22/11/2026

*Bản nháp do trợ lý AI (Claude) soạn theo yêu cầu của Triệu. Triệu đọc và sửa câu chữ trước khi đưa vào báo cáo cuối.*

**Assistant đã đọc gì (22/11):**

| Bài | Đã đọc | Chưa đọc |
|---|---|---|
| PseCo (2311.12386) | Tóm tắt trên arXiv | Toàn văn |
| VA-Count (2407.04948) | Tóm tắt trên arXiv; README GitHub của tác giả (ghi ECCV 2024) | Toàn văn; danh sách kỷ yếu ECCV |
| DAVE (2404.16622) | Tóm tắt; mục 3.2 (bước kiểm), 3.3 (zero-shot và theo câu chữ), 3.4 (huấn luyện) bản HTML trên arXiv | Phần thực nghiệm |
| PrACo (2409.15953) | Tóm tắt; mục 3.2 và 3.3 (hai phép thử) bản HTML trên arXiv | Phần thực nghiệm |

- CountGD, CountGD++, GroundingDINO, MUCCA, CLIP và FSC-147: lấy theo mục Tài liệu tham khảo của `reports/BAO_CAO_CHI_TIET_DO_AN_20261112.md` (theo WORKLOG 12/11, Trí đã kiểm số arXiv).
- Bản nháp chỉ mô tả ý chính, **không trích con số hay kết quả** của các bài.

**Ba chỗ ⚠ cũ đã kiểm xong (22/11):**
1. **VA-Count:** ECCV 2024. Nguồn: README GitHub của chính tác giả (tên repo, mục News, mục BibTeX). Trang arXiv không ghi nơi công bố; chưa đối chiếu với danh sách kỷ yếu.
2. **PrACo:** hai phép thử là *negative-label test* và *mosaic test* (mô tả ở mục d).
3. **DAVE:** bước kiểm dùng phân cụm trên đặc trưng học được. Bản theo câu chữ dùng CLIP để loại cụm (mô tả ở mục c). Đây là công trình **gần bước F nhất**, nên mục c nói rõ khác biệt.

---

## 2.3 Công trình liên quan

### a) Đếm không phân biệt lớp theo mẫu

Ranjan và cộng sự (2021) đặt bài toán đếm không phân biệt lớp (class-agnostic counting) và công bố bộ FSC-147. Người dùng chỉ ra loại vật cần đếm bằng vài khung mẫu ngay trên ảnh, và các lớp ở tập test không xuất hiện khi huấn luyện. FSC-147 trở thành benchmark chuẩn của hướng này. Mỗi ảnh chủ yếu có một loại vật nổi bật, nên benchmark không kiểm được mô hình có đếm đúng loại được hỏi hay không khi ảnh có nhiều loại. Đây là điểm xuất phát của đồ án.

### b) Đếm theo câu chữ

**CountGD** (Amini-Naieni, Han & Zisserman, NeurIPS 2024) cải tạo mô hình phát hiện vật theo câu chữ GroundingDINO (Liu và cộng sự, ECCV 2024) thành mô hình đếm. Mô hình nhận câu chữ, khung mẫu, hoặc cả hai.

**CountGD++** (Amini-Naieni & Zisserman, CVPR 2026) mở rộng cách chỉ định vật cần đếm:
- mẫu giả do chính mô hình tự chọn lúc suy luận;
- mẫu lấy từ ảnh ngoài;
- câu chỉ định "không đếm cái gì".

Đồ án dùng checkpoint công khai của CountGD++ và không huấn luyện lại. Khác với bài gốc (đánh giá chủ yếu trên ảnh một loại), đồ án đo cơ chế mẫu giả hai lượt trên ảnh có nhiều loại vật. Ở đó, mẫu tự chọn có thể rơi vào vật loại khác và kéo lượt 2 đếm sai.

### c) Tự tạo mẫu và kiểm ứng viên

Một nhóm phương pháp tránh việc người dùng phải vẽ khung mẫu bằng cách tự tạo hoặc tự kiểm vật ứng viên:

- **PseCo** (Huang và cộng sự, CVPR 2024): đếm theo mẫu hoặc theo tên lớp. SAM sinh các mặt nạ đề xuất, sau đó CLIP phân loại các đề xuất này. Bộ phân loại dựa trên CLIP được **huấn luyện** bằng chưng cất tri thức.
- **VA-Count** (Zhu và cộng sự, ECCV 2024): đếm chỉ với tên lớp. Một mô-đun dùng mô hình thị giác–ngôn ngữ tìm mẫu tiềm năng. Một mô-đun khác học tương phản để phân biệt mẫu tốt với mẫu kém, nhằm giảm tác hại của **mẫu sai**.
- **DAVE** (Pelhan và cộng sự, CVPR 2024): theo hướng "phát hiện rồi kiểm".
  - Trước hết tạo một tập phát hiện có độ phủ cao.
  - Bước kiểm lấy đặc trưng của từng khung qua một mạng nông **được huấn luyện**, rồi phân cụm phổ (spectral clustering) theo độ giống cosine. Chỉ giữ các cụm có chứa khung mẫu; các khung còn lại bị coi là ngoại lai và bị loại.
  - DAVE có bản zero-shot và bản theo câu chữ. Bản theo câu chữ dùng CLIP so câu chữ với từng **cụm** khung, rồi loại cụm có độ giống thấp hơn một tỉ lệ so với cụm giống nhất.

**Liên hệ với đồ án.** Hai bước cải tiến của đồ án cùng tinh thần với nhóm này, nhưng khác ở chỗ **không huấn luyện gì** và chỉ gắn thêm vào một mô hình đã có:
- Bước **P** (CLIP kiểm mẫu giả trước lượt 2) nhắm cùng vấn đề mẫu sai mà VA-Count nêu, nhưng chỉ dùng một ngưỡng cosine CLIP chọn trên dev, không học thêm mô-đun nào.
- Bước **F** (lọc từng khung bằng điểm kết hợp CountGD++ + CLIP) **gần nhất với bản theo câu chữ của DAVE**: cả hai đều dùng CLIP so khung với câu chữ để loại vật sai. Khác ở ba điểm:
  1. DAVE quyết định theo **cụm** khung; F quyết định cho **từng khung**.
  2. DAVE dựa trên đặc trưng và bộ phát hiện **được huấn luyện** riêng; F gắn vào CountGD++ có sẵn, không huấn luyện.
  3. F kết hợp điểm CLIP với điểm của chính CountGD++, theo một ngưỡng cố định chọn trên dev; DAVE dùng ngưỡng tương đối so với cụm giống nhất.
- Khác PseCo, CLIP trong đồ án không được huấn luyện lại và không tự đếm. CLIP chỉ đóng vai người kiểm thứ hai.

Kết quả của đồ án cho thấy, trong ảnh nhiều loại, **bước kiểm khung (F) mang lại cải thiện**, còn kiểm mẫu với ngưỡng đã chọn (P) gần như không đổi bộ mẫu.

### d) Đánh giá độ bám câu chữ

- **PrACo** (Ciampi và cộng sự, WACV 2025): bộ kiểm cho đếm theo câu chữ, gồm hai phép thử trên ảnh FSC-147:
  - *Negative-label test:* hỏi ảnh một loại bằng tên của loại **không có** trong ảnh; đáp án đúng là 0.
  - *Mosaic test:* ghép hai ảnh một loại thành một ảnh, chỉ hỏi loại của nửa trên; đáp án đúng là chỉ đếm nửa trên, không đếm nửa dưới.

  Mỗi phép thử có chỉ số riêng (NMN, PCCN cho phép thử thứ nhất; CntP, CntR, CntF1 cho phép thử thứ hai). Các tác giả nhận thấy mô hình mạnh đạt điểm tốt trên chỉ số đếm thông thường nhưng **chưa thật sự hiểu câu chữ** được hỏi.
- **MUCCA và PrACo++** (Pacini và cộng sự, 2026): bộ ảnh thật, trong đó nhiều loại vật được gán nhãn cùng lúc trong một ảnh, kèm bộ kiểm PrACo++ (hỏi loại vắng mặt, đếm khi có vật gây nhiễu). Các tác giả báo rằng mô hình mạnh vẫn yếu ở khả năng bám đúng câu chữ.

**Liên hệ với đồ án.** Đồ án dùng dữ liệu MUCCA và cùng tinh thần đánh giá: có câu hỏi về loại vắng mặt, có vật gây nhiễu cùng ảnh. Khác với mosaic của PrACo (ghép hai ảnh, hai loại nằm ở hai nửa tách biệt), ảnh MUCCA là ảnh thật, các loại nằm lẫn với nhau và có thể rất giống nhau (bát–đĩa). Đây đúng là trường hợp đồ án thấy khó nhất. Đồ án khác các bộ kiểm ở ba điểm:
1. Không chỉ **đo** lỗi mà **chẩn đoán và sửa** lỗi cho một mô hình cụ thể (CountGD++).
2. Đo trực tiếp yêu cầu "đổi câu hỏi thì đổi khung" bằng **tỉ lệ khung dùng chung giữa X và Y**.
3. Kiểm chứng bằng giao thức **chọn trên dev, khóa rồi chạy test một lần**.

### e) CLIP làm bộ kiểm

CLIP (Radford và cộng sự, ICML 2021) học từ rất nhiều cặp ảnh–chú thích, nên so được một ô ảnh với một câu mô tả mà không cần huấn luyện cho từng lớp. Đồ án dùng CLIP theo cách zero-shot đó: so ô cắt của từng khung (hoặc từng mẫu giả) với câu "a photo of {X}". Giới hạn ghi ở phần hạn chế: với ô cắt nhỏ và các loại gần nghĩa (dê–chó), điểm CLIP không đủ để tách loại.

### Vị trí của đồ án

Các công trình trên hoặc **huấn luyện** mô hình đếm mới (PseCo, VA-Count, DAVE), hoặc **đánh giá** mô hình có sẵn (PrACo, MUCCA). Đồ án nằm giữa hai hướng: lấy một mô hình đếm theo chữ mạnh, công khai (CountGD++), chẩn đoán lỗi đếm nhầm loại trên ảnh nhiều loại, rồi thử các bước kiểm **không cần huấn luyện** ở đầu ra, với giao thức đánh giá khóa trước.

---

## Tài liệu tham khảo bổ sung (thêm vào danh sách hiện có)

- Huang, Z., Dai, M., Zhang, Y., Zhang, J., & Shan, H. (2024). Point, segment and count: A generalized framework for object counting. *CVPR 2024*. arXiv:2311.12386.
- Pelhan, J., Lukežič, A., Zavrtanik, V., & Kristan, M. (2024). DAVE – A detect-and-verify paradigm for low-shot counting. *CVPR 2024*. arXiv:2404.16622.
- Zhu, H., Yuan, J., Yang, Z., Guo, Y., Wang, Z., Zhong, X., & He, S. (2024). Zero-shot object counting with good exemplars. *ECCV 2024*. arXiv:2407.04948.

Các tài liệu còn lại (Ranjan 2021, CountGD, CountGD++, GroundingDINO, PrACo, MUCCA, CLIP) đã có trong báo cáo chi tiết.
