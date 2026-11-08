"""Parse a kicad-cli netlist (kicadsexpr) into {net: sorted [(ref, pin)]}. Usage: netdump.py file.net [--all]"""
import re, sys

def nets(path):
    t = open(path, encoding='utf-8').read()
    t = t[t.index('(nets'):]
    out = {}
    for blk in re.split(r'\n\t\t\(net\n', t)[1:]:
        name = re.search(r'\(name "((?:[^"\\]|\\.)*)"\)', blk).group(1)
        out[name] = sorted(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk))
    return out

if __name__ == '__main__':
    for n, nodes in nets(sys.argv[1]).items():
        if '--all' in sys.argv or not n.startswith('unconnected'):
            print(n, ' '.join(f'{r}.{p}' for r, p in nodes))
