"""Run with KiCad's python: lay R1 and R3 flat (axial P7.62 horizontal) keeping pad 1 where it is.
R1: pad 2 (GND) to the left, GND reaches it through the pour.
R3: pad 2 (BTN_PAGE) upward; old BTN_PAGE track start is re-joined with a 45-degree track on B.Cu."""
import pathlib, pcbnew
ROOT = pathlib.Path(__file__).resolve().parents[2]
PCB = str(ROOT / 'hardware/pcb/env-monitor.kicad_pcb')
LIB = r'C:\Program Files\KiCad\10.0\share\kicad\footprints\Resistor_THT.pretty'
FP = 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal'
F = pcbnew.FromMM
b = pcbnew.LoadBoard(PCB)


def swap(ref, angle):
    old = b.FindFootprintByReference(ref)
    p1 = next(p for p in old.Pads() if p.GetNumber() == '1').GetPosition()
    nets = {p.GetNumber(): p.GetNet() for p in old.Pads()}
    new = pcbnew.FootprintLoad(LIB, FP)
    new.SetFPID(pcbnew.LIB_ID('Resistor_THT', FP))
    new.SetReference(ref); new.SetValue(old.GetValue()); new.SetPath(old.GetPath())
    new.SetOrientationDegrees(angle)
    new.SetPosition(p1)                      # footprint origin = pad 1
    for p in new.Pads():
        p.SetNet(nets[p.GetNumber()])
    b.Delete(old); b.Add(new)
    new.Reference().SetTextAngleDegrees(0); new.Value().SetVisible(False)
    return new


def track(net, layer, *pts, w=0.5):
    for a, c in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(F(a[0]), F(a[1]))); t.SetEnd(pcbnew.VECTOR2I(F(c[0]), F(c[1])))
        t.SetWidth(F(w)); t.SetLayer(layer); t.SetNet(b.GetNetsByName()[net]); b.Add(t)


r1 = swap('R1', 0)       # pad2 (GND) at x + 7.62, reaches GND through the pour
# R3 moves 1.12 mm down so pad 2 clears the SDA3 track; pad 1 (+5V) re-joined from U4.11
for t in list(b.GetTracks()):
    if t.GetClass() == 'PCB_TRACK' and t.GetNetname() == '+5V':
        ends = {(round(pcbnew.ToMM(q.x), 2), round(pcbnew.ToMM(q.y), 2)) for q in (t.GetStart(), t.GetEnd())}
        if ends in ({(183.54, 125.0), (180.6, 125.0)}, {(180.6, 125.0), (178.4, 127.2)}):
            b.Delete(t)
r3 = swap('R3', 90)
r3.SetPosition(pcbnew.VECTOR2I(F(183.54), F(126.12)))      # pad1 (183.54,126.12), pad2 (183.54,118.50)
track('+5V', pcbnew.F_Cu, (178.40, 127.20), (179.48, 126.12), (183.54, 126.12))
track('/BTN_PAGE', pcbnew.B_Cu, (183.54, 118.50), (186.08, 121.04), (186.08, 125.0))
for r in (r1, r3):
    print(r.GetReference(), [(p.GetNumber(), p.GetNetname(), round(pcbnew.ToMM(p.GetPosition().x), 2),
                              round(pcbnew.ToMM(p.GetPosition().y), 2)) for p in r.Pads()])
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
