"""Compare kicad-cli netlist with the intended NETS in wire_schematic.py."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from wire_schematic import NETS  # noqa: E402

CLI = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
sch = sys.argv[1]
out = Path(tempfile.gettempdir()) / 'env-check.net'
subprocess.run([CLI, 'sch', 'export', 'netlist', '--format', 'kicadsexpr', '-o', str(out), sch],
               check=True, capture_output=True)
text = out.read_text(encoding='utf-8')
actual = {}
for block in text.split('(net')[1:]:
    name = re.search(r'\(name "([^"]+)"\)', block)
    nodes = re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"', block)
    if not name or not nodes:
        continue
    pins = frozenset(f'{a}.{b}' for a, b in nodes if not a.startswith('#PWR'))
    if len(pins) > 1 or not name.group(1).startswith('unconnected'):
        actual[name.group(1).lstrip('/')] = pins
want = {n: frozenset(x for x in p.split() if not x.startswith('#')) for n, p in NETS.items()}  # PWR_FLAGs are not in netlists
ok = True
for n, pins in want.items():
    match = [a for a, ap in actual.items() if ap == pins]
    if not match:
        ok = False
        best = max(actual.items(), key=lambda kv: len(kv[1] & pins))
        print(f'MISMATCH {n}: want {sorted(pins)}\n   closest {best[0]}: {sorted(best[1])}')
extra = [a for a, ap in actual.items() if ap not in want.values() and len(ap) > 1]
for a in extra:
    ok = False
    print(f'EXTRA net {a}: {sorted(actual[a])}')
print('NETLIST MATCH' if ok else 'NETLIST DIFFERS')
sys.exit(0 if ok else 1)
