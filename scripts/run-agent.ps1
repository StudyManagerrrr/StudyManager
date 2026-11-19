$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH="$root\agent"
python "$root\agent\app\main.py"
