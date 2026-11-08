"""Reassign TXS0108E channels / ESP32 GPIOs to match the PCB placement.
Wires on the re-assigned nets are removed; every pin of those nets gets a local label instead."""
import json, os, re, subprocess, tempfile, uuid, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from remove_caps import blocks, drop, ref_of  # noqa

SCH = pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_sch'
CLI = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
NEW = {  # net: pins   (ESP32 GPIO4/3/0 sit right above TXS A4/A5/OE on the PCB)
    'SDA5': 'U1.1 U4.19', 'SCL5': 'U1.2 U4.18', 'TX51': 'U1.11 U4.15', 'RX51': 'U1.10 U4.16',
    'SDA3': 'U4.9 J4.4', 'SCL3': 'U4.8 J4.3', 'TX51_3V3': 'U4.5 U2.4', 'RX51_3V3': 'U4.6 U2.5',
    'OE': 'U4.10 U2.8 R4.1',
}
UNUSED = 'U4.2 U4.3 U4.4 U4.7 U4.12 U4.13 U4.14 U4.17 U2.9 U2.10'
t = SCH.read_text(encoding='utf-8')

# --- pin positions --------------------------------------------------------
lib = {}
ls, le = next(blocks(t, 'lib_symbols', '\t'))
for s, e in blocks(t[ls:le], 'symbol "', '\t\t'):
    b = t[ls:le][s:e]; name = re.search(r'\(symbol "([^"]+)"', b)[1]
    lib[name] = {m[3]: (float(m[1]), float(m[2])) for m in re.finditer(
        r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) [-\d.]+\).*?\(number "([^"]+)"', b, re.S)}
pos = {}
for s, e in blocks(t, 'symbol\n\t\t(lib_id', '\t'):
    b = t[s:e]; r = ref_of(b)
    lid = re.search(r'\(lib_id "([^"]+)"', b)[1]
    ax, ay, rot = map(float, re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)', b).groups())
    mir = re.search(r'\n\t\t\(mirror (\w)\)', b)
    for n, (px, py) in lib.get(lid, {}).items():
        x, y = px, -py
        if mir and mir[1] == 'y': x = -x
        if mir and mir[1] == 'x': y = -y
        for _ in range(int(rot) // 90 % 4): x, y = y, -x
        pos[f'{r}.{n}'] = (round(ax + x, 2), round(ay + y, 2))
pins = {p for v in NEW.values() for p in v.split()} | set(UNUSED.split())
pins |= {'U4.%d' % i for i in list(range(2, 11)) + list(range(12, 20))} | {'U2.9', 'U2.10'}
missing = [p for p in pins if p not in pos]
assert not missing, missing
hot = {pos[p] for p in pins}
near = lambda x, y: any(abs(x - a) < 0.02 and abs(y - b) < 0.02 for a, b in hot)

# --- drop wires / no-connects / labels on those pins, then prune dangling ---
xy = lambda b: [(float(a), float(c)) for a, c in re.findall(r'\(xy ([-\d.]+) ([-\d.]+)\)', b)]
t, n1 = drop(t, 'wire', '\t', lambda b: any(near(*p) for p in xy(b)))
t, n2 = drop(t, 'no_connect', '\t', lambda b: near(*map(float, re.search(r'\(at ([-\d.]+) ([-\d.]+)', b).groups())))
SCH.write_text(t, encoding='utf-8')
print('wires', n1, 'no-connects', n2)
rpt = os.path.join(tempfile.gettempdir(), 'erc_sw.json')
for _ in range(60):
    subprocess.run([CLI, 'sch', 'erc', '--format', 'json', '--units', 'mm', '-o', rpt, str(SCH)], capture_output=True)
    v = [x for s in json.load(open(rpt, encoding='utf-8'))['sheets'] for x in s['violations']]
    dang = {(round(i['pos']['x'] * 100, 2), round(i['pos']['y'] * 100, 2)) for x in v
            if x['type'] in ('wire_dangling', 'unconnected_wire_endpoint') for i in x['items']}
    if not dang: break
    t = SCH.read_text(encoding='utf-8')
    t, n = drop(t, 'wire', '\t', lambda b: any(abs(p[0] - a) < 0.02 and abs(p[1] - c) < 0.02 for p in xy(b) for a, c in dang))
    t, _ = drop(t, 'junction', '\t', lambda b: False)
    SCH.write_text(t, encoding='utf-8')
    if not n: print('stuck', dang); break

# --- labels + no-connects -----------------------------------------------
t = SCH.read_text(encoding='utf-8')
add = ''
for net, ps in NEW.items():
    for p in ps.split():
        x, y = pos[p]
        add += (f'\t(label "{net}"\n\t\t(at {x} {y} 0)\n\t\t(fields_autoplaced yes)\n\t\t(effects\n\t\t\t(font\n'
                f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
for p in UNUSED.split():
    x, y = pos[p]
    add += f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n'
i = t.index('\n\t(sheet_instances')
SCH.write_text(t[:i + 1] + add + t[i + 1:], encoding='utf-8')
print('labels/no-connects added')


