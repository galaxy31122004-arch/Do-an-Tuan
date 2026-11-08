"""Set the Footprint property of schematic symbols: set_sch_fp.py REF=lib:fp ..."""
import re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from remove_caps import blocks, ref_of  # noqa
SCH = pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_sch'
t = SCH.read_text(encoding='utf-8')
want = dict(a.split('=', 1) for a in sys.argv[1:])
for s, e in reversed(list(blocks(t, 'symbol\n\t\t(lib_id', '\t'))):
    r = ref_of(t[s:e])
    if r in want:
        blk = re.sub(r'\(property "Footprint" "[^"]*"', f'(property "Footprint" "{want.pop(r)}"', t[s:e], count=1)
        t = t[:s] + blk + t[e:]; print('set', r)
assert not want, want
SCH.write_text(t, encoding='utf-8')
