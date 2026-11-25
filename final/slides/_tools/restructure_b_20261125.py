"""Bước 2 (25/11): chuyển slide dev và ví dụ thất bại xuống dự phòng để giữ ≤ 25 phút khi có demo."""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "main.tex"
s = P.read_text(encoding="utf-8")
if "[phieu-cham-20261125-b]" in s:
    sys.exit("Đã chạy rồi.")
BF, EF = "\\begin{frame}{", "\\end{frame}\n"


def take(title):
    global s
    i = s.find(BF + title)
    assert i >= 0, title
    j = s.find(EF, i) + len(EF)
    while s[j:j + 1] == "\n":
        j += 1
    b = s[i:j]
    s = s[:i] + s[j:]
    return b.rstrip("\n") + "\n\n"


dev = take("Kết quả dev: luật D9").replace(BF + "Kết quả dev", BF + "Dự phòng · Kết quả dev")
dev = dev.replace("\\note{[0:40]", "\\note{[dự phòng]")
fail = take("Ví dụ thất bại").replace(BF + "Ví dụ thất bại", BF + "Dự phòng · Ví dụ thất bại")
fail = fail.replace("\\note{[0:45]", "\\note{[dự phòng; demo cho xem trực tiếp ví dụ dogs]")
i = s.find(BF + "Dự phòng · Ví dụ: một trường hợp")
assert i >= 0
s = s[:i] + dev + fail + s[i:]

old = "Sau đó trợ lý AI kiểm hash của các file output và tính lại số đếm, MAE từ output thô; kết quả khớp hoàn toàn. Chuyển: phần kết quả, Trí trình bày.}"
assert old in s
s = s.replace(old, "Trên dev, D9 chọn P với tau 0.20, M bằng 5, cộng F; vì threshold chọn ngay trên dev nên số dev lạc quan, số để báo cáo là số test. Sau đó trợ lý AI kiểm hash và tính lại số đếm, MAE từ output thô; kết quả khớp hoàn toàn. Chuyển: phần kết quả, Trí trình bày.}")
assert "\\note{[0:40] (Triệu) Vì dữ liệu ít" in s
s = s.replace("\\note{[0:40] (Triệu) Vì dữ liệu ít", "\\note{[0:45] (Triệu) Vì dữ liệu ít")
old2 = "\\small Cấu hình khóa vào file freeze (có hash), chạy test một lần trên Kaggle T4; sau đó kiểm hash và tính lại số đếm từ output thô."
assert old2 in s
s = s.replace(old2, "\\small Dev: D9 chọn \\PF{} ($\\tau$ 0.20, $M$ 5), MAE dev 3.53 (lạc quan, vì threshold chọn trên dev). Cấu hình khóa vào file freeze (có hash), chạy test một lần trên Kaggle T4; sau đó kiểm hash và tính lại số đếm từ output thô.")
s = s.replace("% [phieu-cham-20261125]", "% [phieu-cham-20261125] [phieu-cham-20261125-b]", 1)
P.write_text(s, encoding="utf-8", newline="\n")
print("OK")
