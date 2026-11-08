param([string]$SdccPath = 'sdcc', [string]$Python = 'python')
$ErrorActionPreference = 'Stop'
& $Python -X utf8 "$PSScriptRoot/build.py" --sdcc $SdccPath
if ($LASTEXITCODE -ne 0) { throw 'AT89S52 build failed; do not use an older HEX.' }
