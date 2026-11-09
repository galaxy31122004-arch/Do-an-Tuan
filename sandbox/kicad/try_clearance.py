"""Count DRC clearance problems if the Default/Power netclass clearances were raised. Usage: try_clearance.py DEF POWER"""
import json, shutil, subprocess, sys, tempfile, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb'
CLI = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
d, pw = float(sys.argv[1]), float(sys.argv[2])
T = pathlib.Path(tempfile.gettempdir()) / f'clr_{d}_{pw}'; T.mkdir(exist_ok=True)
for f in ('env-monitor.kicad_pcb', 'env-monitor.kicad_sch', 'env-monitor.kicad_sym'):
    shutil.copy(ROOT / f, T / f)
shutil.copytree(ROOT / 'env-monitor.pretty', T / 'env-monitor.pretty', dirs_exist_ok=True)
for f in ('fp-lib-table', 'sym-lib-table'):
    if (ROOT / f).exists(): shutil.copy(ROOT / f, T / f)
pro = json.loads((ROOT / 'env-monitor.kicad_pro').read_text(encoding='utf-8'))
for c in pro['net_settings']['classes']:
    if c['name'] == 'Default': c['clearance'] = d
    if c['name'] == 'Power': c['clearance'] = pw
(T / 'env-monitor.kicad_pro').write_text(json.dumps(pro, indent=2), encoding='utf-8')
subprocess.run([CLI, 'pcb', 'drc', '--refill-zones', '--format', 'json', '-o', str(T / 'drc.json'), str(T / 'env-monitor.kicad_pcb')], capture_output=True)
v = json.loads((T / 'drc.json').read_text(encoding='utf-8'))['violations']
c = collections.Counter(x['type'] for x in v)
print(d, pw, dict(c))
if '-v' in sys.argv:
    for x in v:
        if x['type'] == 'clearance':
            print('  ', x['description'][-40:], '|', ' / '.join(i['description'][:60] + f" @({i['pos']['x']:.2f},{i['pos']['y']:.2f})" for i in x['items']))
