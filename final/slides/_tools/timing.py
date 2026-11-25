import re, sys
s = open(sys.argv[1] if len(sys.argv) > 1 else 'main.tex', encoding='utf-8').read().split('\appendix')[0]
BS = chr(92)
parts = s.split(BS + 'begin{frame}')[1:]
tot = 0; who_t = {}
for p in parts:
    b = p.split(BS + 'end{frame}')[0]
    title = b.split('\n')[0][:70]
    m = re.search(r'note\{\[(\d+):(\d+)\]', b)
    sec = int(m[1]) * 60 + int(m[2]) if m else 0
    w = re.search(r'\((Trí|Triệu)\)', b)
    tot += sec
    print(f"{sec:4d}s {w[1] if w else '':6} {title}")
print('frames', len(parts), 'total', tot // 60, 'm', tot % 60, 's')
