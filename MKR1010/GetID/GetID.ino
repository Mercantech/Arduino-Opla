void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Adresse til det unikke chip ID (4 x 32-bit = 128-bit)
  uint32_t* id_ptr = (uint32_t*)0x0080A00C;

  Serial.print("Unikt chip ID: ");
  for (int i = 0; i < 4; i++) {
    if (id_ptr[i] < 0x10000000) Serial.print("0"); // Padding
    Serial.print(id_ptr[i], HEX);
  }
  Serial.println();
}

void loop() {
  // Ingen loop
}
