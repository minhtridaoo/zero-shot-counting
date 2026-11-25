"""Sắp xếp lại final/slides/main.tex theo phiếu chấm (25/11/2026). Chạy một lần; tự dừng nếu không tìm thấy mốc."""
import re, sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "main.tex"
s = P.read_text(encoding="utf-8")
if "% [phieu-cham-20261125]" in s:
    sys.exit("Đã sắp xếp rồi, không chạy lại.")


def take(title):
    """Cắt nguyên khối frame có tiêu đề bắt đầu bằng `title` (kể cả dòng trống sau)."""
    global s
    i = s.find("\\begin{frame}{" + title)
    if i < 0:
        sys.exit("Không thấy frame: " + title)
    j = s.find("\\end{frame}\n", i) + len("\\end{frame}\n")
    while s[j:j + 1] == "\n":
        j += 1
    blk = s[i:j]
    s = s[:i] + s[j:]
    return blk.rstrip("\n") + "\n\n"


def insert_before(marker, text):
    global s
    i = s.find(marker)
    if i < 0:
        sys.exit("Không thấy mốc: " + marker)
    s = s[:i] + text + s[i:]


def insert_after_frame(title, text):
    global s
    i = s.find("\\begin{frame}{" + title)
    if i < 0:
        sys.exit("Không thấy frame: " + title)
    j = s.find("\\end{frame}\n", i) + len("\\end{frame}\n")
    s = s[:j] + "\n" + text.rstrip("\n") + "\n" + s[j:]


def rep(old, new, count=1):
    global s
    if s.count(old) < 1:
        sys.exit("Không thấy chuỗi: " + old[:80])
    s = s.replace(old, new, count)


# ---------------------------------------------------------------- 1. Phân công xuống cuối
phancong = take("Phân công công việc")
phancong = phancong.replace(
    "\\note{[0:20] Đây là phân công công việc trong đồ án.",
    "\\note{[0:20] (Trí) Trước khi nhận câu hỏi, đây là phân công công việc trong đồ án.")
insert_before("\\begin{frame}[standout]", phancong)

# ---------------------------------------------------------------- 2. Mục bài toán: Định nghĩa → RQ → Minh họa
rq = take("Câu hỏi nghiên cứu và đóng góp")
rq = rq.replace("Chuyển: em mời thầy xem CountGD++ đếm như thế nào.}",
                "Chuyển: một ví dụ thật cho thấy lỗi này.}")
insert_before("\\begin{frame}{Minh họa: ba query khác nhau", rq)
rep("Đây chính là lỗi X/Y.}", "Đây chính là lỗi X/Y. Chuyển: em mời thầy xem CountGD++ đếm như thế nào, và nhóm sửa ở đâu.}")

# ---------------------------------------------------------------- 3. Tên mục khớp phiếu chấm
rep("\\section{Mô tả bài toán}", "\\section{Phát biểu bài toán}")
rep("\\section{Phương pháp}", "\\section{Phương pháp giải quyết}")
rep("\\section{Giới hạn và kết luận}", "\\section{Nhận xét và kết luận}")
rep("\\note{[0:15] Bài trình bày gồm năm phần: lý do chọn đề tài, bài toán, phương pháp, thực nghiệm, và cuối cùng là giới hạn, kết luận.}",
    "\\note{[0:15] Bài trình bày gồm năm phần, theo đúng thứ tự: lý do thực hiện đề tài, phát biểu bài toán, phương pháp giải quyết, thực nghiệm, và cuối cùng là nhận xét, kết luận.}")

# Related work ở mục 1: chỉ nêu khoảng trống, so sánh chi tiết để cuối mục 3
rep("\\takeaway{Không huấn luyện mô hình mới, cũng không chỉ đánh giá: nhóm sửa ở bước suy luận của mô hình có sẵn.}",
    "\\takeaway{Không huấn luyện mô hình mới, cũng không chỉ đánh giá: nhóm sửa ở bước suy luận của mô hình có sẵn (so sánh chi tiết ở cuối phần Phương pháp).}")
rep("\\note{[0:45] Các phương pháp tự tạo exemplar như PseCo, VA-Count, DAVE đều phải huấn luyện thêm. Gần nhất với bước lọc F là bản dùng text prompt của DAVE, nhưng DAVE loại theo cụm box và có huấn luyện; F kiểm từng box và không huấn luyện. PrACo và MUCCA chỉ đánh giá. Đồ án nằm giữa: chẩn đoán và sửa ở bước suy luận.}",
    "\\note{[0:30] Các phương pháp tự tạo exemplar như PseCo, VA-Count, DAVE đều phải huấn luyện thêm; PrACo và MUCCA chỉ đánh giá. Đồ án nằm giữa: chẩn đoán và sửa ở bước suy luận của một mô hình có sẵn. Điểm khác biệt cụ thể em sẽ so ở cuối phần phương pháp.}")

# ---------------------------------------------------------------- 4. Bảng khác biệt cuối mục 3
rep("C6 là lọc ngay sau lượt 1, bỏ lượt 2, là đối chứng bắt buộc. Chuyển: phần dữ liệu và giao thức, Triệu trình bày.}",
    "C6 là lọc ngay sau lượt 1, bỏ lượt 2, là đối chứng bắt buộc.}")
khacbiet = r"""\begin{frame}{Điểm khác biệt so với các phương pháp khác}
\source{Huang và cs., CVPR 2024 (PseCo); Zhu và cs., ECCV 2024 (VA-Count); Pelhan và cs., CVPR 2024 (DAVE, mục 3.2--3.4); đối chiếu tóm tắt arXiv 25/11}
\scriptsize
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{@{}>{\bfseries}p{0.13\textwidth} >{\raggedright\arraybackslash}X >{\raggedright\arraybackslash}X >{\centering\arraybackslash}p{0.10\textwidth} >{\raggedright\arraybackslash}p{0.17\textwidth}@{}}
\toprule
\normalfont\bfseries Cách & \textbf{Lấy exemplar / vật ứng viên} & \textbf{Loại vật sai bằng gì} & \textbf{Huấn luyện thêm?} & \textbf{Dạng}\\
\midrule
CountGD++ gốc & Tự lấy top-3 box làm pseudo-exemplar & Không kiểm class của exemplar; giữ box theo threshold điểm & -- & mô hình gốc (checkpoint công khai)\\
PseCo & SAM đề xuất mask cho mọi vật & Classifier dựa trên CLIP phân loại từng đề xuất & có (distill) & framework riêng\\
VA-Count & Mô-đun vision-language tìm exemplar tiềm năng & Mô-đun học tương phản tách exemplar tốt / kém & có & framework riêng\\
DAVE & Detect với độ phủ cao & Phân cụm đặc trưng; bản text dùng CLIP loại theo \emph{cụm} box & có & framework riêng\\
\midrule
\textbf{Đồ án} & \textbf{P}: CLIP kiểm top-$M$ box trước khi lấy pseudo-exemplar & \textbf{F}: CLIP + điểm CountGD++ quyết định cho \textbf{từng box}, threshold khóa trên dev & \textbf{không} & gắn vào bước suy luận của CountGD++\\
\bottomrule
\end{tabularx}
\vspace{1.5mm}
\begin{columns}[T]
\begin{column}{0.48\textwidth}
\begin{block}{Khác ở cách làm}
\scriptsize Không huấn luyện gì, không đổi mô hình; kiểm từng box thay vì từng cụm; đo thêm shared box X/Y và absent query trên ảnh nhiều class.
\end{block}
\end{column}
\begin{column}{0.48\textwidth}
\begin{alertblock}{Chưa so trực tiếp}
\scriptsize Nhóm chưa chạy PseCo, VA-Count, DAVE trên cùng dữ liệu, nên \textbf{không khẳng định tốt hơn} các phương pháp này. Mốc so sánh số là CountGD++ \Bzero, \Btwo.
\end{alertblock}
\end{column}
\end{columns}
\note{[0:50] (Trí) Đây là điểm khác biệt so với các phương pháp gần nhất. CountGD++ gốc tự lấy ba box điểm cao nhất làm pseudo-exemplar và không kiểm class. PseCo, VA-Count và DAVE đều có bước tìm hoặc kiểm vật ứng viên, nhưng đều phải huấn luyện thêm và là framework riêng; DAVE bản text loại theo từng cụm box. Cách của nhóm không huấn luyện gì, gắn thẳng vào bước suy luận của CountGD++, và F quyết định cho từng box. Nhóm chưa chạy ba phương pháp kia trên cùng dữ liệu, nên không nói là tốt hơn; mốc so sánh số là CountGD++ một lượt và hai lượt. Chuyển: phần thực nghiệm, Triệu trình bày dữ liệu và độ đo.}
\end{frame}
"""
insert_after_frame("Tổng thể: các biến thể được so sánh", khacbiet)

# ---------------------------------------------------------------- 5. Dữ liệu: MUCCA + bảng tổng; độ đo tách riêng
rep("\\begin{frame}{Dữ liệu: MUCCA, chia thành bốn tập không trùng nhau}",
    "\\begin{frame}{Dữ liệu chính: MUCCA, chia thành bốn tập không trùng ảnh}")
rep("\\tiny chó--dê\\\\", "\\tiny chó--dê (+80 cừu)\\\\")
rep("\\begin{column}{0.52\\textwidth}\n\\small\n\\begin{tabular}{@{}lll@{}}\n\\toprule\nTập & Ảnh / query & Dùng để\\\\",
    "\\begin{column}{0.52\\textwidth}\n{\\scriptsize\\textbf{MUCCA 1.0:} 200 ảnh thật, 45 class, mỗi ảnh 2--7 class (trung vị 2), 12.265 điểm nhãn; mỗi vật một điểm, có class.}\\\\[1.5mm]\n\\small\n\\begin{tabular}{@{}lll@{}}\n\\toprule\nTập & Ảnh / query & Dùng để\\\\")
rep("\\textbf{test v2} & 40 / 119 & đo một lần duy nhất\\\\",
    "\\textbf{test v2} & 40 / 119$^{*}$ & đo một lần duy nhất\\\\")
rep("\\item Người kiểm từng ảnh (Trí kiểm dev, Triệu kiểm test), sau đó khóa bằng SHA-256\n\\end{itemize}",
    "\\item Người kiểm từng ảnh (Trí kiểm dev, Triệu kiểm test), sau đó khóa bằng SHA-256\n\\item $^{*}$120 query, 1 query nhãn \\texttt{uncertain} (t37\\_1) bị loại trước khi chạy test\n\\end{itemize}")
rep("\\note{[0:55] Dữ liệu là MUCCA, 200 ảnh thật, mỗi ảnh nhiều class.",
    "\\note{[0:55] (Triệu) Dữ liệu chính là MUCCA, 200 ảnh thật, 45 class, mỗi ảnh từ 2 đến 7 class.")

tongdl = r"""\begin{frame}{Tổng hợp các bộ dữ liệu và lần đánh giá}
\source{\texttt{BENCHMARK\_FSCD147.md}; \texttt{KHAI\_BAO\_TRUOC\_FSC147\_20261120.md}; \texttt{dev\_test\_v2/selection\_meta.json}}
\scriptsize\centering
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{@{}l l r >{\raggedright\arraybackslash}X >{\raggedright\arraybackslash}p{0.25\textwidth}@{}}
\toprule
Lần đánh giá & Nguồn ảnh & Ảnh / query & Mục đích & Điều kiện\\
\midrule
Kiểm môi trường & FSCD-147 test & 1.190 / 1.190 & Tái lập số của bài báo (8.34 so với 8.39) & Cấu hình t+p+s của bài báo (có crop, exemplar GPT-5)\\
Pilot, p4\_unseen\_v1 & MUCCA & 5 / 15; 10 / 30 & Tìm lỗi, kiểm bản v1, blind review N4 & Chỉ text prompt\\
\textbf{dev v2} & MUCCA & 20 / 60 & Chọn cấu hình theo luật D9 & Chỉ text prompt\\
\textbf{test v2} & MUCCA & 40 / 119 & Kết quả chính, chạy một lần & Chỉ text prompt, cấu hình đã khóa\\
Khảo sát phạm vi & FSC-147 test & 300 / 300 & Ảnh một class: giữ hay bỏ lượt 2? & Rút ngẫu nhiên, seed 331; không crop, không exemplar GPT-5\\
\bottomrule
\end{tabularx}
\vspace{2mm}
\begin{alertblock}{FSCD-147 và FSC-147 không phải hai bộ dữ liệu độc lập}
\small FSCD-147 là FSC-147 có thêm box: cùng ảnh, cùng split test. 300 ảnh khảo sát là tập con của 1.190 ảnh dùng để kiểm môi trường; khác nhau ở điều kiện chạy, nên hai con số không so trực tiếp với nhau.
\end{alertblock}
\note{[0:40] (Triệu) Bảng này tổng hợp mọi lần đánh giá. Benchmark FSCD-147 chỉ để kiểm môi trường. Bốn tập MUCCA là phần chính. Khảo sát FSC-147 dùng 300 ảnh rút ngẫu nhiên. Lưu ý: FSCD-147 là FSC-147 có thêm box, nên benchmark và khảo sát dùng chung nguồn ảnh, không phải hai bộ độc lập; chỉ khác điều kiện chạy.}
\end{frame}
"""
dodo = r"""\begin{frame}{Độ đo: sai số đếm, absent query và việc đổi box theo query}
\source{Tính trên 119 query test hợp lệ (79 present, 40 absent); bootstrap: Efron, 1979}
\begin{columns}[T]
\begin{column}{0.60\textwidth}
\scriptsize
\renewcommand{\arraystretch}{1.25}
\begin{tabularx}{\linewidth}{@{}l >{\raggedright\arraybackslash}X l@{}}
\toprule
Độ đo & Cách tính & Đo yêu cầu\\
\midrule
\textbf{MAE} (chính) & $\frac{1}{|Q|}\sum_q|\hat n_q-n_q|$: trung bình sai bao nhiêu vật mỗi query & Y1, Y2\\
RMSE & $\sqrt{\frac{1}{|Q|}\sum_q(\hat n_q-n_q)^2}$: phạt nặng query sai nhiều & Y1, Y2\\
MAE present & MAE chỉ trên 79 present query & Y1\\
$\FPRabs$ & Tỉ lệ trong 40 absent query mà mô hình vẫn đếm ra $\hat n>0$ & Y2\\
Shared box X/Y & Tỉ lệ box của X và của Y có box trùng (IoU $\ge 0.5$) ở query kia, gộp trên các ảnh & Y3\\
\bottomrule
\end{tabularx}
\end{column}
\begin{column}{0.36\textwidth}
\begin{block}{Ví dụ}
\scriptsize Query ``bowls'' (GT 3), \Btwo{} đếm 36 $\Rightarrow$ sai 33 vật ở query này.\\
Query ``spoons'' vắng mặt mà đếm 34 $\Rightarrow$ tính là một lần đếm nhầm absent.
\end{block}
\begin{block}{CI 95\% bootstrap theo ảnh}
\scriptsize Lấy mẫu lại \textbf{ảnh} 5000 lần, tính chênh lệch MAE giữa hai cách.\\
CI không chứa 0 $\Rightarrow$ chênh lệch đáng tin.\\
CI chứa 0 $\Rightarrow$ \textbf{chưa đủ bằng chứng}, không có nghĩa là hai cách bằng nhau.
\end{block}
\end{column}
\end{columns}
\note{[0:50] (Triệu) Chỉ số chính là MAE: trung bình mỗi query sai bao nhiêu vật. RMSE phạt nặng query sai nhiều. MAE present chỉ tính trên query có mặt. FPR absent là tỉ lệ query vắng mặt mà mô hình vẫn đếm ra số. Shared box X/Y đo yêu cầu thứ ba: đổi query thì box có đổi không. Khoảng tin cậy lấy mẫu lại theo ảnh, vì ba query trên cùng ảnh không độc lập. CI không chứa 0 thì chênh lệch đáng tin; CI chứa 0 chỉ là chưa đủ bằng chứng, không có nghĩa hai cách bằng nhau.}
\end{frame}
"""
insert_after_frame("Dữ liệu chính: MUCCA", tongdl + "\n" + dodo)

# Giao thức: bỏ khối Chỉ số (đã có slide riêng)
i = s.find("\\begin{frame}{Giao thức ``chọn trước, xem sau'' và cách đo}")
j = s.find("\\end{frame}\n", i)
g = s[i:j]
a = g.find("\\begin{columns}[T]")
b = g.find("\\note{")
g_new = g[:a] + r"""\begin{columns}[T]
\begin{column}{0.48\textwidth}
\begin{block}{Luật chọn D9 (viết trước khi chạy dev)}
\small Chọn cấu hình có MAE dev nhỏ nhất, \emph{với điều kiện} không kém \Bzero{} ở present query và ở absent query.
\end{block}
\end{column}
\begin{column}{0.48\textwidth}
\begin{block}{Test chạy một lần}
\small Cấu hình khóa vào file freeze (có hash), chạy test một lần trên Kaggle T4; sau đó kiểm hash và tính lại số đếm từ output thô.
\end{block}
\end{column}
\end{columns}
""" + "\\note{[0:40] (Triệu) Vì dữ liệu ít mà tham số nhiều, nhóm làm theo kiểu chọn trước, xem sau. Luật chọn D9 được viết trước khi chạy dev: lấy MAE nhỏ nhất, nhưng không được kém B0 ở present query hay absent query. Chọn xong thì khóa lại, rồi em chạy test đúng một lần trên Kaggle. Sau đó trợ lý AI kiểm hash của các file output và tính lại số đếm, MAE từ output thô; kết quả khớp hoàn toàn. Chuyển: phần kết quả, Trí trình bày.}\n"
g_new = g_new.replace("\\begin{frame}{Giao thức ``chọn trước, xem sau'' và cách đo}", "\\begin{frame}{Giao thức ``chọn trước, xem sau''}")
g_new = g_new.replace("\\source{Efron, 1979 (bootstrap); luật D9 trong", "\\source{Luật D9 trong")
s = s[:i] + g_new + s[j:]

# ---------------------------------------------------------------- 6. Rút thời lượng: chuyển 2 slide phụ xuống dự phòng
theocap = take("Theo loại cặp")
vidu = take("Ví dụ: một trường hợp thành công")
for old, new in (("\\begin{frame}{Theo loại cặp", "\\begin{frame}{Dự phòng · Theo loại cặp"),
                 ("\\begin{frame}{Ví dụ: một trường hợp thành công", "\\begin{frame}{Dự phòng · Ví dụ: một trường hợp thành công")):
    theocap = theocap.replace(old, new); vidu = vidu.replace(old, new)
theocap = re.sub(r"\\note\{\[0:50\]", r"\\note{[dự phòng]", theocap)
vidu = re.sub(r"\\note\{\[0:45\]", r"\\note{[dự phòng; demo cho xem trực tiếp hai ví dụ này]", vidu)
rep("\\end{document}", vidu + theocap + "\\end{document}")

# ---------------------------------------------------------------- 7. Câu chữ: CI chứa 0, phạm vi suy rộng
rep("\\item \\BtwoF{} so với \\PF: $-0.13$ [$-0.41$, $+0.18$], gần như bằng nhau",
    "\\item \\BtwoF{} so với \\PF: $-0.13$ [$-0.41$, $+0.18$]: CI chứa 0, không thấy P đóng góp thêm")
rep("nên B2 cộng F gần bằng P cộng F. Vậy phần có tác dụng là filter F.",
    "và B2 cộng F so với P cộng F có CI chứa 0, tức không thấy P đóng góp thêm. Phần có tác dụng là filter F.")
rep("\\takeaway{Cải tiến phù hợp với ảnh nhiều class, số vật ít đến vừa. Với ảnh một class, nhiều vật, nên giữ CountGD++ gốc.}",
    "\\takeaway{Cải thiện mới được kiểm trên ảnh nhiều class, ít đến vừa vật (MUCCA). Trên ảnh một class, nhiều vật (FSC-147), cấu hình của nhóm kém CountGD++ gốc.}")
rep("Ở ảnh tối đa 40 vật thì hai cách gần nhau.}", "Ở ảnh tối đa 40 vật thì chênh lệch nhỏ.}")
rep("$\\Rightarrow$ dùng cho ảnh nhiều class, ít đến vừa vật\\\\",
    "$\\Rightarrow$ mới kiểm chứng cho ảnh nhiều class, ít đến vừa vật\\\\")
rep("Cải tiến dành cho ảnh nhiều class, số vật ít đến vừa.}",
    "Cải thiện mới được kiểm chứng trên ảnh nhiều class, số vật ít đến vừa.}")
rep("\\note{Em cảm ơn thầy và các bạn. Nhóm sẵn sàng nhận câu hỏi. Nếu thầy muốn xem thêm, nhóm có slide dự phòng và demo tĩnh bằng các hình ví dụ.}",
    "\\note{Em cảm ơn thầy và các bạn. Nhóm sẵn sàng nhận câu hỏi. Nếu thầy muốn xem thêm, nhóm có slide dự phòng và có thể mở lại demo.}")
rep("% Source line + page number in the footline (phân công công việc: slide 3)",
    "% Source line + page number in the footline\n% [phieu-cham-20261125] thứ tự theo phiếu chấm: 1 lý do · 2 bài toán · 3 phương pháp · 4 thực nghiệm (4.4 demo) · 5 kết luận")

P.write_text(s, encoding="utf-8", newline="\n")
print("OK")
