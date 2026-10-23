#include <Arduino_MKRIoTCarrier.h>
#include "Hardwaretestere.h"

MKRIoTCarrier carrier;

void setup() {
  Serial.begin(9600);
  unsigned long serialWait = millis();
  while (!Serial && (millis() - serialWait < 3000)) {
    ; // timeout så boardet ikke hænger uden USB-monitor
  }

  Serial.println(F("Arduino Opla Hardware Tester - Fuld Test"));

  carrier.noCase(); // uden kabinet; brug withCase() hvis kabinet er monteret

  if (!carrier.begin()) {
    Serial.println(F("FEJL: carrier.begin() fejlede"));
    while (true) {
      delay(1000);
    }
  }

  initOLEDScreen(carrier);
  printDeviceIds(carrier);
  runAllTests(carrier);
}

void loop() {
  delay(1000);
}
