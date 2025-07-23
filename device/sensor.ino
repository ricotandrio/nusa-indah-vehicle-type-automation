#include <Wire.h>
#include <VL6180X.h>
#include <LiquidCrystal_I2C.h>

// set the LCD address to 0x27 for a 16 chars and 2 line display
LiquidCrystal_I2C lcd(0x27,20,4);  

VL6180X sensor1;
VL6180X sensor2;

const int SHUT1 = 16;  // GPIO pin for sensor 1 shutdown
const int SHUT2 = 17;  // GPIO pin for sensor 2 shutdown

void setup() {
  Serial.begin(115200);
  Wire.begin();

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0,0);
  lcd.print("Nusa Indah!");

  // Set SHUT pins as outputs
  pinMode(SHUT1, OUTPUT);
  pinMode(SHUT2, OUTPUT);

  // Step 1: SHUT both sensors
  digitalWrite(SHUT1, LOW);
  digitalWrite(SHUT2, LOW);
  delay(10);

  // Step 2: Power on Sensor 1
  digitalWrite(SHUT1, HIGH);
  delay(10);
  sensor1.init();
  sensor1.configureDefault();
  sensor1.setAddress(0x30); // Change from default 0x29
  sensor1.setTimeout(500);

  // Step 3: Power on Sensor 2
  digitalWrite(SHUT2, HIGH);
  delay(10);
  sensor2.init(); // Stays at default address 0x29
  sensor2.configureDefault();
  sensor2.setTimeout(500);
}

void loop() {
  uint16_t d1 = sensor1.readRangeSingleMillimeters();
  uint16_t d2 = sensor2.readRangeSingleMillimeters();
  unsigned long ts = millis();
  const int WIDTH = 100;

  Serial.print("Time: ");
  Serial.print(ts);
  Serial.print(" ms | Sensor 1 (0x30): ");
  Serial.print(d1);
  Serial.print(" mm | Sensor 2 (0x29): ");
  Serial.print(d2);
  Serial.print(" mm");
  Serial.print(" | Tire Width: ");

  int tireWidth = WIDTH - d1 - d2;
  Serial.print(tireWidth);
  Serial.println(" mm");

  lcd.setCursor(0, 1);
  lcd.print(d1);

  lcd.setCursor(5, 1);
  lcd.print(" | ");
  lcd.print(d2);

  delay(250);

  lcd.setCursor(0, 1);        

  // Clear the LCD display
  lcd.print("                ");
}