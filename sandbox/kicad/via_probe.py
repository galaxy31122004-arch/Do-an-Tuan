"""Debug: move one via's chain to the other layer in a temp copy and print the DRC problems. Usage: via_probe.py NET B|F"""
import sys, subprocess, pathlib, tempfile, pcbnew
sys.argv += []
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import importlib.util
spec = importlib.util.spec_from_file_location('fv', pathlib.Path(__file__).parent / 'fix_vias.py')
src = (pathlib.Path(__file__).parent / 'fix_vias.py').read_text(encoding='utf-8').split('base = drc(PCB)')[0]
ns = {'__file__': str(pathlib.Path(__file__).parent / 'fix_vias.py')}; exec(src, ns)
net, side = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(str(ns['PCB']))
via = next(v for v in b.GetTracks() if v.GetClass() == 'PCB_VIA' and v.GetNetname() == net)
frm, to = (pcbnew.B_Cu, pcbnew.F_Cu) if side == 'B' else (pcbnew.F_Cu, pcbnew.B_Cu)
for t in ns['chain'](b, via, frm): t.SetLayer(to)
b.Delete(via); pcbnew.ZONE_FILLER(b).Fill(b.Zones())
out = pathlib.Path(tempfile.gettempdir()) / 'probe.kicad_pcb'; pcbnew.SaveBoard(str(out), b)
rep = out.with_suffix('.rpt')
subprocess.run([ns['CLI'], 'pcb', 'drc', '-o', str(rep), str(out)], capture_output=True)
t = rep.read_text(encoding='utf-8')
for blk in t.split('\n['):
    if blk.split(']')[0] in ns['BAD']: print('[' + blk.strip()[:400])
