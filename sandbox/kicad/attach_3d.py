"""Attach 3D models: custom module footprints (library + PCB instances) and the AT89S52 chip on the DIP-40 socket."""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from remove_caps import blocks, ref_of  # noqa
PCBDIR = pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb'
MODELS = {'ESP32-C3_SuperMini': 'U2', 'TXS0108E_Module': 'U4', 'OLED_0.96_I2C_Module': 'J4'}

def model(path, z=0.0, ind='\t'):
    return (f'{ind}(model "{path}"\n{ind}\t(offset\n{ind}\t\t(xyz 0 0 {z})\n{ind}\t)\n{ind}\t(scale\n{ind}\t\t(xyz 1 1 1)\n{ind}\t)\n'
            f'{ind}\t(rotate\n{ind}\t\t(xyz 0 0 0)\n{ind}\t)\n{ind})\n')

def add(block, path, ind, z=0.0):
    if f'(model "{path}"' in block: return block
    i = block.rstrip().rfind(')')  # closing paren of the footprint
    return block[:i] + model(path, z, ind) + block[i:]

for name in MODELS:
    f = PCBDIR / 'env-monitor.pretty' / f'{name}.kicad_mod'
    t = f.read_text(encoding='utf-8')
    f.write_text(add(t, f'${{KIPRJMOD}}/env-monitor.3dshapes/{name}.wrl', '\t'), encoding='utf-8')

pcb = PCBDIR / 'env-monitor.kicad_pcb'; t = pcb.read_text(encoding='utf-8')
want = {ref: (f'${{KIPRJMOD}}/env-monitor.3dshapes/{n}.wrl', 0.0) for n, ref in MODELS.items()}
want['U1'] = ('${KICAD10_3DMODEL_DIR}/Package_DIP.3dshapes/DIP-40_W15.24mm.step', 3.0)  # chip seated in the socket
for s, e in reversed(list(blocks(t, 'footprint "', '\t'))):
    r = ref_of(t[s:e])
    if r in want:
        t = t[:s] + add(t[s:e], want[r][0], '\t\t', want[r][1]) + t[e:]; print('model ->', r)
pcb.write_text(t, encoding='utf-8')
