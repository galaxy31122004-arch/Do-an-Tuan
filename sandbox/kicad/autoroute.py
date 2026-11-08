"""Run with KiCad's python.
  export <dsn>: apply I2C pin move (U1.35/36), lock existing tracks/vias, export Specctra DSN.
  import <ses>: import routed session, unlock tracks, save board."""
import sys, pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
mode, path = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(PCB)
if mode == 'export':
    u1 = b.FindFootprintByReference('U1')
    nets = b.GetNetsByName()
    pad = {p.GetNumber(): p for p in u1.Pads()}
    sda, scl = pad['38'].GetNet(), pad['37'].GetNet()
    if sda.GetNetname().endswith('SDA5'):
        pad['36'].SetNet(sda); pad['35'].SetNet(scl)
        for n in ('38', '37'):
            nc = pcbnew.NETINFO_ITEM(b, f'unconnected-(U1-P0.{39 - int(n)}{{slash}}AD{39 - int(n)}-Pad{n})')
            b.Add(nc); pad[n].SetNet(nc)
        print('I2C moved to U1.36/35')
    n = 0
    for t in b.GetTracks():
        t.SetLocked(True); n += 1
    print('locked', n)
    assert pcbnew.ExportSpecctraDSN(b, path)
else:
    assert pcbnew.ImportSpecctraSES(b, path)
    for t in b.GetTracks(): t.SetLocked(False)
    pcbnew.SaveBoard(PCB, b)
    print('tracks', len(b.GetTracks()))
