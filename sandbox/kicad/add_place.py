"""Run with KiCad's python: re-add footprints deleted from the PCB (taken from the schematic)
and place each at the nearest free spot to a target point.
Usage: add_place.py REF@x,y ..."""
import re, sys, pathlib, subprocess, tempfile, os, pcbnew
ROOT = pathlib.Path(__file__).resolve().parents[2]
PCB = str(ROOT / 'hardware/pcb/env-monitor.kicad_pcb'); SCH = ROOT / 'hardware/pcb/env-monitor.kicad_sch'
SYS = r'C:\Program Files\KiCad\10.0\share\kicad\footprints'
b = pcbnew.LoadBoard(PCB); mm = pcbnew.ToMM; MM = pcbnew.FromMM

# schematic: footprint, value, uuid per ref; netlist: pin -> net
sch = SCH.read_text(encoding='utf-8')
net = os.path.join(tempfile.gettempdir(), 'ap.net')
subprocess.run([r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe', 'sch', 'export', 'netlist', '-o', net, str(SCH)], check=True, capture_output=True)
nt = open(net, encoding='utf-8').read()
pin_net = {}
for m in re.finditer(r'\(net\s+\(code "\d+"\)\s+\(name "([^"]+)"\)(.*?)(?=\n\t\t\(net\s|\n\t\)\n)', nt, re.S):
    for r, p in re.findall(r'\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', m[2]): pin_net[(r, p)] = m[1]

def sym(ref):
    i = sch.index(f'(property "Reference" "{ref}"'); s = sch.rindex('\t(symbol\n', 0, i)
    blk = sch[s:i]
    return (re.search(r'\(uuid "([^"]+)"\)', blk)[1],
            re.search(r'\(property "Value" "([^"]*)"', sch[i:i + 2000])[1],
            re.search(r'\(property "Footprint" "([^"]*)"', sch[i:i + 2000])[1])

def crt(f):
    c = f.GetCourtyard(pcbnew.F_CrtYd)
    bb = c.BBox() if c.OutlineCount() else f.GetBoundingBox(False)
    return mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())

e = b.GetBoardEdgesBoundingBox()
L, T, R, B = mm(e.GetLeft()) + 1, mm(e.GetTop()) + 1, mm(e.GetRight()) - 1, mm(e.GetBottom()) - 1
plan = [(a.split('@')[0], tuple(map(float, a.split('@')[1].split(',')))) for a in sys.argv[1:]]
have = {f.GetReference() for f in b.GetFootprints()}
obs = [crt(f) for f in b.GetFootprints() if f.GetReference() not in {r for r, _ in plan}]
for t in b.GetTracks():
    bb = t.GetBoundingBox()
    obs.append((mm(bb.GetLeft()) - .3, mm(bb.GetTop()) - .3, mm(bb.GetRight()) + .3, mm(bb.GetBottom()) + .3))
hit = lambda a: a[0] < L or a[1] < T or a[2] > R or a[3] > B or any(
    a[0] < o[2] and a[2] > o[0] and a[1] < o[3] and a[3] > o[1] for o in obs)

for ref, (tx, ty) in plan:
    assert ref not in have, f'{ref} already on board'
    uid, val, fpid = sym(ref); lib, name = fpid.split(':')
    libdir = str(ROOT / 'hardware/pcb/env-monitor.pretty') if lib == 'env-monitor' else rf'{SYS}\{lib}.pretty'
    f = pcbnew.FootprintLoad(libdir, name)
    f.SetReference(ref); f.SetValue(val); f.SetFPID(pcbnew.LIB_ID(lib, name))
    f.SetPath(pcbnew.KIID_PATH('/' + uid))
    b.Add(f)
    nets = b.GetNetsByName()
    for p in f.Pads():
        n = pin_net.get((ref, p.GetNumber()))
        if n: p.SetNet(nets[n])
    best = None
    for rot in (0, 90, 180, 270):
        f.SetOrientationDegrees(rot); f.SetPosition(pcbnew.VECTOR2I(0, 0))
        l, t_, r, bt = crt(f); y = T
        while y + (bt - t_) <= B:
            x = L
            while x + (r - l) <= R:
                if not hit((x, y, x + r - l, y + bt - t_)):
                    d = (x + (r - l) / 2 - tx) ** 2 + (y + (bt - t_) / 2 - ty) ** 2
                    if best is None or d < best[0]: best = (d, rot, x - l, y - t_)
                x += 0.25
            y += 0.25
    _, rot, ox, oy = best
    f.SetOrientationDegrees(rot); f.SetPosition(pcbnew.VECTOR2I(MM(round(ox, 2)), MM(round(oy, 2))))
    obs.append(tuple(v + s for v, s in zip(crt(f), (-.3, -.3, .3, .3))))
    print(f'{ref} {val} -> ({mm(f.GetPosition().x):.2f},{mm(f.GetPosition().y):.2f}) rot {rot}; nets',
          {p.GetNumber(): p.GetNetname() for p in f.Pads()})
pcbnew.SaveBoard(PCB, b)
