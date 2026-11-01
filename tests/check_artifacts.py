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
assert {'temperature','humidity','sensor_ok','rtc_ok','demo','temperature_min','temperature_max','humidity_min','humidity_max'}<=data_names
with (root/'hardware/BOM.csv').open(encoding='utf-8-sig',newline='') as stream:
    rows=list(csv.DictReader(stream))
refs=set()
for row in rows:
    names=row['Reference'].split(',')
    assert len(names)==int(row['Quantity']), row
    for name in names:
        assert name not in refs, name
        refs.add(name)
assert all(f'C{i}' in refs for i in range(1,13))
assert all(f'R{i}' in refs for i in range(1,11))
assert {'U1','U2','U3','U4','U5','U6','Q1','Q2','Y1','Y2','BH1','SW1','SW2','J3'}<=refs
assert not (root/'firmware/esp32/include/secrets.h').exists(), 'Private secrets must not enter the deliverable'
print(f'PASS: {len(widgets)} widgets, aliases and telemetry keys; {len(refs)} unique BOM parts')
