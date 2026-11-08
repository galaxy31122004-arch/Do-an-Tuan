"""Run with KiCad's python.
  prep            : fix U1.37/38 net names, update J4 from library, Q1 -> TO-92_Inline_Wide,
                    rip up tracks touching RIP refs and prune dangling stubs.
  place REF=x,y,rot ... : move footprints (mm, deg)."""
import sys, pathlib, pcbnew
ROOT = pathlib.Path(__file__).resolve().parents[2]
PCB = str(ROOT / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB)
RIP = {'R1', 'R3', 'R8', 'R9', 'Q1', 'TP1', 'TP2', 'TP3'}

def net(name):
    n = b.GetNetsByName()
    if name in n: return n[name]
    ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni); return ni

def swap(ref, lib, fp):
    old = b.FindFootprintByReference(ref)
    new = pcbnew.FootprintLoad(lib, fp)
    new.SetPosition(old.GetPosition()); new.SetOrientation(old.GetOrientation())
    new.SetReference(ref); new.SetValue(old.GetValue()); new.SetFPID(pcbnew.LIB_ID(old.GetFPID().GetLibNickname().wx_str(), fp))
    new.SetPath(old.GetPath())
    for f in ('Footprint', 'Datasheet', 'Description'):
        pass
    nets = {p.GetNumber(): p.GetNet() for p in old.Pads()}
    b.Remove(old); b.Add(new)
    for p in new.Pads():
        if p.GetNumber() in nets: p.SetNet(nets[p.GetNumber()])
    print('swapped', ref, fp)

def prune():
    pads = list(b.GetPads())
    while True:
        tr = list(b.GetTracks()); gone = 0; dead = []
        for t in tr:
            if t.GetClass() == 'PCB_VIA': continue
            tid = t.m_Uuid.AsString()
            for pt in (t.GetStart(), t.GetEnd()):
                ok = any(p.GetNetCode() == t.GetNetCode() and p.HitTest(pt) for p in pads) or any(
                    o.m_Uuid.AsString() != tid and o.GetNetCode() == t.GetNetCode() and (
                        (o.GetClass() == 'PCB_VIA' and o.HitTest(pt)) or
                        (o.GetClass() != 'PCB_VIA' and (o.GetStart() == pt or o.GetEnd() == pt or o.HitTest(pt, 1))))
                    for o in tr)
                if not ok: dead.append(t); break
        for t in dead: b.Delete(t); gone += 1
        # vias with nothing attached
        tr = list(b.GetTracks())
        for v in [t for t in tr if t.GetClass() == 'PCB_VIA']:
            if not any(o.GetClass() != 'PCB_VIA' and o.GetNetCode() == v.GetNetCode() and (v.HitTest(o.GetStart()) or v.HitTest(o.GetEnd())) for o in tr):
                b.Delete(v); gone += 1
        if not gone: return

if sys.argv[1] == 'rip':  # rip tracks touching the pads of the given refs, then prune stubs
    refs = set(sys.argv[2:])
    rp = [p for p in b.GetPads() if p.GetParentFootprint().GetReference() in refs]
    dead = [t for t in b.GetTracks() if any(p.GetNetCode() == t.GetNetCode() and p.HitTest(pt) for p in rp
            for pt in ([t.GetPosition()] if t.GetClass() == 'PCB_VIA' else [t.GetStart(), t.GetEnd()]))]
    for t in dead: b.Delete(t)
    prune(); print('ripped', len(dead), 'tracks now', len(b.GetTracks()))
elif sys.argv[1] == 'prune':
    n0 = len(b.GetTracks()); prune(); print('pruned', n0 - len(b.GetTracks()))
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
elif sys.argv[1] == 'prep':
    u1 = b.FindFootprintByReference('U1'); pad = {p.GetNumber(): p for p in u1.Pads()}
    pad['38'].SetNet(net('unconnected-(U1-P0.1{slash}AD1-Pad38)'))
    pad['37'].SetNet(net('unconnected-(U1-P0.2{slash}AD2-Pad37)'))
    swap('J4', str(ROOT / 'hardware/pcb/env-monitor.pretty'), 'OLED_0.96_I2C_Module')
    swap('Q1', r'C:\Program Files\KiCad\10.0\share\kicad\footprints\Package_TO_SOT_THT.pretty', 'TO-92_Inline_Wide')
    rp = [p for p in b.GetPads() if p.GetParentFootprint().GetReference() in RIP]
    n = 0
    for t in list(b.GetTracks()):
        pts = [t.GetPosition()] if t.GetClass() == 'PCB_VIA' else [t.GetStart(), t.GetEnd()]
        if any(p.GetNetCode() == t.GetNetCode() and p.HitTest(pt) for p in rp for pt in pts):
            b.Delete(t); n += 1
    prune()
    print('ripped', n, 'tracks now', len(b.GetTracks()))
else:
    for a in sys.argv[2:]:
        ref, v = a.split('='); x, y, r = map(float, v.split(','))
        f = b.FindFootprintByReference(ref)
        f.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))); f.SetOrientationDegrees(r)
        print('placed', ref, x, y, r)
pcbnew.SaveBoard(PCB, b)
