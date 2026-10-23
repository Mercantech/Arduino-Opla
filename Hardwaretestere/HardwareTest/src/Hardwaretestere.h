#ifndef HARDWARETESTERE_H
#define HARDWARETESTERE_H

#include <Arduino_MKRIoTCarrier.h>

// Stille lokale: sæt til false — springer buzzer-test over og undgår bip ved knapper/gesture
#ifndef ENABLE_SOUND_TEST
#define ENABLE_SOUND_TEST true
#endif

// Enheds-ID'er
void printDeviceIds(MKRIoTCarrier &carrier);

// Bip kun hvis ENABLE_SOUND_TEST er true
void maybeBeep(MKRIoTCarrier &carrier);

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
