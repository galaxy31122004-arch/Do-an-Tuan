"""Remove capacitors from schematic + PCB, then prune wires ERC reports as dangling (loop)."""
import json, os, re, subprocess, sys, pathlib, tempfile
P = pathlib.Path(__file__).resolve().parents[2] / 'hardware' / 'pcb'
SCH, PCB = P / 'env-monitor.kicad_sch', P / 'env-monitor.kicad_pcb'
CLI = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
REFS = set(sys.argv[1:])


def blocks(t, head, indent):
    """Yield (start, end) of top-level-ish blocks '\n<indent>(head' with balanced parens (strings skipped)."""
    pat = '\n' + indent + '(' + head
    i = 0
    while True:
        s = t.find(pat, i)
        if s < 0: return
        s += 1
        d, e, q = 0, s, False
        while True:
            c = t[e]
            if c == '"' and t[e - 1] != '\\': q = not q
            elif not q:
                if c == '(': d += 1
                elif c == ')':
                    d -= 1
                    if d == 0: break
            e += 1
        yield s, e + 1
        i = e


def drop(t, head, indent, pred):
    out, last = [], 0
    n = 0
    for s, e in blocks(t, head, indent):
        if pred(t[s:e]):
            out.append(t[last:s - 1]); last = e; n += 1
    out.append(t[last:])
    return ''.join(out), n


ref_of = lambda b: (re.search(r'\(property "Reference" "([^"]+)"', b) or [None, None])[1]
sch = SCH.read_text(encoding='utf-8')
sch, n = drop(sch, 'symbol\n\t\t(lib_id', '\t', lambda b: ref_of(b) in REFS)
print('schematic symbols removed:', n)
SCH.write_text(sch, encoding='utf-8')
pcb = PCB.read_text(encoding='utf-8')
pcb, n = drop(pcb, 'footprint "', '\t', lambda b: ref_of(b) in REFS)
print('pcb footprints removed:', n)
PCB.write_text(pcb, encoding='utf-8')

rpt = os.path.join(tempfile.gettempdir(), 'erc_rm.json')
for it in range(40):
    subprocess.run([CLI, 'sch', 'erc', '--format', 'json', '--units', 'mm', '-o', rpt, str(SCH)], capture_output=True)
    v = [x for s in json.load(open(rpt, encoding='utf-8'))['sheets'] for x in s['violations']]
    pts = set()
    for x in v:
        if x['type'] in ('wire_dangling', 'unconnected_wire_endpoint'):
            for it2 in x['items']:
                pts.add((round(it2['pos']['x'] * 100, 2), round(it2['pos']['y'] * 100, 2)))
    if not pts:
        print('remaining ERC:', sorted({x['type'] for x in v}) or 'none', len(v)); break
    sch = SCH.read_text(encoding='utf-8')

    def touches(b):
        xy = re.findall(r'\(xy ([-\d.]+) ([-\d.]+)\)', b)
        return any((round(float(a), 2), round(float(c), 2)) in pts or
                   any(abs(float(a) - px) < 0.02 and abs(float(c) - py) < 0.02 for px, py in pts) for a, c in xy)
    sch, n = drop(sch, 'wire', '\t', touches)
    if n == 0:
        print('dangling but no wire matched:', pts, [x['type'] for x in v]); break
    SCH.write_text(sch, encoding='utf-8')
    print('pass', it, 'wires removed', n)

