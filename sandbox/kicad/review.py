"""Run with KiCad's python: PCB review report (board, widths per net, vias, key pin nets, parts off board)."""
import collections, pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB); mm = pcbnew.ToMM
e = b.GetBoardEdgesBoundingBox()
print(f'board {mm(e.GetWidth()):.1f} x {mm(e.GetHeight()):.1f} mm; footprints {len(b.GetFootprints())}')
w = collections.defaultdict(list); vias = []
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA': vias.append((t.GetNetname(), mm(t.GetWidth(pcbnew.F_Cu)), mm(t.GetDrillValue())))
    else: w[t.GetNetname()].append((mm(t.GetWidth()), mm(t.GetLength()), b.GetLayerName(t.GetLayer())))
print('segments', sum(len(v) for v in w.values()), 'vias', len(vias), set((d, dr) for _, d, dr in vias))
print('\nnet: min/max width (mm), total length (mm), layers')
for n in sorted(w):
    ws = [x[0] for x in w[n]]
    print(f'  {n:42} {min(ws):.2f}/{max(ws):.2f}  {sum(x[1] for x in w[n]):6.1f}  {sorted(set(x[2] for x in w[n]))}')
print('\nzones:', [(z.GetNetname(), b.GetLayerName(z.GetLayer()), z.IsFilled()) for z in b.Zones()])
print('\nkey pins:')
for ref, pins in (('U1', '9 10 11 12 13 18 19 20 21 31 35 36 40'), ('U4', '1 2 3 10 11 12 13 18 19 20'),
                  ('U2', '1 2 3 4 5 8'), ('J4', '1 2 3 4'), ('K1', '1 2 3 4 5'), ('J6', '1 2'), ('Q1', '1 2 3')):
    f = b.FindFootprintByReference(ref); pd = {p.GetNumber(): p.GetNetname() for p in f.Pads()}
    print(f'  {ref}: ' + ', '.join(f'{n}={pd.get(n)}' for n in pins.split()))
print('\noff-board / overhanging parts:')
for f in b.GetFootprints():
    c = f.GetCourtyard(pcbnew.F_CrtYd); bb = c.BBox() if c.OutlineCount() else f.GetBoundingBox(False)
    if not e.Contains(bb.GetOrigin()) or not e.Contains(bb.GetEnd()):
        print(f'  {f.GetReference()} crt {mm(bb.GetLeft()):.1f},{mm(bb.GetTop()):.1f}-{mm(bb.GetRight()):.1f},{mm(bb.GetBottom()):.1f}')
