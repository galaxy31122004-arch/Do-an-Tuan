"""Build KICH_BAN_THUYET_TRINH.md from the deck's slide <aside> notes. Usage: slides_script.py VERSION OUT"""
import html, json, pathlib, re, sys
DECK = pathlib.Path(__file__).resolve().parents[1] / 'documents/presentations/do-an-2/deck/project'
ver, out = sys.argv[1], pathlib.Path(sys.argv[2])
order = json.loads((DECK / 'deck.json').read_text(encoding='utf-8'))['order']
txt = lambda s: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()
lines = [f'# Kịch bản thuyết trình — Đồ án 2 (v{ver})', '', 'Bộ slide: https://claude.ai/artifact/ES5pMxzQYagHhdiFTj7gnK', '']
for i, name in enumerate(order, 1):
    h = (DECK / 'slides' / f'{name}.html').read_text(encoding='utf-8')
    title = re.search(r'<h[12][^>]*>(.*?)</h[12]>', h, re.S)
    note = re.search(r'<aside[^>]*>(.*?)</aside>', h, re.S)
    lines += [f'## Slide {i}. {txt(title.group(1)) if title else name}', '', txt(note.group(1)) if note else '', '']
out.write_text('\n'.join(lines), encoding='utf-8')
print('wrote', out, len(order), 'slides')
