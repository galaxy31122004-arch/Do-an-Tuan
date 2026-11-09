"""Run with KiCad's python: re-run SCK (B.Cu) below U1 pins 6/7 with a clean 45-degree jog, clear of MOSI pad 6."""
import pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB); mm, F = pcbnew.ToMM, pcbnew.FromMM
OLD = {(170.32, 149.94), (167.30, 149.94), (167.21, 149.85), (166.87, 149.85), (166.78, 149.94), (165.09, 151.64)}
key = lambda p: (round(mm(p.x), 2), round(mm(p.y), 2))
gone = 0
for t in list(b.GetTracks()):
    if t.GetClass() == 'PCB_TRACK' and t.GetNetname() == '/SCK' and key(t.GetStart()) in OLD and key(t.GetEnd()) in OLD:
        b.Delete(t); gone += 1
pts = [(170.32, 149.94), (168.62, 149.94), (166.92, 151.64), (165.09, 151.64)]
for a, c in zip(pts, pts[1:]):
    t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(F(a[0]), F(a[1]))); t.SetEnd(pcbnew.VECTOR2I(F(c[0]), F(c[1])))
    t.SetWidth(F(0.3)); t.SetLayer(pcbnew.B_Cu); t.SetNet(b.GetNetsByName()['/SCK']); b.Add(t)
print('removed', gone, 'segments, added', len(pts) - 1)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
