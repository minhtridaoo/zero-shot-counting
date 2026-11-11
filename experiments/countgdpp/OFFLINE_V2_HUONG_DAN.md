# Công cụ ngoại tuyến T / S / F / D9 — 10/11/2026

Chạy từ thư mục gốc CS331, Python có NumPy. Các lệnh dưới chỉ dùng output đã lưu; không gọi model hoặc CLIP. Không sửa runner hay evaluator cũ. Kết quả kiểm công cụ ở [báo cáo](../../reports/ASSISTANT_OFFLINE_V2_20261110.md).

## 1. T và P+T

T dùng raw lượt 2 của B2; P+T dùng raw lượt 2 của từng `tau` P. Giữ nguyên threshold 0.23: điểm chữ **> 0.23** và **> điểm phía sau dấu chấm**. Điểm chữ là max trên token tên lớp trước dấu chấm, bỏ CLS/SEP/padding/dấu câu và token mẫu `1008`. Điểm cuối lưu lại là điểm chữ, không phải max có chứa mẫu ảnh. Không có pseudo thì giữ nguyên B0.

Script kiểm replay gốc (số khung, tọa độ, điểm) trước khi xuất T. T là tập con khung gốc ở cùng threshold; dùng `original_ranks` để tái sử dụng đúng crop CLIP, không chấm CLIP lại.

Ví dụ sau khi có raw P1 trên máy/Drive (thay đường dẫn run và tên output cho phù hợp):

```powershell
python experiments/countgdpp/offline_text_v2.py --predictions results/countgdpp/RUN/predictions_B2.jsonl --raw-run results/countgdpp/RUN --out results/countgdpp/RUN_T
python experiments/countgdpp/offline_text_v2.py --predictions results/countgdpp/RUN/predictions_tau0.220.jsonl --raw-run results/countgdpp/RUN --out results/countgdpp/RUN_tau022_T
```

Lặp lệnh thứ hai cho **tất cả tau đã định trước**, không chọn tau dựa trên test. Đây là thao tác trên từng output của cùng lần chạy; không trộn khác GPU hoặc khác stage1. Raw P1 không được push theo D10 nên phải dùng bản trên Drive. Các raw P1 hiện không có tại checkout này.

## 2. Gom nguồn và điểm CLIP đã lưu

Cần output `p1_controls.py` của đúng run (có `sources_predictions.jsonl`, `kept_boxes.json`, `run_config.json`). Công cụ mới chỉ lấy khung/điểm; **bỏ quyết định giữ/xóa theo ngưỡng cũ**. Lần chạy dev vẫn cần tạo điểm CLIP của các nguồn gốc theo quy trình Colab đã có; các công cụ này không thay bước tạo điểm CLIP.

```powershell
python experiments/countgdpp/bundle_offline_v2.py --controls results/countgdpp/RUN_controls --text-source T B2 results/countgdpp/RUN_T/predictions.jsonl --text-source tau0.220_T tau0.220 results/countgdpp/RUN_tau022_T/predictions.jsonl --out results/countgdpp/RUN_offline/bundle.json
```

Thêm một `--text-source` cho mỗi tau. Không truyền `--text-source` nếu chỉ kiểm B0/B2/P. `NAME ORIGINAL PREDICTIONS` lần lượt là tên nguồn mới, tên nguồn gốc, file T. Script kiểm hash nguồn và file T, thứ tự/rank, tọa độ và bộ query trước khi ghép CLIP. Bundle hiện gom **một run P1 (một M)**; không tự gộp nhiều run M khác nhau.

## 3. Fit S/F riêng từng nguồn, rồi chọn D9

```powershell
python experiments/countgdpp/select_offline_v2.py --bundle results/countgdpp/RUN_offline/bundle.json --manifest experiments/countgdpp/dev_test_v2/dev/manifest.csv --selection-meta experiments/countgdpp/dev_test_v2/selection_meta.json --out results/countgdpp/RUN_dev_selection
```

- Chặn dữ liệu chưa `LOCKED`, `verified_by` trống/PENDING, split khác `dev_v2`, thiếu absent, thiếu/nhân đôi query hoặc sai image ID. Manifest phải khớp chính xác bộ query của run.
- Loại `uncertain` trước cả fit ngưỡng, tính min/max và chấm điểm.
- Mỗi nguồn có S riêng, min/max CountGD và CLIP riêng, F = 0.5 × điểm CountGD chuẩn hóa + 0.5 × điểm CLIP chuẩn hóa. Dùng min/max trên dev; khoảng hằng số chuẩn hóa thành 0.5.
- Quy tắc chọn ngưỡng giống 21/10: midpoint giữa các giá trị, hai đầu giữ tất cả/loại tất cả; tối thiểu MAE, rồi RMSE, rồi ngưỡng nhỏ hơn; giữ khung khi điểm **>= ngưỡng**.
- D9: MAE toàn dev nhỏ nhất trong các cách có MAE có mặt và FPR_absent không tệ hơn B0. Nếu không cải thiện nghiêm ngặt so với B0, báo `NO_STRICT_IMPROVEMENT`. Nếu các cách thắng bằng nhau, liệt kê `TIE_REQUIRES_DECISION`, không tự đặt thêm luật chọn.
- `selection.json` chứa bảng điểm, số đếm từng query, tham số, hash nguồn và ứng viên D9. Đây là **đề xuất từ dev**, không tự ký duyệt hay khóa cấu hình. Chưa có lệnh áp dụng test trong gói này.

`--diagnostic` chỉ kiểm công cụ bằng pilot/dữ liệu giả, cho output `DIAGNOSTIC_ONLY`. Không sử dụng ngưỡng này làm freeze v2. Pilot hiện chỉ có query có mặt nên không đủ điều kiện tính D9 đầy đủ.

## 4. Kiểm hồi quy

```powershell
python evaluation/check_offline_v2.py
```

10 kiểm thử: token chữ/mẫu, threshold strict, fallback B0, chọn ngưỡng đối chiếu brute force, điều kiện/tie D9, khung rỗng, uncertain, ghép CLIP và hash, chặn draft/test, evaluator trên output pilot và fixture uncertain/absent. Fixture được tạo riêng, không sửa manifest gốc. Các kiểm này không chứng minh P/T tốt hơn trên dữ liệu mới.
