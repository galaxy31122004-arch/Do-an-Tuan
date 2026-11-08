"""Redraw env-monitor.kicad_sch as tidy functional blocks (frame + title per block).

Keeps every part (uuid, value, footprint) and the connectivity of the current schematic.
Local circuits use real wires; signals between blocks use local labels.
Pins not covered by an explicit wire / label / power symbol get a default:
power net -> power symbol on the pin, signal -> label on a 2-grid stub, unconnected -> no-connect.

Usage: python tidy_sch.py <ref.net> [--write]
  <ref.net> = kicad-cli netlist of the schematic BEFORE the rewrite (connectivity reference).
After --write: export a new netlist and run check with  python tidy_sch.py <ref.net> --check <new.net>
"""
import math
import sys
import uuid
from pathlib import Path

from sexpr import Sym, dump, find, first, parse
from netdump import nets as read_nets

G = 2.54
OY = 3          # whole drawing down (grid units)


def shift(x, y):
    """Extra vertical offset per block (grid units) to spread the blocks over the sheet."""
    if x < 52:
        return OY + (0 if y < 25 else 3 if y < 41 else 6 if y < 62 else 9)
    if x < 99:
        return OY + 12
    return OY + (0 if y < 36 else 4 if y < 52 else 8)
SCH = Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_sch'
POWER = {'+12V', '+5V', '+3V3', 'GND'}
# nets that get a readable label name (old auto name -> new label)
RENAME = {'Net-(J3-Pin_1)': '/RST', 'Net-(J3-Pin_4)': '/MISO', 'Net-(J3-Pin_5)': '/SCK', 'Net-(J3-Pin_6)': '/MOSI',
          'Net-(U1-P3.2)': '/DHT_DATA', 'Net-(U1-P3.3)': '/BTN_PAGE', 'Net-(U1-P2.0{slash}A8)': '/RELAY'}

# ---------------------------------------------------------------- placement (grid units: 1 = 2.54 mm)
# ref: (x, y, rot, mirror)
PLACE = {
    # power
    'J1': (10, 14, 0, None), 'J7': (11, 20, 0, 'y'), 'D2': (21, 13, 180, None), 'C14': (26, 14.5, 0, None),
    'U7': (33, 13, 0, None), 'C16': (40, 14.5, 0, None), 'TP1': (43, 13, 0, None), 'TP3': (46, 16, 0, None),
    # MCU
    'U1': (82, 40, 0, None), 'C1': (86, 23.5, 0, None),
    'C2': (68, 27.5, 0, None), 'SW2': (63, 27, 270, None), 'R1': (59, 30.5, 0, None),
    'C9': (59, 51.5, 0, None), 'Y1': (64, 51.5, 270, None), 'C10': (71, 54.5, 0, None),
    # ISP, button, DHT11
    'J3': (12, 33, 0, 'y'),
    'R3': (12, 48.5, 0, None), 'SW1': (12, 54, 270, None),
    'U5': (14, 74, 0, None), 'R2': (20, 71.5, 0, None),
    # TXS0108E + I2C pull-ups
    'U4': (114, 18, 0, None), 'R4': (107, 23.5, 0, None), 'R8': (122, 28, 270, None), 'R9': (122, 31, 270, None),
    # ESP32
    'U2': (146, 22, 0, None), 'TP2': (148, 12, 0, None),
    # OLED
    'J4': (114, 44, 0, None),
    # relay
    'R6': (106, 68.5, 0, None), 'U8': (112, 71, 0, None), 'R5': (119.5, 72, 90, None), 'R7': (122, 73.5, 0, None),
    'Q1': (126, 72, 0, None), 'D3': (123, 63, 270, None), 'K1': (129, 63, 0, None), 'J6': (146, 64, 0, 'x'),
}

# explicit wires (polylines, grid units)
WIRES = [
    # power: VIN, +12V, +5V, GND
    [(13, 13), (17, 13), (19.5, 13)], [(13, 20), (17, 20), (17, 13)],
    [(13, 15), (15, 15)], [(13, 21), (15, 21)],
    [(22.5, 13), (24, 13), (26, 13), (28, 13), (30, 13)],
    [(36, 13), (38, 13), (40, 13), (43, 13)],
    [(33, 16), (33, 17), (36, 17)],
    # MCU: VCC + C1, reset, crystal
    [(82, 24), (82, 22), (86, 22)],
    [(59, 29), (63, 29), (68, 29), (76, 29)],
    [(76, 50), (64, 50), (59, 50)],
    [(76, 51), (71, 51), (71, 53), (64, 53)],
    # button, DHT11
    [(12, 50), (12, 51), (12, 52)], [(12, 51), (16, 51)],
    [(17, 74), (20, 74), (24, 74)], [(20, 73), (20, 74)],
    # OLED / ISP signals: longer stubs
    [(112, 45), (108, 45)], [(112, 46), (108, 46)],
    [(14, 31), (18, 31)], [(14, 34), (18, 34)], [(14, 35), (18, 35)], [(14, 36), (18, 36)],
    # TXS OE + R4
    [(111, 22), (107, 22), (105, 22)],
    # ESP32 3V3 + TP2
    [(145, 14), (145, 12), (148, 12)],
    # relay
    [(106, 70), (109, 70)], [(109, 72), (104, 72)],
    [(115, 70), (117, 70), (117, 68)],
    [(115, 72), (118, 72)], [(121, 72), (122, 72), (124, 72)],
    [(127, 70), (127, 68), (127, 66)], [(123, 64.5), (123, 68), (127, 68)],
    [(127, 60), (127, 58)], [(123, 61.5), (123, 58), (127, 58)],
    [(132, 60), (132, 59), (142, 59), (142, 63), (144, 63)],
    [(131, 66), (131, 67), (143, 67), (143, 64), (144, 64)],
]
# explicit labels: (name, x, y, dir)  dir = direction the text runs from the anchor
LABELS = [('RST', 73, 29, 'L'), ('BTN_PAGE', 16, 51, 'R'), ('DHT_DATA', 24, 74, 'R'), ('OE', 105, 22, 'L'),
          ('RELAY', 104, 72, 'L'), ('SCL3', 108, 45, 'L'), ('SDA3', 108, 46, 'L'),
          ('RST', 18, 31, 'R'), ('MISO', 18, 34, 'R'), ('SCK', 18, 35, 'R'), ('MOSI', 18, 36, 'R')]
# explicit power symbols: (net, x, y, dir)  dir = direction the symbol body points
PWR = [('+12V', 24, 13, 'U'), ('+5V', 38, 13, 'U'), ('GND', 15, 15, 'D'), ('GND', 15, 21, 'D'), ('GND', 33, 17, 'D'),
       ('+5V', 82, 22, 'U'), ('+3V3', 145, 12, 'U'), ('+12V', 117, 68, 'U'), ('+12V', 127, 58, 'U')]
FLAGS = [(28, 13, 'U'), (36, 17, 'D')]           # PWR_FLAG on +12V and GND
TEXTS = [('COM', 148, 64), ('NO', 148, 63)]  # small notes beside parts (left-justified)

# blocks: (title, x1, y1, x2, y2)
BLOCKS = [
    ('NGUỒN 12 V → 5 V', 6, 7, 50, 24),
    ('NẠP ISP', 6, 27, 30, 39),
    ('NÚT CHUYỂN TRANG', 6, 43, 30, 60),
    ('CẢM BIẾN DHT11', 6, 64, 30, 80),
    ('VI ĐIỀU KHIỂN AT89S52', 53, 17, 98, 60),
    ('CHUYỂN MỨC LOGIC TXS0108E (5 V ↔ 3,3 V)', 100, 7, 134, 34),
    ('ESP32-C3 (Wi-Fi)', 137, 7, 159, 34),
    ('MÀN HÌNH OLED (I²C 3,3 V)', 100, 38, 134, 50),
    ('ĐIỀU KHIỂN RELAY (cách ly PC817)', 100, 54, 152, 79),
]
PIN_MOVE = [('env-monitor:ESP32-C3_SuperMini', '1', -5.08, 20.32), ('env-monitor:ESP32-C3_SuperMini', '3', -2.54, 20.32),
            ('env-monitor:ESP32-C3_SuperMini', '2', -2.54, -20.32)]
# property overrides: ref -> ((dx, dy, justify) for Reference, (dx, dy, justify) for Value), grid units
PROPS = {
    'Y1': ((1.0, -0.3, 'left'), (1.0, 0.6, 'left')),
    'SW2': ((-0.8, -0.4, 'right'), (-0.8, 0.4, 'right')),
    'SW1': ((1.2, -0.4, 'left'), (1.2, 0.4, 'left')),
    'D3': ((-0.8, -0.4, 'right'), (-0.8, 0.4, 'right')),
    'TP1': ((0.8, -1.6, 'left'), None), 'TP2': ((0.8, -1.6, 'left'), None), 'TP3': ((0.8, -1.6, 'left'), None),
    'C1': ((0.8, -0.4, 'left'), (0.8, 0.4, 'left')),
    'U1': ((76.5 - 82, 25.2 - 40, 'left'), (0, 0, None, 90)),
    'U2': ((149.5 - 146, 14.6 - 22, 'left'), (142.6 - 146, 0, None, 90)),
    'U7': ((31 - 33, 11.2 - 13, 'left'), (33.5 - 33, 11.2 - 13, 'left')),
    'Q1': ((2, -0.4, 'left'), (2, 0.6, 'left')),
    'K1': ((133.5 - 129, -0.5, 'left'), (133.5 - 129, 0.5, 'left')),
    'J6': ((0, -2.4, None), (1, 2.2, None)),
    'U4': ((0, -6.4, None), (0, 6.4, None)),
}


def uid():
    return str(uuid.uuid4())


def r(v):
    return round(v, 3)


def transform(px, py, rot, mirror):
    x, y = px, -py
    if mirror == 'y':
        x = -x
    elif mirror == 'x':
        y = -y
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


DIRV = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
VDIR = {v: k for k, v in DIRV.items()}


def font(size=1.27, bold=False):
    f = [Sym('font'), [Sym('size'), size, size]]
    if bold:
        f.append([Sym('bold'), Sym('yes')])
    return f


def power_symbol(net, x, y, d, n, ref_prefix='#PWR'):
    """KiCad power symbol whose body points in direction d (U/D/L/R) from its pin at (x, y) (mm)."""
    down = net == 'GND'
    rot = {('U', False): 0, ('D', False): 180, ('L', False): 90, ('R', False): 270,
           ('D', True): 0, ('U', True): 180, ('L', True): 270, ('R', True): 90}[(d, down)]
    if net == 'PWR_FLAG':
        rot = {'U': 0, 'D': 180, 'L': 90, 'R': 270}[d]
    dx, dy = DIRV[d]
    if dy:
        tx, ty, just = x, y + dy * (3.4 if down or net == 'PWR_FLAG' else 3.2), None
    else:
        tx, ty, just = x + dx * 3.0, y, ('left' if dx > 0 else 'right')
        if rot == 90:   # text drawn at 180 deg: KiCad mirrors the justification
            just = 'right' if just == 'left' else 'left'
    eff = [Sym('effects'), font()] + ([[Sym('justify'), Sym(just)]] if just else [])
    lib = 'power:' + net
    return [Sym('symbol'), [Sym('lib_id'), lib], [Sym('at'), r(x), r(y), rot], [Sym('unit'), 1],
            [Sym('body_style'), 1], [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes')],
            [Sym('on_board'), Sym('yes')], [Sym('in_pos_files'), Sym('yes')], [Sym('dnp'), Sym('no')],
            [Sym('uuid'), uid()],
            [Sym('property'), 'Reference', f'{ref_prefix}{n:02d}', [Sym('at'), r(x), r(y), 0], [Sym('hide'), Sym('yes')],
             [Sym('effects'), font()]],
            [Sym('property'), 'Value', net, [Sym('at'), r(tx), r(ty), 90 if rot in (90, 270) else 0], eff],
            [Sym('property'), 'Footprint', '', [Sym('at'), r(x), r(y), 0], [Sym('hide'), Sym('yes')], [Sym('effects'), font()]],
            [Sym('property'), 'Datasheet', '', [Sym('at'), r(x), r(y), 0], [Sym('hide'), Sym('yes')], [Sym('effects'), font()]],
            [Sym('property'), 'Description', '', [Sym('at'), r(x), r(y), 0], [Sym('hide'), Sym('yes')], [Sym('effects'), font()]],
            [Sym('pin'), '1', [Sym('uuid'), uid()]],
            [Sym('instances'), [Sym('project'), 'env-monitor',
                                [Sym('path'), '/' + ROOT_UUID, [Sym('reference'), f'{ref_prefix}{n:02d}'], [Sym('unit'), 1]]]]]


def label(name, x, y, d):
    ang, just = {'R': (0, 'left'), 'L': (180, 'right'), 'U': (90, 'left'), 'D': (270, 'right')}[d]
    return [Sym('label'), name, [Sym('at'), r(x), r(y), ang],
            [Sym('effects'), font(), [Sym('justify'), Sym(just), Sym('bottom')]], [Sym('uuid'), uid()]]


def on_seg(p, a, b, eps=1e-3):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    if abs((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) > eps:
        return False
    return min(x1, x2) - eps <= x <= max(x1, x2) + eps and min(y1, y2) - eps <= y <= max(y1, y2) + eps


def same(p, q):
    return abs(p[0] - q[0]) < 1e-3 and abs(p[1] - q[1]) < 1e-3


ROOT_UUID = ''


def build(ref_net):
    global ROOT_UUID
    sch = parse(SCH.read_text(encoding='utf-8'))
    ROOT_UUID = first(sch, 'uuid')[1]
    libs = {s[1]: s for s in find(first(sch, 'lib_symbols'), 'symbol')}
    # ESP32 symbol: move supply pins left so their names clear the GPIO names
    for name, num, x, y in PIN_MOVE:
        def walk(n):
            for e in n:
                if isinstance(e, list) and e and e[0] == 'pin' and first(e, 'number')[1] == num:
                    at = first(e, 'at'); at[1], at[2] = x, y
                elif isinstance(e, list):
                    walk(e)
        walk(libs[name])
    insts = {}
    for s in find(sch, 'symbol'):
        ref = next(p[2] for p in find(s, 'property') if p[1] == 'Reference')
        if not ref.startswith('#'):
            insts[ref] = s
    assert set(insts) == set(PLACE), f'missing {set(insts) - set(PLACE)} extra {set(PLACE) - set(insts)}'

    old = read_nets(ref_net)
    net_of = {}
    for n, nodes in old.items():
        name = RENAME.get(n, n)
        for ref, pin in nodes:
            net_of[(ref, pin)] = None if (n.startswith('unconnected') or len(nodes) == 1) else name

    pins = {}   # (ref, pin) -> ((x mm, y mm), outward unit vector)
    for ref, (gx, gy, rot, mir) in PLACE.items():
        lib = libs[first(insts[ref], 'lib_id')[1]]
        for num, (px, py, ang) in lib_pins(lib).items():
            dx, dy = transform(px, py, rot, mir)
            ix, iy = transform(math.cos(math.radians(ang)), math.sin(math.radians(ang)), rot, mir)
            pins[(ref, num)] = ((r(gx * G + dx), r((gy + shift(gx, gy)) * G + dy)), (-round(ix), -round(iy)))

    mm = lambda p: (r(p[0] * G), r((p[1] + shift(*p)) * G))
    wires = []
    for poly in WIRES:
        pts = [mm(p) for p in poly]
        wires += list(zip(pts, pts[1:]))
    labels = [(n, *mm((x, y)), d) for n, x, y, d in LABELS]
    pwrs = [(n, *mm((x, y)), d) for n, x, y, d in PWR]
    flags = [(*mm((x, y)), d) for x, y, d in FLAGS]
    nc = []

    touched = {p for w in wires for p in w} | {(x, y) for _, x, y, _ in labels} | {(x, y) for _, x, y, _ in pwrs}
    for key, ((x, y), (ox, oy)) in pins.items():
        net = net_of[key]
        if any(same((x, y), t) for t in touched):
            continue
        if net is None:
            nc.append((x, y))
        elif net in POWER:
            pwrs.append((net, x, y, VDIR[(ox, oy)]))
        else:
            ex, ey = r(x + ox * 2 * G), r(y + oy * 2 * G)
            wires.append(((x, y), (ex, ey)))
            labels.append((net.lstrip('/'), ex, ey, VDIR[(ox, oy)]))

    # split wires at every connection point lying inside a segment
    points = [p for w in wires for p in w] + [p for p, _ in pins.values()] + \
             [(x, y) for _, x, y, _ in pwrs] + [(x, y) for x, y, _ in flags] + [(x, y) for _, x, y, _ in labels]
    split = []
    for a, b in wires:
        inner = sorted({p for p in points if on_seg(p, a, b) and not same(p, a) and not same(p, b)},
                       key=lambda p: math.hypot(p[0] - a[0], p[1] - a[1]))
        seq = [a] + inner + [b]
        split += list(zip(seq, seq[1:]))
    wires = split

    # junctions: >= 3 connected items meet at one point
    count = {}
    def add(p):
        k = (round(p[0], 2), round(p[1], 2)); count[k] = count.get(k, 0) + 1
    for a, b in wires:
        add(a); add(b)
    for p, _ in pins.values():
        if any(same(p, w) for seg in wires for w in seg):
            add(p)
    for _, x, y, _ in pwrs:
        add((x, y))
    for x, y, _ in flags:
        add((x, y))
    junctions = [p for p, c in count.items() if c >= 3]

    return sch, insts, libs, pins, wires, labels, pwrs, flags, nc, junctions


def place_props(ref, inst, lib, gx, gy, rot, mir):
    X, Y = gx * G, (gy + shift(gx, gy)) * G
    lib_id = first(inst, 'lib_id')[1]
    vertical = rot in (0, 180)
    two_pin = lib_id in ('Device:R', 'Device:C', 'Device:C_Polarized')
    if ref in PROPS:
        rule = PROPS[ref]
    elif two_pin and vertical:
        rule = ((0.8, -0.4, 'left'), (0.8, 0.4, 'left'))
    elif two_pin or lib_id == 'Device:D':
        rule = ((0, -0.9, None), (0, 0.9, None)) if not vertical or lib_id == 'Device:D' and rot in (0, 180) else \
               ((0.8, -0.4, 'left'), (0.8, 0.4, 'left'))
    else:
        rule = None
    libprops = {p[1]: first(p, 'at') for p in find(lib, 'property')}
    for prop in find(inst, 'property'):
        k = prop[1]
        at = first(prop, 'at')
        prop[:] = [x for x in prop if not (isinstance(x, list) and x and x[0] == 'hide')]
        eff = first(prop, 'effects')
        eff[:] = [x for x in eff if not (isinstance(x, list) and x and x[0] == 'justify')]
        if k in ('Reference', 'Value'):
            spec = rule[0 if k == 'Reference' else 1] if rule else None
            if rule and spec is None:
                prop.insert(prop.index(at) + 1, [Sym('hide'), Sym('yes')])
                at[1], at[2], at[3] = r(X), r(Y), 0
                continue
            if spec:
                dx, dy, just = spec[:3]
                ang = spec[3] if len(spec) > 3 else 0      # wanted on-screen angle
                at[1], at[2], at[3] = r(X + dx * G), r(Y + dy * G), (ang + (90 if rot in (90, 270) else 0)) % 180
                if just:
                    eff.append([Sym('justify'), Sym(just)])
            else:
                la = libprops[k]
                dx, dy = transform(float(la[1]), float(la[2]), rot, mir)
                at[1], at[2], at[3] = r(X + dx), r(Y + dy), 90 if rot in (90, 270) else 0
        else:
            at[1], at[2], at[3] = r(X), r(Y), 0
            prop.insert(prop.index(at) + 1, [Sym('hide'), Sym('yes')])


def write(sch, insts, libs, pins, wires, labels, pwrs, flags, nc, junctions):
    body = [x for x in sch if not (isinstance(x, list) and x and x[0] in
            ('symbol', 'label', 'global_label', 'wire', 'junction', 'no_connect', 'text', 'rectangle'))]
    out = []
    for ref, (gx, gy, rot, mir) in PLACE.items():
        s = insts[ref]
        at = first(s, 'at')
        at[1], at[2], at[3] = r(gx * G), r((gy + shift(gx, gy)) * G), rot
        s[:] = [x for x in s if not (isinstance(x, list) and x and x[0] == 'mirror')]
        if mir:
            s.insert(s.index(at) + 1, [Sym('mirror'), Sym(mir)])
        place_props(ref, s, libs[first(s, 'lib_id')[1]], gx, gy, rot, mir)
        out.append(s)
    for i, (net, x, y, d) in enumerate(pwrs, 1):
        out.append(power_symbol(net, x, y, d, i))
    for i, (x, y, d) in enumerate(flags, 1):
        out.append(power_symbol('PWR_FLAG', x, y, d, i, '#FLG'))
    for a, b in wires:
        out.append([Sym('wire'), [Sym('pts'), [Sym('xy'), *a], [Sym('xy'), *b]],
                    [Sym('stroke'), [Sym('width'), 0], [Sym('type'), Sym('default')]], [Sym('uuid'), uid()]])
    for x, y in junctions:
        out.append([Sym('junction'), [Sym('at'), x, y], [Sym('diameter'), 0], [Sym('color'), 0, 0, 0, 0], [Sym('uuid'), uid()]])
    for x, y in nc:
        out.append([Sym('no_connect'), [Sym('at'), x, y], [Sym('uuid'), uid()]])
    for n, x, y, d in labels:
        out.append(label(n, x, y, d))
    for title, x1, y1, x2, y2 in BLOCKS:
        out.append([Sym('rectangle'), [Sym('start'), r(x1 * G), r((y1 + shift(x1, y1)) * G)], [Sym('end'), r(x2 * G), r((y2 + shift(x1, y1)) * G)],
                    [Sym('stroke'), [Sym('width'), 0.25], [Sym('type'), Sym('dash')], [Sym('color'), 0, 90, 140, 1]],
                    [Sym('fill'), [Sym('type'), Sym('none')]], [Sym('uuid'), uid()]])
        out.append([Sym('text'), title, [Sym('exclude_from_sim'), Sym('no')], [Sym('at'), r(x1 * G + 1.5), r((y1 + shift(x1, y1)) * G + 3.0), 0],
                    [Sym('effects'), font(1.8, True) + [[Sym('color'), 0, 90, 140, 1]], [Sym('justify'), Sym('left'), Sym('bottom')]],
                    [Sym('uuid'), uid()]])
    for t, x, y in TEXTS:
        out.append([Sym('text'), t, [Sym('exclude_from_sim'), Sym('no')], [Sym('at'), r(x * G), r((y + shift(x, y)) * G), 0],
                    [Sym('effects'), font(), [Sym('justify'), Sym('left')]], [Sym('uuid'), uid()]])
    idx = body.index(first(body, 'sheet_instances'))
    body[idx:idx] = out
    SCH.write_text(dump(body) + '\n', encoding='utf-8')
    print(f'wrote {SCH.name}: {len(PLACE)} parts, {len(pwrs)} power, {len(wires)} wires, {len(junctions)} junctions, '
          f'{len(labels)} labels, {len(nc)} NC')


def check(ref_net, new_net):
    old, new = read_nets(ref_net), read_nets(new_net)
    def part(ns, ren):
        out = {}
        for n, nodes in ns.items():
            if n.startswith('unconnected') or len(nodes) < 2:
                continue
            out[frozenset(nodes)] = ren(n)
        return out
    a = part(old, lambda n: RENAME.get(n, n))
    b = part(new, lambda n: n)
    bad = 0
    for k, n in a.items():
        if k not in b:
            print('MISSING group', n, sorted(k)); bad += 1
        elif b[k] != n and not n.startswith('Net-('):
            print('NAME', n, '->', b[k]); bad += 1
    for k, n in b.items():
        if k not in a:
            print('EXTRA group', n, sorted(k)); bad += 1
    print('connectivity OK' if not bad else f'{bad} problems')
    renames = {a[k]: b[k] for k in a if k in b and a[k] != b[k]}
    print('renames:', renames)
    return bad


if __name__ == '__main__':
    if '--check' in sys.argv:
        sys.exit(1 if check(sys.argv[1], sys.argv[sys.argv.index('--check') + 1]) else 0)
    res = build(sys.argv[1])
    if '--write' in sys.argv:
        write(*res)
    else:
        print('dry run ok')
