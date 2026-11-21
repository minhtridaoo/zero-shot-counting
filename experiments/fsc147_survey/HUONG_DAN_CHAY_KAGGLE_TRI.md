# Hướng dẫn Trí chạy khảo sát FSC-147 trên Kaggle (một lần)

*Assistant soạn 21/11/2026.* **Chỉ chạy khi:** (1) Trí đã duyệt chính thức [bản khai báo](KHAI_BAO_TRUOC_FSC147_20261120.md), và (2) Triệu đã gửi kết quả phần A (trong ngày 21/11). Chạy **một lần**, dự kiến 22–23/11.

## 1. Tải đúng notebook

- Tải `experiments/fsc147_survey/kaggle_fsc147_survey.ipynb` từ **`main`** (hoặc commit `5988c22`):
  [xem trên GitHub](https://github.com/minhtridaoo/zero-shot-counting/blob/main/experiments/fsc147_survey/kaggle_fsc147_survey.ipynb) → nút **Download raw file**.
- **Kiểm sau khi mở:** Ô 1 phải có dòng
  `REPO_REF = "4cd89092c5160dc0dc79455adba42ff096a44664"`.
  - Nếu thấy SHA khác (ví dụ `d5339c2…`), bạn đã tải nhầm bản cũ: tải lại từ `main`.
  - **Không tự sửa `REPO_REF`.**
  - Lưu ý: bản notebook *nằm bên trong* commit `4cd8909` vẫn ghim SHA cũ. Code chạy lấy từ `4cd8909`, nhưng file notebook phải lấy từ `main`.

## 2. Tạo notebook trên Kaggle

1. Kaggle → **Create → New Notebook → File → Import Notebook**, chọn file vừa tải.
2. Panel phải → **Session options**:
   - **Accelerator: GPU T4 x2.** Không chọn P100. Ô 1 dừng nếu không phải T4.
   - **Internet: On.** Cần để clone code, cài thư viện, tải MUCCA, BERT và ảnh FSC-147.
3. **Add Input → Datasets** (khuyên làm, để khỏi phụ thuộc gdown):
   - **Checkpoint:** Kaggle Dataset riêng tư chứa `countgd_plusplus.pth` (bản ở Drive `MyDrive/CS331_colab/`, cùng tệp đã dùng cho W6/W8). Ô 4 tự tìm trong `/kaggle/input` và kiểm sha256 đã audit 14/10.
   - **Ảnh FSC-147 (tùy chọn):** một Dataset chứa thư mục `images_384_VarV2`. Nếu không gắn, Ô 6 tự tải bằng gdown từ link FSCD-147 trong README CountGD++.
   - MUCCA (chỉ dùng cho Kiểm A) tự tải từ Zenodo, có kiểm md5. Không cần gắn.

## 3. Chạy bằng Save Version

1. Góc phải trên → **Save Version**.
2. Chọn **Save & Run All (Commit)**. Đặt tên version, ví dụ `fsc147_survey_run1`.
3. Bấm **Save**. Không chạy tay từng ô, để Kaggle giữ bản ghi đầy đủ.
4. Theo dõi ở trang version (**Logs**). Thời gian chưa đo trên FSC-147. Notebook ghi thời gian thật vào `timing.json`.

## 4. Khi chạy xong: tải và gửi

1. Mở version → tab **Output** → tải **`for_repo_<stamp>.zip`**. Gói này gồm json/jsonl/csv/txt, không có `.npz` hay ảnh.
2. Tab **Logs** → **Download** log đầy đủ. Hoặc chụp phần in ra của **Ô 2, Ô 5, Ô 7, Ô 8**.
3. Gửi zip và log cho **assistant** và **Triệu**, kèm tên/số version Kaggle.
4. Raw `.npz` để nguyên trong Output Kaggle; không tải vào repo.
5. Kết quả tốt hay xấu đều **không chạy lại**.

## 5. Khi nào phải dừng và gửi log

Gặp các trường hợp dưới đây: **dừng, không sửa notebook, không đổi tham số**. Tải log ở tab Logs (hoặc chụp ô lỗi), rồi gửi assistant kèm số version.

| Ô | Dấu hiệu | Làm gì |
|---|---|---|
| 1 | "Cần GPU T4" | Đổi Accelerator sang GPU T4 x2, chạy lại version mới. Lỗi kỹ thuật, ghi WORKLOG |
| 1 | "Phiên này đã chạy khảo sát rồi" | Dừng. Không chạy lần hai trong cùng phiên |
| 2 | Lỗi `git checkout` / "HEAD … khác commit đã ghim" | Dừng, gửi log. Không sửa `REPO_REF` |
| 2 | "… khác hash lúc tạo mẫu" hoặc "freeze v2 khác sha256" | Dừng, gửi log. Không được chạy tiếp |
| 4 | "checkpoint sha256 sai", hoặc gdown báo quá lượt tải | Gắn Dataset checkpoint đúng (mục 2.3), chạy lại version mới. Hash vẫn sai thì dừng, gửi log |
| 5 | "Kiem A KHONG DAT" | Dừng, gửi log. CLIP trên Kaggle khác bản cũ, kết quả F không tin được |
| 6 | "Thiếu ảnh …", hoặc gdown báo quá lượt tải, hoặc "Cần đúng 1 thư mục images_384_VarV2" | Gắn Dataset ảnh, chạy lại version mới. Thiếu ảnh thật thì dừng. **Không thay hay bỏ ảnh** |
| 7 | Runner in lỗi ở một câu (`fq_xxxx: …Error…`) và dừng | Dừng, gửi log kèm id ảnh. Lỗi môi trường thì chạy lại version mới, tối đa 2 lần. Lỗi lặp lại ở cùng ảnh thì **không chạy tiếp**: khảo sát ghi là chưa hoàn tất |
| 8 | Script chấm báo "Run không hoàn tất…", "…phải là false", "…trùng", "không phủ đúng…" | Dừng, gửi log. Không chạy lại phần chấm với tham số khác |
| bất kỳ | Hết giờ phiên Kaggle, mất kết nối, crash cài đặt | Lỗi kỹ thuật: chạy lại version mới, đủ 300 ảnh, tối đa 2 lần, ghi WORKLOG |

**Không bao giờ:** sửa ô code, đổi tau/M, chạy evaluator khác, chạy lại vì kết quả xấu.
