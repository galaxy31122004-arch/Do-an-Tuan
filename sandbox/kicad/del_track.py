"""Run with KiCad's python: delete track segments with an end at x,y (mm) shorter than L mm. Usage: del_track.py x,y L"""
import sys, pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB); p = pcbnew.VECTOR2I(*(pcbnew.FromMM(float(v)) for v in sys.argv[1].split(',')))
L = pcbnew.FromMM(float(sys.argv[2])); tol = pcbnew.FromMM(0.01)
dead = [t for t in b.GetTracks() if t.GetClass() != 'PCB_VIA' and t.GetLength() <= L and
        any(abs(q.x - p.x) <= tol and abs(q.y - p.y) <= tol for q in (t.GetStart(), t.GetEnd()))]
for t in dead: b.Delete(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(PCB, b); print('deleted', len(dead))
