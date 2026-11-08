"""Run with KiCad's python: list tracks/vias crossing a box. Usage: tracks_in.py x1 y1 x2 y2"""
import sys, pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB); mm = pcbnew.ToMM
x1, y1, x2, y2 = map(float, sys.argv[1:5])
box = pcbnew.BOX2I(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)), pcbnew.VECTOR2L(pcbnew.FromMM(x2 - x1), pcbnew.FromMM(y2 - y1)))
for t in b.GetTracks():
    if not t.GetBoundingBox().Intersects(box): continue
    if t.GetClass() == 'PCB_VIA': print(f'via {t.GetNetname():12} ({mm(t.GetPosition().x):.2f},{mm(t.GetPosition().y):.2f})'); continue
    s, e = t.GetStart(), t.GetEnd()
    print(f'{b.GetLayerName(t.GetLayer()):5} {t.GetNetname():14} w{mm(t.GetWidth()):.2f} ({mm(s.x):.2f},{mm(s.y):.2f})-({mm(e.x):.2f},{mm(e.y):.2f})')
