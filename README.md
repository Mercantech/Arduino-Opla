# Arduino-Opla

Kodeeksempler og hardware-tester til Arduino Oplà (MKR WiFi 1010 + MKR IoT Carrier).

## Arduino Starter (Upload & Monitor)

Desktop-app (Python) der efterligner PlatformIO **Upload and Monitor** — vælg et hvilket som helst PIO-projekt:

```powershell
cd Hardwaretestere/ArduinoStarter
.\Start.ps1
# eller dobbeltklik Start.bat
# Elev-.exe: .\build_exe.ps1  →  dist\ArduinoStarter\ArduinoStarter.exe
```

Appen har favoritter, farvet OK/FEJL-log, dark/light + stor font, Secrets-editor, Build/Clean og NINA+SSL.

## HardwareTest (PlatformIO)

```bash
cd Hardwaretestere/HardwareTest
pio run -e mkrwifi1010
pio run -e mkrwifi1010 -t upload
pio device monitor
```

Tester OLED, sensorer (temp/fugt, tryk, IMU accel+gyro), SD, relæ, knapper, LED, buzzer — og udskriver SAMD chip-ID, WiFi MAC og ECCX08-serienummer. (RGB/Prox er fjernet — ustabil med kabinet.)

Efter tests registrerer/opdaterer boardet sig selv på API’et (`POST /api/devices` på SAMD-ID) og gemmer testrapporten.

```bash
cd Hardwaretestere/HardwareTest
cp src/Secrets.h.example src/Secrets.h
# Udfyld WIFI_SSID og WIFI_PASSWORD
```

Lyd: `ENABLE_SOUND_TEST` i `src/Hardwaretestere.h`. API-upload: `ENABLE_API_REPORT`.

## Opdater NINA + SSL (enheder)

Luk Serial Monitor, tilslut MKR WiFi 1010, og kør:

```powershell
cd Hardwaretestere
.\Update-Device.ps1              # auto-port, nyeste NINA, certs, HardwareTest
.\Update-Device.ps1 -Port COM8
.\Update-Device.ps1 -ListOnly    # se firmwareversioner + porte
.\Update-Device.ps1 -SkipSketch  # kun NINA + SSL-certifikater
```

Scriptet henter `arduino-fwuploader`, flasher nyeste NINA-firmware, SSL-rodcertifikater (`opla.mercantec.tech` m.fl.) og uploader HardwareTest.

## Web API (opla.mercantec.tech)

Hurtig FastAPI + Postgres + Nginx:

- `GET /health` / `GET /api/health`
- `GET|POST /api/devices`
- `POST /api/devices/{id}/tests`

Lokalt:

```bash
cp .env.example .env
# sæt POSTGRES_PASSWORD
docker compose -f docker-compose.yml -f docker-compose.local.yml up --build
```

Åbn http://localhost:3000

## Dokumentation

[MKR IoT Carrier Technical Reference](https://docs.arduino.cc/tutorials/mkr-iot-carrier/mkr-iot-carrier-01-technical-reference)
