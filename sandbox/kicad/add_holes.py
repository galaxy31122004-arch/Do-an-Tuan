"""Run with KiCad's python: add M3 mounting holes (board-only) at the free spot nearest each board corner,
if that spot is within MAXD mm of the corner."""
import pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
LIB = r'C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty'
b = pcbnew.LoadBoard(PCB); mm = pcbnew.ToMM; MM = pcbnew.FromMM; MAXD = float(__import__('os').environ.get('MAXD', 12))
def crt(f):
    c = f.GetCourtyard(pcbnew.F_CrtYd); bb = c.BBox() if c.OutlineCount() else f.GetBoundingBox(False)
    return mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())
e = b.GetBoardEdgesBoundingBox(); L, T, R, B = mm(e.GetLeft()), mm(e.GetTop()), mm(e.GetRight()), mm(e.GetBottom())
obs = [crt(f) for f in b.GetFootprints()]
for t in b.GetTracks():
    bb = t.GetBoundingBox(); obs.append((mm(bb.GetLeft()) - .5, mm(bb.GetTop()) - .5, mm(bb.GetRight()) + .5, mm(bb.GetBottom()) + .5))
FPN = __import__('os').environ.get('HOLE', 'MountingHole_3.2mm_M3'); SIZE = FPN.split('_')[-1]
r = {'M3': 3.6, 'M2.5': 3.15, 'M2': 2.6}[SIZE]  # half courtyard + margin
free = lambda x, y: x - r >= L + .5 and y - r >= T + .5 and x + r <= R - .5 and y + r <= B - .5 and not any(
    x - r < o[2] and x + r > o[0] and y - r < o[3] and y + r > o[1] for o in obs)
n = len([f for f in b.GetFootprints() if f.GetReference().startswith('H')])
for cx, cy in ((L, T), (R, T), (L, B), (R, B)):
    best = None
    if any(f.GetReference().startswith('H') and ((mm(f.GetPosition().x) - cx) ** 2 + (mm(f.GetPosition().y) - cy) ** 2) ** .5 < MAXD + 5
           for f in b.GetFootprints()): continue  # corner already has a hole
    for i in range(0, int(MAXD * 4)):
        for j in range(0, int(MAXD * 4)):
            x = cx + (1 if cx == L else -1) * (r + .5 + i / 4); y = cy + (1 if cy == T else -1) * (r + .5 + j / 4)
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** .5
            if d <= MAXD + r and free(x, y) and (best is None or d < best[0]): best = (d, x, y)
    if not best: print('corner', cx, cy, 'no room'); continue
    n += 1; f = pcbnew.FootprintLoad(LIB, FPN)
    f.SetReference(f'H{n}'); f.SetValue(SIZE); f.SetFPID(pcbnew.LIB_ID('MountingHole', FPN))
    f.SetBoardOnly(True); f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
    f.SetPosition(pcbnew.VECTOR2I(MM(round(best[1], 2)), MM(round(best[2], 2)))); b.Add(f)
    obs.append(crt(f)); print(f'H{n} at ({best[1]:.2f},{best[2]:.2f}), {best[0]:.1f} mm from corner')
pcbnew.SaveBoard(PCB, b)
