"""Run with KiCad's python: find free spots (no courtyard, no foreign copper) for a WxH mm box.
Usage: free_space.py W H exclude_refs(comma) [near_x near_y]"""
import sys, pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB); mm = pcbnew.ToMM
W, H = float(sys.argv[1]), float(sys.argv[2]); ex = set(sys.argv[3].split(','))
near = tuple(map(float, sys.argv[4:6])) if len(sys.argv) > 5 else None
e = b.GetBoardEdgesBoundingBox(); L, T, R, B = mm(e.GetLeft()) + 1, mm(e.GetTop()) + 1, mm(e.GetRight()) - 1, mm(e.GetBottom()) - 1
obs = []
for f in b.GetFootprints():
    if f.GetReference() in ex: continue
    c = f.GetCourtyard(pcbnew.F_CrtYd)
    bb = c.BBox() if c.OutlineCount() else f.GetBoundingBox(False)
    obs.append((mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())))
exnets = {p.GetNetCode() for f in b.GetFootprints() if f.GetReference() in ex for p in f.Pads()}
for t in b.GetTracks():
    bb = t.GetBoundingBox(); m = 0.3
    obs.append((mm(bb.GetLeft()) - m, mm(bb.GetTop()) - m, mm(bb.GetRight()) + m, mm(bb.GetBottom()) + m))
hit = lambda x, y: any(x < o[2] and x + W > o[0] and y < o[3] and y + H > o[1] for o in obs)
spots = []
y = T
while y + H <= B:
    x = L
    while x + W <= R:
        if not hit(x, y): spots.append((x, y))
        x += 0.5
    y += 0.5
if near: spots.sort(key=lambda s: (s[0] + W / 2 - near[0]) ** 2 + (s[1] + H / 2 - near[1]) ** 2)
print(len(spots), 'spots;', ' '.join(f'({x:.1f},{y:.1f})' for x, y in spots[:15]))
