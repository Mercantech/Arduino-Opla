#Requires -Version 5.1
<#
.SYNOPSIS
  Opdaterer Arduino MKR WiFi 1010 (Opla) til nyeste NINA-firmware + SSL-rodcertifikater.

.DESCRIPTION
  1) Henter arduino-fwuploader (hvis mangler)
  2) Frigør COM-port (lukker PlatformIO Serial Monitor o.l.)
  3) Flasher NINA-firmware (default: nyeste)
  4) Flasher SSL-rodcertifikater til opla.mercantec.tech m.fl.
  5) (valgfrit) Uploader HardwareTest-sketch via PlatformIO

.EXAMPLE
  .\Update-Device.ps1
  .\Update-Device.ps1 -Port COM8
  .\Update-Device.ps1 -Port COM8 -Firmware "NINA@1.5.0"
  .\Update-Device.ps1 -SkipSketch
  .\Update-Device.ps1 -CertUrl "opla.mercantec.tech:443","www.google.com:443"
#>
[CmdletBinding()]
param(
  [string] $Port,
  [string] $Firmware = "",                 # tom = nyeste (fwuploader uden -m)
  [string[]] $CertUrl = @(
    "opla.mercantec.tech:443",
    "www.google.com:443",
    "arduino.cc:443"
  ),
  [string] $Fqbn = "arduino:samd:mkrwifi1010",
  [string] $PioEnv = "mkrwifi1010",
  [switch] $SkipFirmware,
  [switch] $SkipCerts,
  [switch] $SkipSketch,                    # default: upload HardwareTest efter update
  [switch] $ListOnly,                      # list firmware + porte, flash ikke
  [int] $Retries = 9
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
$HardwareTestDir = Join-Path $ScriptRoot "HardwareTest"
$ToolDir = Join-Path $env:LOCALAPPDATA "ArduinoOpla\fwuploader"
$FwUploader = Join-Path $ToolDir "arduino-fwuploader.exe"

function Write-Step([string] $Message) {
  Write-Host ""
  Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Ok([string] $Message) {
  Write-Host "    OK  $Message" -ForegroundColor Green
}

function Write-Warn([string] $Message) {
  Write-Host "    !   $Message" -ForegroundColor Yellow
}

function Get-PlatformIo {
  $candidates = @(
    (Join-Path $env:USERPROFILE ".platformio\penv\Scripts\platformio.exe"),
    (Join-Path $env:USERPROFILE ".platformio\penv\Scripts\pio.exe")
  )
  foreach ($c in $candidates) {
    if (Test-Path $c) { return $c }
  }
  $cmd = Get-Command platformio, pio -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($cmd) { return $cmd.Source }
  return $null
}

function Ensure-FwUploader {
  if (Test-Path $FwUploader) {
    Write-Ok "fwuploader: $FwUploader"
    return
  }

  Write-Step "Henter arduino-fwuploader (seneste release)"
  New-Item -ItemType Directory -Force -Path $ToolDir | Out-Null

  $release = Invoke-RestMethod -Uri "https://api.github.com/repos/arduino/arduino-fwuploader/releases/latest" -Headers @{
    "User-Agent" = "Arduino-Opla-Update-Device"
  }
  $asset = $release.assets | Where-Object { $_.name -match "Windows_64bit\.zip$" } | Select-Object -First 1
  if (-not $asset) {
    throw "Kunne ikke finde Windows_64bit.zip i fwuploader-release."
  }

  $zipPath = Join-Path $env:TEMP "arduino-fwuploader.zip"
  $extractDir = Join-Path $env:TEMP "arduino-fwuploader-extract"
  Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipPath -UseBasicParsing
  if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
  Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force

  $exe = Get-ChildItem -Path $extractDir -Recurse -Filter "arduino-fwuploader.exe" | Select-Object -First 1
  if (-not $exe) { throw "arduino-fwuploader.exe ikke fundet i zip." }
  Copy-Item $exe.FullName -Destination $FwUploader -Force
  Write-Ok "Installeret $($release.tag_name) -> $FwUploader"
}

function Free-SerialPort([string] $ComPort) {
  Write-Step "Frigør $ComPort (lukker Serial Monitor / PIO monitor)"
  $killed = 0

  # PlatformIO device monitor holder ofte porten
  Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
      $_.Name -match '^(python|platformio|pio|pythonw)\.exe$' -and
      $_.CommandLine -match 'device monitor|serial'
    } |
    ForEach-Object {
      try {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop
        $killed++
        Write-Warn "Stoppede PID $($_.ProcessId): $($_.Name)"
      } catch { }
    }

  # Arduino IDE Serial Monitor / java kan også låse
  Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
      $_.Name -match '^(java|arduino-cli)\.exe$' -and
      $_.CommandLine -match $ComPort
    } |
    ForEach-Object {
      try {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop
        $killed++
        Write-Warn "Stoppede PID $($_.ProcessId) (brugte $ComPort)"
      } catch { }
    }

  Start-Sleep -Seconds 1
  if ($killed -eq 0) {
    Write-Ok "Ingen monitor-processer fundet"
  } else {
    Write-Ok "Frigjorde $killed proces(ser)"
  }
}

function Get-MkrComPorts {
  $ports = @()

  # Prefer PlatformIO device list when available
  $pio = Get-PlatformIo
  if ($pio) {
    try {
      $json = & $pio device list --json-output 2>$null | Out-String
      if ($json) {
        $devices = $json | ConvertFrom-Json
        foreach ($d in $devices) {
          $desc = "$($d.description) $($d.hwid) $($d.port)"
          if ($desc -match 'MKR|Arduino|2341|USB Serial Device|COM\d+') {
            if ($d.port) { $ports += $d.port }
          }
        }
      }
    } catch { }
  }

  # Fallback: Win32 serial ports
  Get-CimInstance Win32_SerialPort -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.DeviceID -match '^COM\d+$') {
      $ports += $_.DeviceID
    }
  }

  # Fallback: registry mode names
  try {
    $mode = Get-ItemProperty -Path "HKLM:\HARDWARE\DEVICEMAP\SERIALCOMM" -ErrorAction Stop
    $mode.PSObject.Properties | Where-Object { $_.Name -notlike 'PS*' } | ForEach-Object {
      if ($_.Value -match '^COM\d+$') { $ports += $_.Value }
    }
  } catch { }

  $ports | Select-Object -Unique | Sort-Object {
    if ($_ -match 'COM(\d+)') { [int]$Matches[1] } else { 999 }
  }
}

function Resolve-Port {
  param([string] $Requested)

  if ($Requested) {
    $normalized = $Requested.ToUpperInvariant()
    if ($normalized -notmatch '^COM\d+$') {
      throw "Ugyldig port: $Requested (forventet COMx)"
    }
    return $normalized
  }

  $ports = @(Get-MkrComPorts)
  if ($ports.Count -eq 0) {
    throw "Ingen COM-port fundet. Tilslut MKR WiFi 1010 og prøv igen, eller angiv -Port COMx."
  }
  if ($ports.Count -eq 1) {
    Write-Ok "Auto-valgt port: $($ports[0])"
    return $ports[0]
  }

  Write-Host "Flere COM-porte fundet:" -ForegroundColor Yellow
  for ($i = 0; $i -lt $ports.Count; $i++) {
    Write-Host ("  [{0}] {1}" -f $i, $ports[$i])
  }
  $choice = Read-Host "Vælg port-nummer"
  if ($choice -notmatch '^\d+$' -or [int]$choice -ge $ports.Count) {
    throw "Ugyldigt valg."
  }
  return $ports[[int]$choice]
}

function Show-FirmwareList {
  Write-Step "Tilgængelige NINA-firmwareversioner"
  & $FwUploader firmware list -b $Fqbn
}

function Invoke-FwFlash([string] $ComPort) {
  Write-Step "Flasher NINA-firmware ($(if ($Firmware) { $Firmware } else { 'nyeste' }))"
  $args = @(
    "firmware", "flash",
    "-b", $Fqbn,
    "-a", $ComPort,
    "--retries", "$Retries"
  )
  if ($Firmware) {
    $args += @("-m", $Firmware)
  }
  & $FwUploader @args
  if ($LASTEXITCODE -ne 0) {
    throw "Firmware flash fejlede (exit $LASTEXITCODE). Luk Serial Monitor og prøv igen."
  }
  Write-Ok "Firmware flash fuldført"
}

function Invoke-CertFlash([string] $ComPort) {
  Write-Step "Flasher SSL-rodcertifikater"
  foreach ($u in $CertUrl) { Write-Host "    - $u" }

  $args = @(
    "certificates", "flash",
    "-b", $Fqbn,
    "-a", $ComPort
  )
  foreach ($u in $CertUrl) {
    $args += @("-u", $u)
  }
  & $FwUploader @args
  if ($LASTEXITCODE -ne 0) {
    throw "Certificate flash fejlede (exit $LASTEXITCODE)."
  }
  Write-Ok "Certifikater flash fuldført"
}

function Invoke-SketchUpload {
  Write-Step "Uploader HardwareTest (PlatformIO)"
  if (-not (Test-Path $HardwareTestDir)) {
    throw "HardwareTest-mappe mangler: $HardwareTestDir"
  }
  $pio = Get-PlatformIo
  if (-not $pio) {
    throw "PlatformIO ikke fundet. Installér PlatformIO eller kør med -SkipSketch."
  }

  Push-Location $HardwareTestDir
  try {
    & $pio run -e $PioEnv -t upload
    if ($LASTEXITCODE -ne 0) {
      throw "Sketch upload fejlede (exit $LASTEXITCODE)."
    }
  } finally {
    Pop-Location
  }
  Write-Ok "HardwareTest uploadet"
}

# --- main ---
Write-Host "Arduino Opla / MKR WiFi 1010 — device update" -ForegroundColor White
Write-Host "FQBN: $Fqbn"

Ensure-FwUploader

if ($ListOnly) {
  Show-FirmwareList
  Write-Step "COM-porte"
  Get-MkrComPorts | ForEach-Object { Write-Host "  $_" }
  exit 0
}

$com = Resolve-Port -Requested $Port
Free-SerialPort -ComPort $com

if (-not $SkipFirmware) {
  Invoke-FwFlash -ComPort $com
  Start-Sleep -Seconds 2
  Free-SerialPort -ComPort $com
} else {
  Write-Warn "Springer firmware over (-SkipFirmware)"
}

if (-not $SkipCerts) {
  Invoke-CertFlash -ComPort $com
  Start-Sleep -Seconds 2
  Free-SerialPort -ComPort $com
} else {
  Write-Warn "Springer certifikater over (-SkipCerts)"
}

if (-not $SkipSketch) {
  Invoke-SketchUpload
} else {
  Write-Warn "Springer sketch over (-SkipSketch). Boardet har updater-sketch indtil du uploader igen."
}

Write-Host ""
Write-Host "Færdig. Åbn Serial Monitor og tjek:" -ForegroundColor Green
Write-Host "  API: NINA firmware=..."
Write-Host "  API: SSL-probe www.google.com:443 ... OK"
Write-Host "  API: SSL-probe opla.mercantec.tech:443 ... OK"
Write-Host ""
Write-Host "Tip: Luk altid Serial Monitor før næste update (scriptet forsøger at frigøre porten)."
