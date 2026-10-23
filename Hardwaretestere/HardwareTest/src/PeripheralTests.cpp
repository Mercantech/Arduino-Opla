#include "Hardwaretestere.h"

bool testRelays(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println(F("Relay Test"));
  delay(800);

  carrier.display.setCursor(20, 60);
  carrier.display.println(F("Relay 1 ON"));
  carrier.Relay1.open();
  delay(800);
  carrier.Relay1.close();

  carrier.display.setCursor(20, 90);
  carrier.display.println(F("Relay 2 ON"));
  carrier.Relay2.open();
  delay(800);
  carrier.Relay2.close();

  carrier.Relay1.open();
  carrier.Relay2.open();
  delay(500);
  carrier.Relay1.close();
  carrier.Relay2.close();

  showTestResult(carrier, "Relay", true);
  return true;
}

bool testButtons(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println(F("Knap Test"));
  carrier.display.setCursor(20, 50);
  carrier.display.println(F("Tryk alle 5"));

  unsigned long startTime = millis();
  bool buttonPressed[5] = {false, false, false, false, false};
  bool allButtonsPressed = false;
  touchButtons buttons[5] = {TOUCH0, TOUCH1, TOUCH2, TOUCH3, TOUCH4};

  while (!allButtonsPressed && (millis() - startTime < 30000)) {
    carrier.Buttons.update();
    for (int i = 0; i < 5; i++) {
      if (carrier.Buttons.onTouchDown(buttons[i])) {
        buttonPressed[i] = true;
        carrier.display.fillRect(0, 110 + (i * 22), 240, 22, ST77XX_BLACK);
        carrier.display.setCursor(20, 110 + (i * 22));
        carrier.display.print(F("Knap "));
        carrier.display.print(i);
        carrier.display.println(F(" OK"));
        Serial.print(F("Knap "));
        Serial.print(i);
        Serial.println(F(" trykket"));
        carrier.Buzzer.beep();
      }
    }
    allButtonsPressed = true;
    for (int i = 0; i < 5; i++) {
      if (!buttonPressed[i]) {
        allButtonsPressed = false;
        break;
      }
    }
    delay(10);
  }

  showTestResult(carrier, "Knapper", allButtonsPressed);
  return allButtonsPressed;
}

bool testLEDs(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println(F("LED Test"));
  delay(500);

  carrier.leds.setBrightness(255);

  for (int led = 0; led < 5; led++) {
    carrier.leds.clear();
    carrier.leds.setPixelColor(led, 255, 0, 0);
    carrier.leds.show();
    delay(200);
    carrier.leds.setPixelColor(led, 0, 255, 0);
    carrier.leds.show();
    delay(200);
    carrier.leds.setPixelColor(led, 0, 0, 255);
    carrier.leds.show();
    delay(200);
  }

  uint32_t colors[] = {
      carrier.leds.Color(255, 0, 0),
      carrier.leds.Color(0, 255, 0),
      carrier.leds.Color(0, 0, 255),
      carrier.leds.Color(255, 255, 0),
      carrier.leds.Color(0, 255, 255),
      carrier.leds.Color(255, 0, 255)};

  for (int c = 0; c < 6; c++) {
    carrier.leds.fill(colors[c], 0, 5);
    carrier.leds.show();
    delay(300);
  }

  carrier.leds.clear();
  carrier.leds.show();

  showTestResult(carrier, "LED", true);
  return true;
}

bool testBuzzer(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println(F("Buzzer Test"));
  delay(500);

  int tones[] = {262, 294, 330, 349, 392, 440, 494, 523};
  for (int i = 0; i < 8; i++) {
    carrier.display.fillRect(0, 60, 240, 30, ST77XX_BLACK);
    carrier.display.setCursor(20, 60);
    carrier.display.print(F("Tone: "));
    carrier.display.println(tones[i]);
    carrier.Buzzer.sound(tones[i]);
    delay(150);
    carrier.Buzzer.noSound();
    delay(50);
  }

  for (int i = 0; i < 3; i++) {
    carrier.Buzzer.beep();
    delay(300);
  }

  showTestResult(carrier, "Buzzer", true);
  return true;
}
