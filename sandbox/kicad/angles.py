"""Run with KiCad's python: report tracks that break the 45-degree rule.
- segments whose direction is not a multiple of 45 deg
- corners where two segments of the same net/layer meet with a turn > 45 deg (90 deg or sharper)
Corners on pads or vias are ignored."""
import math, pathlib, sys, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(sys.argv[1] if len(sys.argv) > 1 else PCB)
mm = pcbnew.ToMM
segs = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK']
vias = {(t.GetPosition().x, t.GetPosition().y) for t in b.GetTracks() if t.GetClass() == 'PCB_VIA'}
pads = [p for p in b.GetPads()]

def on_pad(x, y, layer):
    v = pcbnew.VECTOR2I(x, y)
    return any(p.IsOnLayer(layer) and p.HitTest(v) for p in pads)

def ang(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))

bad_dir, bad_turn = [], []
ends = {}
for t in segs:
    s, e = t.GetStart(), t.GetEnd()
    a = ang((s.x, s.y), (e.x, e.y)) % 45
    if min(a, 45 - a) > 0.5 and t.GetLength() > pcbnew.FromMM(0.05):
        bad_dir.append(t)
    for p, q in (((s.x, s.y), (e.x, e.y)), ((e.x, e.y), (s.x, s.y))):
        ends.setdefault((p, t.GetLayer(), t.GetNetCode()), []).append((t, q))
for (p, layer, net), lst in ends.items():
    if len(lst) != 2 or p in vias or on_pad(p[0], p[1], layer):
        continue
    (t1, q1), (t2, q2) = lst
    d1, d2 = ang(p, q1), ang(p, q2)      # directions leaving the corner
    inner = abs((d1 - d2 + 180) % 360 - 180)   # angle between the two legs
    if inner < 134:                      # turn sharper than 45 deg
        bad_turn.append((p, layer, net, inner, t1, t2))

print(f'{len(segs)} segments; {len(bad_dir)} off-45 segments; {len(bad_turn)} sharp corners')
for t in bad_dir:
    s, e = t.GetStart(), t.GetEnd()
    print(f'  DIR  {t.GetNetname():12} {b.GetLayerName(t.GetLayer()):5} ({mm(s.x):.2f},{mm(s.y):.2f})-({mm(e.x):.2f},{mm(e.y):.2f}) '
          f'{ang((s.x, s.y), (e.x, e.y)):.1f}deg')
for p, layer, net, inner, t1, t2 in bad_turn:
    print(f'  TURN {t1.GetNetname():12} {b.GetLayerName(layer):5} ({mm(p[0]):.2f},{mm(p[1]):.2f}) inner {inner:.0f}deg')
