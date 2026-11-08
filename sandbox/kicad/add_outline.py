"""Add a 100 x 100 mm board outline (Edge.Cuts) centred on the placed footprints."""
import re, pathlib, uuid
f = pathlib.Path(__file__).resolve().parents[2] / 'hardware' / 'pcb' / 'env-monitor.kicad_pcb'
t = f.read_text(encoding='utf-8')
pts = [(float(x), float(y)) for x, y in re.findall(r'\n\t\(footprint "[^"]*"\n(?:\t\t[^\n]*\n)*?\t\t\(at ([-\d.]+) ([-\d.]+)', t)]
xs, ys = [p[0] for p in pts], [p[1] for p in pts]
cx, cy = round((min(xs) + max(xs)) / 2), round((min(ys) + max(ys)) / 2)
print(f'{len(pts)} footprints, x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)}, centre {cx},{cy}')
rect = (f'\t(gr_rect\n\t\t(start {cx - 50} {cy - 50})\n\t\t(end {cx + 50} {cy + 50})\n'
        f'\t\t(stroke\n\t\t\t(width 0.1)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "Edge.Cuts")\n'
        f'\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
e = t.rstrip().rindex(')')
f.write_text(t[:e] + rect + t[e:], encoding='utf-8')
