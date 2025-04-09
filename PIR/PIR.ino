#include <Arduino_MKRIoTCarrier.h>

// Definér pin for PIR sensor
const int pirPin = A6;

// Global variabel for PIR status
bool pirStatus = false;
unsigned long t0;
MKRIoTCarrier carrier;

void setup() {
  Serial.begin(9600);
  pinMode(pirPin, INPUT);
  
  // Initialiser MKR IoT carrier
  if (!carrier.begin()) {
    Serial.println("Fejl ved initialisering af MKR IoT carrier!");
    while (1);
  }
  
  // Vis opstartsskærm
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextSize(2);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setCursor(50, 100);
  carrier.display.println("PIR Monitor");
  
  // Opvarmningstid for PIR
  carrier.display.setCursor(20, 140);
  carrier.display.println("Varmer op...");
  delay(60000); // 60 sekunders opvarmning
  
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setCursor(40, 100);
  carrier.display.println("Klar!");
  delay(2000);
}

void loop() {
  // Læs PIR sensor med støjreduktion
  if (!pirStatus && isPIRTriggered()) {
    // Log til serial monitor
    Serial.println("PIR aktiveret!");
    
    // Opdater skærm
    carrier.display.fillScreen(ST77XX_BLACK);
    carrier.display.setTextSize(3);
    carrier.display.setTextColor(ST77XX_RED);
    carrier.display.setCursor(30, 100);
    carrier.display.println("BEVAEGELSE!");
    
    pirStatus = true;
    t0 = millis();
  }
  
  // Nulstil PIR status efter 6 sekunder
  if (millis() - t0 > 6000 && pirStatus == true) {
    pirStatus = false;
    
    // Opdater skærm
    carrier.display.fillScreen(ST77XX_BLACK);
    carrier.display.setTextSize(2);
    carrier.display.setTextColor(ST77XX_GREEN);
    carrier.display.setCursor(40, 100);
    carrier.display.println("Ingen aktivitet");
  }
  
  delay(50); // Lille forsinkelse for at reducere støj
}

// Ny funktion til at verificere PIR-signal
bool isPIRTriggered() {
  // Tag 3 målinger med kort mellemrum
  int readings = 0;
  for(int i = 0; i < 3; i++) {
    if(digitalRead(pirPin)) {
      readings++;
    }
    delay(10);
  }
  // Returner true hvis mindst 2 af 3 målinger er positive
  return (readings >= 2);
}
