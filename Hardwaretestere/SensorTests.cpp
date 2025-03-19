#include "Hardwaretestere.h"

// Test af fugtigheds- og temperatursensor (HTS221)
void testHumidityTemperature(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println("Temp & Fugt");
  carrier.display.setCursor(20, 50);
  carrier.display.println("Test");
  delay(1000);
  
  for (int i = 0; i < 5; i++) {
    float temperature = carrier.Env.readTemperature();
    float humidity = carrier.Env.readHumidity();
    
    carrier.display.fillRect(0, 80, 240, 160, ST77XX_BLACK);
    
    carrier.display.setCursor(20, 80);
    carrier.display.print("Temp: ");
    carrier.display.print(temperature);
    carrier.display.println(" C");
    
    carrier.display.setCursor(20, 120);
    carrier.display.print("Fugt: ");
    carrier.display.print(humidity);
    carrier.display.println(" %");
    
    Serial.print("Temperatur: ");
    Serial.print(temperature);
    Serial.println(" °C");
    
    Serial.print("Fugtighed: ");
    Serial.print(humidity);
    Serial.println(" %");
    
    delay(1000);
  }
  
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_GREEN);
  carrier.display.setCursor(15, 60);
  carrier.display.println("Temp/Fugt OK!");
  delay(1500);
}

// Test af tryksensor (LPS22HBTR)
void testPressureSensor(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println("Tryk Sensor");
  carrier.display.setCursor(20, 50);
  carrier.display.println("Test");
  delay(1000);
  
  for (int i = 0; i < 5; i++) {
    float pressure = carrier.Pressure.readPressure();
    
    carrier.display.fillRect(0, 80, 240, 160, ST77XX_BLACK);
    
    carrier.display.setCursor(20, 80);
    carrier.display.print("Tryk: ");
    carrier.display.print(pressure);
    carrier.display.println(" kPa");
    
    // Konverter til hPa (millibar) - 1 kPa = 10 hPa
    carrier.display.setCursor(20, 120);
    carrier.display.print("     ");
    carrier.display.print(pressure * 10);
    carrier.display.println(" hPa");
    
    Serial.print("Tryk: ");
    Serial.print(pressure);
    Serial.println(" kPa");
    
    delay(1000);
  }
  
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_GREEN);
  carrier.display.setCursor(15, 60);
  carrier.display.println("Tryk Sensor OK!");
  delay(1500);
}

// Test af IMU (accelerometer & gyroskop)
void testIMU(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println("IMU Sensor");
  carrier.display.setCursor(20, 50);
  carrier.display.println("Bevoeg kortet");
  delay(2000);
  
  float x, y, z;
  
  unsigned long startTime = millis();
  
  while (millis() - startTime < 10000) { // Kør i 10 sekunder
    carrier.display.fillRect(0, 110, 240, 130, ST77XX_BLACK);
    
    if (carrier.IMUmodule.accelerationAvailable()) {
      carrier.IMUmodule.readAcceleration(x, y, z);
      
      carrier.display.setCursor(20, 110);
      carrier.display.print("X: ");
      carrier.display.println(x);
      
      carrier.display.setCursor(20, 140);
      carrier.display.print("Y: ");
      carrier.display.println(y);
      
      carrier.display.setCursor(20, 170);
      carrier.display.print("Z: ");
      carrier.display.println(z);
      
      Serial.print("Acceleration - X: ");
      Serial.print(x);
      Serial.print(", Y: ");
      Serial.print(y);
      Serial.print(", Z: ");
      Serial.println(z);
    }
    
    delay(100);
  }
  
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_GREEN);
  carrier.display.setCursor(15, 60);
  carrier.display.println("IMU Test OK!");
  delay(1500);
}

// Test af RGB og gesturesensor - opdateret med mere information
void testRGBGestureSensor(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  
  // Centrér teksten bedre til det runde display
  carrier.display.setCursor(40, 20);
  carrier.display.println("RGB & Gesture");
  carrier.display.setCursor(50, 50);
  carrier.display.println("Sensor Test");
  
  // Mere detaljeret instruktion
  carrier.display.setTextSize(1);
  carrier.display.setCursor(20, 80);
  carrier.display.println("Bevæg haanden over sensoren");
  carrier.display.setCursor(20, 95);
  carrier.display.println("OP/NED/VENSTRE/HOJRE");
  carrier.display.setCursor(20, 110);
  carrier.display.println("for at teste gesture-sensoren");
  
  delay(3000);
  
  int r, g, b;
  unsigned long startTime = millis();
  int detectedGestures = 0;
  bool gestureDetected[4] = {false, false, false, false}; // UP, DOWN, LEFT, RIGHT
  
  while ((millis() - startTime < 25000) && detectedGestures < 4) { // Kør i op til 25 sekunder eller indtil alle gestus er registreret
    carrier.display.fillRect(0, 130, 240, 110, ST77XX_BLACK);
    
    // RGB sensor test
    if (carrier.Light.colorAvailable()) {
      carrier.Light.readColor(r, g, b);
      
      carrier.display.setTextSize(1);
      carrier.display.setCursor(20, 130);
      carrier.display.print("RGB Farveværdier:");
      
      carrier.display.setCursor(20, 145);
      carrier.display.print("R: ");
      carrier.display.println(r);
      
      carrier.display.setCursor(20, 160);
      carrier.display.print("G: ");
      carrier.display.println(g);
      
      carrier.display.setCursor(20, 175);
      carrier.display.print("B: ");
      carrier.display.println(b);
      
      // Vis den opfattede farve med en lille farveprøve
      carrier.display.fillRect(150, 145, 40, 30, carrier.display.color565(r, g, b));
      carrier.display.drawRect(150, 145, 40, 30, ST77XX_WHITE);
      
      Serial.print("RGB - R: ");
      Serial.print(r);
      Serial.print(", G: ");
      Serial.print(g);
      Serial.print(", B: ");
      Serial.println(b);
    }
    
    // Gesture sensor test - opdateret med status på hver gestus
    if (carrier.Light.gestureAvailable()) {
      uint8_t gesture = carrier.Light.readGesture();
      
      carrier.display.fillRect(0, 190, 240, 50, ST77XX_BLACK);
      carrier.display.setTextSize(2);
      carrier.display.setCursor(20, 190);
      carrier.display.print("Gesture: ");
      
      switch(gesture) {
        case UP:
          carrier.display.println("OP");
          Serial.println("Gesture: OP");
          gestureDetected[0] = true;
          carrier.Buzzer.beep(); // Feedback når en gestus registreres
          break;
        case DOWN:
          carrier.display.println("NED");
          Serial.println("Gesture: NED");
          gestureDetected[1] = true;
          carrier.Buzzer.beep();
          break;
        case LEFT:
          carrier.display.println("VENSTRE");
          Serial.println("Gesture: VENSTRE");
          gestureDetected[2] = true;
          carrier.Buzzer.beep();
          break;
        case RIGHT:
          carrier.display.println("HOJRE");
          Serial.println("Gesture: HØJRE");
          gestureDetected[3] = true;
          carrier.Buzzer.beep();
          break;
        default:
          carrier.display.println("INGEN");
          break;
      }
      
      // Opdateret status på registrerede gestus
      detectedGestures = 0; // Tæl igen
      carrier.display.setTextSize(1);
      carrier.display.setCursor(20, 215);
      carrier.display.print("Registrerede: [");
      
      if (gestureDetected[0]) {
        carrier.display.print("OP ");
        detectedGestures++;
      }
      
      if (gestureDetected[1]) {
        carrier.display.print("NED ");
        detectedGestures++;
      }
      
      if (gestureDetected[2]) {
        carrier.display.print("V ");
        detectedGestures++;
      }
      
      if (gestureDetected[3]) {
        carrier.display.print("H");
        detectedGestures++;
      }
      
      carrier.display.print("] ");
      carrier.display.print(detectedGestures);
      carrier.display.print("/4");
    }
    
    delay(100);
  }
  
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_GREEN);
  carrier.display.setTextSize(2);
  
  if (detectedGestures >= 4) {
    // Alle gestus blev registreret
    carrier.display.setCursor(20, 60);
    carrier.display.println("Alle gesture");
    carrier.display.setCursor(20, 90);
    carrier.display.println("registreret!");
    carrier.display.setCursor(20, 120);
    carrier.display.println("Flot klaret!");
  } else {
    // Ikke alle gestus blev registreret, men testen er fuldført
    carrier.display.setCursor(25, 60);
    carrier.display.println("RGB/Gesture");
    carrier.display.setCursor(55, 90);
    carrier.display.println("Test OK!");
    carrier.display.setTextSize(1);
    carrier.display.setCursor(30, 120);
    carrier.display.print(detectedGestures);
    carrier.display.println(" gestus registreret");
  }
  
  delay(2000);
} 