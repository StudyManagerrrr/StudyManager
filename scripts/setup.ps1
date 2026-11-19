param([switch]$SkipInstall)
$ErrorActionPreference='Stop'
if (-not $SkipInstall) { python -m pip install -r backend/requirements.txt; npm install --prefix frontend }
Write-Host 'Dependencies ready. Local secrets remain in the root .env.'
