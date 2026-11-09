"""Run with KiCad's python: flip R3 so BTN_PAGE is the lower pad and drop the BTN_PAGE via.
R3 straddles the +5V F.Cu rail (y 127.37): pad 1 (+5V) at (183.54,121.50) drops straight onto the rail,
pad 2 (BTN_PAGE) at (183.54,129.12) joins the existing F.Cu BTN_PAGE run at y 130.16.
The B.Cu BTN_PAGE tracks, the via and the old +5V branch to R3 are removed. Written only if DRC is clean."""
import json, pathlib, shutil, subprocess, tempfile, pcbnew
ROOT = pathlib.Path(__file__).resolve().parents[2]
PCB = ROOT / 'hardware/pcb/env-monitor.kicad_pcb'
CLI = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
TMP = pathlib.Path(tempfile.gettempdir()) / 'flip_r3'; TMP.mkdir(exist_ok=True)
BAD = {'clearance', 'shorting_items', 'tracks_crossing', 'unconnected_items', 'copper_edge_clearance',
       'hole_clearance', 'track_dangling', 'solder_mask_bridge', 'via_dangling', 'courtyards_overlap'}
mm, F = pcbnew.ToMM, pcbnew.FromMM
b = pcbnew.LoadBoard(str(PCB))


def at(p, x, y):
    return abs(mm(p.x) - x) < 0.02 and abs(mm(p.y) - y) < 0.02


def track(net, layer, w, *pts):
    for a, c in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(F(a[0]), F(a[1]))); t.SetEnd(pcbnew.VECTOR2I(F(c[0]), F(c[1])))
        t.SetWidth(F(w)); t.SetLayer(layer); t.SetNet(b.GetNetsByName()[net]); b.Add(t)


for t in list(b.GetTracks()):
    n = t.GetNetname()
    if t.GetClass() == 'PCB_VIA' and n == '/BTN_PAGE':
        b.Delete(t)
    elif t.GetClass() == 'PCB_TRACK' and n == '/BTN_PAGE' and t.GetLayer() == pcbnew.B_Cu \
            and any(at(p, 183.54, 118.50) or at(p, 186.08, 121.04) or at(p, 186.08, 125.0) for p in (t.GetStart(), t.GetEnd())):
        b.Delete(t)
    elif t.GetClass() == 'PCB_TRACK' and n == '+5V' and any(at(p, 179.48, 126.12) for p in (t.GetStart(), t.GetEnd())):
        b.Delete(t)
    elif t.GetClass() == 'PCB_TRACK' and n == '/BTN_PAGE' and at(t.GetStart(), 195.55, 130.16) and at(t.GetEnd(), 186.08, 130.16):
        t.SetEnd(pcbnew.VECTOR2I(F(184.58), F(130.16)))
r3 = b.FindFootprintByReference('R3')
r3.SetOrientationDegrees(270)
r3.SetPosition(pcbnew.VECTOR2I(F(183.54), F(121.50)))
print({p.GetNumber(): (p.GetNetname(), round(mm(p.GetPosition().x), 2), round(mm(p.GetPosition().y), 2)) for p in r3.Pads()})
track('+5V', pcbnew.F_Cu, 0.5, (183.54, 121.50), (183.54, 127.37))
track('/BTN_PAGE', pcbnew.F_Cu, 0.5, (183.54, 129.12), (184.58, 130.16))
r = r3.Reference(); r.SetTextAngleDegrees(90); r.SetPosition(pcbnew.VECTOR2I(F(186.0), F(125.3)))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
cand = TMP / 'cand.kicad_pcb'; pcbnew.SaveBoard(str(cand), b)
rep = TMP / 'drc.json'
subprocess.run([CLI, 'pcb', 'drc', '--format', 'json', '--schematic-parity', '-o', str(rep), str(cand)], capture_output=True)
d = json.loads(rep.read_text(encoding='utf-8'))
bad = [v['type'] + ' ' + '; '.join(i.get('description', '') for i in v.get('items', []))
       for v in d.get('violations', []) + d.get('unconnected_items', []) if v['type'] in BAD and 'R8' not in str(v) and 'R9' not in str(v)]
if bad:
    print('NOT applied:'); print('\n'.join(bad))
else:
    shutil.copy(PCB, TMP / 'backup.kicad_pcb'); shutil.copy(cand, PCB); print('applied: BTN_PAGE via removed')
