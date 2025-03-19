#include <Arduino_MKRIoTCarrier.h>
#include "Hardwaretestere.h"

MKRIoTCarrier carrier;

void setup() {
  Serial.begin(9600);
  while (!Serial);
  
  Serial.println("Arduino Opla Hardware Tester - Fuld Test");
  
  // Initialiser Opla med standard konfiguration
  // Kommenter den relevante linje ud baseret på om du bruger kabinettet eller ej
  carrier.noCase(); // Uden kabinet
  //carrier.withCase(); // Med kabinet
  
  carrier.begin();
  
  // Initialiser skærmen
  initOLEDScreen(carrier);
  
  // Kør alle hardware tests
  runAllTests(carrier);
}

void loop() {
  // Intet behov for løbende handlinger efter tests er fuldført
  delay(1000);
}
