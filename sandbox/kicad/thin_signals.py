"""Run with KiCad's python: set every Default-netclass (signal) track to W mm (default 0.3). Power classes untouched."""
import pathlib, sys, collections, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
W = float(sys.argv[1]) if len(sys.argv) > 1 else 0.3

b = pcbnew.LoadBoard(PCB); n = collections.Counter()
for t in b.GetTracks():
    if t.GetClass() == 'PCB_TRACK' and t.GetNetClassName() == 'Default' and abs(pcbnew.ToMM(t.GetWidth()) - W) > 1e-3:
        n[round(pcbnew.ToMM(t.GetWidth()), 2)] += 1; t.SetWidth(pcbnew.FromMM(W))
print('re-width', dict(n), '->', W)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
