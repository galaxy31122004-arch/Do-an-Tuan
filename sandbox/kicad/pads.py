"""Print absolute pad positions + nets for given refs from the PCB."""
import math, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from remove_caps import blocks, ref_of  # noqa
t = (pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb').read_text(encoding='utf-8')
want = set(sys.argv[1:])
for s, e in blocks(t, 'footprint "', '\t'):
    b = t[s:e]; r = ref_of(b)
    if r not in want: continue
    ax, ay, *ang = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)( [-\d.]+)?\)', b).groups()
    a = math.radians(float(ang[0] or 0)); ax, ay = float(ax), float(ay)
    print(r, 'at', ax, ay, 'rot', ang[0])
    for m in re.finditer(r'\(pad "(\d+)".*?\(at ([-\d.]+) ([-\d.]+)[^)]*\)(.*?)\n\t\t\)', b, re.S):
        x, y = float(m[2]), float(m[3])
        X = ax + x * math.cos(a) + y * math.sin(a); Y = ay - x * math.sin(a) + y * math.cos(a)
        net = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', m[4])
        print(f'  {r}.{m[1]:>2} ({X:7.2f},{Y:7.2f}) {net[1] if net else "-"}')
