$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
Set-Location "$root\frontend"
npm run dev -- --host 127.0.0.1
