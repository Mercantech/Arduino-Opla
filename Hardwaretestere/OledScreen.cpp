#include "Hardwaretestere.h"

// Vi bruger denne fil til at implementere yderligere skærmfunktioner
// efter behov. I denne simple skærmtest bruger vi hovedsageligt 
// funktionerne direkte i Hardwaretestere.ino-filen.

// Her kan du tilføje mere avancerede skærmfunktioner, hvis du får
// brug for det senere, f.eks.:

void initOLEDScreen(MKRIoTCarrier &carrier) {
  // Ryd skærmen
  carrier.display.fillScreen(ST77XX_BLACK);
}

void testOLEDScreen(MKRIoTCarrier &carrier) {
  // Vis velkomsttekst - centreret
  carrier.display.setTextSize(2);
  carrier.display.setTextColor(ST77XX_WHITE);
  
  // Beregn centrering for "OLED Test" (cirka 10 pixels per tegn med tekststørrelse 2)
  int textWidth = 9 * 10; // "OLED Test" er 9 tegn
  int xPosition = (240 - textWidth) / 2;
  
  carrier.display.setCursor(xPosition, 30);
  carrier.display.println("OLED Test");
  
  // Beregn centrering for "Arduino Opla" (12 tegn)
  textWidth = 12 * 10;
  xPosition = (240 - textWidth) / 2;
  
  carrier.display.setCursor(xPosition, 70);
  carrier.display.println("Arduino Opla");
  delay(2000);
  
  // Test forskellige farver
  testFarver(carrier);
  
  // Test tekststørrelser
  testTekstStorrelse(carrier);
  
  // Test cirkler og grafik
  drawCircleTest(carrier);
  drawGraphicsTest(carrier);
  
  // Afsluttende besked
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextSize(2);
  carrier.display.setTextColor(ST77XX_GREEN);
  
  // Centrér "Test Fuldfort!"
  textWidth = 14 * 10; // "Test Fuldfort!" er ca. 14 tegn
  xPosition = (240 - textWidth) / 2;
  
  carrier.display.setCursor(xPosition, 100);
  carrier.display.println("Test Fuldfort!");
  delay(2000);
}

void testFarver(MKRIoTCarrier &carrier) {
  // Test forskellige farver
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextSize(2);
  
  int yPosition = 20;
  int xPosition;
  
  // Rød tekst - centreret
  xPosition = (240 - 9 * 10) / 2; // "Rod tekst" er 9 tegn
  carrier.display.setTextColor(ST77XX_RED);
  carrier.display.setCursor(xPosition, yPosition);
  carrier.display.println("Rod tekst");
  delay(1000);
  
  // Grøn tekst - centreret
  yPosition += 30;
  xPosition = (240 - 10 * 10) / 2; // "Gron tekst" er 10 tegn
  carrier.display.setTextColor(ST77XX_GREEN);
  carrier.display.setCursor(xPosition, yPosition);
  carrier.display.println("Gron tekst");
  delay(1000);
  
  // Blå tekst - centreret
  yPosition += 30;
  xPosition = (240 - 9 * 10) / 2; // "Bla tekst" er 9 tegn
  carrier.display.setTextColor(ST77XX_BLUE);
  carrier.display.setCursor(xPosition, yPosition);
  carrier.display.println("Bla tekst");
  delay(1000);
  
  // Gul tekst - centreret
  yPosition += 30;
  xPosition = (240 - 9 * 10) / 2; // "Gul tekst" er 9 tegn
  carrier.display.setTextColor(ST77XX_YELLOW);
  carrier.display.setCursor(xPosition, yPosition);
  carrier.display.println("Gul tekst");
  delay(1000);
  
  // Cyan tekst - centreret
  yPosition += 30;
  xPosition = (240 - 10 * 10) / 2; // "Cyan tekst" er 10 tegn
  carrier.display.setTextColor(ST77XX_CYAN);
  carrier.display.setCursor(xPosition, yPosition);
  carrier.display.println("Cyan tekst");
  delay(1000);
  
  // Magenta tekst - centreret
  yPosition += 30;
  xPosition = (240 - 13 * 10) / 2; // "Magenta tekst" er 13 tegn
  carrier.display.setTextColor(ST77XX_MAGENTA);
  carrier.display.setCursor(xPosition, yPosition);
  carrier.display.println("Magenta tekst");
  delay(2000);
}

void testTekstStorrelse(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  
  // Størrelse 1 - centreret
  carrier.display.setTextSize(1);
  int textWidth = 16 * 6; // "Tekststorrelse 1" er 16 tegn, og tekststørrelse 1 er ca. 6 pixels per tegn
  int xPosition = (240 - textWidth) / 2;
  carrier.display.setCursor(xPosition, 30);
  carrier.display.println("Tekststorrelse 1");
  
  // Størrelse 2 - centreret
  carrier.display.setTextSize(2);
  textWidth = 11 * 12; // "Storrelse 2" er 11 tegn, tekststørrelse 2 er ca. 12 pixels per tegn
  xPosition = (240 - textWidth) / 2;
  carrier.display.setCursor(xPosition, 60);
  carrier.display.println("Storrelse 2");
  
  // Størrelse 3 - centreret
  carrier.display.setTextSize(3);
  textWidth = 5 * 18; // "Str 3" er 5 tegn, tekststørrelse 3 er ca. 18 pixels per tegn
  xPosition = (240 - textWidth) / 2;
  carrier.display.setCursor(xPosition, 100);
  carrier.display.println("Str 3");
  
  // Størrelse 4 - centreret
  carrier.display.setTextSize(4);
  textWidth = 5 * 24; // "Str 4" er 5 tegn, tekststørrelse 4 er ca. 24 pixels per tegn
  xPosition = (240 - textWidth) / 2;
  carrier.display.setCursor(xPosition, 150);
  carrier.display.println("Str 4");
  
  delay(3000);
}

void drawCircleTest(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  
  // Tegn cirkler med forskellige farver
  carrier.display.fillCircle(80, 60, 30, ST77XX_RED);
  carrier.display.fillCircle(160, 60, 30, ST77XX_GREEN);
  carrier.display.fillCircle(240, 60, 30, ST77XX_BLUE);
  
  carrier.display.fillCircle(80, 140, 30, ST77XX_YELLOW);
  carrier.display.fillCircle(160, 140, 30, ST77XX_MAGENTA);
  carrier.display.fillCircle(240, 140, 30, ST77XX_CYAN);
  
  delay(2000);
}

void drawGraphicsTest(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  
  // Tegn linjer
  for (int i = 0; i < 240; i += 10) {
    carrier.display.drawLine(0, 0, i, 240, ST77XX_WHITE);
  }
  
  delay(1000);
  carrier.display.fillScreen(ST77XX_BLACK);
  
  // Tegn rektangler
  carrier.display.drawRect(20, 20, 100, 60, ST77XX_RED);
  carrier.display.fillRect(150, 20, 80, 60, ST77XX_GREEN);
  carrier.display.drawRoundRect(20, 100, 100, 60, 10, ST77XX_BLUE);
  carrier.display.fillRoundRect(150, 100, 80, 60, 10, ST77XX_YELLOW);
  
  delay(2000);
}
