param([string]$Net, [string]$Layer, [string]$Width, [string[]]$Pts)
# Add a track, run DRC; keep it only if it adds no clearance/short/hole errors. Prints the unconnected count.
$pcb = "D:\Randombullsheet\Do-an-Tuan\hardware\pcb\env-monitor.kicad_pcb"
$cli = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"; $py = "C:\Program Files\KiCad\10.0\bin\python.exe"
$bak = "$env:TEMP\pcb_try.kicad_pcb"; Copy-Item $pcb $bak -Force
& $py D:\Randombullsheet\Do-an-Tuan\sandbox\kicad\add_track.py $Net $Layer $Width @Pts 2>&1 | Out-Null
& $cli pcb drc -o "$env:TEMP\try.rpt" $pcb | Out-Null
$bad = Select-String -Path "$env:TEMP\try.rpt" -Pattern '^\[(clearance|shorting_items|hole_clearance|copper_edge_clearance|tracks_crossing)'
$unc = (Select-String -Path "$env:TEMP\try.rpt" -Pattern 'Found (\d+) unconnected').Matches[0].Groups[1].Value
if ($bad) { Copy-Item $bak $pcb -Force; "REVERTED ($($bad.Count) errors): " + (($bad | ForEach-Object { $_.Line.Substring(0, [Math]::Min(60, $_.Line.Length)) }) -join '; ') }
else { "KEPT; unconnected now $unc" }
