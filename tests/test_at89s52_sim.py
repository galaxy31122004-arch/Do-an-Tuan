"""Run compiled 8051 instructions in uCsim; no programmer or real hardware access.

OLED ACKs are simulator ROM stubs for display/stack tests only. Control frames
are injected into completed RX buffers, not through a physical UART receiver.
DHT tests drive P3.2 with timed external 26/70 us pulses.
"""
import argparse
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--s51', required=True)
parser.add_argument('--build-dir', type=Path, default=ROOT / 'firmware/at89s52/build')
args = parser.parse_args()
listing = (args.build_dir / 'main.rst').read_text()


def address(name):
    match = re.search(r'^\s*([0-9A-F]{6})\s+\d+ ' + re.escape(name) + r':', listing, re.M)
    return int(match[1], 16)


def put(memory, offset, data):
    return f'set memory {memory} {offset:#x} ' + ' '.join(f'{x:#x}' for x in data)


def run(commands):
    result = subprocess.run([args.s51, '-q', '-t', 'C52', '-X', '11059200',
                             os.path.relpath(args.build_dir / 'main.ihx', ROOT)], cwd=ROOT,
                            input='\n'.join(commands + ['state', 'quit']) + '\n',
                            text=True, capture_output=True, timeout=30)
    output = result.stdout + result.stderr
    assert result.returncode == 0 and 'Stack overflow' not in output, output[-3000:]
    peaks = re.findall(r'Most value of stack pointer= 0x([0-9a-f]+)', output)
    assert peaks and max(int(x, 16) for x in peaks) <= 0xF4, output[-3000:]
    return output, max(int(x, 16) for x in peaks)


def crc(text):
    value = 0
    for char in text.encode():
        value ^= char
        for _ in range(8):
            value = ((value << 1) ^ (7 if value & 128 else 0)) & 255
    return value


commands = [f'break {address("_control"):#x}', 'run 0']
for body in ['T,1793500000', 'S,1,1,1793499990']:
    frame = f'${body}*{crc(body):02X}'.encode() + b'\0'
    commands += [put('iram', address('_rx'), frame),
                 put('iram', address('_rx_ready'), [1]), 'step', 'run']
commands += [f'dump iram {address("_clock_mirror"):#x} {address("_clock_mirror") + 3:#x}']
for page in [0, 1]:
    # MOV DPL,#1; RET: emulate a connected OLED ACK without modelling I2C.
    for function in ['_i2c_start', '_i2c_write']:
        commands += [put('rom', address(function), [0x75, 0x82, 1, 0x22])]
    for name, data in [('_flags', b'\x03'), ('_page', bytes([page])),
                       ('_epoch', (1793500000).to_bytes(4, 'little')),
                       ('_temp', (253).to_bytes(2, 'little')),
                       ('_humidity', (651).to_bytes(2, 'little'))]:
        commands += [put('iram', address(name), data)]
    # At _control entry a valid main-loop return address is already on stack.
    commands += [f'pc {address("_screen"):#x}', 'run']
output, peak = run(commands)
assert re.search(r'0x[0-9a-f]+\s+60 a3 e6 6a', output), 'UTC mirror was not updated'
print(f'PASS: S/T parsing, both OLED pages; simulated stack peak {peak:#x}')

data = bytes([65, 0, 25, 0, 90])
for short, long in [(26, 70), (22, 65), (30, 75)]:
    commands = [f'break {address("_control"):#x}', 'run 0',
                f'pc {address("_dht_capture"):#x}', 'set memory sfr 0xa8 0x80',
                'step 20 us', 'set hw port[3] 0xfb', 'step 80 us',
                'set hw port[3] 0xff', 'step 80 us', 'set hw port[3] 0xfb']
    for byte in data:
        for bit in range(7, -1, -1):
            commands += ['step 50 us', 'set hw port[3] 0xff',
                         f'step {long if byte & (1 << bit) else short} us',
                         'set hw port[3] 0xfb']
    commands += ['step 80 us',
                 f'dump iram {address("_dht_bytes"):#x} {address("_dht_bytes") + 4:#x}']
    output, peak = run(commands)
    assert re.search(r'0x[0-9a-f]+\s+41 00 19 00 5a', output), output[-3000:]
    print(f'PASS: DHT11 {short}/{long} us pulses, all 40 bits decoded')
