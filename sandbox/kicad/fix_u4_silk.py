"""Replace the TXS0108E silk rectangle with lines, leaving a gap at the R8 pad."""
import pathlib
import re
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[2] / "hardware/pcb"
PCB = ROOT / "env-monitor.kicad_pcb"
LIB = ROOT / "env-monitor.pretty/TXS0108E_Module.kicad_mod"
X, Y, GAP = 7.85, 13.5, 1.2
SEGMENTS = [
    (-X, -Y, X, -Y),
    (X, -Y, X, Y),
    (-X, Y, -X, -Y),
    (X, Y, GAP, Y),
    (-GAP, Y, -X, Y),
]


def line(seg):
    x1, y1, x2, y2 = seg
    return (
        f'(fp_line (start {x1} {y1}) (end {x2} {y2}) '
        f'(stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uuid.uuid4()}"))'
    )


def patch(path, pattern):
    raw = path.read_bytes().decode("utf-8")
    new, count = re.subn(pattern, lambda _: " ".join(line(s) for s in SEGMENTS), raw, flags=re.S)
    if count != 1:
        raise SystemExit(f"{path.name}: expected 1 silk rectangle, found {count}")
    path.write_bytes(new.encode("utf-8"))
    print("patched", path.name)


patch(PCB, r'\(fp_rect\s+\(start -7\.85 -13\.5\)\s+\(end 7\.85 13\.5\)\s+\(stroke\s+\(width 0\.12\)\s+\(type solid\)\s+\)\s+\(fill no\)\s+\(layer "F\.SilkS"\)\s+\(uuid "86c7ca8c-b1c1-475a-9d8e-b36b5abc537d"\)\s+\)')
patch(LIB, r'\(fp_rect \(start -7\.85 -13\.5\) \(end 7\.85 13\.5\) \(stroke \(width 0\.12\) \(type solid\)\) \(fill no\) \(layer "F\.SilkS"\) \(uuid "a03e82b6-9067-45ce-8f2a-abb505e414b9"\)\)')
