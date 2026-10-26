# Arduino Starter — Upload & Monitor

Windows-desktopapp der efterligner PlatformIO **Upload and Monitor**, plus værksteds-værktøjer.

## Hent .exe (elever)

[**Download ArduinoStarter-win64.zip**](https://github.com/Mercantech/Arduino-Opla/raw/main/Hardwaretestere/ArduinoStarter/release/ArduinoStarter-win64.zip)

1. Pak zip’en ud
2. Dobbeltklik `ArduinoStarter.exe`
3. **PlatformIO CLI** skal være installeret på PC’en (appen kalder `pio`)

## Start (udvikler)

```powershell
cd Hardwaretestere/ArduinoStarter
.\Start.ps1
```

Eller dobbeltklik `Start.bat`.

### Byg .exe selv

```powershell
cd Hardwaretestere/ArduinoStarter
.\build_exe.ps1
```

Kør `dist\ArduinoStarter\ArduinoStarter.exe`, eller opdatér zip’en i `release\` før commit.
## Funktioner

| Knap | Handling |
|------|----------|
| **Favoritter** | Genveje til HardwareTest m.fl. (`+ Favorit` / `− Favorit`) |
| **Upload** / **Monitor** / **Upload & Monitor** | Som PlatformIO |
| **Auto** | Vælg Arduino/MKR-port (ignorer Bluetooth) |
| **Build** / **Clean** / **Rebuild** | Compile / clean |
| **NINA + SSL** | `Update-Device.ps1 -SkipSketch` |
| **Secrets…** | Redigér projektets secrets (`secrets.h` / `Secrets.h`) — læser makroer fra `.example` (fx `SECRET_SSID` eller `WIFI_SSID`) |
| **Gem log** | Eksporter log til `.txt` |
| **dark / light** + **Font** | Projektor-venlig visning |

Log farver automatisk **grøn** (OK/SUCCESS), **rød** (FEJL/FAIL) og **blå** (Test-opsummering).

Upload blokeres hvis `Secrets.h` mangler eller SSID er placeholder.
