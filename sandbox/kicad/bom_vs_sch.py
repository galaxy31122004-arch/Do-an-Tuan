"""Compare references in hardware/generate.py (BOM source) with the KiCad schematic."""
import re, pathlib
R = pathlib.Path(__file__).resolve().parents[2]
src = (R / 'hardware/generate.py').read_text(encoding='utf-8')
bom = {r.strip() for m in re.finditer(r"^\('([^']+)',\s*\d+", src, re.M) for r in m[1].split(',')}
sch = set(re.findall(r'\(property "Reference" "([A-Z]+\d+)"', (R / 'hardware/pcb/env-monitor.kicad_sch').read_text(encoding='utf-8')))
print('in BOM not in schematic:', sorted(bom - sch))
print('in schematic not in BOM:', sorted(sch - bom))
