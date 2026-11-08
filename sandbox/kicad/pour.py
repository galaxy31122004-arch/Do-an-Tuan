"""Run with KiCad's python: ensure copper pours (GND on B.Cu, +5V on F.Cu) over the board outline, then fill."""
import pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB)
for netname, layer in (('GND', pcbnew.B_Cu), ('+5V', pcbnew.F_Cu)):
    if any(z.GetNetname() == netname and z.GetLayer() == layer for z in b.Zones()): continue
    bb = b.GetBoardEdgesBoundingBox()
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.GetNetsByName()[netname])
    o = z.Outline(); o.NewOutline()
    for x, y in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()), (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())):
        o.Append(x, y)
    z.SetLocalClearance(pcbnew.FromMM(0.3)); z.SetMinThickness(pcbnew.FromMM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(pcbnew.FromMM(0.5)); z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.5))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z); print('added', netname, b.GetLayerName(layer))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
