#include <Arduino_MKRIoTCarrier.h>

MKRIoTCarrier carrier;

void setup() {
  Serial.begin(9600);
  while (!Serial);
  carrier.begin();
}

void loop() {
  float temperature = carrier.Env.readTemperature();
  Serial.print("Temperatur: ");
  Serial.print(temperature);
  Serial.println(" °C");
  delay(1000);
}