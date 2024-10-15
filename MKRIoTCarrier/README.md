## Arduino MKR IoT Carrier

[Officiel Arduino dokumentation](https://docs.arduino.cc/tutorials/mkr-iot-carrier/mkr-iot-carrier-01-technical-reference/)

Vores IoT sæt - har mange funktioner de er alle dokumenteret heroppe ⬆

### Funktioner

- **Indbygget display**: Et farvedisplay til at vise data og interagere med brugeren.
- **Sensorer**: Inkluderer temperatur, fugtighed, lys, og bevægelsessensorer.
- **Knappanel**: Flere knapper til brugerinput.
- **RGB LED**: En flerfarvet LED til visuel feedback.
- **Buzzer**: En lille højttaler til lydsignaler.

### Kom godt i gang

1. Tilslut MKR IoT Carrier til din Arduino MKR board.
2. Installer de nødvendige biblioteker via Arduino IDE.
3. Upload et eksempelprogram til din Arduino for at teste funktionerne.

### Eksempel

Her er et simpelt eksempel på, hvordan du kan læse temperaturdata fra sensoren:

```cpp
#include <Arduino_MKRIoTCarrier.h>

MKRIoTCarrier carrier;

void setup() {
  Serial.begin(9600);
  while (!Serial);
  carrier.begin();
}

void loop() {
  float temperature = carrier.Env.readTemperature();
  Serial.print("Temperatur: ");
  Serial.print(temperature);
  Serial.println(" °C");
  delay(1000);
}
```
