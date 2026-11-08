"""Run with KiCad's python: swap footprints and place parts at the nearest free spot to a target.
Obstacles: other courtyards, tracks (+0.3 mm), board edge (1 mm). Tries rotations 0/90/180/270."""
import pathlib, pcbnew
ROOT = pathlib.Path(__file__).resolve().parents[2]
PCB = str(ROOT / 'hardware/pcb/env-monitor.kicad_pcb')
SYS = r'C:\Program Files\KiCad\10.0\share\kicad\footprints'
b = pcbnew.LoadBoard(PCB); mm = pcbnew.ToMM; MM = pcbnew.FromMM
VERT = (SYS + r'\Resistor_THT.pretty', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical')
# ref: (new footprint or None, target pad "REF.PAD" to stay close to)
PLAN = [('Q1', None, '131.5,116.5'), ('R8', VERT, 'U4.19'), ('R9', VERT, 'U4.18'),
        ('R1', VERT, 'U1.9'), ('R3', VERT, 'U1.13'),
        ('TP1', None, 'U7.3'), ('TP2', None, 'U2.3'), ('TP3', None, 'U7.2')]
import sys
if len(sys.argv) > 1:  # REF=lib_dir|fp_name@target ...  (fp part may be '-' to keep the footprint)
    PLAN = []
    for a in sys.argv[1:]:
        ref, rest = a.split('=', 1); fp, tgt = rest.rsplit('@', 1)
        PLAN.append((ref, None if fp == '-' else tuple(fp.split('|')), tgt))

def swap(ref, lib, fp):
    old = FP[ref]
    new = pcbnew.FootprintLoad(lib, fp)
    new.SetPosition(old.GetPosition()); new.SetReference(ref); new.SetValue(old.GetValue())
    new.SetFPID(pcbnew.LIB_ID(pathlib.Path(lib).stem, fp)); new.SetPath(old.GetPath())
    nets = {p.GetNumber(): p.GetNet() for p in old.Pads()}
    b.Remove(old); b.Add(new)
    for p in new.Pads():
        if p.GetNumber() in nets: p.SetNet(nets[p.GetNumber()])
    return new

def crt(f):
    c = f.GetCourtyard(pcbnew.F_CrtYd)
    bb = c.BBox() if c.OutlineCount() else f.GetBoundingBox(False)
    return mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())

def pad(spec):
    if ',' in spec: return tuple(map(float, spec.split(',')))
    r, n = spec.split('.')
    p = next(p for p in b.FindFootprintByReference(r).Pads() if p.GetNumber() == n).GetPosition()
    return mm(p.x), mm(p.y)

refs = {r for r, _, _ in PLAN}
e = b.GetBoardEdgesBoundingBox()
L, T, R, B = mm(e.GetLeft()) + 1, mm(e.GetTop()) + 1, mm(e.GetRight()) - 1, mm(e.GetBottom()) - 1
obs = [crt(f) for f in b.GetFootprints() if f.GetReference() not in refs]
for t in b.GetTracks():
    bb = t.GetBoundingBox()
    obs.append((mm(bb.GetLeft()) - .3, mm(bb.GetTop()) - .3, mm(bb.GetRight()) + .3, mm(bb.GetBottom()) + .3))
hit = lambda a: a[0] < L or a[1] < T or a[2] > R or a[3] > B or any(
    a[0] < o[2] and a[2] > o[0] and a[1] < o[3] and a[3] > o[1] for o in obs)

TGT = {tgt: pad(tgt) for _, _, tgt in PLAN}
FP = {f.GetReference(): f for f in b.GetFootprints()}
for ref, new, tgt in PLAN:
    f = swap(ref, *new) if new else FP[ref]
    tx, ty = TGT[tgt]; best = None
    for rot in (0, 90, 180, 270):
        f.SetOrientationDegrees(rot); f.SetPosition(pcbnew.VECTOR2I(0, 0))
        l, t_, r, bt = crt(f)
        y = T
        while y + (bt - t_) <= B:
            x = L
            while x + (r - l) <= R:
                box = (x, y, x + r - l, y + bt - t_)
                if not hit(box):
                    d = (x + (r - l) / 2 - tx) ** 2 + (y + (bt - t_) / 2 - ty) ** 2
                    if best is None or d < best[0]: best = (d, rot, x - l, y - t_)
                x += 0.25
            y += 0.25
    assert best, ref
    _, rot, ox, oy = best
    f.SetOrientationDegrees(rot); f.SetPosition(pcbnew.VECTOR2I(MM(round(ox, 2)), MM(round(oy, 2))))
    obs.append(tuple(v + s for v, s in zip(crt(f), (-.2, -.2, .2, .2))))
    print(f'{ref} -> ({mm(f.GetPosition().x):.2f},{mm(f.GetPosition().y):.2f}) rot {rot}, {best[0] ** .5:.1f} mm from {tgt}')
pcbnew.SaveBoard(PCB, b)
