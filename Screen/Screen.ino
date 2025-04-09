#include <Arduino_MKRIoTCarrier.h>
#include "mercantec.h"
#include "dog.h"

MKRIoTCarrier carrier;

// Variabel til at holde styr på hvilket billede der vises
int currentImage = 0;

// Erstat den eksisterende bitmap array med Mercantec billedet
extern const unsigned char epd_bitmap_mercantec[] PROGMEM;

void setup() {
  Serial.begin(9600);
  // Initialiser carrier
  carrier.begin();
  
  // Sæt baggrunden til sort
  carrier.display.fillScreen(0x0000);
  
  // Vis det første billede
  showCurrentImage();
}

void showCurrentImage() {
  // Ryd skærmen først
  carrier.display.fillScreen(0x0000);
  
  if (currentImage == 0) {
    // Vis Mercantec logo
    carrier.display.drawBitmap(
      5,                           // x position
      10,                          // y position
      epd_bitmap_mercantec,        // bitmap data
      225,                         // billedets bredde i pixels
      225,                         // billedets højde i pixels
      0xFFFF                       // farve (hvid)
    );
  } else {
    // Vis hunde billedet
    carrier.display.drawBitmap(
      0,                          // x position
      0,                          // y position
      epd_bitmap_drawn,           // bitmap data
      240,                        // billedets bredde i pixels
      240,                        // billedets højde i pixels
      0xFFFF                      // farve (hvid)
    );
  }
}

void loop() {
  // Opdater knappernes status
  carrier.Buttons.update();
  
  // Skift billede ved tryk på knap 0 (venstre)
  if (carrier.Buttons.onTouchDown(TOUCH0)) {
    currentImage = 0;  // Skift til Mercantec logo
    showCurrentImage();
    Serial.println("Viser Mercantec logo");
  }
  
  // Skift billede ved tryk på knap 1 (højre)
  if (carrier.Buttons.onTouchDown(TOUCH1)) {
    currentImage = 1;  // Skift til hunde billede
    showCurrentImage();
    Serial.println("Viser hunde billede");
  }
}
