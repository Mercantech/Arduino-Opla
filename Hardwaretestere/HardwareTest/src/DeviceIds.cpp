#include "Hardwaretestere.h"
#include <WiFiNINA.h>
#include <ArduinoECCX08.h>

static void printSamdIdHex(char *out, size_t outLen) {
  // SAMD21 unique ID: 128-bit at 0x0080A00C
  volatile uint32_t *id = (volatile uint32_t *)0x0080A00C;
  snprintf(out, outLen, "%08lX%08lX%08lX%08lX",
           (unsigned long)id[0], (unsigned long)id[1],
           (unsigned long)id[2], (unsigned long)id[3]);
}

void printDeviceIds(MKRIoTCarrier &carrier) {
  char samdId[40];
  printSamdIdHex(samdId, sizeof(samdId));

  byte mac[6];
  WiFi.macAddress(mac);
  char macStr[18];
  snprintf(macStr, sizeof(macStr), "%02X:%02X:%02X:%02X:%02X:%02X",
           mac[5], mac[4], mac[3], mac[2], mac[1], mac[0]);

  char eccSerial[32] = "-";
  bool eccOk = false;
  if (ECCX08.begin()) {
    String sn = ECCX08.serialNumber();
    if (sn.length() > 0) {
      sn.toCharArray(eccSerial, sizeof(eccSerial));
      eccOk = true;
    }
  }

  Serial.println(F("=== Enheds-ID'er ==="));
  Serial.print(F("SAMD chip ID: "));
  Serial.println(samdId);
  Serial.print(F("WiFi MAC:     "));
  Serial.println(macStr);
  Serial.print(F("ECCX08 SN:    "));
  Serial.println(eccOk ? eccSerial : "(ikke fundet)");
  Serial.println(F("===================="));

  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_CYAN);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 10);
  carrier.display.println(F("Enheds-ID"));

  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(1);
  carrier.display.setCursor(10, 50);
  carrier.display.println(F("SAMD:"));
  carrier.display.setCursor(10, 65);
  carrier.display.println(samdId);

  carrier.display.setCursor(10, 95);
  carrier.display.println(F("WiFi MAC:"));
  carrier.display.setCursor(10, 110);
  carrier.display.println(macStr);

  carrier.display.setCursor(10, 140);
  carrier.display.println(F("ECCX08:"));
  carrier.display.setCursor(10, 155);
  carrier.display.println(eccOk ? eccSerial : "(ikke fundet)");

  delay(4000);
}

void maybeBeep(MKRIoTCarrier &carrier) {
#if ENABLE_SOUND_TEST
  carrier.Buzzer.beep();
#else
  (void)carrier;
#endif
}

void showTestResult(MKRIoTCarrier &carrier, const char *name, bool ok) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextSize(2);
  carrier.display.setTextColor(ok ? ST77XX_GREEN : ST77XX_RED);
  carrier.display.setCursor(15, 60);
  carrier.display.println(name);
  carrier.display.setCursor(15, 100);
  carrier.display.println(ok ? F("OK!") : F("FEJL!"));
  Serial.print(name);
  Serial.println(ok ? F(": OK") : F(": FEJL"));
  delay(1500);
}
