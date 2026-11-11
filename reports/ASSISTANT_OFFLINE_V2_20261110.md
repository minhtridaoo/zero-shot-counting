# Phần việc assistant — kết quả ngày 10/11/2026

Trí đã cho phép **kiểm thử CPU** trực tiếp trong chat. Không chạy model/GPU, không đánh giá tập test v2, không ký duyệt hay khóa dữ liệu/cấu hình.

## Đã hoàn thành

| Việc | Bằng chứng / giới hạn |
|---|---|
| Kiểm hồi quy evaluator đã sửa `uncertain` | Đạt: so số MAE từng cách với tính độc lập; fixture uncertain được loại, fixture absent có FPR đúng, tất cả uncertain bị từ chối. Hash evaluator/manifest/counts gốc không đổi |
| Xuất T/P+T ngoại tuyến | File mới `offline_text_v2.py`; replay **30/30 query** raw p4_unseen_v1 khớp khung và điểm nguồn trước khi chuyển T. Đây là kiểm triển khai, không phải đánh giá hiệu quả v2 |
| Gom nguồn, tái sử dụng CLIP | File mới `bundle_offline_v2.py`; kiểm hash cùng run và rank/tọa độ để lấy đúng CLIP của khung gốc |
| S/F riêng nguồn, D9 | File mới `select_offline_v2.py`; fit thử chẩn đoán trên **7 nguồn / 21 cách** của pilot P1. Pilot không có absent nên D9 báo không đủ điều kiện; không xuất freeze |
| Bộ kiểm | **10/10 PASS**; log ở `results/countgdpp/offline_v2_cpu_20261110/checks.txt` |

Hướng dẫn và lệnh: [OFFLINE_V2_HUONG_DAN.md](../experiments/countgdpp/OFFLINE_V2_HUONG_DAN.md).

## Chưa được coi là hoàn thành

- **Chưa kiểm kết quả dev W6:** dữ liệu mới vẫn chưa kiểm/khóa; chưa có output W6 để chấm.
- **Chưa chạy P+T trên raw P1 thật tại máy này:** raw không có trong repo theo D10. Đã kiểm logic T trên raw B2 thật và ghép CLIP bằng fixture; cần chạy trên Drive/Colab nơi giữ raw P1 để xác nhận toàn luồng P+T.
- Bundle hỗ trợ một run P1/một M. Nếu chạy nhiều M, cần bổ sung bước ghép có kiểm cùng stage1/GPU trước khi chọn D9 toàn bộ lưới; không tự chọn riêng từng M rồi tuyên bố thắng toàn lưới.
- D9 chưa chốt xử lý nhiều cấu hình thắng bằng điểm: công cụ liệt kê để nhóm quyết định. Chưa có công cụ áp dụng freeze v2 lên test trong gói này.

## Hồ sơ kiểm

Thư mục: `results/countgdpp/offline_v2_cpu_20261110/`.
- `text_replay_final/`: output kiểm T bằng bản script cuối; `text_replay/` là kiểm ban đầu trước bổ sung hash output.
- `pilot_bundle.json`, `pilot_manifest_subset.csv`, `pilot_diagnostic/selection.json`: kiểm fit bằng đúng 15 query pilot. Manifest gốc có 30 query; lần thử với cả manifest bị chặn thiếu coverage, nên tạo bản con riêng 15 query, không sửa bản gốc.
- `checks.txt`, `check_provenance.json`: kết quả bộ kiểm và hash.

Ngưỡng fit trong thư mục chẩn đoán chỉ chứng minh công cụ chạy được; không dùng làm cấu hình v2 hoặc làm bằng chứng cải tiến. Các script cũ, prediction, freeze và dữ liệu gốc được giữ nguyên. Chưa commit/push các file của phiên này.
