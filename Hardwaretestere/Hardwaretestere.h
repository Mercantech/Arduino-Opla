#ifndef HARDWARETESTERE_H
#define HARDWARETESTERE_H

#include <Arduino_MKRIoTCarrier.h>

// Funktioner til at teste OLED-skærmen
void initOLEDScreen(MKRIoTCarrier &carrier);
void testOLEDScreen(MKRIoTCarrier &carrier);
void testFarver(MKRIoTCarrier &carrier);
void testTekstStorrelse(MKRIoTCarrier &carrier);
void drawCircleTest(MKRIoTCarrier &carrier);
void drawGraphicsTest(MKRIoTCarrier &carrier);

// Funktioner til at teste sensorer
void testHumidityTemperature(MKRIoTCarrier &carrier);
void testPressureSensor(MKRIoTCarrier &carrier);
void testIMU(MKRIoTCarrier &carrier);
void testRGBGestureSensor(MKRIoTCarrier &carrier);

// Funktioner til at teste perifere enheder
void testRelays(MKRIoTCarrier &carrier);
void testButtons(MKRIoTCarrier &carrier);
void testLEDs(MKRIoTCarrier &carrier);
void testBuzzer(MKRIoTCarrier &carrier);

// Hovedtestfunktion
void runAllTests(MKRIoTCarrier &carrier);

#endif // HARDWARETESTERE_H 