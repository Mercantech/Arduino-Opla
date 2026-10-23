#include "Hardwaretestere.h"
#include <WiFiNINA.h>

#if __has_include("Secrets.h")
#include "Secrets.h"
#endif

#ifndef WIFI_SSID
#define WIFI_SSID ""
#endif
#ifndef WIFI_PASSWORD
#define WIFI_PASSWORD ""
#endif

static bool wifiConnect() {
  if (WIFI_SSID[0] == '\0') {
    Serial.println(F("API: Ingen WIFI_SSID i Secrets.h — springer over"));
    return false;
  }

  Serial.print(F("API: Forbinder til WiFi "));
  Serial.println(WIFI_SSID);

  WiFi.disconnect();
  delay(200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    Serial.print('.');
    delay(500);
  }
  Serial.println();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.print(F("API: WiFi fejlede, status="));
    Serial.println(WiFi.status());
    return false;
  }

  Serial.print(F("API: WiFi OK, IP="));
  Serial.println(WiFi.localIP());
  return true;
}

static String httpRequest(const char *method, const char *path, const char *jsonBody) {
  WiFiSSLClient client;
  client.setTimeout(20000);

  Serial.print(F("API: "));
  Serial.print(method);
  Serial.print(' ');
  Serial.println(path);

  if (!client.connect(API_HOST, API_PORT)) {
    Serial.println(F("API: TLS/connect fejlede (tjek NINA-firmware / cert)"));
    return "";
  }

  size_t bodyLen = jsonBody ? strlen(jsonBody) : 0;

  client.print(method);
  client.print(' ');
  client.print(path);
  client.println(F(" HTTP/1.1"));
  client.print(F("Host: "));
  client.println(API_HOST);
  client.println(F("User-Agent: Arduino-Opla-HardwareTest"));
  client.println(F("Accept: application/json"));
  if (bodyLen > 0) {
    client.println(F("Content-Type: application/json"));
    client.print(F("Content-Length: "));
    client.println(bodyLen);
  }
  client.println(F("Connection: close"));
  client.println();
  if (bodyLen > 0) {
    client.print(jsonBody);
  }

  unsigned long headerStart = millis();
  while (client.connected() || client.available()) {
    if (millis() - headerStart > 20000) {
      Serial.println(F("API: timeout (headers)"));
      client.stop();
      return "";
    }
    if (!client.available()) {
      delay(10);
      continue;
    }
    String line = client.readStringUntil('\n');
    if (line == "\r" || line.length() == 0) {
      break;
    }
  }

  String response = "";
  unsigned long bodyStart = millis();
  while (millis() - bodyStart < 20000) {
    while (client.available()) {
      response += (char)client.read();
      bodyStart = millis();
    }
    if (!client.connected() && !client.available()) {
      break;
    }
    delay(10);
  }
  client.stop();

  Serial.print(F("API: svar "));
  Serial.print(response.length());
  Serial.println(F(" bytes"));
  return response;
}

bool reportToApi(MKRIoTCarrier &carrier) {
#if !ENABLE_API_REPORT
  Serial.println(F("API: ENABLE_API_REPORT=false — springer over"));
  (void)carrier;
  return false;
#else
  clearDisplay(carrier);
  drawCenteredF(carrier, F("Sender til"), 80, 2, ST77XX_WHITE);
  drawCenteredF(carrier, F("API..."), 120, 2, ST77XX_CYAN);

  if (!wifiConnect()) {
    clearDisplay(carrier);
    drawCenteredF(carrier, F("WiFi/API"), OLED_CY - 20, 2, ST77XX_YELLOW);
    drawCenteredF(carrier, F("skip"), OLED_CY + 16, 2, ST77XX_YELLOW);
    delay(2000);
    return false;
  }

  // Upsert på unikt SAMD chip-ID
  char deviceJson[256];
  snprintf(deviceJson, sizeof(deviceJson),
           "{\"samd_id\":\"%s\",\"mac\":\"%s\",\"ecc_serial\":\"%s\",\"label\":\"Arduino Opla\"}",
           g_samdId, g_macStr, g_eccOk ? g_eccSerial : "");

  String deviceResp = httpRequest("POST", "/api/devices", deviceJson);
  if (deviceResp.length() == 0 || deviceResp.indexOf(g_samdId) < 0) {
    Serial.println(F("API: device upsert fejlede"));
    if (deviceResp.length()) {
      Serial.println(deviceResp);
    }
    clearDisplay(carrier);
    drawCenteredF(carrier, F("API FEJL"), OLED_CY - 12, 2, ST77XX_RED);
    delay(2000);
    return false;
  }

  Serial.print(F("API: enhed ID (SAMD)="));
  Serial.println(g_samdId);

  delay(500); // pause mellem TLS-forbindelser

  bool allOk = (g_testsFailed == 0);
  char testPath[96];
  snprintf(testPath, sizeof(testPath), "/api/devices/%s/tests", g_samdId);

  char testJson[192];
  snprintf(testJson, sizeof(testJson),
           "{\"passed\":%s,\"passed_count\":%d,\"failed_count\":%d,\"details\":\"sound=%d\"}",
           allOk ? "true" : "false", g_testsPassed, g_testsFailed,
           ENABLE_SOUND_TEST ? 1 : 0);

  String testResp = httpRequest("POST", testPath, testJson);
  if (testResp.length() == 0) {
    Serial.println(F("API: testrapport fejlede"));
    clearDisplay(carrier);
    drawCenteredF(carrier, F("Device OK"), 80, 2, ST77XX_YELLOW);
    drawCenteredF(carrier, F("Test FEJL"), 120, 2, ST77XX_RED);
    delay(2500);
    return false;
  }

  Serial.println(F("API: enhed registreret/opdateret + testrapport gemt"));
  clearDisplay(carrier);
  drawCenteredF(carrier, F("API OK"), 55, 3, ST77XX_GREEN);
  drawCenteredF(carrier, F("SAMD"), 110, 1, ST77XX_WHITE);
  char samdA[20], samdB[20];
  strncpy(samdA, g_samdId, 16);
  samdA[16] = '\0';
  strncpy(samdB, g_samdId + 16, 16);
  samdB[16] = '\0';
  drawCentered(carrier, samdA, 130, 1, ST77XX_YELLOW);
  drawCentered(carrier, samdB, 146, 1, ST77XX_YELLOW);
  delay(3000);
  return true;
#endif
}
