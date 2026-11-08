"""Rebuild env-monitor.kicad_sch with real wires instead of global labels.

Signals: each net gets a vertical trunk; every pin reaches it with a short
orthogonal stub. Power rails use KiCad power symbols placed on the pin.
Unused pins get no-connect flags. The script refuses to write if any wire
touches a pin or wire of another net.

Usage: python wire_schematic.py <schematic> [--write]
"""
import math
import sys
import uuid
from pathlib import Path

from sexpr import Sym, dump, find, first, parse

G = 2.54
POWER = {'+5V', '+3V3', 'GND'}
POWER_LIB = Path(r'C:\Program Files\KiCad\10.0\share\kicad\symbols\power.kicad_sym')

# ---------------------------------------------------------------- placement
# ref: (x_g, y_g, rotation, mirror_y)   positions in 2.54 mm grid units
PLACE = {
    # left column (AT89S52 side), each part in its own horizontal band
    'J3': (34, 22, 0, True), 'J5B': (34, 33, 0, True), 'U5': (34, 44, 0, False),
    'R2': (34, 52, 0, False), 'Y1': (34, 60, 90, False), 'C9': (34, 67, 0, False),
    'C10': (34, 74, 0, False), 'C2': (34, 81, 0, False), 'R1': (34, 88, 0, False),
    'SW2': (34, 94, 0, False), 'R3': (34, 100, 0, False), 'SW1': (34, 107, 0, True),
    'U1': (82, 60, 0, False), 'J6': (100, 62, 0, False),
    # 3V3 side
    'J4': (120, 30, 0, True), 'J2A': (120, 46, 0, True), 'J2B': (120, 60, 0, True),
    'R4': (126, 70, 0, False), 'J5A': (150, 40, 0, False),
    # power row
    # DC jack -> D2 (reverse polarity) -> LM7805 lying flat, tab screwed to GND copper
    'J1X': (4, 10, 0, False), 'D2X': (11, 9, 0, True), 'C14': (15, 12.5, 0, False),
    'C15': (17, 12.5, 0, False), 'U7': (21, 9, 0, False), 'C16': (26, 12.5, 0, False),
    'R10': (30, 11.5, 0, False), 'D1': (34, 15, 0, True),
    # decoupling caps sit next to the part they serve, wired to its supply pin
    'C1': (92, 45.5, 0, False), 'C11': (96, 45.5, 0, False),          # AT89S52 VCC
    'C6': (126, 40.5, 0, False), 'C7': (129, 40.5, 0, False),         # ESP32 5V
    'C3': (39.5, 27, 90, False),                                       # TXS VCCB 5V
    'C13': (144.5, 34, 270, False),                                    # TXS VCCA 3V3
    'C12': (30, 42.5, 0, False),                                       # DHT11 VDD
    'C5': (126, 26.5, 0, False), 'C8': (129, 26.5, 0, False),         # OLED 3V3
    'TP1': (78, 10, 0, False), 'TP2': (82, 10, 0, False), 'TP3': (86, 10, 0, False),
    '#FLG01': (13, 7, 0, False), '#FLG02': (96, 10, 0, False), '#FLG03': (100, 10, 0, False),
}

# ---------------------------------------------------------------- netlist
NETS = {
    '+5V': 'U1.40 U1.31 U7.3 C16.1 R10.1 C6.1 C7.1 TP1.1 C1.1 C11.1 C2.1 SW2.1 R3.1 U5.1 R2.1 C12.1 J3.2 J6.1 J5B.1 C3.1 J2A.1',
    'GND': 'U1.20 J1X.2 U7.2 C14.2 C15.2 C16.2 D1.1 C6.2 C7.2 TP3.1 #FLG02.1 C1.2 C11.2 C9.2 C10.2 R1.2 SW1.2 U5.4 C12.2 J3.3 J6.2 J5B.10 C13.2 C3.2 R4.2 J2A.2 J4.1 C5.2 C8.2',
    '+3V3': 'TP2.1 #FLG03.1 J5A.1 C13.1 J2A.3 J4.2 C5.1 C8.1',
    'VJACK': 'J1X.1 D2X.2', 'VIN': 'D2X.1 C14.1 C15.1 U7.1 #FLG01.1', 'LED_A': 'R10.2 D1.2',
    'RST': 'U1.9 C2.2 R1.1 SW2.2 J3.1', 'XTAL1': 'U1.19 Y1.1 C9.1', 'XTAL2': 'U1.18 Y1.2 C10.1',
    'SDA5': 'U1.1 J5B.2', 'SCL5': 'U1.2 J5B.3', 'MOSI': 'U1.6 J3.6', 'MISO': 'U1.7 J3.4', 'SCK': 'U1.8 J3.5',
    'RX51': 'U1.10 J5B.5', 'TX51': 'U1.11 J5B.4', 'DHT_DATA': 'U1.12 U5.2 R2.2', 'BTN_PAGE': 'U1.13 R3.2 SW1.1',
    'RELAY_IN': 'U1.21 J6.3',
    'SDA3': 'J5A.2 J4.4', 'SCL3': 'J5A.3 J4.3', 'TX51_3V3': 'J5A.4 J2A.4', 'RX51_3V3': 'J5A.5 J2B.1', 'OE': 'J5A.10 J2B.2 R4.1',
}
TRUNK = {  # x in grid units
    'RST': 74, 'SDA5': 72, 'SCL5': 70, 'MOSI': 68, 'MISO': 66, 'SCK': 64, 'RX51': 62, 'TX51': 60,
    'DHT_DATA': 58, 'BTN_PAGE': 56, 'XTAL2': 54, 'XTAL1': 52, 'RELAY_IN': 93,
    'SDA3': 140, 'SCL3': 138, 'TX51_3V3': 136, 'RX51_3V3': 134, 'OE': 132,
}
MANUAL = {  # explicit polylines (grid units) for tiny local nets
    'VJACK': [[(7, 9), (9.5, 9)]],
    'VIN': [[(12.5, 9), (18, 9)], [(15, 11), (15, 9)], [(17, 11), (17, 9)], [(13, 7), (13, 9)]],
    'LED_A': [[(30, 13), (30, 15), (32.5, 15)]],
    '+5V': [[(82, 44), (96, 44)],                               # U1 VCC -> C1, C11
            [(122, 43), (124, 43), (124, 39), (129, 39)],       # ESP32 5V -> C6, C7
            [(36, 29), (37, 29), (37, 27), (38, 27)],           # TXS VCCB -> C3
            [(34, 41), (30, 41)],                               # DHT11 VDD -> C12
            [(24, 9), (26, 9), (26, 11)]],                      # LM7805 OUT -> C16
    '+3V3': [[(148, 36), (147, 36), (147, 34), (146, 34)],      # TXS VCCA -> C13
             [(122, 30), (124, 30), (124, 25), (129, 25)]],     # OLED VCC -> C5, C8
}
MANUAL_JUNCTIONS = [(13, 9), (15, 9), (17, 9), (92, 44), (126, 39), (37, 27), (147, 34), (126, 25), (26, 9)]
# supply pins already joined to a cap by wire: one power symbol per cap group is enough
SKIP_POWER = {'U1.40', 'C11.1', 'J2A.1', 'C7.1', 'J5B.1', 'C3.1', 'J5A.1', 'C13.1', 'U5.1',
              'J4.2', 'C8.1', 'U7.3', 'C16.1'}
EXTRA_POWER = [('+5V', 37, 27), ('+3V3', 147, 34), ('+5V', 26, 9)]   # symbols on wire corners, pointing up
RENAME = {'J1X': 'J1', 'D2X': 'D2'
}
NC = 'J1X.3 U1.3 U1.4 U1.5 U1.14 U1.15 U1.16 U1.17 U1.22 U1.23 U1.24 U1.25 U1.26 U1.27 U1.28 U1.29 U1.30 ' \
     'U1.32 U1.33 U1.34 U1.35 U1.36 U1.37 U1.38 U1.39 U5.3 J5A.6 J5A.7 J5A.8 J5A.9 J5B.6 J5B.7 J5B.8 J5B.9 ' \
     'J2A.5 J2A.6 J2A.7 J2A.8 J2B.3 J2B.4 J2B.5 J2B.6 J2B.7 J2B.8'


VALUES = {'J2A': 'ESP32-C3 SuperMini - hang phai (5V side)',
          'J2B': 'ESP32-C3 SuperMini - hang trai (GPIO5 side)'}
# pin captions drawn left of mirrored headers: ref -> names for pins 1..n
CAPTIONS = {
    'J2A': ['5V', 'GND', '3V3', 'GPIO4 / RX1', 'GPIO3', 'GPIO2', 'GPIO1', 'GPIO0'],
    'J2B': ['GPIO5 / TX1', 'GPIO6 / OE', 'GPIO7', 'GPIO8', 'GPIO9', 'GPIO10', 'GPIO20', 'GPIO21'],
}


def uid():
    return str(uuid.uuid4())


def r(v):
    return round(v, 3)


# ---------------------------------------------------------------- geometry
def transform(px, py, rot, mirror):
    x, y = px, -py                      # library y-up -> schematic y-down
    if mirror:
        x = -x
    a = math.radians(rot)
    return (x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a))


def lib_pins(lib):
    out = {}
    def walk(n):
        for x in n:
            if isinstance(x, list) and x and x[0] == 'pin':
                at = first(x, 'at')
                out[first(x, 'number')[1]] = (float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0)
            elif isinstance(x, list):
                walk(x)
    walk(lib)
    return out


def on_segment(p, a, b, eps=1e-3):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    if abs((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) > eps:
        return False
    return min(x1, x2) - eps <= x <= max(x1, x2) + eps and min(y1, y2) - eps <= y <= max(y1, y2) + eps


def overlap(a, b):
    (p1, p2), (q1, q2) = a, b
    if not (on_segment(q1, p1, p2) or on_segment(q2, p1, p2) or on_segment(p1, q1, q2)):
        return False
    vertical = abs(p1[0] - p2[0]) < 1e-3 and abs(q1[0] - q2[0]) < 1e-3 and abs(p1[0] - q1[0]) < 1e-3
    horizontal = abs(p1[1] - p2[1]) < 1e-3 and abs(q1[1] - q2[1]) < 1e-3 and abs(p1[1] - q1[1]) < 1e-3
    if not (vertical or horizontal):
        return False
    lo1, hi1 = sorted([p1[1], p2[1]] if vertical else [p1[0], p2[0]])
    lo2, hi2 = sorted([q1[1], q2[1]] if vertical else [q1[0], q2[0]])
    return min(hi1, hi2) - max(lo1, lo2) > 1e-3


def main():
    path = Path(sys.argv[1])
    sch = parse(path.read_text(encoding='utf-8'))
    libs = {s[1]: s for s in find(first(sch, 'lib_symbols'), 'symbol')}
    insts = {}
    for s in find(sch, 'symbol'):
        ref = next(p[2] for p in find(s, 'property') if p[1] == 'Reference')
        insts[ref] = s
    for tmp, real in RENAME.items():   # file already rewritten: J1 is the renamed J1X
        if tmp not in insts and real in insts and first(insts[real], 'lib_id')[1] in (
                'Connector:Barrel_Jack_Switch', 'Device:D'):
            insts[tmp] = insts[real]

    # pin endpoints and outward directions
    pins = {}
    for ref, (gx, gy, rot, mir) in PLACE.items():
        lib = libs[first(insts[ref], 'lib_id')[1]]
        cx, cy = gx * G, gy * G
        for num, (px, py, ang) in lib_pins(lib).items():
            dx, dy = transform(px, py, rot, mir)
            ix, iy = transform(math.cos(math.radians(ang)), math.sin(math.radians(ang)), rot, mir)
            pins[f'{ref}.{num}'] = ((r(cx + dx), r(cy + dy)), (-round(ix), -round(iy)))

    net_of = {p: n for n, ps in NETS.items() for p in ps.split()}
    for p in NC.split():
        net_of[p] = None
    missing = set(pins) - set(net_of)
    assert not missing, f'pins without a net or NC: {sorted(missing)}'

    wires, junctions = [], []      # wires: (net, a, b)
    for net, polys in MANUAL.items():
        for poly in polys:
            pts = [(r(x * G), r(y * G)) for x, y in poly]
            wires += [(net, a, b) for a, b in zip(pts, pts[1:])]
    junctions += [(r(x * G), r(y * G)) for x, y in MANUAL_JUNCTIONS]
    for net, tx in TRUNK.items():
        T = r(tx * G)
        attach = []
        for p in NETS[net].split():
            (x, y), (ox, oy) = pins[p]
            if oy == 0:            # horizontal pin: must face the trunk
                assert (T - x) * ox > 0, f'{p} faces away from trunk {net}'
                wires.append((net, (x, y), (T, y))); attach.append(y)
            else:                  # vertical pin: step out, then across
                y2 = r(y + oy * G)
                wires += [(net, (x, y), (x, y2)), (net, (x, y2), (T, y2))]; attach.append(y2)
        lo, hi = min(attach), max(attach)
        if hi - lo > 1e-3:
            wires.append((net, (T, lo), (T, hi)))
        junctions += [(T, y) for y in attach if lo + 1e-3 < y < hi - 1e-3]

    # ------------------------------------------------ connectivity self-check
    errors = []
    for p, ((x, y), _) in pins.items():
        for net, a, b in wires:
            if on_segment((x, y), a, b) and net_of[p] != net:
                errors.append(f'pin {p} ({net_of[p]}) touches wire of {net}')
    for i, (n1, a1, b1) in enumerate(wires):
        for n2, a2, b2 in wires[i + 1:]:
            if n1 == n2:
                continue
            if overlap((a1, b1), (a2, b2)):
                errors.append(f'{n1} overlaps {n2} at {a1}-{b1}')
            for e in (a1, b1):
                if on_segment(e, a2, b2):
                    errors.append(f'{n1} end {e} lands on {n2}')
            for e in (a2, b2):
                if on_segment(e, a1, b1):
                    errors.append(f'{n2} end {e} lands on {n1}')
    for net, p in [(net_of[p], p) for p in pins]:
        if net is None:
            continue
    if errors:
        print('\n'.join(sorted(set(errors))))
        sys.exit(1)
    print(f'OK: {len(wires)} wire segments, {len(junctions)} junctions, no cross-net contact')
    if '--write' not in sys.argv:
        return

    # ------------------------------------------------ rebuild the file
    body = [x for x in sch if not (isinstance(x, list) and x and x[0] in
            ('symbol', 'global_label', 'label', 'wire', 'junction', 'no_connect', 'text'))]
    first(body, 'paper')[1] = 'A3'
    power_src = parse(POWER_LIB.read_text(encoding='utf-8'))
    lib_block = first(body, 'lib_symbols')
    for name in sorted(POWER):
        if f'power:{name}' not in libs:
            d = next(s for s in find(power_src, 'symbol') if s[1] == name)
            d[1] = f'power:{name}'
            lib_block.append(d)

    out = []
    for ref, (gx, gy, rot, mir) in PLACE.items():
        s = insts[ref]
        at = first(s, 'at'); ox, oy = float(at[1]), float(at[2])
        nx, ny = r(gx * G), r(gy * G)
        at[1], at[2], at[3] = nx, ny, rot
        s[:] = [x for x in s if not (isinstance(x, list) and x and x[0] == 'mirror')]
        if mir:
            s.insert(s.index(at) + 1, [Sym('mirror'), Sym('y')])
        for prop in find(s, 'property'):
            if prop[1] == 'Value' and ref in VALUES:
                prop[2] = VALUES[ref]
            if prop[1] == 'Reference' and ref in RENAME:
                prop[2] = RENAME[ref]
            pa = first(prop, 'at')
            pa[1], pa[2] = r(float(pa[1]) - ox + nx), r(float(pa[2]) - oy + ny)
            if len(pa) > 3:
                pa[3] = 0
        out.append(s)

    n = 0
    spots = [(net_of[p], xy, d) for p, (xy, d) in pins.items() if net_of[p] in POWER and p not in SKIP_POWER]
    spots += [(net, (r(x * G), r(y * G)), (0, -1)) for net, x, y in EXTRA_POWER]
    for net, (x, y), (ox, oy) in spots:
        n += 1
        down = net == 'GND'
        # rotate the symbol so its body points away from the pin
        if (ox, oy) == (0, -1):   rot = 180 if down else 0
        elif (ox, oy) == (0, 1):  rot = 0 if down else 180
        elif (ox, oy) == (-1, 0): rot = 270 if down else 90
        else:                     rot = 90 if down else 270
        out.append([Sym('symbol'), [Sym('lib_id'), f'power:{net}'], [Sym('at'), x, y, rot], [Sym('unit'), 1],
                    [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes')], [Sym('on_board'), Sym('yes')],
                    [Sym('dnp'), Sym('no')], [Sym('uuid'), uid()],
                    [Sym('property'), 'Reference', f'#PWR{n:03d}', [Sym('at'), x, y, 0],
                     [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]], [Sym('hide'), Sym('yes')]]],
                    [Sym('property'), 'Value', net, [Sym('at'), x, r(y + (3.2 if down else -3.2)), 0],
                     [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]]]],
                    [Sym('property'), 'Footprint', '', [Sym('at'), x, y, 0],
                     [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]], [Sym('hide'), Sym('yes')]]],
                    [Sym('pin'), '1', [Sym('uuid'), uid()]]])
    for net, a, b in wires:
        out.append([Sym('wire'), [Sym('pts'), [Sym('xy'), *a], [Sym('xy'), *b]],
                    [Sym('stroke'), [Sym('width'), 0], [Sym('type'), Sym('default')]], [Sym('uuid'), uid()]])
    for x, y in junctions:
        out.append([Sym('junction'), [Sym('at'), x, y], [Sym('diameter'), 0],
                    [Sym('color'), 0, 0, 0, 0], [Sym('uuid'), uid()]])
    for p in NC.split():
        (x, y), _ = pins[p]
        out.append([Sym('no_connect'), [Sym('at'), x, y], [Sym('uuid'), uid()]])

    for ref, names in CAPTIONS.items():
        gx, gy, _, _ = PLACE[ref]
        for i, name in enumerate(names, 1):
            (_, y), _ = pins[f'{ref}.{i}']
            out.append([Sym('text'), name, [Sym('exclude_from_sim'), Sym('no')],
                        [Sym('at'), r((gx - 2) * G), y, 0],
                        [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]], [Sym('justify'), Sym('right')]],
                        [Sym('uuid'), uid()]])

    used = {first(s, 'lib_id')[1] for s in out if s[0] == 'symbol'}
    lib_block[:] = [x for x in lib_block if not (isinstance(x, list) and x and x[0] == 'symbol' and x[1] not in used)]

    idx = body.index(first(body, 'sheet_instances'))
    body[idx:idx] = out
    path.write_text(dump(body) + '\n', encoding='utf-8')
    print(f'Wrote {path}: {len(PLACE)} parts, {n} power symbols, {len(NC.split())} no-connects')


if __name__ == '__main__':
    main()
