#include "Hardwaretestere.h"
#include <SD.h>
#include <math.h>

bool testHumidityTemperature(MKRIoTCarrier &carrier) {
  clearDisplay(carrier);
  drawCenteredF(carrier, F("Temp & Fugt"), OLED_CY - 12, 2, ST77XX_WHITE);
  delay(1000);

  bool ok = false;
  float temperature = 0;
  float humidity = 0;
  char line[32];

  for (int i = 0; i < 5; i++) {
    temperature = carrier.Env.readTemperature();
    humidity = carrier.Env.readHumidity();

    clearDisplay(carrier);
    drawCenteredF(carrier, F("Temp & Fugt"), 45, 2, ST77XX_CYAN);
    snprintf(line, sizeof(line), "%.1f C", temperature);
    drawCentered(carrier, line, 100, 3, ST77XX_WHITE);
    snprintf(line, sizeof(line), "%.0f %%", humidity);
    drawCentered(carrier, line, 145, 2, ST77XX_WHITE);

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

  snprintf(line, sizeof(line), "temp_c=%.2f humidity=%.1f", temperature, humidity);
  setTestNote(line);
  showTestResult(carrier, "Temp/Fugt", ok);
  return ok;
}

bool testPressureSensor(MKRIoTCarrier &carrier) {
  clearDisplay(carrier);
  drawCenteredF(carrier, F("Tryk"), OLED_CY - 12, 2, ST77XX_WHITE);
  delay(1000);

  bool ok = false;
  float pressure = 0;
  char line[32];

  for (int i = 0; i < 5; i++) {
    pressure = carrier.Pressure.readPressure();

    clearDisplay(carrier);
    drawCenteredF(carrier, F("Tryk"), 50, 2, ST77XX_CYAN);
    snprintf(line, sizeof(line), "%.2f kPa", pressure);
    drawCentered(carrier, line, 105, 2, ST77XX_WHITE);
    snprintf(line, sizeof(line), "%.0f hPa", pressure * 10);
    drawCentered(carrier, line, 145, 2, ST77XX_WHITE);

    Serial.print(F("Tryk: "));
    Serial.print(pressure);
    Serial.println(F(" kPa"));

    if (pressure > 20 && pressure < 2000) {
      ok = true;
    }
    delay(1000);
  }

  snprintf(line, sizeof(line), "pressure_kpa=%.2f", pressure);
  setTestNote(line);
  showTestResult(carrier, "Tryk", ok);
  return ok;
}

bool testIMU(MKRIoTCarrier &carrier) {
  clearDisplay(carrier);
  drawCenteredF(carrier, F("IMU"), 55, 3, ST77XX_WHITE);
  drawCenteredF(carrier, F("Bevoeg kortet"), 120, 2, ST77XX_CYAN);
  delay(2000);

  float ax = 0, ay = 0, az = 0, gx = 0, gy = 0, gz = 0;
  bool accelOk = false;
  bool gyroOk = false;
  unsigned long startTime = millis();
  char line[40];

  while (millis() - startTime < 10000) {
    clearDisplay(carrier);
    drawCenteredF(carrier, F("IMU"), 40, 2, ST77XX_CYAN);

    if (carrier.IMUmodule.accelerationAvailable()) {
      carrier.IMUmodule.readAcceleration(ax, ay, az);
      snprintf(line, sizeof(line), "A %.1f %.1f %.1f", ax, ay, az);
      drawCentered(carrier, line, 90, 1, ST77XX_WHITE);
      Serial.print(F("Accel X:"));
      Serial.print(ax);
      Serial.print(F(" Y:"));
      Serial.print(ay);
      Serial.print(F(" Z:"));
      Serial.println(az);
      if (fabs(ax) < 5 && fabs(ay) < 5 && fabs(az) < 5) {
        accelOk = true;
      }
    }

    if (carrier.IMUmodule.gyroscopeAvailable()) {
      carrier.IMUmodule.readGyroscope(gx, gy, gz);
      snprintf(line, sizeof(line), "G %.0f %.0f %.0f", gx, gy, gz);
      drawCentered(carrier, line, 120, 1, ST77XX_WHITE);
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
  snprintf(line, sizeof(line), "accel=%.2f,%.2f,%.2f gyro=%.1f,%.1f,%.1f", ax, ay, az, gx, gy, gz);
  setTestNote(line);
  showTestResult(carrier, "IMU", ok);
  return ok;
}

bool testRGBGestureSensor(MKRIoTCarrier &carrier) {
  clearDisplay(carrier);
  drawCenteredF(carrier, F("RGB Gesture"), 50, 2, ST77XX_WHITE);
  drawCenteredF(carrier, F("Sving haanden"), 100, 1, ST77XX_CYAN);
  drawCenteredF(carrier, F("OP NED V H"), 120, 1, ST77XX_CYAN);
  delay(2500);

  int r, g, b;
  int proximity = 0;
  bool colorOk = false;
  bool proxOk = false;
  unsigned long startTime = millis();
  int detectedGestures = 0;
  bool gestureDetected[4] = {false, false, false, false};
  char line[40];

  while ((millis() - startTime < 25000) && detectedGestures < 4) {
    clearDisplay(carrier);
    drawCenteredF(carrier, F("RGB Gesture"), 36, 2, ST77XX_CYAN);

    if (carrier.Light.colorAvailable()) {
      carrier.Light.readColor(r, g, b);
      snprintf(line, sizeof(line), "R%d G%d B%d", r, g, b);
      drawCentered(carrier, line, 70, 1, ST77XX_WHITE);
      carrier.display.fillCircle(OLED_CX, 100, 14, carrier.display.color565(r, g, b));
      colorOk = true;
    }

    if (carrier.Light.proximityAvailable()) {
      proximity = carrier.Light.readProximity();
      snprintf(line, sizeof(line), "Prox %d", proximity);
      drawCentered(carrier, line, 125, 1, ST77XX_WHITE);
      proxOk = true;
    }

    if (carrier.Light.gestureAvailable()) {
      uint8_t gesture = carrier.Light.readGesture();
      const char *gName = "-";
      switch (gesture) {
        case UP:
          gName = "OP";
          gestureDetected[0] = true;
          maybeBeep(carrier);
          break;
        case DOWN:
          gName = "NED";
          gestureDetected[1] = true;
          maybeBeep(carrier);
          break;
        case LEFT:
          gName = "VENSTRE";
          gestureDetected[2] = true;
          maybeBeep(carrier);
          break;
        case RIGHT:
          gName = "HOJRE";
          gestureDetected[3] = true;
          maybeBeep(carrier);
          break;
        default:
          break;
      }
      drawCentered(carrier, gName, 155, 2, ST77XX_YELLOW);
      detectedGestures = 0;
      for (int i = 0; i < 4; i++) {
        if (gestureDetected[i]) detectedGestures++;
      }
      snprintf(line, sizeof(line), "%d/4", detectedGestures);
      drawCentered(carrier, line, 185, 1, ST77XX_WHITE);
    }

    delay(100);
  }

  bool ok = colorOk && proxOk;
  snprintf(line, sizeof(line), "rgb=%d,%d,%d prox=%d gestures=%d/4", r, g, b, proximity, detectedGestures);
  setTestNote(line);
  showTestResult(carrier, "RGB/Prox", ok);
  return ok;
}

bool testSDCard(MKRIoTCarrier &carrier) {
  clearDisplay(carrier);
  drawCenteredF(carrier, F("SD Kort"), OLED_CY - 12, 2, ST77XX_WHITE);
  delay(800);

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
    setTestNote("rw=fail");
  } else {
    Serial.println(F("SD: skriv/laes OK"));
    setTestNote("rw=ok");
  }

  showTestResult(carrier, "SD Kort", ok);
  return ok;
}
