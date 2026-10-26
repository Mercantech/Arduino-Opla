# Arduino Starter — Upload & Monitor

Windows-desktopapp der efterligner PlatformIO **Upload and Monitor**, plus værksteds-værktøjer.

## Start (udvikler)

```powershell
cd Hardwaretestere/ArduinoStarter
.\Start.ps1
```

Eller dobbeltklik `Start.bat`.

## Start (elever — .exe)

```powershell
cd Hardwaretestere/ArduinoStarter
.\build_exe.ps1
```

Kør derefter `dist\ArduinoStarter\ArduinoStarter.exe`.  
**PlatformIO CLI skal stadig være installeret** på PC’en (appen kalder `pio`).

## Funktioner

| Knap | Handling |
|------|----------|
| **Favoritter** | Genveje til HardwareTest m.fl. (`+ Favorit` / `− Favorit`) |
| **Upload** / **Monitor** / **Upload & Monitor** | Som PlatformIO |
| **Auto** | Vælg Arduino/MKR-port (ignorer Bluetooth) |
| **Build** / **Clean** / **Rebuild** | Compile / clean |
| **NINA + SSL** | `Update-Device.ps1 -SkipSketch` |
| **Secrets…** | Redigér WiFi i `Secrets.h` |
| **Gem log** | Eksporter log til `.txt` |
| **dark / light** + **Font** | Projektor-venlig visning |

Log farver automatisk **grøn** (OK/SUCCESS), **rød** (FEJL/FAIL) og **blå** (Test-opsummering).

Upload blokeres hvis `Secrets.h` mangler eller SSID er placeholder.
