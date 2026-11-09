"""Run with KiCad's python: clear the last silkscreen warnings (J4 outline is grown in the library/PCB text).
D3 'K' text hidden, J6 reference below the block."""
import pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB); F = pcbnew.FromMM
for it in b.FindFootprintByReference('D3').GraphicalItems():
    if it.GetClass() == 'PCB_TEXT' and it.GetText() == 'K':
        it.SetVisible(False); print('D3 K hidden')
r = b.FindFootprintByReference('J6').Reference()
r.SetTextAngleDegrees(0); r.SetPosition(pcbnew.VECTOR2I(F(128.6), F(163.6))); print('J6 ref moved')
pcbnew.SaveBoard(PCB, b)
