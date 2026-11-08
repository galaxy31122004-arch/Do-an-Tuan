"""Generate simple VRML 3D models (boxes) for the custom module footprints.
KiCad VRML units: 1 unit = 2.54 mm; x right, y up (footprint y is down), z up from board top.
Output: hardware/pcb/env-monitor.3dshapes/*.wrl"""
import pathlib
OUT = pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.3dshapes'
OUT.mkdir(exist_ok=True)
COL = {'hdr': (0.1, 0.1, 0.1), 'pcb_blue': (0.1, 0.25, 0.7), 'pcb_black': (0.08, 0.08, 0.1), 'chip': (0.12, 0.12, 0.12),
       'metal': (0.75, 0.75, 0.78), 'glass': (0.02, 0.02, 0.04), 'gold': (0.85, 0.7, 0.2), 'brass': (0.8, 0.65, 0.3),
       'ant': (0.85, 0.85, 0.8), 'led': (0.9, 0.2, 0.2)}
HDR_H = 8.5  # female header height (mm)

def box(x1, y1, x2, y2, z1, z2, c):
    """Axis-aligned box in footprint mm coordinates (y down)."""
    u = lambda v: v / 2.54
    X1, X2 = u(x1), u(x2); Y1, Y2 = u(-y2), u(-y1); Z1, Z2 = u(z1), u(z2)
    p = [(X1, Y1, Z1), (X2, Y1, Z1), (X2, Y2, Z1), (X1, Y2, Z1), (X1, Y1, Z2), (X2, Y1, Z2), (X2, Y2, Z2), (X1, Y2, Z2)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    r, g, b = COL[c]
    return ('Shape { appearance Appearance { material Material { diffuseColor %.3f %.3f %.3f specularColor 0.2 0.2 0.2 shininess 0.3 } }\n'
            ' geometry IndexedFaceSet { solid FALSE coord Coordinate { point [ %s ] } coordIndex [ %s ] } }\n'
            % (r, g, b, ', '.join('%.4f %.4f %.4f' % q for q in p), ', '.join('%d,%d,%d,%d,-1' % q for q in f)))

def header_row(x, y1, y2):  # female header along y at column x, pins from y1 to y2 (pitch 2.54)
    return box(x - 1.27, y1 - 1.27, x + 1.27, y2 + 1.27, 0, HDR_H, 'hdr')

def write(name, parts):
    (OUT / name).write_text('#VRML V2.0 utf8\n' + ''.join(parts), encoding='utf-8'); print('wrote', name)

z0 = HDR_H
# ESP32-C3 SuperMini: 18 x 22.52 mm, pins at x = +-7.62, y = -8.89..8.89; USB-C at top (y negative)
write('ESP32-C3_SuperMini.wrl', [
    header_row(7.62, -8.89, 8.89), header_row(-7.62, -8.89, 8.89),
    box(-9.0, -11.26, 9.0, 11.26, z0, z0 + 1.0, 'pcb_black'),
    box(-4.5, -12.0, 4.5, -4.7, z0 + 1.0, z0 + 4.2, 'metal'),        # USB-C
    box(-2.5, -1.5, 2.5, 3.5, z0 + 1.0, z0 + 1.9, 'chip'),           # ESP32-C3 QFN
    box(-5.5, 7.0, 5.5, 10.2, z0 + 1.0, z0 + 2.2, 'ant'),            # ceramic antenna
    box(-6.5, -3.5, -4.5, -1.5, z0 + 1.0, z0 + 2.0, 'metal'),         # BOOT / RST buttons
    box(4.5, -3.5, 6.5, -1.5, z0 + 1.0, z0 + 2.0, 'metal'),
    box(-1.0, 4.5, 1.0, 5.5, z0 + 1.0, z0 + 1.6, 'led'),
])
# TXS0108E breakout: 15.7 x 27 mm, pins at x = +-6.35, y = -11.43..11.43
write('TXS0108E_Module.wrl', [
    header_row(-6.35, -11.43, 11.43), header_row(6.35, -11.43, 11.43),
    box(-7.85, -13.5, 7.85, 13.5, z0, z0 + 1.6, 'pcb_blue'),
    box(-2.2, -3.25, 2.2, 3.25, z0 + 1.6, z0 + 2.8, 'chip'),         # TSSOP-20
    box(-4.0, 5.0, -2.5, 6.0, z0 + 1.6, z0 + 2.4, 'brass'),          # 0603 caps
    box(2.5, 5.0, 4.0, 6.0, z0 + 1.6, z0 + 2.4, 'brass'),
])
# OLED 0.96" I2C: board (-26.2,-9.84)-(1.6,17.46); 1x4 header at x=0, y=0..7.62; M2 holes at the corners
holes = [(-0.4, -7.84), (-24.2, -7.84), (-0.4, 15.46), (-24.2, 15.46)]
write('OLED_0.96_I2C_Module.wrl', [header_row(0, 0, 7.62)] +
      [box(x - 1.6, y - 1.6, x + 1.6, y + 1.6, 0, z0, 'brass') for x, y in holes] + [   # standoffs
    box(-26.2, -9.84, 1.6, 17.46, z0, z0 + 1.2, 'pcb_blue'),
    box(-23.8, -9.54, -4.5, 17.16, z0 + 1.2, z0 + 2.6, 'glass'),      # display panel
    box(-22.5, -6.0, -5.8, 13.6, z0 + 2.6, z0 + 2.65, 'pcb_black'),   # active area
])
