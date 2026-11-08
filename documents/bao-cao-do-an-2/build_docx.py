"""Assemble the report DOCX from the approved Markdown parts + QNU cover template."""
import copy, re, pathlib, shutil
import docx
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm, RGBColor

D = pathlib.Path(__file__).parent
TEMPLATE = pathlib.Path.home() / '.claude/skills/document-authoring/references/cover-template.docx'
OUT = D / 'drafts' / 'bao-cao-do-an-2.docx'
OUT.parent.mkdir(exist_ok=True)
PARTS = ['03-mo-dau.md', '04-chuong-1.md', '05-chuong-2.md', '06-chuong-3.md', '07-chuong-4.md', '08-ket-luan-tltk-phu-luc.md']
FIG = D / 'figures'
FIGS = {  # caption prefix -> (image, caption, width cm)
    'Hình 2.1': ('so-do-khoi.png', 'Hình 2.1. Sơ đồ khối hệ thống', 16),
    'Hình 2.2': ('so-do-nguyen-ly.png', 'Hình 2.2. Sơ đồ nguyên lý toàn mạch (KiCad)', 16),
    'Hình 2.3': ('pcb-top.png', 'Hình 2.3. Mạch in hai lớp, mặt trên (dựng 3D từ KiCad)', 14),
    'Hình 2.4': ('pcb-3d.png', 'Hình 2.4. Mạch in nhìn nghiêng (dựng 3D từ KiCad)', 15),
    'Hình 3.1': ('luu-do-at89s52.png', 'Hình 3.1. Lưu đồ vòng lặp chính firmware AT89S52', 11),
    'Hình 3.2': ('luu-do-esp32.png', 'Hình 3.2. Lưu đồ firmware ESP32-C3', 11),
}
SKIP_CAPTION = ('Hình 3.3', 'Ví dụ minh họa')

doc = docx.Document(str(TEMPLATE))
FONT = 'Times New Roman'


def set_font(run, size=13, bold=None, italic=None, mono=False):
    f = run.font; f.name = 'Consolas' if mono else FONT; f.size = Pt(11 if mono else size)
    run._element.rPr.rFonts.set(qn('w:eastAsia'), f.name)
    if bold is not None: f.bold = bold
    if italic is not None: f.italic = italic
    f.color.rgb = RGBColor(0, 0, 0)


# ---- styles ----
st = doc.styles['Normal']; st.font.name = FONT; st.font.size = Pt(13)
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
for name, size, align in [('Heading 1', 14, WD_ALIGN_PARAGRAPH.CENTER), ('Heading 2', 13, None), ('Heading 3', 13, None)]:
    s = doc.styles[name]; s.font.name = FONT; s.font.size = Pt(size); s.font.bold = True
    s.font.italic = name == 'Heading 3'; s.font.color.rgb = RGBColor(0, 0, 0)
    rpr = s.element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rpr.append(rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'): rf.set(qn(a), FONT)
    for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
    pf = s.paragraph_format; pf.space_before = Pt(12 if name == 'Heading 1' else 8); pf.space_after = Pt(6)
    pf.keep_with_next = True; pf.line_spacing = 1.3; pf.first_line_indent = Cm(0)
    if align is not None: pf.alignment = align
    pf.page_break_before = name == 'Heading 1'

# ---- cover ----
rep = {'[LOẠI TÀI LIỆU]': 'BÁO CÁO ĐỒ ÁN 2',
       '[TÊN/CHỦ ĐỀ]': 'THIẾT KẾ HỆ THỐNG GIÁM SÁT NHIỆT ĐỘ, ĐỘ ẨM SỬ DỤNG AT89S52, ESP32-C3 VÀ NỀN TẢNG IoT',
       '[HỌ VÀ TÊN]': 'Phạm Thanh Tuấn, Nguyễn Quốc Sinh', '[MÃ SỐ]': '',
       '[LỚP]': 'Kỹ thuật điện tử - viễn thông K46', '[GIẢNG VIÊN HƯỚNG DẪN]': 'TS Nguyễn Đỗ Dũng'}
for p in list(doc.paragraphs):
    if p.text.strip() == '[PHỤ ĐỀ]':
        p._element.getparent().remove(p._element); continue
    for r in p.runs:
        for a, b in rep.items():
            if a in r.text: r.text = r.text.replace(a, b)
for p in doc.sections[0].first_page_footer.paragraphs:
    for r in p.runs: r.text = r.text.replace('[ĐỊA DANH, NĂM]', '')
cover_last = doc.paragraphs[-1]
cover_last.add_run().add_break(WD_BREAK.PAGE)

# page number in primary footer
fp = doc.sections[0].footer.paragraphs[0] if doc.sections[0].footer.paragraphs else doc.sections[0].footer.add_paragraph()
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER


def field(par, instr):
    r = par.add_run(); set_font(r, 12)
    for kind, txt in (('begin', None), (None, instr), ('separate', None), (None, '1'), ('end', None)):
        if kind:
            e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), kind); r._element.append(e)
        elif txt == instr:
            e = OxmlElement('w:instrText'); e.set(qn('xml:space'), 'preserve'); e.text = instr; r._element.append(e)
        else:
            e = OxmlElement('w:t'); e.text = txt; r._element.append(e)


for r in list(fp.runs): r._element.getparent().remove(r._element)
field(fp, 'PAGE')


def para(text='', style=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=True):
    p = doc.add_paragraph(style=style)
    pf = p.paragraph_format; pf.line_spacing = 1.3; pf.space_after = Pt(4); pf.space_before = Pt(0)
    if style is None:
        pf.alignment = align
        if indent: pf.first_line_indent = Cm(1)
    if text: inline(p, text)
    return p


def inline(p, text, size=13, bold=False, italic=False):
    for tok in re.split(r'(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)', text):
        if not tok: continue
        if tok.startswith('**'): r = p.add_run(tok[2:-2]); set_font(r, size, True, italic)
        elif tok.startswith('`'): r = p.add_run(tok[1:-1]); set_font(r, size, bold, italic); r.font.name = 'Consolas'; r.font.size = Pt(size - 1)
        elif tok.startswith('*') and len(tok) > 2: r = p.add_run(tok[1:-1]); set_font(r, size, bold, True)
        else: r = p.add_run(tok); set_font(r, size, bold or None, italic or None)


def caption(text):
    p = para('', align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
    r = p.add_run(text); set_font(r, 12, None, True); p.paragraph_format.space_after = Pt(8)
    return p


def picture(img, cap, width):
    p = para('', align=WD_ALIGN_PARAGRAPH.CENTER, indent=False); p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(FIG / img), width=Cm(width))
    caption(cap + '.')


def borders(table):
    tbl = table._tbl; pr = tbl.tblPr; b = OxmlElement('w:tblBorders')
    for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        x = OxmlElement(f'w:{e}'); x.set(qn('w:val'), 'single'); x.set(qn('w:sz'), '4'); x.set(qn('w:color'), '000000'); b.append(x)
    pr.append(b)


def table(rows):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows if not re.match(r'^\|[\s:|-]+\|$', r.strip())]
    n = max(len(r) for r in cells)
    t = doc.add_table(rows=len(cells), cols=n); borders(t)
    for i, r in enumerate(cells):
        for j in range(n):
            c = t.cell(i, j); c.text = ''
            p = c.paragraphs[0]; p.paragraph_format.line_spacing = 1.15; p.paragraph_format.space_after = Pt(2)
            inline(p, r[j] if j < len(r) else '', 12, bold=i == 0)
    tr = t.rows[0]._tr; trPr = tr.get_or_add_trPr(); h = OxmlElement('w:tblHeader'); h.set(qn('w:val'), 'true'); trPr.append(h)
    para('', indent=False).paragraph_format.space_after = Pt(2)


# ---- TOC ----
h = para('', align=WD_ALIGN_PARAGRAPH.CENTER, indent=False); r = h.add_run('MỤC LỤC'); set_font(r, 14, True)
tp = doc.add_paragraph(); field(tp, 'TOC \\o "1-3" \\h \\z \\u')
tp.runs[0]._element.findall(qn('w:t'))[0].text = 'Nhấn chuột phải → Update Field để cập nhật mục lục.'

# ---- body ----
for part in PARTS:
    lines = (D / part).read_text(encoding='utf-8').splitlines()
    i = 0; code = None; tbl = []
    while i < len(lines):
        ln = lines[i]; s = ln.strip(); i += 1
        if part == '04-chuong-1.md' and s == '---': break  # chapter-local refs merged into final list
        if code is not None:
            if s.startswith('```'):
                txt = '\n'.join(code)
                if '─►' not in txt:  # ASCII block diagram replaced by Hình 2.1
                    p = para('', align=WD_ALIGN_PARAGRAPH.LEFT, indent=False); p.paragraph_format.line_spacing = 1.0
                    for k, cl in enumerate(code):
                        r = p.add_run(cl); set_font(r, mono=True)
                        if k < len(code) - 1: r.add_break()
                code = None
            else: code.append(ln)
            continue
        if s.startswith('```'): code = []; continue
        if s.startswith('|'): tbl.append(s); continue
        if tbl: table(tbl); tbl = []
        if not s or s.startswith('>'): continue
        if s.startswith('### '): doc.add_paragraph(s[4:], style='Heading 3'); continue
        if s.startswith('## '): doc.add_paragraph(s[3:], style='Heading 2'); continue
        if s.startswith('# '): doc.add_paragraph(s[2:], style='Heading 1'); continue
        m = re.match(r'^\*(Hình \d\.\d)', s)
        if m or s.startswith(SKIP_CAPTION) or s.startswith('*' + SKIP_CAPTION[1]):
            if m and m[1] in FIGS: picture(*FIGS[m[1]])
            elif s.startswith('*Ví dụ'): caption(s.strip('*'))
            continue
        m = re.match(r'^\*\*(Bảng \d\.\d\..*)\*\*$', s)
        if m:
            p = caption(m[1]); p.paragraph_format.keep_with_next = True; p.runs[0].font.italic = False; p.runs[0].font.bold = True; continue
        lvl = (len(ln) - len(ln.lstrip(' '))) // 2
        m = re.match(r'^([-+]|\d+\.) (.*)', s)
        if m:
            mark = m[1] if m[1].endswith('.') else ('-' if lvl == 0 else '+')
            p = para('', align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=False)
            p.paragraph_format.left_indent = Cm(0.75 + 0.75 * lvl); p.paragraph_format.first_line_indent = Cm(-0.5)
            inline(p, f'{mark} ' if mark in '-+' else f'{mark} '); inline(p, m[2]); continue
        if part.startswith('08') and re.match(r'^\[\d+\]', s):
            p = para(s, indent=False); p.paragraph_format.left_indent = Cm(1); p.paragraph_format.first_line_indent = Cm(-1); continue
        para(s, indent=lvl == 0)
    if tbl: table(tbl)
    if part.startswith('08'):
        pass

# ---- appendix content ----
body = doc.element.body
apps = [p for p in doc.paragraphs if p.text.startswith('(Bảng vật tư đầy đủ') or p.text.startswith('(Sơ đồ nguyên lý xuất')]
bom = (D.parents[1] / 'hardware' / 'BOM.md').read_text(encoding='utf-8').splitlines()
start = next(k for k, l in enumerate(bom) if l.startswith('| Ký hiệu'))
rows = []
for l in bom[start:]:
    if not l.startswith('|'): break
    rows.append(l)
keep = []
for r in rows:
    c = [x.strip() for x in r.strip('|').split('|')]
    if set(r.replace('|', '').strip()) <= set('-: '): continue
    keep.append('| ' + ' | '.join([c[0], c[1], re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', c[2]), c[5]]) + ' |')
mark = len(doc.paragraphs)
table(keep)
new = list(body)[-3:]  # table + spacer + sectPr? ensure we move table & spacer only
tbl_el = [e for e in body if e.tag == qn('w:tbl')][-1]
apps[0]._p.addnext(tbl_el); apps[0]._p.getparent().remove(apps[0]._p)
pic = para('', align=WD_ALIGN_PARAGRAPH.CENTER, indent=False); pic.add_run().add_picture(str(FIG / 'so-do-nguyen-ly.png'), width=Cm(16))
apps[1]._p.addnext(pic._p); apps[1]._p.getparent().remove(apps[1]._p)

doc.save(str(OUT))
print('saved', OUT)
