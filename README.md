# Arduino-Opla

Kodeeksempler og hardware-tester til Arduino Oplà (MKR WiFi 1010 + MKR IoT Carrier).

## HardwareTest (PlatformIO)

```bash
cd Hardwaretestere/HardwareTest
pio run -e mkrwifi1010
pio run -e mkrwifi1010 -t upload
pio device monitor
```

Tester OLED, sensorer (temp/fugt, tryk, IMU accel+gyro, RGB/proximity/gesture), SD, relæ, knapper, LED, buzzer — og udskriver SAMD chip-ID, WiFi MAC og ECCX08-serienummer.

Efter tests registrerer/opdaterer boardet sig selv på API’et (`POST /api/devices` på SAMD-ID) og gemmer testrapporten.

```bash
cd Hardwaretestere/HardwareTest
cp src/Secrets.h.example src/Secrets.h
# Udfyld WIFI_SSID og WIFI_PASSWORD
```

Lyd: `ENABLE_SOUND_TEST` i `src/Hardwaretestere.h`. API-upload: `ENABLE_API_REPORT`.

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
