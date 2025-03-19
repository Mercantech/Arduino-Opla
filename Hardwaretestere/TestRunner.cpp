#include "Hardwaretestere.h"

// Hovedfunktion til at køre alle tests
void runAllTests(MKRIoTCarrier &carrier) {
  // Først tester vi skærmen 
  testOLEDScreen(carrier);
  
  // Derefter tester vi sensorerne
  testHumidityTemperature(carrier);
  testPressureSensor(carrier);
  testIMU(carrier);
  testRGBGestureSensor(carrier);
  
  // Test perifere enheder
  testRelays(carrier);
  testButtons(carrier);
  testLEDs(carrier);
  testBuzzer(carrier);
  
  // Afsluttende besked
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextSize(3);
  carrier.display.setTextColor(ST77XX_GREEN);
  carrier.display.setCursor(15, 60);
  carrier.display.println("Alle tests");
  carrier.display.setCursor(15, 100);
  carrier.display.println("fuldfort!");
  carrier.display.setTextSize(2);
  carrier.display.setCursor(15, 160);
  carrier.display.println("Arduino Opla");
  carrier.display.setCursor(15, 190);
  carrier.display.println("Hardware OK!");
  
  // Blink alle LED'er grønt som indikation på at alle tests er bestået
  for (int i = 0; i < 5; i++) {
    carrier.leds.fill(carrier.leds.Color(0, 255, 0), 0, 5);
    carrier.leds.show();
    delay(300);
    carrier.leds.clear();
    carrier.leds.show();
    delay(300);
  }
} 