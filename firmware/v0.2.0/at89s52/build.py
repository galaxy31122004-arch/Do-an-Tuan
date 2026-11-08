"""Build the AT89S52 image with SDCC; keep reproducible source/HEX evidence."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sdcc', default='sdcc')
    args = parser.parse_args()
    compiler = Path(shutil.which(args.sdcc) or args.sdcc).resolve()
    build = HERE / 'build'
    release = HERE / 'release'
    build.mkdir(exist_ok=True)
    release.mkdir(exist_ok=True)
    flags = ['-mmcs51', '--std-c99', '--opt-code-size', '--iram-size', '256',
             '--code-size', '8192', '--out-fmt-ihx']
    image = build / 'main.ihx'
    # A failed link must never package a previous successful image.
    image.unlink(missing_ok=True)
    subprocess.run([str(compiler), *flags, '-o', str(image), str(HERE / 'main.c')], check=True)
    memory = (build / 'main.mem').read_text()
    if 'ERROR' in memory or 'Couldn\'t' in memory:
        raise RuntimeError('Memory allocation failed')
    packed = subprocess.run([str(compiler.with_name('packihx' + compiler.suffix)), str(image)],
                            check=True, capture_output=True)
    hexfile = release / 'environment-monitor.hex'
    hexfile.write_bytes(packed.stdout.replace(b'\r\n', b'\n'))
    (release / 'memory.txt').write_text(memory, encoding='utf-8')
    sources = [HERE / 'main.c', HERE / 'board.h', HERE / 'build.py',
               HERE.parent / 'common/protocol.h', HERE.parent / 'common/clock.h']
    libraries = compiler.parent.parent / 'lib/small'
    info = {
        'target': 'AT89S52 DIP40, 11.0592 MHz, classic 12T, no external RAM',
        'compiler': subprocess.check_output([str(compiler), '--version'], text=True).strip(),
        'compiler_sha256': sha(compiler), 'flags': flags,
        'runtime_origin': 'SDCC 4.5.0 official mcs51 small libraries (RSCH-20261101-0012)',
        'library_sha256': {p.name: sha(p) for p in sorted(libraries.glob('*.lib'))},
        'source_hash_format': 'UTF-8 file bytes, CRLF normalized to LF',
        'source_sha256': {p.relative_to(ROOT).as_posix():
                          hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                          for p in sources},
        'hex_sha256': sha(hexfile),
        'hardware_verify': 'Not performed; user will Verify with Burn-E',
    }
    (release / 'build-info.json').write_text(json.dumps(info, indent=2) + '\n', encoding='utf-8')
    print(hexfile)


if __name__ == '__main__':
    main()
