Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$postgresBin = "C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe"
$postgresData = "C:\Program Files\PostgreSQL\16\data"

Write-Host "[1/2] Verifying PostgreSQL..."
if (-not (Test-Path $postgresBin)) {
    throw "PostgreSQL 16 is not installed. Install PostgreSQL and ensure pg_ctl.exe exists at $postgresBin"
}

$pgService = Get-Service -Name "postgresql-x64-16" -ErrorAction SilentlyContinue
if ($pgService -and $pgService.Status -ne "Running") {
    Start-Service -Name "postgresql-x64-16"
}

if (-not $pgService) {
    & $postgresBin -D $postgresData -l "$postgresData\postgres.log" start
}

Write-Host "[2/2] Checking Grafana service..."
$grafanaService = Get-Service -Name "Grafana" -ErrorAction SilentlyContinue
if ($grafanaService) {
    if ($grafanaService.Status -ne "Running") {
        Start-Service -Name "Grafana"
    }
} else {
    Write-Host "Grafana is not installed as a Windows service. Start it manually from the Grafana application or installer."
}

Write-Host "Local services expected to be available:"
Write-Host " - PostgreSQL: localhost:5432"
Write-Host " - Grafana: http://localhost:3000"
Write-Host "No Grafana API key is required for local dashboard access."
