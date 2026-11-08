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

from layout_v2 import (CAPTIONS, EXTRA_POWER, MANUAL, MANUAL_JUNCTIONS, NC, NETS, NEW_PARTS,  # noqa: E402
                       PLACE, RENAME, SKIP_POWER, TMP_LIB, TRUNK, VALUES, FOOTPRINTS)

PROJECT_LIB = Path(__file__).resolve().parents[2] / 'hardware' / 'pcb' / 'env-monitor.kicad_sym'


def uid():
    return str(uuid.uuid4())


def r(v):
    return round(v, 3)


# ---------------------------------------------------------------- geometry
def transform(px, py, rot, mirror):
    x, y = px, -py                      # library y-up -> schematic y-down
    if mirror in ('y', True):
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


def new_instance(ref, lib_id, value, footprint, lib):
    def prop(k, v, hide=False):
        e = [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]]] + ([[Sym('hide'), Sym('yes')]] if hide else [])
        return [Sym('property'), k, v, [Sym('at'), 0, 0, 0], e]
    return [Sym('symbol'), [Sym('lib_id'), lib_id], [Sym('at'), 0, 0, 0], [Sym('unit'), 1],
            [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes')], [Sym('on_board'), Sym('yes')],
            [Sym('dnp'), Sym('no')], [Sym('uuid'), uid()],
            prop('Reference', ref), prop('Value', value), prop('Footprint', footprint, True), prop('Datasheet', '', True),
            *[[Sym('pin'), n, [Sym('uuid'), uid()]] for n in lib_pins(lib)]]


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
    lib_block = first(sch, 'lib_symbols')
    for s in find(parse(PROJECT_LIB.read_text(encoding='utf-8')), 'symbol'):
        name = f'env-monitor:{s[1]}'
        lib_block[:] = [x for x in lib_block if not (isinstance(x, list) and x and x[0] == 'symbol' and x[1] == name)]
        s[1] = name
        lib_block.append(s)
    libs = {s[1]: s for s in find(lib_block, 'symbol')}
    insts = {}
    for s in find(sch, 'symbol'):
        ref = next(p[2] for p in find(s, 'property') if p[1] == 'Reference')
        insts[ref] = s
    for tmp, real in RENAME.items():   # file already rewritten: J1 is the renamed J1X
        if tmp not in insts and real in insts and first(insts[real], 'lib_id')[1] == TMP_LIB[tmp]:
            insts[tmp] = insts[real]
    for ref, (sym, value) in NEW_PARTS.items():
        if ref not in insts:
            insts[ref] = new_instance(ref, f'env-monitor:{sym}', value, f'env-monitor:{sym}', libs[f'env-monitor:{sym}'])

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
            s.insert(s.index(at) + 1, [Sym('mirror'), Sym('x' if mir == 'x' else 'y')])
        new = ref in NEW_PARTS and abs(ox) < 1e-6 and abs(oy) < 1e-6
        for i, prop in enumerate(find(s, 'property')):
            if new:   # fresh instance: put reference above and value below the body
                first(prop, 'at')[2] = {0: -24, 1: 24}.get(i, 0)
            if prop[1] == 'Value' and ref in VALUES:
                prop[2] = VALUES[ref]
            if prop[1] == 'Footprint' and ref in FOOTPRINTS:
                prop[2] = FOOTPRINTS[ref]
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
