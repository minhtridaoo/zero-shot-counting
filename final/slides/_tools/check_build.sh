#!/bin/sh
# Biên dịch, liệt kê overfull, trang thiếu số, rồi render ảnh xem nhanh
cd "$(dirname "$0")/.." || exit 1
latexmk -xelatex -interaction=nonstopmode main.tex > _tools/build_log.txt 2>&1 || { echo BUILD FAIL; tail -20 _tools/build_log.txt; exit 1; }
grep -o "Output written.*" main.log
grep "Overfull" main.log
n=$(pdfinfo main.pdf | awk '/Pages/{print $2}')
for p in $(seq 1 $n); do pdftotext -f $p -l $p main.pdf - 2>/dev/null | grep -qE "^[0-9]+/[0-9]+$" || echo "trang $p: không thấy số trang"; done
rm -rf /tmp/pg; mkdir -p /tmp/pg; pdftoppm -r 80 -png main.pdf /tmp/pg/p
python "$(cygpath -m /tmp/sheet.py)"
