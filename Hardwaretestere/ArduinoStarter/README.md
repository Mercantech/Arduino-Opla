# Arduino Starter — Upload & Monitor

Lille Windows-desktopapp der efterligner PlatformIO’s **Upload and Monitor**, plus værksteds-værktøjer.

## Krav

- Python 3.11+
- PlatformIO CLI (`pio` / `platformio`)
- USB-board (fx MKR WiFi 1010)

## Start

Dobbeltklik **`Start.bat`**, eller:

```powershell
cd Hardwaretestere/ArduinoStarter
.\Start.ps1
```

## Funktioner

| Knap | Handling |
|------|----------|
| **Upload** / **Monitor** / **Upload & Monitor** | Som PlatformIO |
| **Stop monitor** | Frigør COM-port |
| **Auto** | Vælg bedste Arduino/MKR-port (ignorer Bluetooth) |
| **Build** | `pio run` (compile only) |
| **Clean** / **Rebuild** | `pio run -t clean` (+ build) |
| **NINA + SSL** | Kører `../Update-Device.ps1 -Port COMx -SkipSketch` |
| **Secrets…** | Redigér `src/Secrets.h` (WiFi SSID/password) |
| **Gem log** | Gem log-vindue til `.txt` |

Upload **blokeres**, hvis `Secrets.h` mangler eller SSID er tom/placeholder — appen kan oprette filen fra `Secrets.h.example`.

Luk monitor (**Stop monitor**) før upload/NINA, hvis porten er optaget.
