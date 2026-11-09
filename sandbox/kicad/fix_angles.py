"""Run with KiCad's python: make every track obey the 45-degree rule.
- sharp corners (90 deg or less) between two segments get a 45-degree chamfer
- off-45 segments are split into a straight + 45-degree pair
Each change is kept only if a DRC run shows no new clearance/short/connection problem."""
import math, pathlib, shutil, subprocess, json, tempfile, pcbnew
ROOT = pathlib.Path(__file__).resolve().parents[2]
PCB = ROOT / 'hardware/pcb/env-monitor.kicad_pcb'
CLI = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
TMP = pathlib.Path(tempfile.gettempdir()) / 'fix_angles'
TMP.mkdir(exist_ok=True)
BAD = {'clearance', 'shorting_items', 'tracks_crossing', 'unconnected_items', 'copper_edge_clearance',
       'hole_clearance', 'track_dangling', 'solder_mask_bridge'}
F = pcbnew.FromMM


def drc(path):
    rep = TMP / 'drc.json'
    subprocess.run([CLI, 'pcb', 'drc', '--format', 'json', '--schematic-parity', '-o', str(rep), str(path)],
                   capture_output=True)
    d = json.loads(rep.read_text(encoding='utf-8'))
    items = d.get('violations', []) + d.get('unconnected_items', [])
    return sorted(v['type'] + ':' + ';'.join(i.get('description', '') for i in v.get('items', []))
                  for v in items if v['type'] in BAD)


def load(path):
    return pcbnew.LoadBoard(str(path))


def seg(b, ref, a, c):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(int(a[0]), int(a[1]))); t.SetEnd(pcbnew.VECTOR2I(int(c[0]), int(c[1])))
    t.SetWidth(ref.GetWidth()); t.SetLayer(ref.GetLayer()); t.SetNet(ref.GetNet())
    b.Add(t)


def find_corners(b):
    pads = list(b.GetPads())
    vias = {(t.GetPosition().x, t.GetPosition().y) for t in b.GetTracks() if t.GetClass() == 'PCB_VIA'}
    ends = {}
    for t in b.GetTracks():
        if t.GetClass() != 'PCB_TRACK':
            continue
        s, e = t.GetStart(), t.GetEnd()
        for p, q in (((s.x, s.y), (e.x, e.y)), ((e.x, e.y), (s.x, s.y))):
            ends.setdefault((p, t.GetLayer(), t.GetNetCode()), []).append((t, q))
    out = []
    for (p, layer, net), lst in ends.items():
        if len(lst) != 2 or p in vias or any(pd.IsOnLayer(layer) and pd.HitTest(pcbnew.VECTOR2I(*p)) for pd in pads):
            continue
        (t1, q1), (t2, q2) = lst
        a1 = math.atan2(q1[1] - p[1], q1[0] - p[0]); a2 = math.atan2(q2[1] - p[1], q2[0] - p[0])
        inner = abs(math.degrees((a1 - a2 + math.pi) % (2 * math.pi) - math.pi))
        if inner < 134:
            out.append((p, t1.m_Uuid.AsString(), q1, t2.m_Uuid.AsString(), q2))
    return out


def off45(b):
    out = []
    for t in b.GetTracks():
        if t.GetClass() != 'PCB_TRACK':
            continue
        s, e = t.GetStart(), t.GetEnd()
        a = math.degrees(math.atan2(e.y - s.y, e.x - s.x)) % 45
        if min(a, 45 - a) > 0.5 and t.GetLength() > F(0.05):
            out.append((t.m_Uuid.AsString(), (s.x, s.y), (e.x, e.y)))
    return out


def by_uuid(b, u):
    return next(t for t in b.GetTracks() if t.m_Uuid.AsString() == u)


def try_change(apply, label):
    b = load(PCB)
    apply(b)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    cand = TMP / 'cand.kicad_pcb'
    pcbnew.SaveBoard(str(cand), b)
    new = drc(cand)
    if new == BASE[0]:
        shutil.copy(cand, PCB); print('  ok  ', label); return True
    print('  FAIL', label, [x for x in new if x not in BASE[0]][:2]); return False


shutil.copy(PCB, TMP / 'backup.kicad_pcb')
BASE = [drc(PCB)]
print('baseline problems:', len(BASE[0]))

# 1. off-45 segments: s -> knee -> e, knee chosen so one leg is 45 deg and the other straight
for u, s, e in off45(load(PCB)):
    dx, dy = e[0] - s[0], e[1] - s[1]
    m = min(abs(dx), abs(dy)); sx = 1 if dx > 0 else -1; sy = 1 if dy > 0 else -1
    knees = [(s[0] + sx * m, s[1] + sy * m), (e[0] - sx * m, e[1] - sy * m)]   # diagonal first / diagonal last
    for k in knees:
        def apply(b, u=u, s=s, e=e, k=k):
            t = by_uuid(b, u); seg(b, t, s, k); seg(b, t, k, e); b.Delete(t)
        if try_change(apply, f'split {pcbnew.ToMM(s[0]):.2f},{pcbnew.ToMM(s[1]):.2f}'):
            break

# 2. sharp corners: chamfer (re-scan after every change; give up on a corner after all sizes fail)
failed = set()
while True:
    todo = [c for c in find_corners(load(PCB)) if (round(c[0][0], -3), round(c[0][1], -3)) not in failed]
    if not todo:
        break
    p, u1, q1, u2, q2 = todo[0]
    l1 = math.dist(p, q1); l2 = math.dist(p, q2)
    done = False
    for d_mm in (1.0, 0.6, 0.35):
        d = min(F(d_mm), 0.45 * l1, 0.45 * l2)
        if d < F(0.1):
            break
        c1 = (p[0] + (q1[0] - p[0]) * d / l1, p[1] + (q1[1] - p[1]) * d / l1)
        c2 = (p[0] + (q2[0] - p[0]) * d / l2, p[1] + (q2[1] - p[1]) * d / l2)
        def apply(b, u1=u1, u2=u2, q1=q1, q2=q2, c1=c1, c2=c2):
            t1, t2 = by_uuid(b, u1), by_uuid(b, u2)
            seg(b, t1, q1, c1); seg(b, t1, c1, c2); seg(b, t2, c2, q2); b.Delete(t1); b.Delete(t2)
        if try_change(apply, f'chamfer {pcbnew.ToMM(p[0]):.2f},{pcbnew.ToMM(p[1]):.2f} d={pcbnew.ToMM(d):.2f}'):
            done = True; break
    if not done:
        print('  SKIP', f'{pcbnew.ToMM(p[0]):.2f},{pcbnew.ToMM(p[1]):.2f}', f'legs {pcbnew.ToMM(l1):.2f}/{pcbnew.ToMM(l2):.2f}')
        failed.add((round(p[0], -3), round(p[1], -3)))

# 3. corners with a tiny leg (< 0.1 mm stub): drop the stub and stretch the long leg to the stub's far end
for p, u1, q1, u2, q2 in find_corners(load(PCB)):
    l1 = math.dist(p, q1); l2 = math.dist(p, q2)
    if min(l1, l2) >= F(0.1):
        continue
    us, qs, ul, ql = (u1, q1, u2, q2) if l1 < l2 else (u2, q2, u1, q1)
    def apply(b, us=us, qs=qs, ul=ul, ql=ql):
        ts, tl = by_uuid(b, us), by_uuid(b, ul)
        seg(b, tl, ql, qs); b.Delete(ts); b.Delete(tl)
    try_change(apply, f'merge stub {pcbnew.ToMM(p[0]):.2f},{pcbnew.ToMM(p[1]):.2f}')
