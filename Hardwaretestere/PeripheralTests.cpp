#include "Hardwaretestere.h"

// Test af relæer
void testRelays(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println("Relay Test");
  delay(1000);
  
  // Test relæ 1
  carrier.display.setCursor(20, 60);
  carrier.display.println("Relay 1 ON");
  carrier.Relay1.open();
  delay(1000);
  
  carrier.display.setCursor(20, 90);
  carrier.display.println("Relay 1 OFF");
  carrier.Relay1.close();
  delay(1000);
  
  // Test relæ 2
  carrier.display.setCursor(20, 130);
  carrier.display.println("Relay 2 ON");
  carrier.Relay2.open();
  delay(1000);
  
  carrier.display.setCursor(20, 160);
  carrier.display.println("Relay 2 OFF");
  carrier.Relay2.close();
  delay(1000);
  
  // Test begge relæer
  carrier.display.setCursor(20, 200);
  carrier.display.println("Begge ON");
  carrier.Relay1.open();
  carrier.Relay2.open();
  delay(1000);
  
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setCursor(20, 20);
  carrier.display.println("Begge OFF");
  carrier.Relay1.close();
  carrier.Relay2.close();
  delay(1000);
  
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_GREEN);
  carrier.display.setCursor(15, 60);
  carrier.display.println("Relay Test OK!");
  delay(1500);
}

// Test af knapper
void testButtons(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println("Knap Test");
  carrier.display.setCursor(20, 50);
  carrier.display.println("Tryk paa en");
  carrier.display.setCursor(20, 80);
  carrier.display.println("af knapperne");
  
  unsigned long startTime = millis();
  bool buttonPressed[5] = {false, false, false, false, false};
  bool allButtonsPressed = false;
  
  // Array af touchButtons enum værdier
  touchButtons buttons[5] = {TOUCH0, TOUCH1, TOUCH2, TOUCH3, TOUCH4};
  
  while (!allButtonsPressed && (millis() - startTime < 30000)) { // Kør i maks 30 sekunder
    carrier.Buttons.update();
    
    // Kontroller hver knap
    for (int i = 0; i < 5; i++) {
      if (carrier.Buttons.onTouchDown(buttons[i])) {
        buttonPressed[i] = true;
        
        carrier.display.fillRect(0, 110 + (i * 25), 240, 25, ST77XX_BLACK);
        carrier.display.setCursor(20, 110 + (i * 25));
        carrier.display.print("Knap ");
        carrier.display.print(i);
        carrier.display.println(" trykket!");
        
        Serial.print("Knap ");
        Serial.print(i);
        Serial.println(" trykket!");
        
        // Afspil en lille bip-lyd når en knap trykkes
        carrier.Buzzer.beep();
      }
    }
    
    // Kontroller om alle knapper er blevet trykket
    allButtonsPressed = true;
    for (int i = 0; i < 5; i++) {
      if (!buttonPressed[i]) {
        allButtonsPressed = false;
        break;
      }
    }
    
    delay(10);
  }
  
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_GREEN);
  carrier.display.setCursor(15, 60);
  carrier.display.println("Knap Test OK!");
  delay(1500);
}

// Test af LED'er
void testLEDs(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println("LED Test");
  delay(1000);
  
  // Sæt lysstyrken til maksimum
  carrier.leds.setBrightness(255);
  
  // Test hver LED med forskellige farver
  for (int led = 0; led < 5; led++) {
    // Rød
    carrier.display.fillRect(0, 60, 240, 30, ST77XX_BLACK);
    carrier.display.setCursor(20, 60);
    carrier.display.print("LED ");
    carrier.display.print(led);
    carrier.display.println(" ROD");
    carrier.leds.clear();
    carrier.leds.setPixelColor(led, 255, 0, 0);
    carrier.leds.show();
    delay(500);
    
    // Grøn
    carrier.display.fillRect(0, 60, 240, 30, ST77XX_BLACK);
    carrier.display.setCursor(20, 60);
    carrier.display.print("LED ");
    carrier.display.print(led);
    carrier.display.println(" GRON");
    carrier.leds.clear();
    carrier.leds.setPixelColor(led, 0, 255, 0);
    carrier.leds.show();
    delay(500);
    
    // Blå
    carrier.display.fillRect(0, 60, 240, 30, ST77XX_BLACK);
    carrier.display.setCursor(20, 60);
    carrier.display.print("LED ");
    carrier.display.print(led);
    carrier.display.println(" BLA");
    carrier.leds.clear();
    carrier.leds.setPixelColor(led, 0, 0, 255);
    carrier.leds.show();
    delay(500);
  }
  
  // Test alle LED'er sammen
  uint32_t colors[] = {
    carrier.leds.Color(255, 0, 0),    // Rød
    carrier.leds.Color(0, 255, 0),    // Grøn
    carrier.leds.Color(0, 0, 255),    // Blå
    carrier.leds.Color(255, 255, 0),  // Gul
    carrier.leds.Color(0, 255, 255),  // Cyan
    carrier.leds.Color(255, 0, 255)   // Magenta
  };
  
  for (int c = 0; c < 6; c++) {
    carrier.display.fillRect(0, 100, 240, 30, ST77XX_BLACK);
    carrier.display.setCursor(20, 100);
    carrier.display.println("Alle LEDs");
    carrier.leds.fill(colors[c], 0, 5);
    carrier.leds.show();
    delay(500);
  }
  
  carrier.leds.clear();
  carrier.leds.show();
  
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_GREEN);
  carrier.display.setCursor(15, 60);
  carrier.display.println("LED Test OK!");
  delay(1500);
}

// Test af buzzer
void testBuzzer(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println("Buzzer Test");
  delay(1000);
  
  // Afspil forskellige toner
  int tones[] = {262, 294, 330, 349, 392, 440, 494, 523};
  
  // Spil en simpel melodi
  for (int i = 0; i < 8; i++) {
    carrier.display.fillRect(0, 60, 240, 30, ST77XX_BLACK);
    carrier.display.setCursor(20, 60);
    carrier.display.print("Tone: ");
    carrier.display.println(tones[i]);
    
    carrier.Buzzer.sound(tones[i]);
    delay(200);
    carrier.Buzzer.noSound();
    delay(100);
  }
  
  // Afspil en simpel bip-lyd
  carrier.display.fillRect(0, 60, 240, 30, ST77XX_BLACK);
  carrier.display.setCursor(20, 60);
  carrier.display.println("Beep");
  
  for (int i = 0; i < 3; i++) {
    carrier.Buzzer.beep();
    delay(500);
  }
  
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_GREEN);
  carrier.display.setCursor(15, 60);
  carrier.display.println("Buzzer Test OK!");
  delay(1500);
} 