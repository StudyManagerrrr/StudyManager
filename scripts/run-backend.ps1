$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH="$root\backend"
Set-Location "$root\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765 --reload
