"""Run with KiCad's python: move reference texts of given footprints to the nearest spot that does not
overlap pads, other silkscreen, or the board edge. Usage: fix_silk.py REF ..."""
import sys, pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB); MM = pcbnew.FromMM
e = b.GetBoardEdgesBoundingBox(); e.Inflate(-MM(0.6))
FP = {f.GetReference(): f for f in b.GetFootprints()}
def box(it, m=0.15):
    bb = it.GetBoundingBox(); bb.Inflate(MM(m)); return bb
obs = [box(p, 0.2) for p in b.GetPads()]
for f in b.GetFootprints():
    for g in f.GraphicalItems():
        if g.GetLayer() == pcbnew.F_SilkS: obs.append(box(g))
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.F_SilkS: obs.append(box(d))
texts = {r: box(FP[r].Reference()) for r in FP if FP[r].Reference().IsVisible()}
for ref in sys.argv[1:]:
    if ref.startswith('='):  # =REF: put the reference text back next to the part's first pad
        f = FP[ref[1:]]; p = next(iter(f.Pads())).GetPosition()
        f.Reference().SetPosition(pcbnew.VECTOR2I(p.x - MM(1.8), p.y)); print(ref, 'reset'); continue
    t = FP[ref].Reference(); p0 = t.GetPosition(); best = None
    others = [v for k, v in texts.items() if k != ref]
    for dx in range(-80, 81, 5):
        for dy in range(-80, 81, 5):
            t.SetPosition(pcbnew.VECTOR2I(p0.x + MM(dx / 10), p0.y + MM(dy / 10)))
            bb = box(t)
            if not e.Contains(bb.GetOrigin()) or not e.Contains(bb.GetEnd()): continue
            if any(bb.Intersects(o) for o in obs + others): continue
            d = dx * dx + dy * dy
            if best is None or d < best[0]: best = (d, dx, dy)
    if best:
        t.SetPosition(pcbnew.VECTOR2I(p0.x + MM(best[1] / 10), p0.y + MM(best[2] / 10)))
        texts[ref] = box(t); print(ref, 'moved', best[1] / 10, best[2] / 10, 'mm')
    else:
        t.SetPosition(p0); print(ref, 'no free spot')
pcbnew.SaveBoard(PCB, b)
