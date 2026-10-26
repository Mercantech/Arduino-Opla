#Requires -Version 5.1
<#
.SYNOPSIS
  Bygger ArduinoStarter.exe med PyInstaller (windowed).
#>
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

function Find-Python {
  $candidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
  )
  foreach ($c in $candidates) {
    if (Test-Path $c) { return $c }
  }
  return $null
}

$py = Find-Python
if (-not $py) {
  Write-Host "Python ikke fundet." -ForegroundColor Red
  exit 1
}

Write-Host "Python: $py"
& $py -m pip install -r (Join-Path $Root "requirements.txt") -q
& $py -m pip install "pyinstaller>=6.0" -q

$dist = Join-Path $Root "dist"
$work = Join-Path $Root "build"
Set-Location $Root

& $py -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --name "ArduinoStarter" `
  --paths $Root `
  --collect-all customtkinter `
  --hidden-import serial `
  --hidden-import serial.tools.list_ports `
  --hidden-import log_style `
  --hidden-import pio_runner `
  --hidden-import secrets_editor `
  --hidden-import serial_monitor `
  --distpath $dist `
  --workpath $work `
  (Join-Path $Root "app.py")

if ($LASTEXITCODE -ne 0) {
  Write-Host "PyInstaller fejlede" -ForegroundColor Red
  exit $LASTEXITCODE
}

$exe = Join-Path $dist "ArduinoStarter\ArduinoStarter.exe"
if (-not (Test-Path $exe)) {
  # one-folder vs onefile layout
  $alt = Join-Path $dist "ArduinoStarter.exe"
  if (Test-Path $alt) { $exe = $alt }
}

Write-Host ""
Write-Host "Faerdig: $exe" -ForegroundColor Green
Write-Host "Elever kan dobbeltklikke exe. PlatformIO skal stadig vaere installeret."
