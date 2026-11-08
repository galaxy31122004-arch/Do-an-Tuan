"""Run with KiCad's python: move the right side of the Edge.Cuts rectangle to X mm, refill zones to the new outline.
Usage: set_edge.py RIGHT_X"""
import sys, pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB); X = pcbnew.FromMM(float(sys.argv[1]))
r = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
assert len(r) == 1 and r[0].GetShape() == pcbnew.SHAPE_T_RECT, [d.GetShapeStr() for d in r]
s, e = r[0].GetStart(), r[0].GetEnd()
if e.x > s.x: r[0].SetEnd(pcbnew.VECTOR2I(X, e.y))
else: r[0].SetStart(pcbnew.VECTOR2I(X, s.y))
bb = r[0].GetBoundingBox()
for z in b.Zones():
    o = z.Outline(); o.RemoveAllContours(); o.NewOutline()
    for x, y in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()), (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())):
        o.Append(x, y)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
print('board', pcbnew.ToMM(bb.GetWidth()), 'x', pcbnew.ToMM(bb.GetHeight()), 'mm')
