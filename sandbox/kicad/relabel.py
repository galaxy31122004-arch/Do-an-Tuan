"""Move net labels between pins: relabel.py U1.38=U1.36 U1.37=U1.35
Label at the old pin moves to the new pin; the old pin gets a no-connect, the new pin loses its no-connect."""
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
moves = [a.split('=') for a in sys.argv[1:]]
add = ''
for old, new in moves:
    labs = [t[s:e] for s, e in blocks(t, 'label "', '\t') if close(at(t[s:e]), pos[old])]
    assert len(labs) == 1, (old, len(labs))
    net = re.search(r'\(label "([^"]+)"', labs[0])[1]
    t, _ = drop(t, 'label "', '\t', lambda b: close(at(b), pos[old]))
    t, n = drop(t, 'no_connect', '\t', lambda b: close(at(b), pos[new]))
    x, y = pos[new]
    add += (f'\t(label "{net}"\n\t\t(at {x} {y} 0)\n\t\t(fields_autoplaced yes)\n\t\t(effects\n\t\t\t(font\n'
            f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    x, y = pos[old]
    add += f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n'
    print(net, old, '->', new, 'nc removed', n)
i = t.index('\n\t(sheet_instances')
SCH.write_text(t[:i + 1] + add + t[i + 1:], encoding='utf-8')
