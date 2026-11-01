param([string]$Compiler = 'xc8-cc')
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force -Path "$PSScriptRoot/build" | Out-Null
& $Compiler '-mcpu=16F877A' '-O2' '-std=c99' "-o$PSScriptRoot/build/environment.elf" "$PSScriptRoot/main.c"
if ($LASTEXITCODE -ne 0) { throw 'XC8 build failed' }
