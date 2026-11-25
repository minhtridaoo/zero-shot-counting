# Demo suy luận THẬT trên ảnh mới (CountGD++: B0, B2, P+F, C6)

Luồng dùng: **Ctrl+V dán ảnh** (hoặc kéo thả / bấm chọn file) → nhập tên vật, ví dụ `bowls, plates` → bấm **Chạy**. Model chạy trên chính ảnh đó và trả kết quả riêng cho từng tên vật, hiện cạnh nhau cho cả bốn cách. Không dùng kết quả đã lưu.

> Demo xem lại kết quả test (`demo/app_replay.py`) chỉ còn là **phương án dự phòng** khi mất mạng hoặc không có GPU.

## Model chạy ở đâu

| | Demo chính: Kaggle T4 | Kiểm chức năng: laptop CPU |
|---|---|---|
| Nơi chạy model | GPU T4 trong phiên Kaggle của Trí | CPU Xeon của laptop |
| Mở web | Link `https://….gradio.live` (in ở ô 7 của notebook), có đăng nhập | http://127.0.0.1:7870 |
| Môi trường | Giống hệt lần chạy test 11/11: ô 3 chép nguyên văn từ `kaggle_p1_test.ipynb`, cùng CUDA ops | `.venv-live` (Python 3.11, torch 2.5.1 **CPU**, transformers 4.44.2, numpy 2.2.6, pillow 10.4.0, gradio 5.50) |
| Tốc độ | dự kiến vài giây mỗi tên vật (lần test: B0 khoảng 0.9 s, B2 khoảng 1.5 s mỗi query); **chưa đo trong demo** | khoảng 10 s mỗi lượt; 20–100 s mỗi tên vật; ảnh rất đông vật chậm hơn vì CLIP chấm tới 900 box |
| Dùng để | trình bày | chỉ kiểm code; **không** dùng trình bày |

Laptop (RTX A2000 4 GB, Windows) không chạy GPU được:
- không có torch bản CUDA;
- không có nvcc để build CUDA ops `MultiScaleDeformableAttention`;
- 4 GB chưa kiểm chứng đủ cho model.

Ép chạy GPU trên laptop sẽ phải đổi đường tính toán, nên mình không làm.

## Giữ nguyên điều kiện đã khóa

- Checkpoint `countgd_plusplus.pth`, sha256 `b89395d7…`, kiểm theo audit 14/10. `process_folder.py` và mã model khớp hash đã pin.
- Nạp model đúng như `run_b2_verified_pseudo.py`:
  - seed 42 trước lượt 1;
  - khôi phục RNG về cuối lượt 1 trước mỗi lượt 2;
  - resize cạnh ngắn 800, tối đa 1333;
  - ngưỡng 0.23.
- **B0** = lượt 1. **B2** = lượt 2 với top-3 pseudo-exemplar gốc.
- **P+F** = P(τ 0.20, M 5), rồi F với bounds/θ 0.604 của cấu hình chính.
- **C6** = B0, rồi F với bounds/θ **riêng** 0.427. Tất cả lấy từ `freeze_v2_20261111.json`, có kiểm sha256.
- Lượt 1 chạy **một lần** mỗi tên vật và dùng chung cho cả bốn cách. Nếu P chọn đúng bộ exemplar của B2 thì dùng lại lượt 2 đó, giống runner gốc. Bảng thời gian ghi rõ phần nào dùng chung.
- Không sửa file gốc nào. `live_engine.py` import và dùng lại `select_pseudo`, `top_candidates`, `choose`, `ClipVerifier`, `source_sha`.

**Đã kiểm wrapper khớp pipeline:** `check_against_test.py` chạy 3 query test đã có kết quả chính thức (t01_1 plates, t01_2 bowls, t05_1 blueberries). Số đếm cả bốn cách **trùng hết** `result.json`, ngay cả trên CPU. Notebook chạy lại bước này trên T4 (ô 6) trước khi mở demo. Đây chỉ là kiểm wrapper, không phải chạy lại test.

## Mở demo chính trên Kaggle (Trí làm)

1. Kaggle → **Create → New Notebook** → **File → Import Notebook** → chọn `demo/live/kaggle_live_demo.ipynb`.
2. Bên phải, mục **Session options**:
   - **Accelerator: GPU T4 x2**;
   - **Internet: On**.
3. Nếu ô 4 báo gdown quá lượt tải: **Add Input** → dataset riêng có `countgd_plusplus.pth`, đúng dataset đã gắn lúc chạy test.
4. Bấm **Run All** trong chế độ chỉnh sửa. **Không** dùng "Save & Run All", vì chạy nền thì không mở được link.
   - Lần đầu mất khoảng 10–15 phút (cài môi trường, build CUDA ops).
   - Ô 6 phải in `CHECK: PASS (khớp hết)`.
5. Ô 7 in khung `LINK DEMO: https://….gradio.live` và mật khẩu (user `cs331`). Mở link trên trình duyệt máy mình.
6. Giữ tab Kaggle mở và ô 7 chạy trong suốt buổi demo. Tắt bằng nút Stop (■).

**Giới hạn phiên:**
- Link chết khi phiên Kaggle tắt; mỗi phiên mới có link mới.
- Phiên tương tác tối đa khoảng 12 giờ và có thể tắt nếu bỏ lâu không thao tác.
- GPU miễn phí khoảng 30 giờ/tuần.
- Không tốn phí.
- Nên mở phiên khoảng 20 phút trước giờ trình bày.

## Kiểm chức năng trên laptop (CPU)

```powershell
.venv-live\Scripts\python demo\live\app_live.py --device cpu --port 7870
```

Mở http://127.0.0.1:7870. Model cần `CountGDPlusPlus/checkpoints/countgd_plusplus.pth` và `bert-base-uncased/model.safetensors`; đã chép từ checkout gốc vào worktree (gitignore).

Kiểm wrapper so với kết quả test chính thức:

```powershell
.venv-live\Scripts\python demo\live\check_against_test.py --device cpu --data-root D:\MINHTRIHOCCODE\HOCKI5\CS331
```

Kiểm giao diện tự động bằng Edge (Ctrl+V thật):

```powershell
.venv-live\Scripts\python demo\live\ui_test_paste.py --url http://127.0.0.1:7870 --img1 <ảnh 1> --img2 <ảnh 2> --q1 "sheep, dogs" --q2 "bowls"
```

Dùng với link Kaggle: `--url https://….gradio.live --auth cs331:<mật khẩu>`.

## Giao diện

- **Ô ảnh:**
  - Ctrl+V ở bất kỳ đâu trên trang, trừ khi đang gõ trong ô chữ;
  - kéo thả, bấm để chọn file, hoặc nút dán từ clipboard;
  - dán ảnh mới khi ô đang có ảnh thì ảnh cũ được thay.
- **Tên vật:** tiếng Anh, số nhiều, tối đa 3, cách nhau bởi dấu phẩy. Ví dụ `bowls, plates`, `people, cars`. Không dùng dấu chấm, vì CountGD++ dùng dấu chấm để tách câu.
- **GT (tùy chọn):** cùng thứ tự với tên vật, `-` nếu không biết. Chỉ dùng tính sai số của ví dụ đó. Không có GT thì app **không** tính sai số.
- **Kết quả:**
  - mỗi tên vật có 4 ảnh box (B0, B2, P+F, C6);
  - mỗi ảnh ghi số đếm và tên vật;
  - nét đứt xám là box bị F bỏ;
  - bảng thời gian ghi rõ lượt 1 dùng chung;
  - khi có ≥ 2 tên vật có thêm bảng **box dùng chung** (IoU ≥ 0.5, cùng định nghĩa với báo cáo) để thấy đếm lẫn X/Y.
- **Giới hạn của model:** CountGD++ chỉ có 900 box đề xuất mỗi ảnh. Khi chạm 900, app cảnh báo rằng đó là trần của mô hình, không phải số vật.
- **Tránh nhầm kết quả cũ:**
  - đổi ảnh hoặc tên vật thì kết quả cũ bị xóa ngay;
  - nếu đổi trong lúc đang chạy, kết quả về muộn bị bỏ;
  - một cách bị lỗi thì ghi lỗi riêng, không lấy kết quả cách khác thay vào.
- **Nút "Xóa và bắt đầu lại"** xóa ảnh, ô chữ và kết quả.
- **Log** mỗi lần bấm Chạy (`logs/requests.jsonl`; trên Kaggle là `/kaggle/working/demo_logs/`) ghi:
  - request id, sha256 ảnh, tên vật;
  - thiết bị, checkpoint, freeze, toàn bộ cấu hình;
  - số đếm và thời gian từng cách.
  
  Trong app xem ở mục "Log của lần chạy này".

## File

| File | Vai trò |
|---|---|
| `live_engine.py` | Nạp model một lần, chạy B0/B2/P+F/C6, ghi log |
| `app_live.py` | Giao diện Gradio |
| `check_against_test.py` | Kiểm wrapper khớp số đếm chính thức trên vài query test |
| `ui_test_paste.py` | Kiểm giao diện bằng Edge: Ctrl+V, chạy, đổi ảnh/query, lỗi, xóa, upload |
| `build_kaggle_notebook.py` | Sinh `kaggle_live_demo.ipynb` (nhúng code demo kèm sha256). Chạy lại sau mỗi lần sửa code |
| `kaggle_live_demo.ipynb` | Notebook Kaggle T4 mở demo qua link https |

Ảnh dùng để thử demo **không** phải dữ liệu nghiên cứu và không đưa vào bảng kết quả.
