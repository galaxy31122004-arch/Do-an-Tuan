"""Export netlist and print members of the given nets."""
import os, re, subprocess, sys, tempfile, pathlib
SCH = pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb/env-monitor.kicad_sch'
out = os.path.join(tempfile.gettempdir(), 'nets.net')
subprocess.run([r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe', 'sch', 'export', 'netlist', '-o', out, str(SCH)], check=True, capture_output=True)
t = open(out, encoding='utf-8').read()
for m in re.finditer(r'\(name "/?([^"]+)"\)(.*?)(?=\(net |\Z)', t, re.S):
    if m[1] in sys.argv[1:]:
        print(m[1], ['%s.%s' % p for p in re.findall(r'ref "(\w+)"\)\s*\(pin "(\d+)"', m[2])])
