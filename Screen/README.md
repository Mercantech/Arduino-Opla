# Arduino Opla : Skærmen

Indbygget i jeres MKR IoT Carrier, findes der en OLED Skærm. Den er lidt speciel da den er rund og at start punktet altså (0,0) er ude for skærmen.

## Specifikationer

- Type: Rund OLED-skærm
- Opløsning: 240x240 pixels
- Synligt område: Cirkulært med radius ~117 pixels
- Centrum: (120, 120)

## Grundlæggende Funktioner

### Initialisering

```cpp
#include <Arduino_MKRIoTCarrier.h>
MKRIoTCarrier carrier;
carrier.begin();
```

### Vigtige Display Funktioner

1. Fyld skærmen med en farve:

```cpp
carrier.display.fillScreen(farve);
```

2. Tegn en cirkel:

```cpp
carrier.display.drawCircle(x, y, radius, farve);
```

3. Tegn en linje:

```cpp
carrier.display.drawLine(x1, y1, x2, y2, farve);
```

4. Vis et bitmap billede:

```cpp
carrier.display.drawBitmap(x, y, bitmap_data, bredde, højde, farve);
```

## Farver

Farverne defineres i 16-bit format:

- Sort: `0x0000`
- Hvid: `0xFFFF`
- Gul: `0xFFE0`
- Grøn: `0x07E0`

## Bemærkninger

- Da skærmen er rund, er hjørnerne af koordinatsystemet ikke synlige
- Start koordinatet (0,0) ligger uden for det synlige område
- Ved placering af elementer, husk at tage højde for den runde form
- Det anbefales at centrere vigtige elementer omkring (120, 120)

## Eksempel

Se `Screen.ino` for et komplet eksempel på hvordan man:

1. Initialiserer skærmen
2. Rydder skærmen med en baggrundsfarve
3. Tegner hjælpelinjer og en cirkel
4. Viser et bitmap billede
