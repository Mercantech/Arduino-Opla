#ifndef HARDWARETESTERE_H
#define HARDWARETESTERE_H

#include <Arduino_MKRIoTCarrier.h>

// Stille lokale: sæt til false — springer buzzer-test over og undgår bip ved knapper/gesture
#ifndef ENABLE_SOUND_TEST
#define ENABLE_SOUND_TEST false
#endif

// Send resultat til opla.mercantec.tech efter tests (kræver WiFi i Secrets.h)
#ifndef ENABLE_API_REPORT
#define ENABLE_API_REPORT true
#endif

#define API_HOST "opla.mercantec.tech"
#define API_PORT 443

// Globale enheds-ID'er (udfyldes af printDeviceIds)
extern char g_samdId[40];
extern char g_macStr[18];
extern char g_eccSerial[32];
extern bool g_eccOk;

// Test-opsummering (udfyldes af runAllTests)
extern int g_testsPassed;
extern int g_testsFailed;

// Enheds-ID'er
void printDeviceIds(MKRIoTCarrier &carrier);

// Bip kun hvis ENABLE_SOUND_TEST er true
void maybeBeep(MKRIoTCarrier &carrier);

// Registrér/opdatér enhed + testrapport via HTTPS
bool reportToApi(MKRIoTCarrier &carrier);

// OLED
void initOLEDScreen(MKRIoTCarrier &carrier);
bool testOLEDScreen(MKRIoTCarrier &carrier);
void testFarver(MKRIoTCarrier &carrier);
void testTekstStorrelse(MKRIoTCarrier &carrier);
void drawCircleTest(MKRIoTCarrier &carrier);
void drawGraphicsTest(MKRIoTCarrier &carrier);

// Sensorer (returnerer true = bestået)
bool testHumidityTemperature(MKRIoTCarrier &carrier);
bool testPressureSensor(MKRIoTCarrier &carrier);
bool testIMU(MKRIoTCarrier &carrier);
bool testRGBGestureSensor(MKRIoTCarrier &carrier);
bool testSDCard(MKRIoTCarrier &carrier);

// Periferi
bool testRelays(MKRIoTCarrier &carrier);
bool testButtons(MKRIoTCarrier &carrier);
bool testLEDs(MKRIoTCarrier &carrier);
bool testBuzzer(MKRIoTCarrier &carrier);

// Hovedtest
void runAllTests(MKRIoTCarrier &carrier);

// Hjælpere til resultatvisning
void showTestResult(MKRIoTCarrier &carrier, const char *name, bool ok);

#endif // HARDWARETESTERE_H
