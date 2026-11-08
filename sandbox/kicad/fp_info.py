"""Run with KiCad's python: list footprints with fpid, position and courtyard bbox (mm)."""
import pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB)
mm = pcbnew.ToMM
e = b.GetBoardEdgesBoundingBox()
print('board', mm(e.GetLeft()), mm(e.GetTop()), mm(e.GetRight()), mm(e.GetBottom()))
for f in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    c = f.GetCourtyard(pcbnew.F_CrtYd).BBox() if f.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else f.GetBoundingBox(False)
    p = f.GetPosition()
    print(f'{f.GetReference():5} {f.GetFPIDAsString():70} at {mm(p.x):7.2f},{mm(p.y):7.2f} rot {f.GetOrientationDegrees():6.1f} '
          f'crt {mm(c.GetLeft()):.1f},{mm(c.GetTop()):.1f}-{mm(c.GetRight()):.1f},{mm(c.GetBottom()):.1f}')

