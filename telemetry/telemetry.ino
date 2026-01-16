#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 10, 9, 8, 7);
int contrastPin = 3;

String incomingData = "";
int speed = 0;

void setup() {
  lcd.begin(16, 2);
  Serial.begin(9600);

  pinMode(contrastPin, OUTPUT);
  analogWrite(contrastPin, 100);

  lcd.clear();
  lcd.print("DRIVE DASH");
  lcd.setCursor(0, 1);
  lcd.print("Waiting...");
}

void loop() {
  while (Serial.available()) {
    char character = Serial.read();
    incomingData += character;

    if (character == '\n') {

      speed = incomingData.toInt();

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("SPEED:");

      lcd.setCursor(0, 1);
      lcd.print(speed);
      lcd.print(" km/h");

      incomingData = "";
    }
  }
}