$ErrorActionPreference = 'Stop'

& "$PSScriptRoot\start-cosmos-emulator.ps1" -TimeoutSeconds 90

$env:PORT = if ($env:PORT) { $env:PORT } else { "3000" }
if (-not $env:PYTHONHTTPSVERIFY) { $env:PYTHONHTTPSVERIFY = "0" }
# Optional: set offline mode for fast demo without emulator dependency
# Uncomment the next line for live talks to avoid connectivity flakiness
# $env:USE_INMEMORY = "1"
Write-Host "[app] Starting Flask on port $env:PORT" -ForegroundColor Green

& "$PSScriptRoot\..\.venv\Scripts\python.exe" "$PSScriptRoot\..\app.py"
