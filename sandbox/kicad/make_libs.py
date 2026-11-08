"""Write the project symbol and footprint libraries for the two plug-in modules.

ESP32-C3 SuperMini pin numbers follow documents/sources/esp32-c3-supermini/pinout.png
(USB up, component side): right row 1-8 = 5V GND 3V3 GPIO4 GPIO3 GPIO2 GPIO1 GPIO0,
left row 9-16 = GPIO5 GPIO6 GPIO7 GPIO8 GPIO9 GPIO10 GPIO20 GPIO21.
TXS0108E module: row A 1-10 = VA A1..A8 OE, row B 11-20 = VB B1..B8 GND.
Row spacings are NOT measured yet (ROW_ESP, ROW_TXS): verify on the bought boards.
"""
import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / 'hardware' / 'pcb'
ROW_ESP = 15.24   # mm between the two ESP32 header rows (to verify)
ROW_TXS = 12.70   # mm between the two TXS module header rows (to verify)


def uid():
    return str(uuid.uuid4())


FONT = '(effects (font (size 1.27 1.27)))'
HIDE = '(effects (font (size 1.27 1.27)) (hide yes))'


def pin(kind, x, y, ang, name, num):
    return (f'\t\t\t(pin {kind} line (at {x} {y} {ang}) (length 2.54)\n'
            f'\t\t\t\t(name "{name}" {FONT}) (number "{num}" {FONT}))\n')


def symbol(name, ref, fp, desc, rect, pins):
    body = ''.join(pin(*p) for p in pins)
    x1, y1, x2, y2 = rect
    return f'''\t(symbol "{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
\t\t(property "Reference" "{ref}" (at 0 {y1 + 5.08} 0) {FONT})
\t\t(property "Value" "{name}" (at 0 {y2 - 5.08} 0) {FONT})
\t\t(property "Footprint" "env-monitor:{fp}" (at 0 0 0) {HIDE})
\t\t(property "Datasheet" "" (at 0 0 0) {HIDE})
\t\t(property "Description" "{desc}" (at 0 0 0) {HIDE})
\t\t(symbol "{name}_0_1"
\t\t\t(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.254) (type default)) (fill (type background))))
\t\t(symbol "{name}_1_1"
{body}\t\t)
\t)
'''


esp_right = [('GPIO4', 4), ('GPIO5', 9), ('GPIO6', 10), ('GPIO0', 8), ('GPIO1', 7), ('GPIO2', 6), ('GPIO3', 5),
             ('GPIO7', 11), ('GPIO8', 12), ('GPIO9', 13), ('GPIO10', 14), ('GPIO20', 15), ('GPIO21', 16)]
esp_pins = [('power_in', -2.54, 20.32, 270, '5V', 1), ('power_out', 2.54, 20.32, 270, '3V3', 3),
            ('power_in', 0, -20.32, 90, 'GND', 2)]
esp_pins += [('bidirectional', 10.16, round(15.24 - 2.54 * i, 2), 180, n, k) for i, (n, k) in enumerate(esp_right)]

txs_pins = [('power_in', -7.62, 12.7, 0, 'VA', 1), ('input', -7.62, -10.16, 0, 'OE', 10),
            ('power_in', 7.62, 12.7, 180, 'VB', 11), ('power_in', 7.62, -10.16, 180, 'GND', 20)]
for i in range(8):
    y = round(10.16 - 2.54 * i, 2)
    txs_pins += [('bidirectional', -7.62, y, 0, f'A{i + 1}', i + 2), ('bidirectional', 7.62, y, 180, f'B{i + 1}', i + 12)]

(OUT / 'env-monitor.kicad_sym').write_text(
    '(kicad_symbol_lib (version 20241209) (generator "claude") (generator_version "1.0")\n'
    + symbol('ESP32-C3_SuperMini', 'U', 'ESP32-C3_SuperMini',
             'ESP32-C3 SuperMini plug-in board, 2x8 pins', (-7.62, 17.78, 7.62, -17.78), esp_pins)
    + symbol('TXS0108E_Module', 'U', 'TXS0108E_Module',
             'TXS0108E 8-bit level shifter module, 2x10 pins', (-5.08, 15.24, 5.08, -12.7), txs_pins)
    + ')\n', encoding='utf-8')


def footprint(name, desc, rows, width, height):
    pads = ''
    for x, nums in rows:
        n = len(nums)
        for i, num in enumerate(nums):
            y = round((i - (n - 1) / 2) * 2.54, 3)
            shape = 'rect' if num == 1 else 'circle'
            pads += (f'\t(pad "{num}" thru_hole {shape} (at {x} {y}) (size 1.7 1.7) (drill 1)'
                     f' (layers "*.Cu" "*.Mask") (uuid "{uid()}"))\n')
    w, h = width / 2, height / 2
    return f'''(footprint "{name}" (version 20240108) (generator "claude") (layer "F.Cu")
\t(descr "{desc}")
\t(attr through_hole)
\t(property "Reference" "REF**" (at 0 {-h - 1.5} 0) (layer "F.SilkS") (uuid "{uid()}")
\t\t(effects (font (size 1 1) (thickness 0.15))))
\t(property "Value" "{name}" (at 0 {h + 1.5} 0) (layer "F.Fab") (uuid "{uid()}")
\t\t(effects (font (size 1 1) (thickness 0.15))))
\t(fp_rect (start {-w} {-h}) (end {w} {h}) (stroke (width 0.12) (type solid)) (fill no) (layer "F.SilkS") (uuid "{uid()}"))
\t(fp_rect (start {-w - 0.5} {-h - 0.5}) (end {w + 0.5} {h + 0.5}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "{uid()}"))
\t(fp_rect (start {-w} {-h}) (end {w} {h}) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab") (uuid "{uid()}"))
{pads})
'''


pretty = OUT / 'env-monitor.pretty'
pretty.mkdir(exist_ok=True)
(pretty / 'ESP32-C3_SuperMini.kicad_mod').write_text(footprint(
    'ESP32-C3_SuperMini', f'ESP32-C3 SuperMini on 2x8 female headers, row spacing {ROW_ESP} mm (verify), USB edge at top',
    [(ROW_ESP / 2, list(range(1, 9))), (-ROW_ESP / 2, list(range(9, 17)))], 18.0, 22.52), encoding='utf-8')
(pretty / 'TXS0108E_Module.kicad_mod').write_text(footprint(
    'TXS0108E_Module', f'TXS0108E module on 2x10 female headers, row spacing {ROW_TXS} mm (verify)',
    [(-ROW_TXS / 2, list(range(1, 11))), (ROW_TXS / 2, list(range(11, 21)))], ROW_TXS + 3.0, 27.0), encoding='utf-8')

(OUT / 'sym-lib-table').write_text(
    '(sym_lib_table\n\t(version 7)\n\t(lib (name "env-monitor") (type "KiCad") (uri "${KIPRJMOD}/env-monitor.kicad_sym") (options "") (descr "Project modules"))\n)\n',
    encoding='utf-8')
(OUT / 'fp-lib-table').write_text(
    '(fp_lib_table\n\t(version 7)\n\t(lib (name "env-monitor") (type "KiCad") (uri "${KIPRJMOD}/env-monitor.pretty") (options "") (descr "Project modules"))\n)\n',
    encoding='utf-8')
print('libraries written to', OUT)
