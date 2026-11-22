"""Export schematic PDF, report renders and the fabrication package. Usage: export_release.py VERSION"""
import pathlib
import shutil
import subprocess
import sys
import zipfile

CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
ROOT = pathlib.Path(__file__).resolve().parents[2]
PCB_DIR = ROOT / "hardware/pcb"
SCH = PCB_DIR / "env-monitor.kicad_sch"
PCB = PCB_DIR / "env-monitor.kicad_pcb"
FIG = ROOT / "documents/bao-cao-do-an-2/figures"
VERSION = sys.argv[1]
OUT = ROOT / f"versions/pcb/env-monitor/v{VERSION}"
if OUT.exists():
    raise SystemExit(f"{OUT} already exists; delivered versions are never overwritten")
WORK = ROOT / f"sandbox/kicad/fab-v{VERSION}"
if WORK.exists():
    shutil.rmtree(WORK)
WORK.mkdir(parents=True)
LAYERS = "F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"


def run(*args):
    print(">", " ".join(args[:3]), flush=True)
    subprocess.run([CLI, *args], check=True, timeout=280)


run("sch", "erc", "--format", "json", "--severity-all", "--exit-code-violations",
    "--output", str(WORK / "erc.json"), str(SCH))
run("pcb", "drc", "--format", "json", "--schematic-parity", "--severity-all", "--exit-code-violations",
    "--output", str(WORK / "drc.json"), str(PCB))
run("sch", "export", "pdf", "--output", str(PCB_DIR / "env-monitor-schematic.pdf"), str(SCH))
shutil.copy2(PCB_DIR / "env-monitor-schematic.pdf", FIG / "so-do-nguyen-ly.pdf")
run("pcb", "render", "--output", str(FIG / "pcb-top.png"), "--width", "1960", "--height", "1960",
    "--side", "top", "--quality", "high", "--background", "opaque", "--zoom", "0.92", str(PCB))
run("pcb", "render", "--output", str(FIG / "pcb-3d.png"), "--width", "1960", "--height", "1456",
    "--side", "top", "--quality", "high", "--background", "opaque", "--perspective",
    "--rotate", "-45,0,-25", "--zoom", "0.9", str(PCB))

GERBER = WORK / "gerber"
GERBER.mkdir()
run("pcb", "export", "gerbers", "--output", str(GERBER), "--layers", LAYERS, "--no-x2", str(PCB))
run("pcb", "export", "drill", "--output", str(GERBER), "--format", "excellon",
    "--excellon-units", "mm", "--generate-map", "--map-format", "pdf", str(PCB))

OUT.mkdir(parents=True)
archive = OUT / f"env-monitor-gerber_v{VERSION}.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as package:
    for item in sorted(GERBER.iterdir()):
        package.write(item, item.name)
shutil.copy2(PCB_DIR / "env-monitor-schematic.pdf", OUT / f"env-monitor-schematic_v{VERSION}.pdf")
with zipfile.ZipFile(archive) as package:
    print("\n".join(package.namelist()))
print("wrote", archive)
