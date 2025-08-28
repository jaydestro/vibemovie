param(
    [int]$TimeoutSeconds = 90
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[emulator] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[emulator] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[emulator] $msg" -ForegroundColor Red }

Write-Info "Checking Docker..."
docker --version | Out-Null

$name = 'cosmos-emulator'
$image = 'mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest'
$keyFileHost = Join-Path $PSScriptRoot '..' | Join-Path -ChildPath 'emulator-key.txt'
$keyValue = 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9K0HB4Q=='
if (-not (Test-Path $keyFileHost)) {
    Set-Content -LiteralPath $keyFileHost -Value $keyValue -NoNewline -Encoding ascii
}

$exists = docker ps -a --format "{{.Names}}" | Where-Object { $_ -eq $name }
if (-not $exists) {
    Write-Info "Pulling image: $image"
    docker pull $image | Out-Null
    Write-Info "Creating and starting container: $name (https, pinned key)"
    docker run --name $name `
        -p 8081:8081 -p 10251:10251 -p 10252:10252 -p 10253:10253 -p 10254:10254 `
        --mount type=bind,source="$keyFileHost",target="/emukey" `
        --memory=3g -d $image --protocol https --key-file /emukey | Out-Null
} else {
    $running = docker ps --format "{{.Names}}" | Where-Object { $_ -eq $name }
    if (-not $running) {
        Write-Info "Starting existing container: $name"
        docker start $name | Out-Null
    } else {
        Write-Info "Container already running: $name"
    }
}

# Wait for HTTPS endpoint to be ready
Write-Info "Waiting for emulator on https://localhost:8081/ ..."
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$ready = $false
while(-not $ready -and (Get-Date) -lt $deadline) {
    try {
    # -k: allow insecure (self-signed) during readiness probe only
    $resp = curl.exe -k -sS -m 3 https://localhost:8081/_explorer/emulator.pem
        if ($LASTEXITCODE -eq 0 -and $resp) { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 2
}

if (-not $ready) {
    Write-Err "Emulator did not become ready within $TimeoutSeconds seconds"
    exit 1
}

Write-Info "Emulator is ready on https://localhost:8081/"
