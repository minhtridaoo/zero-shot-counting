"""Ghi người nói vào đầu \\note của từng slide chính (25/11), theo phân công mới trong
reports/PHAN_CONG_TRI_TRIEU_BAO_CAO_SLIDE.md. Không đổi nội dung lời nói. In bảng slide → người nói → thời lượng."""
import re
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "main.tex"
s = P.read_text(encoding="utf-8")
BS = chr(92)

# tiền tố tiêu đề frame -> người nói
SPEAKER = [
    ("Nội dung", "Trí"), ("Bối cảnh", "Trí"), ("Khoảng trống", "Trí"), ("Related work", "Trí"),
    ("Định nghĩa", "Trí"), ("Câu hỏi nghiên cứu", "Trí"), ("Minh họa", "Trí"), ("Baseline", "Trí"),
    ("Chẩn đoán", "Triệu"), ("VĐ1", "Triệu"), ("VĐ2", "Triệu"), ("VĐ3", "Triệu"),
    ("Cải tiến P", "Trí"), ("Cải tiến F", "Trí"), ("Tổng thể", "Trí"), ("Điểm khác biệt", "Trí"),
    ("Dữ liệu chính", "Triệu"), ("Tổng hợp các bộ", "Triệu"), ("Độ đo", "Triệu"), ("Giao thức", "Triệu"),
    ("Kết quả test", "Trí"), ("Phân rã", "Triệu"), ("F bỏ được box", "Triệu"), ("Kiểm thêm trên 300", "Triệu"),
    ("Các hướng đã thử", "Triệu"), ("Demo", "Trí"), ("Những điều kết quả", "Triệu"), ("Kết luận", "Trí"),
    ("Hướng phát triển", "Trí"), ("Phân công", "Trí"),
]
main, sep, backup = s.partition(BS + "appendix")
parts = main.split(BS + "begin{frame}")
rows, total = [], 0
for k in range(1, len(parts)):
    p = parts[k]
    m = re.match(r"\{([^\n]*?)\}\s*\n", p)
    title = m.group(1) if m else ("Bìa" if k == 1 else "[standout]")
    who = next((w for pre, w in SPEAKER if title.startswith(pre)), "Trí")
    nm = re.search(BS * 2 + r"note\{\[(\d+):(\d+)\] (\((Trí|Triệu)\) )?", p)
    if nm:
        sec = int(nm.group(1)) * 60 + int(nm.group(2))
        if nm.group(3) is None:
            i = nm.end()
            p = p[:i] + f"({who}) " + p[i:]
        elif nm.group(4) != who:
            sys.exit(f"Lệch người nói ở '{title}': ghi {nm.group(4)}, phân công {who}")
    else:
        sec = 0
    total += sec
    rows.append((title, who, sec))
    parts[k] = p
s = BS.join([""]) if False else (BS + "begin{frame}").join(parts) + sep + backup
P.write_text(s, encoding="utf-8", newline="\n")

n = 0
by = {"Trí": 0, "Triệu": 0}
for title, who, sec in rows:
    by[who] += sec
    print(f"{who:<6}{sec // 60}:{sec % 60:02d}  {title[:70]}")
print(f"Tổng {total // 60}:{total % 60:02d} · Trí {by['Trí'] // 60}:{by['Trí'] % 60:02d} · Triệu {by['Triệu'] // 60}:{by['Triệu'] % 60:02d}")
