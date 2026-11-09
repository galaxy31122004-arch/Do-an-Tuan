"""Run with KiCad's python: remove vias where the net can stay on one copper layer.
For each via, the chain of tracks on one side (followed from the via until a pad) is moved to the
other layer and the via deleted. Kept only if DRC (zones refilled) shows no new problem."""
import json, pathlib, shutil, subprocess, tempfile, pcbnew
ROOT = pathlib.Path(__file__).resolve().parents[2]
PCB = ROOT / 'hardware/pcb/env-monitor.kicad_pcb'
CLI = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
TMP = pathlib.Path(tempfile.gettempdir()) / 'fix_vias'; TMP.mkdir(exist_ok=True)
BAD = {'clearance', 'shorting_items', 'tracks_crossing', 'unconnected_items', 'copper_edge_clearance',
       'hole_clearance', 'track_dangling', 'solder_mask_bridge'}


def drc(path):
    rep = TMP / 'drc.json'
    subprocess.run([CLI, 'pcb', 'drc', '--format', 'json', '--schematic-parity', '-o', str(rep), str(path)], capture_output=True)
    d = json.loads(rep.read_text(encoding='utf-8'))
    return len([v for v in d.get('violations', []) + d.get('unconnected_items', []) if v['type'] in BAD])


def chain(b, via, layer):
    """Tracks on `layer` reachable from the via without passing through a pad."""
    pads = list(b.GetPads())
    tracks = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK' and t.GetNetCode() == via.GetNetCode() and t.GetLayer() == layer]
    seen, todo, out = set(), [via.GetPosition()], []
    while todo:
        p = todo.pop(); key = (p.x, p.y)
        if key in seen: continue
        seen.add(key)
        if key != (via.GetPosition().x, via.GetPosition().y) and any(pd.HitTest(p) for pd in pads if pd.GetNetCode() == via.GetNetCode()):
            continue
        for t in tracks:
            for a, c in ((t.GetStart(), t.GetEnd()), (t.GetEnd(), t.GetStart())):
                if (a.x, a.y) == key and t not in out:
                    out.append(t); todo.append(c)
    return out


base = drc(PCB)
print('baseline problems', base)
shutil.copy(PCB, TMP / 'backup.kicad_pcb')
b0 = pcbnew.LoadBoard(str(PCB))
targets = [(v.m_Uuid.AsString(), v.GetNetname()) for v in b0.GetTracks() if v.GetClass() == 'PCB_VIA']
for uid, net in targets:
    done = False
    for frm, to in ((pcbnew.B_Cu, pcbnew.F_Cu), (pcbnew.F_Cu, pcbnew.B_Cu)):
        b = pcbnew.LoadBoard(str(PCB))
        via = next(v for v in b.GetTracks() if v.m_Uuid.AsString() == uid)
        moved = chain(b, via, frm)
        for t in moved:
            t.SetLayer(to)
        b.Delete(via)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        cand = TMP / 'cand.kicad_pcb'; pcbnew.SaveBoard(str(cand), b)
        n = drc(cand)
        side = 'B->F' if frm == pcbnew.B_Cu else 'F->B'
        if n <= base:
            shutil.copy(cand, PCB); print(f'  ok   {net:10} {side}: {len(moved)} tracks moved, via removed'); done = True; break
        print(f'  FAIL {net:10} {side}: {n - base} new problems')
    if not done:
        print(f'  KEEP {net} via (no single-layer route with the current tracks)')
