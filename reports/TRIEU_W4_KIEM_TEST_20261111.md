# W4 — Triệu kiểm 40 ảnh test dev_test_v2 (11/11/2026)

*Assistant soạn theo yêu cầu của Triệu. Phần nhận xét về ảnh là của Triệu, gửi trong chat; nguyên văn từng câu nằm trong [human_review_test_20261111.json](../experiments/countgdpp/dev_test_v2/human_review_test_20261111.json). Assistant chỉ đối chiếu từng câu báo với tọa độ điểm MUCCA và ảnh phóng to.*

## 1. Kết quả

- **Đã kiểm t01–t40:** 40 query vắng mặt, 80 query có mặt. Quy ước của Triệu: "tôi sẽ nói các ảnh có lỗi thôi, các ảnh bị skip qua mà không nói đến = đã đúng". Lời xác nhận cuối: "xác nhận tất cả đều đã chuẩn".
- **Ghi theo D11**, cùng định dạng dev của Trí:
  - 67 query `visual_checked`;
  - 13 query `needs_review` (GT giữ số MUCCA, số Triệu đếm ghi trong `uncertainty_note`);
  - 40 query `absent_checked`.
- **Đổi 1 lớp vắng mặt:** t37_3 (mcac_204) từ `pencils` sang `cups`. Ảnh có 3 bút chì, và cups là ứng viên kế tiếp đầu tiên. Triệu xác nhận không có cốc. Loại query đổi từ khó sang dễ, nên số absent loại khó của test còn 28/40.
- **Quy ước key holders (t29–t31):** vòng kim loại trơn và dây xâu chìa **không** tính là key holders. Căn cứ là cách chính MUCCA gán nhãn lớp này ở mcac_162–164: chỉ móc khóa trang trí (thẻ, mặt dây, móc nhựa, carabiner) có điểm. Mảng xanh ngọc mà Triệu hỏi là ổ khóa.
- Tập vẫn `DRAFT_NOT_LOCKED`; `selection_meta.json` chưa đổi.

## 2. Bảng độ nhạy cho D11 ("nếu dùng số Triệu đếm")

| Query | Ảnh | Lớp | MUCCA | Triệu | Lý do |
|---|---|---|---:|---|---|
| t04_2 | mcac_19 | blueberries | 25 | 24 | điểm 17 và 23 trùng một quả |
| t07_2 | mcac_75 | motorbikes | 27 | 28 | thiếu xe đỏ giữa điểm 23 và 26 |
| t08_1 | mcac_76 | people | 30 | 31 | thiếu 1 người cạnh điểm 27 (ảnh 480×270) |
| t13_2 | mcac_93 | cars | 7 | 8 | thiếu 1 xe sau xe điểm 7 |
| t14_1 | mcac_95 | people | 27 | 26 | điểm 15 và 16 trùng một người |
| t15_1 | mcac_103 | amplifiers | 19 | 19–21 | thiếu âm ly dưới điểm 15; điểm 7 là thùng đỏ không núm, không nhất quán với thùng vàng dưới điểm 10 |
| t16_2 | mcac_104 | guitars | 30 | 31 | thiếu guitar đen sau guitar đỏ điểm 25 |
| t21_2 | mcac_124 | dogs | 27 | 26 | điểm 1 và 3 trùng một con; nhóm từ điểm 19 rất dày, kiểm được khoảng 90% |
| t23_2 | mcac_135 | windows | 20 | 19–20 | điểm 14 không chắc là cửa sổ hay khung cửa mở |
| t27_2 | mcac_147 | desks | 7 | 8 | thiếu bàn ở góc trên bên phải |
| t37_1 | mcac_204 | pens | 3 | 0 | 3 vật là bút chì gỗ (xem mục 3) |
| t39_1 | mcac_222 | people | 31 | 32 | thiếu người áo cam giữa điểm 29 và 30 (ảnh 390×280) |
| t39_2 | mcac_222 | motorbikes | 28 | 29 | thiếu xe của người áo cam, bị người 30 che |

Ngoài ra: t27_1 (chairs) có số khớp 11, nhưng điểm 11 bị đặt lệch lên góc bàn; ghế thật nằm ngay phía sau. Lỗi này không ảnh hưởng MAE, chỉ ảnh hưởng khi dùng điểm GT để đối chiếu khung.

## 3. Cần Trí quyết trước khi chạy test (23–24/11)

**t37_1 (mcac_204, `pens`, GT 3):** ba vật MUCCA gán `pens` là bút chì gỗ (đầu gọt lộ gỗ, hai cây có tẩy). Khác các ca thiếu hay thừa một điểm, ở đây có thể GT đúng là 0, vì ảnh không có cây bút mực nào. D11 giữ GT 3, nên hiện file vẫn ghi 3 và `needs_review`. Ba cách:

1. giữ GT 3 theo D11 và ghi vào hạn chế;
2. loại t37_1 khỏi phần chấm (`evaluate_research.py` đã nhận `uncertain` từ 10/11), ghi lý do;
3. thay cả ảnh mcac_204, nhưng như vậy là rút lại một phần tập test.

Assistant nghiêng về cách 1 hoặc 2. Quyết định là của Trí, và phải chốt **trước** khi chạy test.

> **Đã chốt 11/11, trước khi khóa:** Trí chọn **cách 2** ở trên (Triệu chuyển lời trong chat; trong bảng hỏi của Trí, cách này là "1. Đánh uncertain, loại khỏi chấm"). `test/manifest.csv` dòng t37_1: `presence_status=uncertain`; `gt_count=3` giữ để lưu vết; ghi chú nêu lý do. Evaluator bỏ query này khỏi mọi chỉ số. Còn 119 query được chấm: 79 có mặt, 40 vắng mặt. Ghi trong `selection_meta.json` → `post_selection_changes`.

## 4. File đã sửa (chỉ các dòng test)

| File | Thay đổi | sha256 sau khi sửa |
|---|---|---|
| `absent_candidates.csv` | 40 dòng test: `human_check`, `checked_by`, `date`; `note` ở 4 dòng; t37: `proposed_absent`, `proposed_type` | `375744ce255dbf00d2c65680c746ad0ae414c731bcb4722dad42661c30e68473` |
| `test/manifest.csv` | 120 dòng: `verified_by`, `uncertainty_note`; t37_3: `class_id` 2, `target_class`/`prompt` cups | `1f54ec20b45afaaf797c26a592aaeb02450d606fb2334f2a79a3743bb0b635a1` |
| `test/inputs.jsonl` | t37_3: `prompt` cups | `5fdf6120665122ac87d7026526f3a5831a8eb4e2ea9ceb7c8ecb6aaab7f462ad` |

**Kiểm sau khi sửa (assistant, chỉ đọc):**
- Dòng dev và các cột khác không đổi.
- Lớp vắng mặt mới (cups) không có nhãn trong ảnh.
- `inputs.jsonl` khớp từng dòng với manifest; file UTF-8, xuống dòng LF, không BOM.

**Bước tiếp:** W5 khóa cả dev và test (`status=LOCKED`, người/ngày, hash), sau khi Trí trả lời mục 3 hoặc chấp nhận để t37_1 cho tới lúc chấm test.
