"""UART through TXS B1/B2 (U4.12/13), right above AT89S52 pins 11/10 on the PCB.
TX51: U1.11-U4.12(B1)/U4.2(A1)-U2.5 (GPIO3 = ESP RX); RX51: U1.10-U4.13(B2)/U4.3(A2)-U2.4 (GPIO4 = ESP TX).
Lower ESP pin goes to the right-most A pin so the two traces do not cross."""
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

at = lambda b: tuple(map(float, re.search(r'\(at ([-\d.]+) ([-\d.]+)', b).groups()))
close = lambda p, q: abs(p[0] - q[0]) < 0.02 and abs(p[1] - q[1]) < 0.02
LABEL = {'U4.12': 'TX51', 'U4.13': 'RX51', 'U4.2': 'TX51_3V3', 'U4.3': 'RX51_3V3',
         'U2.5': 'TX51_3V3', 'U2.4': 'RX51_3V3'}
OLD = ['U4.15', 'U4.16', 'U4.5', 'U4.6', 'U2.4', 'U2.5']   # labels to drop
NC_ADD = ['U4.15', 'U4.16', 'U4.5', 'U4.6']
NC_DEL = ['U4.12', 'U4.13', 'U4.2', 'U4.3']
t, nl = drop(t, 'label "', '\t', lambda b: any(close(at(b), pos[p]) for p in OLD))
t, nn = drop(t, 'no_connect', '\t', lambda b: any(close(at(b), pos[p]) for p in NC_DEL))
assert nl == 6 and nn == 4, (nl, nn)
add = ''
for p, net in LABEL.items():
    x, y = pos[p]
    add += (f'\t(label "{net}"\n\t\t(at {x} {y} 0)\n\t\t(fields_autoplaced yes)\n\t\t(effects\n\t\t\t(font\n'
            f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
for p in NC_ADD:
    x, y = pos[p]
    add += f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n'
i = t.index('\n\t(sheet_instances')
SCH.write_text(t[:i + 1] + add + t[i + 1:], encoding='utf-8')
print('ok')
