# Hướng dẫn kiểm absent/GT tập dev_test_v2 (W4 và phần kiểm dev của Trí)

*Assistant soạn ngày 11/11/2026 theo yêu cầu của Triệu, dựa trên [hướng dẫn kiểm p4_unseen_v1](../p4_unseen_v1/HUONG_DAN_KIEM_DU_LIEU.md) và lưu ý W4 trong [GIAO_VIEC_TRIEU_20261106.md](../../../HANDOFF/GIAO_VIEC_TRIEU_20261106.md). File này không chứa xác nhận của ai.*

| Người | Tập | Phải kiểm |
|---|---|---|
| Triệu | test, `t01`–`t40` | 40 dòng absent + 80 dòng GT có mặt |
| Trí | dev, `d01`–`d20` | 20 dòng absent + 40 dòng GT có mặt |

Tập vẫn là `DRAFT_NOT_LOCKED` cho tới W5. Không chạy model trên tập nào trước khi khóa.

## 1. Tạo ảnh chấm GT (một lần, CPU, khoảng 1 phút)

Script [render_gt_review_v2.py](../render_gt_review_v2.py) chỉ đọc nhãn và ảnh MUCCA rồi vẽ điểm. Nó không sửa file dữ liệu, không chạy model, và **chỉ ghi ra ngoài repo** (ảnh không commit, theo D10). Chạy từ thư mục gốc CS331:

```text
python experiments/countgdpp/render_gt_review_v2.py --split test --mucca <thư mục MUCCA_1.0> --out <thư mục ngoài repo>
```

Trí dùng `--split dev`. Script kiểm hash `annotations.json` và từng ảnh so với `selection_meta.json` trước khi vẽ.

Mở `<out>/<split>/index.html` bằng Edge hoặc Chrome. Mỗi ảnh có một khối gồm:
- bảng số điểm, lớp vắng mặt đề xuất và các lớp dự phòng;
- **ảnh chấm GT**: nửa trái là lớp của query `_1`, nửa phải là lớp của query `_2`, số thứ tự đặt cạnh từng điểm;
- **ảnh gốc** không có chấm.

Ảnh nhỏ được phóng to tới chiều rộng 1000 px. Bấm vào ảnh để mở cỡ đầy đủ rồi zoom.

**Điểm vẽ ra chính là nhãn MUCCA.** Số chấm khớp `gt_count` không chứng minh nhãn đúng: phải nhìn từng vật.

## 2. Kiểm absent: một dòng mỗi ảnh trong `absent_candidates.csv`

1. Đọc `proposed_absent`, mở ảnh gốc, rà **toàn ảnh**, kể cả vật nhỏ, bị che hay ở mép ảnh. Câu hỏi là "loại này có xuất hiện không?".
2. **Không có:** `human_check=absent_ok`, `checked_by=<tên>`, `date=YYYY-MM-DD` (ngày kiểm thật), `note` ghi ngắn căn cứ, ví dụ `Da ra toan anh; khong thay forks`.
3. **Có, hoặc nghi là có:** **đổi sang lớp dự phòng kế tiếp** trong `next_candidates` (đọc từ trái sang phải). Lớp mới cũng phải được xem ảnh xác nhận vắng mặt, không mặc định nó vắng. **Không ghi `uncertain`** (lưu ý W4). `note` ghi dạng `Cu: forks; thay o goc trai duoi; doi sang: spoons; kiem spoons: khong thay`.
4. Nếu hết lớp dự phòng phù hợp thì **dừng ảnh đó và báo lại**. Đây là trường hợp bất thường theo GIAO_VIEC §5.

Khi đổi lớp, ba file phải khớp nhau theo `image_id` + `query_id`:

| File | Đổi gì |
|---|---|
| `absent_candidates.csv` | `proposed_absent` = lớp mới; `proposed_type` nếu đổi siêu nhóm (ghi rõ trong `note` là thay sau kiểm người); `human_check=absent_ok` cho lớp cuối |
| `<split>/manifest.csv` | Dòng `presence_status=absent` của ảnh đó: `class_id`, `target_class`, `prompt` (mã lớp lấy ở `class_mapping.json`; `sheeps` → prompt `sheep`, `cigaretts` → `cigarettes`); giữ `gt_count=0` và ID |
| `<split>/inputs.jsonl` | Dòng cùng `query_id`: chỉ đổi `prompt` |

Đồng bộ này là thao tác máy móc. Người kiểm chỉ cần ghi quyết định vào `absent_candidates.csv`, rồi assistant có thể đồng bộ hai file kia và báo lại phần đã đổi.

## 3. Kiểm GT có mặt: hai dòng mỗi ảnh trong `<split>/manifest.csv`

1. Mở ảnh chấm GT. Với từng nửa ảnh, xem ba điều: mỗi điểm có nằm trên một vật đúng loại không; có điểm nào lặp trên cùng một vật không; có vật nhìn thấy mà không có điểm không. Đối chiếu thêm với ảnh gốc ở chỗ chấm che vật.
2. **Đồng ý với số MUCCA:** `verified_by=<tên> | YYYY-MM-DD | visual_checked`, `uncertainty_note=Da doi chieu anh va diem nguon; khong thay bat dong`.
3. **Nghi ngờ:** `verified_by` ghi giống như trên; `uncertainty_note` ghi cụ thể, ví dụ `nguon 12, toi thay chac 11; diem 7 nam tren dia, khong phai coc`. **Giữ nguyên `gt_count` theo MUCCA**, không đổi `presence_status` (lưu ý W4).
4. Dòng absent trong manifest: `verified_by=<tên> | YYYY-MM-DD | absent_ok`, `uncertainty_note=Da ra toan anh; khong thay <lop>`.

## 4. Cách ghi kết quả

- **Cách A (khuyên dùng):** kể kết quả từng ảnh trong chat với assistant, ví dụ `t01: absent ok; GT 2 lớp ok` hay `t05: thấy forks ở góc trái → đổi; cups nguồn 6 tôi thấy 5`. Assistant điền vào các file và lưu nguyên văn lời người kiểm vào `human_review_<split>_<ngày>.json` (giống `p4_unseen_v1/human_review_20261027.json`), kèm hash file trước và sau khi điền.
- **Cách B:** tự sửa CSV bằng VS Code. **Không dùng Excel**: Excel đổi xuống dòng và bảng mã, từng thêm một cột trống ở v1. Ô có dấu phẩy phải nằm trong dấu ngoặc kép `"..."`.

Làm theo lô khoảng 10 ảnh rồi lưu hoặc báo, để không mất kết quả giữa chừng.

## 5. Sau khi cả dev và test đã kiểm (W5)

Khóa giống `p4_unseen_v1`: đổi `selection_meta.json` sang `status=LOCKED`, thêm `locked_by`, `locked_at`, `review_protocol` (bản hướng dẫn này) và `locked_file_sha256` của `dev/inputs.jsonl`, `dev/manifest.csv`, `test/inputs.jsonl`, `test/manifest.csv` và `absent_candidates.csv`. Việc khóa là người ký, không tự động. Chỉ khóa khi không còn dòng `PENDING`.
