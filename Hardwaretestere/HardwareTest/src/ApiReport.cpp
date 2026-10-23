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

static int parseJsonIntField(const String &body, const char *key) {
  String needle = String("\"") + key + "\":";
  int idx = body.indexOf(needle);
  if (idx < 0) {
    return -1;
  }
  idx += needle.length();
  while (idx < (int)body.length() &&
         (body.charAt(idx) == ' ' || body.charAt(idx) == '\t')) {
    idx++;
  }
  return body.substring(idx).toInt();
}

static String httpRequest(const char *method, const char *path, const char *jsonBody) {
  WiFiSSLClient client;
  client.setTimeout(15000);

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

  // Skip headers
  while (client.connected() || client.available()) {
    String line = client.readStringUntil('\n');
    if (line == "\r" || line.length() == 0) {
      break;
    }
  }

  String response = client.readString();
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
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 60);
  carrier.display.println(F("Sender til"));
  carrier.display.setCursor(20, 100);
  carrier.display.println(F("API..."));

  if (!wifiConnect()) {
    carrier.display.fillScreen(ST77XX_BLACK);
    carrier.display.setTextColor(ST77XX_YELLOW);
    carrier.display.setCursor(15, 80);
    carrier.display.println(F("WiFi/API skip"));
    delay(2000);
    return false;
  }

  // Upsert enhed på unikt SAMD-ID (+ MAC/ECC)
  char deviceJson[256];
  snprintf(deviceJson, sizeof(deviceJson),
           "{\"samd_id\":\"%s\",\"mac\":\"%s\",\"ecc_serial\":\"%s\",\"label\":\"Arduino Opla\"}",
           g_samdId, g_macStr, g_eccOk ? g_eccSerial : "");

  String deviceResp = httpRequest("POST", "/api/devices", deviceJson);
  if (deviceResp.length() == 0) {
    carrier.display.fillScreen(ST77XX_BLACK);
    carrier.display.setTextColor(ST77XX_RED);
    carrier.display.setCursor(15, 80);
    carrier.display.println(F("API FEJL"));
    delay(2000);
    return false;
  }

  int deviceId = parseJsonIntField(deviceResp, "id");
  if (deviceId <= 0) {
    Serial.println(F("API: kunne ikke parse device id"));
    Serial.println(deviceResp);
    carrier.display.fillScreen(ST77XX_BLACK);
    carrier.display.setTextColor(ST77XX_RED);
    carrier.display.setCursor(15, 80);
    carrier.display.println(F("API parse"));
    delay(2000);
    return false;
  }

  Serial.print(F("API: enhed id="));
  Serial.println(deviceId);

  bool allOk = (g_testsFailed == 0);
  char testPath[64];
  snprintf(testPath, sizeof(testPath), "/api/devices/%d/tests", deviceId);

  char testJson[192];
  snprintf(testJson, sizeof(testJson),
           "{\"passed\":%s,\"passed_count\":%d,\"failed_count\":%d,\"details\":\"sound=%d\"}",
           allOk ? "true" : "false", g_testsPassed, g_testsFailed,
           ENABLE_SOUND_TEST ? 1 : 0);

  String testResp = httpRequest("POST", testPath, testJson);
  if (testResp.length() == 0) {
    Serial.println(F("API: testrapport fejlede"));
    carrier.display.fillScreen(ST77XX_BLACK);
    carrier.display.setTextColor(ST77XX_RED);
    carrier.display.setCursor(15, 60);
    carrier.display.println(F("Device OK"));
    carrier.display.setCursor(15, 100);
    carrier.display.println(F("Test FEJL"));
    delay(2500);
    return false;
  }

  Serial.println(F("API: enhed registreret/opdateret + testrapport gemt"));
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_GREEN);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 50);
  carrier.display.println(F("API OK"));
  carrier.display.setTextSize(1);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setCursor(20, 100);
  carrier.display.print(F("Device #"));
  carrier.display.println(deviceId);
  carrier.display.setCursor(20, 120);
  carrier.display.println(g_samdId);
  delay(3000);
  return true;
#endif
}
