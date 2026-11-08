"""Check native dashboard connections and complete BOM reference uniqueness."""
import csv
import hashlib
import json
import re
from pathlib import Path

root=Path(__file__).resolve().parents[1]
doc=json.loads((root/'dashboard/environment-monitor.json').read_text(encoding='utf-8'))
config=doc['configuration']
widgets=config['widgets']
layout=config['states']['default']['layouts']['main']['widgets']
assert len(widgets)==12 and set(widgets)==set(layout)
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
assert {'temperature','humidity','sensor_ok','time_ok','demo','relay','temperature_min','temperature_max','humidity_min','humidity_max'}<=data_names
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
assert not {'Q2','SK3','R8','R9','U3','Y2','BH1','SK2','C4'} & refs
assert {'K1','Q1','R5','R6','R7','D3','J6','U7'} <= refs  # on-board relay driver and LM7805 supply
assert any(row['Reference']=='U4' and 'TXS0108E' in row['Component'] for row in rows)
assert {'U1','U2','U4','U5','U6','Y1','SW1','SW2','J3','J5A','J5B'}<=refs
assert not (root/'firmware/v0.2.0/esp32/include/secrets.h').exists(), 'Private secrets must not enter the deliverable'
print(f'PASS: {len(widgets)} widgets, aliases and telemetry keys; {len(refs)} unique BOM parts')

assert any(row['Reference']=='U1' and 'AT89S52' in row['Component'] for row in rows)
assert any('C2' in row['Reference'].split(',') and '10 µF' in row['Component'] for row in rows)

# The delivered image must be valid Intel HEX, fit AT89S52's 8KB, and match sources.
release=root/'firmware/v0.2.0/at89s52/release'
manifest=json.loads((release/'build-info.json').read_text())
hexfile=release/'environment-monitor.hex'
assert hashlib.sha256(hexfile.read_bytes()).hexdigest()==manifest['hex_sha256']
for name,digest in manifest['source_sha256'].items():
    assert hashlib.sha256((root/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==digest, name
addresses=set();eof=False
for line in hexfile.read_text().splitlines():
    assert line.startswith(':') and not eof
    record=bytes.fromhex(line[1:])
    size,high,low,kind=record[:4]
    assert len(record)==size+5 and sum(record)%256==0
    if kind==0:
        start=(high<<8)|low
        assert start+size<=8192
        for address in range(start,start+size):
            assert address not in addresses
            addresses.add(address)
    else:
        assert kind==1 and size==0
        eof=True
assert eof and addresses and min(addresses)==0
print(f'PASS: AT89S52 Intel HEX checksums, {len(addresses)} programmed bytes, source hashes')
