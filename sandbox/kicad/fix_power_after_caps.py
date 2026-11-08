"""After cap removal: delete orphaned power symbols, put a fresh power symbol on each orphaned supply pin."""
import json, os, re, uuid, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from remove_caps import blocks, drop, ref_of  # noqa: E402  (module runs nothing with no args)

SCH = pathlib.Path(__file__).resolve().parents[2] / 'hardware' / 'pcb' / 'env-monitor.kicad_sch'
NET = {'U2.1': '+5V', 'U4.11': '+5V', 'U1.40': '+5V', 'J4.2': '+3V3', 'U4.1': '+3V3'}
d = json.load(open(os.environ['TEMP'] + '/erc_rm.json', encoding='utf-8'))
orphan, pins = set(), {}
for s in d['sheets']:
    for x in s['violations']:
        if x['type'] != 'pin_not_connected': continue
        it = x['items'][0]
        m = re.match(r'Symbol (\S+) Pin (\d+)', it['description'])
        if m[1].startswith('#PWR'): orphan.add(m[1])
        else: pins[f'{m[1]}.{m[2]}'] = (it['pos']['x'] * 100, it['pos']['y'] * 100)
t = SCH.read_text(encoding='utf-8')
t, n = drop(t, 'symbol\n\t\t(lib_id', '\t', lambda b: ref_of(b) in orphan)
print('orphan power symbols removed', n)
tmpl = {}
for s, e in blocks(t, 'symbol\n\t\t(lib_id "power:', '\t'):
    b = t[s:e]; v = re.search(r'\(property "Value" "([^"]+)"', b)[1]
    tmpl.setdefault(v, b)
used = {int(r) for r in re.findall(r'"#PWR(\d+)"', t)}
nxt = max(used) + 1
add = ''
for pin, (x, y) in pins.items():
    b = tmpl[NET[pin]]
    ax, ay = re.search(r'\(at ([-\d.]+) ([-\d.]+) [-\d.]+\)', b).groups()
    dx, dy = round(x - float(ax), 4), round(y - float(ay), 4)
    b = re.sub(r'\(at ([-\d.]+) ([-\d.]+)( [-\d.]+)?\)',
               lambda m: f'(at {round(float(m[1]) + dx, 4)} {round(float(m[2]) + dy, 4)}{m[3] or ""})', b)
    b = re.sub(r'\(uuid "[^"]+"\)', lambda m: f'(uuid "{uuid.uuid4()}")', b)
    old = re.search(r'"(#PWR\d+)"', b)[1]
    b = b.replace(f'"{old}"', f'"#PWR{nxt:03d}"'); nxt += 1
    add += '\t' + b + '\n'
    print(pin, '->', NET[pin], (round(x, 2), round(y, 2)))
i = t.index('\n\t(sheet_instances')
t = t[:i + 1] + add + t[i + 1:]
SCH.write_text(t, encoding='utf-8')
