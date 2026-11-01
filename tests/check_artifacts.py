"""Check native dashboard connections and complete BOM reference uniqueness."""
import csv
import json
import re
from pathlib import Path

root=Path(__file__).resolve().parents[1]
doc=json.loads((root/'dashboard/environment-monitor.json').read_text(encoding='utf-8'))
config=doc['configuration']
widgets=config['widgets']
layout=config['states']['default']['layouts']['main']['widgets']
assert len(widgets)==11 and set(widgets)==set(layout)
aliases=config['entityAliases']
assert len(aliases)==1
alias=next(iter(aliases.values()))
assert alias['filter']['type']=='entityName' and alias['filter']['entityType']=='DEVICE'
assert alias['filter']['entityNameFilter']=='ENV-MONITOR-01'
data_names=set()
for widget in widgets.values():
    cfg=widget['config']
    for source in cfg.get('datasources',[]):
        assert source['type']=='entity' and source['entityAliasId'] in aliases
        data_names.update(item['name'] for item in source['dataKeys'])
    if 'alarmSource' in cfg:
        assert cfg['alarmSource']['entityAliasId'] in aliases
assert {'temperature','humidity','sensor_ok','time_ok','demo','temperature_min','temperature_max','humidity_min','humidity_max'}<=data_names
with (root/'hardware/BOM.csv').open(encoding='utf-8-sig',newline='') as stream:
    rows=list(csv.DictReader(stream))
refs=set()
for row in rows:
    names=row['Reference'].split(',')
    assert len(names)==int(row['Quantity']), row
    for name in names:
        assert name not in refs, name
        refs.add(name)
assert all(f'C{i}' in refs for i in [1,2,3,5,6,7,8,9,10,11,12,13])
assert {'R1','R2','R3','R4','R10'}<=refs
assert not {'Q1','Q2','SK3','R5','R6','R7','R8','R9','U3','Y2','BH1','SK2','C4'} & refs
assert any(row['Reference']=='U4' and 'TXS0108E' in row['Component'] for row in rows)
assert {'U1','U2','U4','U5','U6','Y1','SW1','SW2','J3','J5A','J5B'}<=refs
assert not (root/'firmware/esp32/include/secrets.h').exists(), 'Private secrets must not enter the deliverable'
print(f'PASS: {len(widgets)} widgets, aliases and telemetry keys; {len(refs)} unique BOM parts')
