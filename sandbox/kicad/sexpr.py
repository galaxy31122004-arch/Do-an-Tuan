"""Minimal S-expression reader/writer for KiCad files."""
import re

TOKEN = re.compile(r'\s*(?:(\()|(\))|("(?:[^"\\]|\\.)*")|([^\s()]+))')


class Sym(str):
    """Bare atom (unquoted)."""


def parse(text):
    stack, cur = [], []
    for m in TOKEN.finditer(text):
        lp, rp, s, a = m.groups()
        if lp:
            stack.append(cur); cur = []
        elif rp:
            done = cur; cur = stack.pop(); cur.append(done)
        elif s is not None:
            cur.append(s[1:-1].replace('\\"', '"').replace('\\\\', '\\'))
        elif a is not None:
            cur.append(Sym(a))
    return cur[0]


def dump(node, indent=0):
    if isinstance(node, list):
        if not node:
            return '()'
        simple = all(not isinstance(x, list) for x in node)
        if simple:
            return '(' + ' '.join(dump(x) for x in node) + ')'
        pad = '\t' * (indent + 1)
        parts = [dump(node[0])]
        for x in node[1:]:
            parts.append('\n' + pad + dump(x, indent + 1) if isinstance(x, list) else ' ' + dump(x))
        return '(' + ''.join(parts) + '\n' + '\t' * indent + ')'
    if isinstance(node, Sym):
        return str(node)
    if isinstance(node, (int, float)):
        return fmt(node)
    return '"' + str(node).replace('\\', '\\\\').replace('"', '\\"') + '"'


def fmt(v):
    v = round(float(v), 4)
    return str(int(v)) if v == int(v) else ('%.4f' % v).rstrip('0').rstrip('.')


def find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def first(node, key):
    r = find(node, key)
    return r[0] if r else None
