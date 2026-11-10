# Danh mục kết quả — `results/countgdpp/`

**Không di chuyển hay đổi tên** các thư mục ở đây: code (`run_b2_pilot.py` đọc `smoke_*`, các scorer đọc `p4_*`) và các audit/report trỏ thẳng vào đường dẫn. Chỉ thêm run mới, không ghi đè.

## A. Dùng cho báo cáo cuối

| Bước | Thư mục / file | Nội dung |
|---|---|---|
| Kiểm model | `checkpoint_audit_2026-10-14.json` | Hash checkpoint + source đã kiểm (mọi runner đều đối chiếu file này) |
| Pilot B0 | `m4_first5_b0/` | B0 trên 5 ảnh / 15 query |
| Pilot B2 | `b2_two_images_20261015/`, `b2_remaining3_20261015/` | B2 trên 5 ảnh (2 + 3 ảnh), kèm REVIEW |
| Pilot chấm | `pilot_eval_20261020/`, `pilot_eval_20261027_trieu/` | Evaluator (MAE B0 19.4 / B2 22.0); bản Triệu chạy lại trùng hoàn toàn |
| Cải tiến v1 | `p4_clip_all15_20261020/`, `p4_count_cv_20261020/`, `p4_fixed_fusion_cv_20261021/` | Điểm CLIP, kiểm chéo theo ảnh, Fusion |
| Freeze v1 | `p4_candidate_freeze_20261021.json`, `p4_freeze_audit_20261021.json` | **Ngưỡng đã khóa (không sửa)** + audit |
| Kiểm runner | `p4_b2_devcheck_20261027/`, `p4_clip_devcheck_20261027/`, `p4_freeze_devcheck_20261027/`, `p4_freeze_e2e_devcheck_20261027/` | Runner mới tái lập trùng tuyệt đối |
| Tập 10 ảnh mới | `p4_unseen_v1_b2_20261027/`, `p4_unseen_v1_clip_20261027/`, `p4_unseen_v1_freeze_20261027/`, `p4_unseen_v1_eval_20261027/` | Kết quả P4.6 (Fusion 5.53, B0 6.77, …) |
| N4 | `p4_n4_review_package_20261027/` (nhãn tầng A + B, `bo_sung_F0/`, `_KEY_…`) | Review khung bằng người |
| q05_3 | `q05_error_analysis_package_20261027/` | Nhãn 103 khung (V3) |
| Nhánh P pilot | `p1_pilot_colab_20261103_1519/` (+ `_controls`, `_controls_clip`, `_controls_eval`), `p1_pilot_colab_20261103_1528/` | P1 trên Colab T4, kiểm code (Kiểm A/C) |

## B. Lịch sử / chẩn đoán (giữ để truy vết, không cần mở khi viết báo cáo)

`smoke_cat/`, `smoke_fork/`, `smoke_spoon/`, `smoke_verification_2026-10-13.json`, `adapter_check_cat_20261014/`, `m4_first_image_b0/`, `b2_smoke_20261015/`, `m6_e1_final_20261015/`, `m6_e2_sample010_20261015/`, `m6_e2_sample050_20261015/`, `token_diagnostic_more_20261015/`, `token_diagnostic_rulers_20261015/`, `p4_clip_probe_20261020/`, `p4_review_q03_1/2/3_20261020/`, `p4_label_review_handoff_20261021.zip` (47 nhãn q03, đang tạm hoãn), `p4_class_score_analysis_20261021.json`, `p4_rank_diagnostic_20261021.json`, `p4_prompt_number_20261021/`, `p4_fusion_object_review_20261021.json`, `p4_two_case_object_review_20261020.json`, `pilot_eval_20261020_r2/` (trùng run chính).

## C. Đã xóa khi dọn 10/11 (còn trong lịch sử git)

`results/countgdpp.zip` và `results/countgdpp/b2_remaining3_20261015.zip`: bản sao của các thư mục ở trên. File duy nhất có trong zip mà đĩa bị rỗng (`m4_first5_b0/jobs/004_q02_1/console.log`) đã được khôi phục trước khi xóa.
