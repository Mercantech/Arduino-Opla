#Requires -Version 5.1
<#
.SYNOPSIS
  Starter Arduino Starter (Upload & Monitor). Finder Python 3.11+ automatisk.
#>
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

function Find-Python {
  $candidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "$env:USERPROFILE\.platformio\python3\python.exe"
  )
  foreach ($c in $candidates) {
    if ($c -and (Test-Path $c)) { return $c }
  }
  foreach ($name in @("py", "python3", "python")) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue |
      Where-Object { $_.Source -notmatch "WindowsApps" } |
      Select-Object -First 1
    if ($cmd) { return $cmd.Source }
  }
  return $null
}

$py = Find-Python
if (-not $py) {
  Write-Host "Python ikke fundet." -ForegroundColor Red
  Write-Host "Installér Python 3.11+ fra https://www.python.org/downloads/"
  Write-Host "Sæt kryds i 'Add python.exe to PATH' under installation."
  exit 1
}

Write-Host "Python: $py" -ForegroundColor Cyan
& $py -m pip install -r (Join-Path $Root "requirements.txt") -q
if ($LASTEXITCODE -ne 0) {
  Write-Host "pip install fejlede" -ForegroundColor Red
  exit $LASTEXITCODE
}

Set-Location $Root
& $py (Join-Path $Root "app.py")
exit $LASTEXITCODE
