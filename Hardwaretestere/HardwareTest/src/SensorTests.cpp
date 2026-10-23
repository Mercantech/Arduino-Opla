#include "Hardwaretestere.h"
#include <SD.h>

bool testHumidityTemperature(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println(F("Temp & Fugt"));
  carrier.display.setCursor(20, 50);
  carrier.display.println(F("Test"));
  delay(1000);

  bool ok = false;
  float temperature = 0;
  float humidity = 0;

  for (int i = 0; i < 5; i++) {
    temperature = carrier.Env.readTemperature();
    humidity = carrier.Env.readHumidity();

    carrier.display.fillRect(0, 80, 240, 160, ST77XX_BLACK);
    carrier.display.setCursor(20, 80);
    carrier.display.print(F("Temp: "));
    carrier.display.print(temperature);
    carrier.display.println(F(" C"));
    carrier.display.setCursor(20, 120);
    carrier.display.print(F("Fugt: "));
    carrier.display.print(humidity);
    carrier.display.println(F(" %"));

    Serial.print(F("Temperatur: "));
    Serial.print(temperature);
    Serial.println(F(" C"));
    Serial.print(F("Fugtighed: "));
    Serial.print(humidity);
    Serial.println(F(" %"));

    if (temperature > -20 && temperature < 60 && humidity >= 0 && humidity <= 100) {
      ok = true;
    }
    delay(1000);
  }

  showTestResult(carrier, "Temp/Fugt", ok);
  return ok;
}

bool testPressureSensor(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println(F("Tryk Sensor"));
  delay(1000);

  bool ok = false;
  float pressure = 0;

  for (int i = 0; i < 5; i++) {
    pressure = carrier.Pressure.readPressure();

    carrier.display.fillRect(0, 80, 240, 160, ST77XX_BLACK);
    carrier.display.setCursor(20, 80);
    carrier.display.print(F("Tryk: "));
    carrier.display.print(pressure);
    carrier.display.println(F(" kPa"));
    carrier.display.setCursor(20, 120);
    carrier.display.print(pressure * 10);
    carrier.display.println(F(" hPa"));

    Serial.print(F("Tryk: "));
    Serial.print(pressure);
    Serial.println(F(" kPa"));

    // LPS22: typisk ~100 kPa ved havniveau (bibliotek kan også give hPa)
    if (pressure > 20 && pressure < 2000) {
      ok = true;
    }
    delay(1000);
  }

  showTestResult(carrier, "Tryk", ok);
  return ok;
}

bool testIMU(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println(F("IMU Sensor"));
  carrier.display.setCursor(20, 50);
  carrier.display.println(F("Bevoeg kortet"));
  delay(2000);

  float ax, ay, az, gx, gy, gz;
  bool accelOk = false;
  bool gyroOk = false;
  unsigned long startTime = millis();

  while (millis() - startTime < 10000) {
    carrier.display.fillRect(0, 90, 240, 150, ST77XX_BLACK);
    carrier.display.setTextSize(1);

    if (carrier.IMUmodule.accelerationAvailable()) {
      carrier.IMUmodule.readAcceleration(ax, ay, az);
      carrier.display.setCursor(20, 95);
      carrier.display.print(F("A X:"));
      carrier.display.print(ax);
      carrier.display.print(F(" Y:"));
      carrier.display.print(ay);
      carrier.display.print(F(" Z:"));
      carrier.display.println(az);
      Serial.print(F("Accel X:"));
      Serial.print(ax);
      Serial.print(F(" Y:"));
      Serial.print(ay);
      Serial.print(F(" Z:"));
      Serial.println(az);
      // Z ca. 1g i ro
      if (fabs(ax) < 5 && fabs(ay) < 5 && fabs(az) < 5) {
        accelOk = true;
      }
    }

    if (carrier.IMUmodule.gyroscopeAvailable()) {
      carrier.IMUmodule.readGyroscope(gx, gy, gz);
      carrier.display.setCursor(20, 130);
      carrier.display.print(F("G X:"));
      carrier.display.print(gx);
      carrier.display.print(F(" Y:"));
      carrier.display.print(gy);
      carrier.display.print(F(" Z:"));
      carrier.display.println(gz);
      Serial.print(F("Gyro X:"));
      Serial.print(gx);
      Serial.print(F(" Y:"));
      Serial.print(gy);
      Serial.print(F(" Z:"));
      Serial.println(gz);
      gyroOk = true;
    }

    delay(100);
  }

  bool ok = accelOk && gyroOk;
  showTestResult(carrier, "IMU", ok);
  return ok;
}

bool testRGBGestureSensor(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(40, 20);
  carrier.display.println(F("RGB & Gesture"));
  carrier.display.setTextSize(1);
  carrier.display.setCursor(20, 60);
  carrier.display.println(F("Bevaeg haanden over sensor"));
  carrier.display.setCursor(20, 75);
  carrier.display.println(F("OP/NED/VENSTRE/HOJRE"));
  delay(2500);

  int r, g, b;
  int proximity = 0;
  bool colorOk = false;
  bool proxOk = false;
  unsigned long startTime = millis();
  int detectedGestures = 0;
  bool gestureDetected[4] = {false, false, false, false};

  while ((millis() - startTime < 25000) && detectedGestures < 4) {
    carrier.display.fillRect(0, 100, 240, 140, ST77XX_BLACK);
    carrier.display.setTextSize(1);

    if (carrier.Light.colorAvailable()) {
      carrier.Light.readColor(r, g, b);
      carrier.display.setCursor(20, 105);
      carrier.display.print(F("R:"));
      carrier.display.print(r);
      carrier.display.print(F(" G:"));
      carrier.display.print(g);
      carrier.display.print(F(" B:"));
      carrier.display.println(b);
      carrier.display.fillRect(150, 105, 40, 20, carrier.display.color565(r, g, b));
      Serial.print(F("RGB R:"));
      Serial.print(r);
      Serial.print(F(" G:"));
      Serial.print(g);
      Serial.print(F(" B:"));
      Serial.println(b);
      colorOk = true;
    }

    if (carrier.Light.proximityAvailable()) {
      proximity = carrier.Light.readProximity();
      carrier.display.setCursor(20, 130);
      carrier.display.print(F("Proximity: "));
      carrier.display.println(proximity);
      Serial.print(F("Proximity: "));
      Serial.println(proximity);
      proxOk = true;
    }

    if (carrier.Light.gestureAvailable()) {
      uint8_t gesture = carrier.Light.readGesture();
      carrier.display.setTextSize(2);
      carrier.display.setCursor(20, 155);
      carrier.display.print(F("G: "));
      switch (gesture) {
        case UP:
          carrier.display.println(F("OP"));
          gestureDetected[0] = true;
          maybeBeep(carrier);
          break;
        case DOWN:
          carrier.display.println(F("NED"));
          gestureDetected[1] = true;
          maybeBeep(carrier);
          break;
        case LEFT:
          carrier.display.println(F("VENSTRE"));
          gestureDetected[2] = true;
          maybeBeep(carrier);
          break;
        case RIGHT:
          carrier.display.println(F("HOJRE"));
          gestureDetected[3] = true;
          maybeBeep(carrier);
          break;
        default:
          carrier.display.println(F("-"));
          break;
      }
      detectedGestures = 0;
      for (int i = 0; i < 4; i++) {
        if (gestureDetected[i]) detectedGestures++;
      }
    }

    delay(100);
  }

  // Farve + proximity er nok til PASS; gesture er bonus (manuel)
  bool ok = colorOk && proxOk;
  showTestResult(carrier, "RGB/Prox", ok);
  return ok;
}

bool testSDCard(MKRIoTCarrier &carrier) {
  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(20, 20);
  carrier.display.println(F("SD Kort"));
  delay(800);

  // SD initialiseres typisk i carrier.begin(); prøv alligevel
  bool ok = false;
  const char *path = "oplatest.txt";
  const char *payload = "opla-ok";

  File f = SD.open(path, FILE_WRITE);
  if (f) {
    f.print(payload);
    f.close();

    f = SD.open(path, FILE_READ);
    if (f) {
      char buf[16] = {0};
      int n = f.read(buf, sizeof(buf) - 1);
      f.close();
      SD.remove(path);
      if (n > 0 && strstr(buf, "opla") != NULL) {
        ok = true;
      }
    }
  }

  if (!ok) {
    Serial.println(F("SD: ingen kort eller I/O-fejl"));
  } else {
    Serial.println(F("SD: skriv/laes OK"));
  }

  showTestResult(carrier, "SD Kort", ok);
  return ok;
}
