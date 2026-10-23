#include "Hardwaretestere.h"

static void track(bool ok, int &passed, int &failed) {
  if (ok) {
    passed++;
  } else {
    failed++;
  }
}

void runAllTests(MKRIoTCarrier &carrier) {
  int passed = 0;
  int failed = 0;

#if ENABLE_SOUND_TEST
  Serial.println(F("Lyd: TIL (buzzer + bip)"));
#else
  Serial.println(F("Lyd: FRA (stille lokale — buzzer sprunget over)"));
#endif

  track(testOLEDScreen(carrier), passed, failed);
  track(testHumidityTemperature(carrier), passed, failed);
  track(testPressureSensor(carrier), passed, failed);
  track(testIMU(carrier), passed, failed);
  track(testRGBGestureSensor(carrier), passed, failed);
  track(testSDCard(carrier), passed, failed);
  track(testRelays(carrier), passed, failed);
  track(testButtons(carrier), passed, failed);
  track(testLEDs(carrier), passed, failed);
#if ENABLE_SOUND_TEST
  track(testBuzzer(carrier), passed, failed);
#else
  Serial.println(F("Buzzer: SPRUNGET OVER"));
#endif

  Serial.println(F("=== Test-opsummering ==="));
  Serial.print(F("Bestået: "));
  Serial.println(passed);
  Serial.print(F("Fejlet:  "));
  Serial.println(failed);

  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextSize(2);
  if (failed == 0) {
    carrier.display.setTextColor(ST77XX_GREEN);
    carrier.display.setCursor(15, 60);
    carrier.display.println(F("Alle tests"));
    carrier.display.setCursor(15, 100);
    carrier.display.println(F("fuldfort!"));
    carrier.display.setCursor(15, 150);
    carrier.display.println(F("Hardware OK!"));
    for (int i = 0; i < 5; i++) {
      carrier.leds.fill(carrier.leds.Color(0, 255, 0), 0, 5);
      carrier.leds.show();
      delay(250);
      carrier.leds.clear();
      carrier.leds.show();
      delay(250);
    }
  } else {
    carrier.display.setTextColor(ST77XX_RED);
    carrier.display.setCursor(15, 50);
    carrier.display.println(F("Tests FEJL"));
    carrier.display.setTextColor(ST77XX_WHITE);
    carrier.display.setCursor(15, 100);
    carrier.display.print(F("OK: "));
    carrier.display.println(passed);
    carrier.display.setCursor(15, 130);
    carrier.display.print(F("Fejl: "));
    carrier.display.println(failed);
    for (int i = 0; i < 5; i++) {
      carrier.leds.fill(carrier.leds.Color(255, 0, 0), 0, 5);
      carrier.leds.show();
      delay(250);
      carrier.leds.clear();
      carrier.leds.show();
      delay(250);
    }
  }
}
