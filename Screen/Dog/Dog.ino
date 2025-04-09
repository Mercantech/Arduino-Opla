#include <Arduino_MKRIoTCarrier.h>
#include "dog.h"  // Include the visuals.h file containing the bitmap data
 
MKRIoTCarrier carrier;
 
void setup() {
  Serial.begin(9600);
  delay(1500);
  carrier.begin();  // Initialize the MKR IoT Carrier
 
  carrier.display.fillScreen(0x0000);  // Clear the screen
  carrier.display.drawBitmap(
    0,   // x postition
    0,   // y position
    epd_bitmap_drawn,    // bitmap data
    240,    // billedets bredde
    240,    //billedets højde
    0xFFFF);  // farve
}
 
void loop() {
  // Nothing to do in the loop for now. You can add functionality here.
}