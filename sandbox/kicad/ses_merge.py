"""Run with KiCad's python: merge a Freerouting .ses into the PCB WITHOUT touching existing tracks.
Also moves the I2C pad nets U1.38/37 -> U1.36/35 (schematic change not yet pulled in with F8).
Usage: ses_merge.py <session.ses>"""
import re, sys, pathlib, pcbnew
PCB = str(pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_pcb')
b = pcbnew.LoadBoard(PCB)

# --- I2C pad move ---
u1 = b.FindFootprintByReference('U1'); pad = {p.GetNumber(): p for p in u1.Pads()}
if pad['38'].GetNetname().endswith('SDA5'):
    sda, scl = pad['38'].GetNet(), pad['37'].GetNet()
    for n, net in (('38', None), ('37', None)):
        nc = pcbnew.NETINFO_ITEM(b, 'unconnected-(U1-Pad%s)' % n); b.Add(nc); pad[n].SetNet(nc)
    pad['36'].SetNet(sda); pad['35'].SetNet(scl)
    print('I2C pads moved')

# --- parse session ---
s = open(sys.argv[1], encoding='utf-8').read()
res = float(re.search(r'\(resolution um (\d+)\)', s)[1])
mm = lambda v: pcbnew.FromMM(float(v) / res / 1000)
P = lambda x, y: pcbnew.VECTOR2I(mm(x), -mm(y))
nets = b.GetNetsByName(); layers = {b.GetLayerName(i): i for i in range(pcbnew.PCB_LAYER_ID_COUNT)}
old = set()
for t in b.GetTracks():
    a, e = t.GetStart(), t.GetEnd(); k = lambda p: (round(p.x / 5000), round(p.y / 5000))
    old.add(frozenset((k(a), k(e)))) if t.GetClass() != 'PCB_VIA' else old.add(('v', k(a)))
key = lambda p: (round(p.x / 5000), round(p.y / 5000))
added = skipped = 0
out = s[s.index('(network_out'):]
for nm, body in re.findall(r'\(net "((?:[^"\\]|\\.)*)"(.*?)\n      \)', out, re.S):
    net = nets[nm] if nm in nets else None
    if net is None: print('unknown net', nm); continue
    for layer, w, pts in re.findall(r'\(path (\S+) (\d+)\s+([-\d\s]+)\)', body):
        v = list(map(int, pts.split())); pts = [P(v[i], v[i + 1]) for i in range(0, len(v), 2)]
        for a, e in zip(pts, pts[1:]):
            if a == e or frozenset((key(a), key(e))) in old: skipped += 1; continue
            t = pcbnew.PCB_TRACK(b); t.SetStart(a); t.SetEnd(e); t.SetWidth(mm(w))
            t.SetLayer(layers[layer]); t.SetNet(net); b.Add(t); added += 1
    for x, y in re.findall(r'\(via "[^"]+" (-?\d+) (-?\d+)', body):
        p = P(x, y)
        if ('v', key(p)) in old: skipped += 1; continue
        v = pcbnew.PCB_VIA(b); v.SetPosition(p); v.SetWidth(pcbnew.FromMM(0.6)); v.SetDrill(pcbnew.FromMM(0.3))
        v.SetNet(net); b.Add(v); added += 1
pcbnew.SaveBoard(PCB, b)
print('added', added, 'skipped (existing)', skipped, 'total', len(b.GetTracks()))
