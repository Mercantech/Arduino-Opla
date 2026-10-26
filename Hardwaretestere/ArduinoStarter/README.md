# Arduino Starter — Upload & Monitor

Lille Windows-desktopapp der efterligner PlatformIO’s **Upload and Monitor**.

## Krav

- Python 3.11+
- PlatformIO CLI (`pio` / `platformio`) installeret
- USB-board (fx MKR WiFi 1010)

## Start

Dobbeltklik **`Start.bat`**, eller i PowerShell:

```powershell
cd Hardwaretestere/ArduinoStarter
.\Start.ps1
```

`python` virker ofte ikke i Windows-terminal (Store-alias / mangler PATH). Scriptet finder selv Python 3.11+ under `%LOCALAPPDATA%\Programs\Python\`.

Manuelt (fuld sti):

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" -m pip install -r requirements.txt
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" app.py
```

1. Vælg en mappe med `platformio.ini`
2. Vælg environment og COM-port
3. **Upload & Monitor**

Luk monitor (**Stop monitor**) før du uploader igen, hvis porten er optaget.
