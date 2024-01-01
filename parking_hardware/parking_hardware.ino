#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <LiquidCrystal_I2C.h>

#define SS_PIN 10
#define RST_PIN 9


MFRC522 mfrc522(SS_PIN, RST_PIN);
Servo gateServo;  // create servo object to control a servo

LiquidCrystal_I2C lcd(0x27, 20, 4);
const int irSensorPins[] = {2, 3, 4, 6, 7}; 

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  gateServo.attach(8);  // attaches the servo on pin 8
  // Serial.println("Servo Control Ready");
  lcd.begin();      // Initialize the LCD
  lcd.backlight();
  for (int i = 0; i < 4; i++) {
    pinMode(irSensorPins[i], INPUT);
  }
}

void loop() {
  // Gate sensors
  int irStatus1 = digitalRead(irSensorPins[4]);
  int irStatus2 = digitalRead(irSensorPins[3]);

  //Parking sensors
  int irStatus3 = digitalRead(irSensorPins[2]);
  int irStatus4 = digitalRead(irSensorPins[1]);
  int irStatus5 = digitalRead(irSensorPins[0]);

  displaySlotsStatus(irStatus3, irStatus4, irStatus5);


  if (irStatus1 == LOW) {
    // IR Sensor 1 detects a vehicle
    // Serial.println("IR Sensor 1 detects a vehicle.");
    displayMessage("Welcome!");

    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
      String rfid = getRFID();  // Function to convert RFID bytes to String
      // Send RFID data to Python over Serial
      Serial.println(rfid+ ",isEntering");

      delay(2000);  // Add a delay to avoid reading the same card multiple times

      if (Serial.available() > 0){
        // displayMessage("Received");
        char receivedChar = Serial.read();
        // String receivedString = Serial.readStringUntil('\n');
        processPythonData(receivedChar);
      }
      //Check for data from python
      // if (Serial.available() > 0) {
      //   displayMessage("Received");
      //   char receivedChar = Serial.read();
      //   if (receivedChar == 'O') {
      //   //  processPythonCommand();
      //   openGate();
      //    displayMessage("Process");
      //   } else{
      //     displayMessage("Error Processing");
      //   }
      // } else{
      //   displayMessage("Not received");
      // }
      
    }
  }

  else if (irStatus2 == LOW) {
    // IR Sensor 2 detects a vehicle
    // Serial.println("IR Sensor 2 detects a vehicle.");

    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
      String rfid = getRFID();  // Function to convert RFID bytes to String
      // Send RFID data and status to Python over Serial
      Serial.println(rfid + ",isExiting");
        delay(2000);  // Add a delay to avoid reading the same card multiple times
    }
  }

  delay(1000);
}

void processPythonData(char receivedChar){
  if (receivedChar == 'O'){
    openGate();
    displayMessage("Opening gate");
  } else if(receivedChar == 'F'){
    displayMessage("Parking full");
  } else if(receivedChar == 'N'){
    displayMessage("Not registered");
  }
}
void processPythonCommand() {
  String command = Serial.readStringUntil('\n');

  if (command == "OPEN_GATE") {
    // Check if the IR sensor detects a vehicle (you can replace this with your own logic)
    displayMessage("Access Granted");
    openGate();
  } else{
    displayMessage("Access Denied");
  }
}

void openGate() {
  gateServo.write(90);  // Adjust the angle based on your setup
  delay(2000);          // Keep the gate open for 5 seconds
  gateServo.write(0);   // Close the gate
}

void displayMessage(String message) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(message);
  delay(2000);
}

void displaySlotsStatus(int status3, int status4, int status5) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Smart Parking System");
  lcd.setCursor(0, 1);
  lcd.print("Slot 1: " + String(status3 == LOW ? "Occupied" : "Free"));
  lcd.setCursor(0, 2);
  lcd.print("Slot 2: " + String(status4 == LOW ? "Occupied" : "Free"));
  lcd.setCursor(0, 3);
  lcd.print("Slot 3: " + String(status5 == LOW ? "Occupied" : "Free"));
  delay(2000);
}

String getRFID() {
  String rfid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    rfid += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    rfid += String(mfrc522.uid.uidByte[i], HEX);
  }
  return rfid;
}
