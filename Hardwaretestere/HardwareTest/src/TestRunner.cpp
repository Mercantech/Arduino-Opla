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
  char line[24];

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

  g_testsPassed = passed;
  g_testsFailed = failed;

  Serial.println(F("=== Test-opsummering ==="));
  Serial.print(F("Bestået: "));
  Serial.println(passed);
  Serial.print(F("Fejlet:  "));
  Serial.println(failed);

  clearDisplay(carrier);
  if (failed == 0) {
    drawCenteredF(carrier, F("Alle tests"), 70, 2, ST77XX_GREEN);
    drawCenteredF(carrier, F("fuldfort"), 105, 2, ST77XX_GREEN);
    drawCenteredF(carrier, F("Hardware OK"), 150, 2, ST77XX_WHITE);
    for (int i = 0; i < 5; i++) {
      carrier.leds.fill(carrier.leds.Color(0, 255, 0), 0, 5);
      carrier.leds.show();
      delay(250);
      carrier.leds.clear();
      carrier.leds.show();
      delay(250);
    }
  } else {
    drawCenteredF(carrier, F("Tests FEJL"), 65, 2, ST77XX_RED);
    snprintf(line, sizeof(line), "OK: %d", passed);
    drawCentered(carrier, line, 115, 2, ST77XX_WHITE);
    snprintf(line, sizeof(line), "Fejl: %d", failed);
    drawCentered(carrier, line, 150, 2, ST77XX_WHITE);
    for (int i = 0; i < 5; i++) {
      carrier.leds.fill(carrier.leds.Color(255, 0, 0), 0, 5);
      carrier.leds.show();
      delay(250);
      carrier.leds.clear();
      carrier.leds.show();
      delay(250);
    }
  }

  reportToApi(carrier);
}
