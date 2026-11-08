"""Run with KiCad's python: delete the via at x,y (mm) and refill zones. Usage: del_via.py x,y ..."""
import sys, pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB)
for a in sys.argv[1:]:
    p = pcbnew.VECTOR2I(*(pcbnew.FromMM(float(v)) for v in a.split(',')))
    vs = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA' and t.HitTest(p)]
    for v in vs: b.Delete(v)
    print(a, 'deleted', len(vs))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
