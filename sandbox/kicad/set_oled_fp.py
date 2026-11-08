"""Swap J4 to env-monitor:OLED_0.96_I2C_Module in schematic and PCB (pads keep position and nets)."""
import re, pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'hardware' / 'pcb'
OLD = 'Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical'
NEW = 'env-monitor:OLED_0.96_I2C_Module'

sch = (P / 'env-monitor.kicad_sch').read_text(encoding='utf-8')
i = sch.index('(property "Reference" "J4"')
j = sch.index(OLD, i)
sch = sch[:j] + NEW + sch[j + len(OLD):]
(P / 'env-monitor.kicad_sch').write_text(sch, encoding='utf-8')

pcb = (P / 'env-monitor.kicad_pcb').read_text(encoding='utf-8')
k = pcb.index('(property "Reference" "J4"')
s = pcb.rindex('(footprint "' + OLD + '"', 0, k)
pcb = pcb[:s] + '(footprint "' + NEW + '"' + pcb[s + len('(footprint "' + OLD + '"'):]
# block end: matching paren
d, e, q = 0, s, False
while True:
    c = pcb[e]
    if c == '"': q = not q
    elif q: pass
    elif c == '(': d += 1
    elif c == ')':
        d -= 1
        if d == 0: break
    e += 1
block = pcb[s:e]
# drop old silk/courtyard/fab graphics, keep properties and pads
block = re.sub(r'\n\t\t\((fp_line|fp_rect|fp_text|fp_arc|fp_poly)\b.*?\n\t\t\)', '', block, flags=re.S)
lib = (P / 'env-monitor.pretty' / 'OLED_0.96_I2C_Module.kicad_mod').read_text(encoding='utf-8')
gfx = [l.strip() for l in lib.splitlines() if l.strip().startswith(('(fp_rect', '(pad ""'))]
txt = re.findall(r'\(fp_text user.*?\n\t\t\(effects.*?\)\)\)\)', lib, flags=re.S)
add = ''.join('\n\t\t' + g for g in gfx + [t.replace('\n\t\t', ' ') for t in txt])
block = block.replace('Through hole straight socket strip, 1x04, 2.54mm pitch, single row (from Kicad 4.0.7), script generated',
                      'OLED 0.96in I2C module outline 27.3 x 27.8 mm')
pcb = pcb[:s] + block + add + '\n\t' + pcb[e:]
(P / 'env-monitor.kicad_pcb').write_text(pcb, encoding='utf-8')
print('J4 ->', NEW)


