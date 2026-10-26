# Arduino Starter — Upload & Monitor

Lille Windows-desktopapp der efterligner PlatformIO’s **Upload and Monitor**.

## Krav

- Python 3.11+
- PlatformIO CLI (`pio` / `platformio`) installeret
- USB-board (fx MKR WiFi 1010)

## Start

```powershell
cd Hardwaretestere/ArduinoStarter
python -m pip install -r requirements.txt
python app.py
```

1. Vælg en mappe med `platformio.ini`
2. Vælg environment og COM-port
3. **Upload & Monitor**

Luk monitor (**Stop monitor**) før du uploader igen, hvis porten er optaget.
