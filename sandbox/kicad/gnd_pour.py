"""Run with KiCad's python: add a GND copper pour on B.Cu over the Edge.Cuts outline and fill zones."""
import pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB)
if not any(z.GetNetname() == 'GND' and z.GetLayer() == pcbnew.B_Cu for z in b.Zones()):
    bb = b.GetBoardEdgesBoundingBox()
    z = pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); z.SetNet(b.GetNetsByName()['GND'])
    o = z.Outline(); o.NewOutline()
    for x, y in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()), (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())):
        o.Append(x, y)
    z.SetLocalClearance(pcbnew.FromMM(0.3)); z.SetMinThickness(pcbnew.FromMM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(pcbnew.FromMM(0.5)); z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.5))
    b.Add(z)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
print('zones', len(b.Zones()))
