"""Print pin offsets (lib coords, y up) of every symbol embedded in the schematic."""
import sys
from pathlib import Path
from sexpr import parse, find, first

sch = parse(Path(sys.argv[1]).read_text(encoding='utf-8'))
for sym in find(first(sch, 'lib_symbols'), 'symbol'):
    print(sym[1])
    def walk(n):
        for x in n:
            if isinstance(x, list) and x and x[0] == 'pin':
                at = first(x, 'at'); num = first(x, 'number')[1]; name = first(x, 'name')[1]
                print(f'   {num:>3} {name:<12} at {float(at[1]):8.2f} {float(at[2]):8.2f} ang {at[3] if len(at) > 3 else 0}')
            elif isinstance(x, list):
                walk(x)
    walk(sym)
