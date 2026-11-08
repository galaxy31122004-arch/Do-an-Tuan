"""Run with KiCad's python: add a polyline track. Usage: add_track.py NET LAYER WIDTH x1,y1 x2,y2 ...  (mm)"""
import sys, pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB)
net = b.GetNetsByName()[sys.argv[1]]; layer = b.GetLayerID(sys.argv[2]); w = pcbnew.FromMM(float(sys.argv[3]))
pts = [pcbnew.VECTOR2I(pcbnew.FromMM(float(x)), pcbnew.FromMM(float(y))) for x, y in (a.split(',') for a in sys.argv[4:])]
for a, e in zip(pts, pts[1:]):
    t = pcbnew.PCB_TRACK(b); t.SetStart(a); t.SetEnd(e); t.SetWidth(w); t.SetLayer(layer); t.SetNet(net); b.Add(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
print('added', len(pts) - 1, 'segments')
