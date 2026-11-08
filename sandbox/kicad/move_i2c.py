"""Move AT89S52 software I2C from P1.0/P1.1 (pins 1/2) to P0.1/P0.2 (pins 38/37), right under
TXS B8/B7 on the PCB. P0 is open-drain -> add R8/R9 10k pull-ups to +5V."""
import re, uuid, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from remove_caps import blocks, drop, ref_of  # noqa

SCH = pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_sch'
t = SCH.read_text(encoding='utf-8')

lib = {}
ls, le = next(blocks(t, 'lib_symbols', '\t'))
for s, e in blocks(t[ls:le], 'symbol "', '\t\t'):
    b = t[ls:le][s:e]; name = re.search(r'\(symbol "([^"]+)"', b)[1]
    lib[name] = {m[3]: (float(m[1]), float(m[2])) for m in re.finditer(
        r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) [-\d.]+\).*?\(number "([^"]+)"', b, re.S)}
pos, blk = {}, {}
for s, e in blocks(t, 'symbol\n\t\t(lib_id', '\t'):
    b = t[s:e]; r = ref_of(b); blk.setdefault(r, b)
    lid = re.search(r'\(lib_id "([^"]+)"', b)[1]
    ax, ay, rot = map(float, re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)', b).groups())
    mir = re.search(r'\n\t\t\(mirror (\w)\)', b)
    for n, (px, py) in lib.get(lid, {}).items():
        x, y = px, -py
        if mir and mir[1] == 'y': x = -x
        if mir and mir[1] == 'x': y = -y
        for _ in range(int(rot) // 90 % 4): x, y = y, -x
        pos[f'{r}.{n}'] = (round(ax + x, 2), round(ay + y, 2))

at = lambda b: tuple(map(float, re.search(r'\(at ([-\d.]+) ([-\d.]+)', b).groups()))
close = lambda p, q: abs(p[0] - q[0]) < 0.02 and abs(p[1] - q[1]) < 0.02
old = [pos['U1.1'], pos['U1.2']]
new = [pos['U1.38'], pos['U1.37']]
t, nl = drop(t, 'label "', '\t', lambda b: any(close(at(b), p) for p in old))
t, nn = drop(t, 'no_connect', '\t', lambda b: any(close(at(b), p) for p in new))
assert nl == 2, nl
print('labels removed', nl, 'no-connects removed', nn)

def label(net, x, y):
    return (f'\t(label "{net}"\n\t\t(at {x} {y} 0)\n\t\t(fields_autoplaced yes)\n\t\t(effects\n\t\t\t(font\n'
            f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')

def clone(src, ref, x, y, value=None):
    b = src
    ox, oy = at(re.search(r'\n\t\t\(at [^)]*\)', b)[0])
    b = re.sub(r'\(at ([-\d.]+) ([-\d.]+)', lambda m: f'(at {round(float(m[1]) - ox + x, 2)} {round(float(m[2]) - oy + y, 2)}', b)
    b = re.sub(r'\(uuid "[^"]+"\)', lambda m: f'(uuid "{uuid.uuid4()}")', b)
    b = re.sub(r'"Reference" "[^"]+"', f'"Reference" "{ref}"', b)
    b = re.sub(r'\(reference "[^"]+"\)', f'(reference "{ref}")', b)
    if value: b = re.sub(r'"Value" "[^"]+"', f'"Value" "{value}"', b)
    return b + '\n'

add = ''
for (x, y), net in zip(old, ('SDA5', 'SCL5')):
    add += f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n'
r4 = blk['R4']; pwr = next(b for r, b in blk.items() if r.startswith('#PWR') and 'lib_id "power:+5V"' in b)
dx = pos['R4.1'][0] - at(re.search(r'\n\t\t\(at [^)]*\)', r4)[0])[0]
dy1 = pos['R4.1'][1] - at(re.search(r'\n\t\t\(at [^)]*\)', r4)[0])[1]
dy2 = pos['R4.2'][1] - at(re.search(r'\n\t\t\(at [^)]*\)', r4)[0])[1]
assert abs(dx) < 0.01, dx
for i, ((px, py), net, ref, pr) in enumerate(zip(new, ('SDA5', 'SCL5'), ('R8', 'R9'), ('#PWR058', '#PWR059'))):
    lx, ly = px, py
    add += label(net, lx, ly)
    cx, cy = round(px + 25.4 + 7.62 * i, 2), round(py - 20.32, 2)  # resistor body, right of U1
    add += clone(r4, ref, cx, cy, '10k')
    add += label(net, cx, round(cy + dy2, 2))
    add += clone(pwr, pr, cx, round(cy + dy1, 2))
i = t.index('\n\t(sheet_instances')
SCH.write_text(t[:i + 1] + add + t[i + 1:], encoding='utf-8')
print('done', new)
