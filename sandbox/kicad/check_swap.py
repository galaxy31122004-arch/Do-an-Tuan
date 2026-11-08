import re, subprocess, os, tempfile, pathlib
P = pathlib.Path(__file__).resolve().parents[2] / 'hardware/pcb'
out = os.path.join(tempfile.gettempdir(), 'sw.net')
subprocess.run([r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe', 'sch', 'export', 'netlist', '-o', out, str(P / 'env-monitor.kicad_sch')], capture_output=True)
t = open(out, encoding='utf-8').read()
nets = {}
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]+)"\)(.*?)\)\s*\)\s*(?=\(net |\)\s*\)\s*$)', t, re.S):
    nets[m[1]] = sorted(f'{a}.{b}' for a, b in re.findall(r'\(ref "([^"]+)"\) \(pin "([^"]+)"', m[2]))
for n, p in nets.items():
    if any(x.startswith(('U4.', 'U2.')) for x in p) and n not in ('GND', '+5V', '+3V3'):
        print(n, p)
