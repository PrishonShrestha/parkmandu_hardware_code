#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <LiquidCrystal_I2C.h>

#define SS_PIN 10
#define RST_PIN 9


MFRC522 mfrc522(SS_PIN, RST_PIN);
Servo myservo;  // create servo object to control a servo

LiquidCrystal_I2C lcd(0x27, 20, 4);
const int irSensorPins[] = {2, 3, 4, 6, 7}; 

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  myservo.attach(8);  // attaches the servo on pin 8
  // Serial.println("Servo Control Ready");
  lcd.begin();      // Initialize the LCD
  lcd.backlight();
  for (int i = 0; i < 4; i++) {
    pinMode(irSensorPins[i], INPUT);
  }
}

void loop() {
  int irStatus1 = digitalRead(irSensorPins[4]);
  int irStatus2 = digitalRead(irSensorPins[3]);

  if (irStatus1 == LOW) {
    // IR Sensor 1 detects a vehicle
    // Serial.println("IR Sensor 1 detects a vehicle.");

    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
      String rfid = getRFID();  // Function to convert RFID bytes to String
      // Send RFID data to Python over Serial
      Serial.println(rfid+ ",isEntering");
      delay(5000);  // Add a delay to avoid reading the same card multiple times
    }
    delay(5000);
  }

  else if (irStatus2 == LOW) {
    // IR Sensor 2 detects a vehicle
    // Serial.println("IR Sensor 2 detects a vehicle.");

    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
      String rfid = getRFID();  // Function to convert RFID bytes to String
      // Send RFID data and status to Python over Serial
      Serial.println(rfid + ",isExiting");
      delay(5000);  // Add a delay to avoid reading the same card multiple times
    }
    delay(5000);
  }

  delay(1000);
}

String getRFID() {
  String rfid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    rfid += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    rfid += String(mfrc522.uid.uidByte[i], HEX);
  }
  return rfid;
}
