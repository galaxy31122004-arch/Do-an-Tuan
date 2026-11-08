"""Run with KiCad's python: rotate footprints 180 deg about the centre of their pads. Usage: flip_fp.py REF ..."""
import sys, pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB); mm = pcbnew.ToMM
for ref in sys.argv[1:]:
    f = b.FindFootprintByReference(ref); ps = [p.GetPosition() for p in f.Pads()]
    c = pcbnew.VECTOR2I(sum(p.x for p in ps) // len(ps), sum(p.y for p in ps) // len(ps))
    f.Rotate(c, pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))
    print(ref, 'rot', f.GetOrientationDegrees(), {p.GetNumber(): (round(mm(p.GetPosition().x), 2), round(mm(p.GetPosition().y), 2)) for p in f.Pads()})
pcbnew.SaveBoard(PCB, b)
