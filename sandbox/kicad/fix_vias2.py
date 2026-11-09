"""Run with KiCad's python: drop the TX51 / RX51 / RELAY vias.
TX51, RX51: the short F.Cu stubs from U1 to their vias go to B.Cu (same side as the rest of the net).
RELAY: the diagonal + long horizontal (192.40,137.43)-(183.67,146.17)-(157.11,146.17) go from B.Cu to F.Cu,
so they no longer cross TX51/RX51; one via is added at (157.11,146.17) where RELAY must dive under +5V.
Written only if DRC (zones refilled) shows no new problem."""
import json, pathlib, shutil, subprocess, tempfile, pcbnew
ROOT = pathlib.Path(__file__).resolve().parents[2]
PCB = ROOT / 'hardware/pcb/env-monitor.kicad_pcb'
CLI = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
TMP = pathlib.Path(tempfile.gettempdir()) / 'fix_vias'; TMP.mkdir(exist_ok=True)
BAD = {'clearance', 'shorting_items', 'tracks_crossing', 'unconnected_items', 'copper_edge_clearance',
       'hole_clearance', 'track_dangling', 'solder_mask_bridge', 'via_dangling'}
mm, F = pcbnew.ToMM, pcbnew.FromMM


def drc(path):
    rep = TMP / 'drc.json'
    subprocess.run([CLI, 'pcb', 'drc', '--format', 'json', '--schematic-parity', '-o', str(rep), str(path)], capture_output=True)
    d = json.loads(rep.read_text(encoding='utf-8'))
    return [v['type'] + ' ' + '; '.join(i.get('description', '') for i in v.get('items', []))
            for v in d.get('violations', []) + d.get('unconnected_items', []) if v['type'] in BAD]


b = pcbnew.LoadBoard(str(PCB))
pads = list(b.GetPads())
vias = {v.GetNetname(): v for v in b.GetTracks() if v.GetClass() == 'PCB_VIA'}


def chain(via, layer, stop=None):
    tracks = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK' and t.GetNetCode() == via.GetNetCode() and t.GetLayer() == layer]
    seen, todo, out = set(), [via.GetPosition()], []
    while todo:
        p = todo.pop(); key = (p.x, p.y)
        if key in seen: continue
        seen.add(key)
        if stop and abs(mm(p.x) - stop[0]) < 0.01 and abs(mm(p.y) - stop[1]) < 0.01: continue
        if key != (via.GetPosition().x, via.GetPosition().y) and any(pd.HitTest(p) for pd in pads if pd.GetNetCode() == via.GetNetCode()):
            continue
        for t in tracks:
            for a, c in ((t.GetStart(), t.GetEnd()), (t.GetEnd(), t.GetStart())):
                if (a.x, a.y) == key and t not in out:
                    out.append(t); todo.append(c)
    return out


for net in ('/TX51', '/RX51'):
    for t in chain(vias[net], pcbnew.F_Cu): t.SetLayer(pcbnew.B_Cu)
    b.Delete(vias[net])
rv = vias['/RELAY']
moved = chain(rv, pcbnew.B_Cu, stop=(157.11, 146.17))
print('RELAY tracks to F.Cu:', [((round(mm(t.GetStart().x), 2), round(mm(t.GetStart().y), 2)),
                                (round(mm(t.GetEnd().x), 2), round(mm(t.GetEnd().y), 2))) for t in moved])
end = next(p for t in moved for p in (t.GetStart(), t.GetEnd()) if abs(mm(p.x) - 157.11) < 0.01 and abs(mm(p.y) - 146.17) < 0.01)
for t in moved: t.SetLayer(pcbnew.F_Cu)
nv = pcbnew.PCB_VIA(b); nv.SetPosition(end); nv.SetWidth(rv.GetWidth()); nv.SetDrill(rv.GetDrill())
nv.SetNet(rv.GetNet()); nv.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); b.Add(nv)
b.Delete(rv)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
cand = TMP / 'cand2.kicad_pcb'; pcbnew.SaveBoard(str(cand), b)
problems = drc(cand)
if problems:
    print('NOT applied:'); print('\n'.join(problems))
else:
    shutil.copy(PCB, TMP / 'backup2.kicad_pcb'); shutil.copy(cand, PCB); print('applied: 4 vias -> 2')
