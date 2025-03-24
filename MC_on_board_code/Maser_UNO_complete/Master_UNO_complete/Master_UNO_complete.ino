#include <Wire.h>
#include <SoftwareSerial.h>

// Pin definitions
const int picoRX = 19;  // Connect to TX of Pico
const int picoTX = 18;  // Connect to RX of Pico
const int SLAVE1_ADDRESS = 8;
const int SLAVE2_ADDRESS = 9;
const int SLAVE3_ADDRESS = 7;

const int countEnable = 13;  // Active-LOW latch reset
const int counterClear = 12; // Counter IC clear pin
const int lastDigit = 11;    // Last digit read pin
  const int gShutPin = 9;      // Grating shutter pin
const int ldr0pin = A15;      // LDR input pin

// Variables
int ldr0value = 0;
volatile unsigned long counter = 0;

// Serial communication
SoftwareSerial picoSerial(picoRX, picoTX);

void setup() {
  pinMode(counterClear, OUTPUT);
  pinMode(lastDigit, INPUT);
  pinMode(countEnable, OUTPUT);
  pinMode(gShutPin, OUTPUT);

  digitalWrite(countEnable, LOW);  // Initial states
  digitalWrite(counterClear, LOW);
  digitalWrite(gShutPin, LOW);

  Serial.begin(9600);
  picoSerial.begin(9600);
  Wire.begin();
  Serial.println("Arduino ready to receive commands.");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command.length() > 0) {
      processCommand(command);
      Serial.println("#CF");
    }
  }
}

void processCommand(String command) {
  if (command.startsWith("p") && command.endsWith("p")) {
    String message = command.substring(1, command.length() - 1);
    Serial.println("Sending to Pico...");
    int result = sendToPico(message);
    if (result == 1) {
      String response = readFromPico();
      Serial.print("Response from Pico: ");
      Serial.println(response);
    } else {
      Serial.println("Error: Communication with Pico failed.");
    }
  } else if (command.startsWith("m") && command.endsWith("m")) {
    String content = command.substring(1, command.length() - 1);
    String com = content.substring(0, 3);
    String comvalstring = content.substring(4); //Assumes space in message

    if (com == "acq") {
      float acqTime = comvalstring.toFloat();
      acquireAPD(acqTime);
    } else if (com == "gsh") {
      monoShutter(comvalstring);
    } else if (com == "ld0") {
      readLDR();
    } else {
      Serial.println("Unknown command.");
    }
  } else if (command.startsWith("o") && command.endsWith("o")) {
    String content = command.substring(1, command.length() - 1);
    char device = content.charAt(0);  // First character is the device identifier
    String message = content.substring(1);  // The rest is the message

    switch (device) {
      case 'A':
        sendI2C(message, SLAVE1_ADDRESS);
        break;
      case 'B':
        sendI2C(message, SLAVE2_ADDRESS);
        break;
      case 'C':
        sendI2C(message, SLAVE3_ADDRESS);
        break;
      default:
        Serial.println("Unknown device identifier - failed to send command.");
        break;
    }
  } else {
    Serial.println("Invalid command format.");
  }
}

void monoShutter(String state) {
  if (state == "on") {
    digitalWrite(gShutPin, LOW);
    Serial.println("Shutter closed.");
  } else if (state == "off") {
    digitalWrite(gShutPin, HIGH);
    Serial.println("Shutter open.");
  }
}

void readLDR() {
  int count = 0;
  ldr0value = 0;
  while (count < 10) {
    ldr0value += analogRead(ldr0pin);
    count++;
  }
  Serial.print('t');
  Serial.println(ldr0value);
}

int sendToPico(String command) {
  picoSerial.println(command);
  for (int i = 0; i < 1000; i++) {
    if (picoSerial.available() > 0) {
      return 1;
    }
    delay(1);
  }
  return 0;
}

String readFromPico() {
  if (picoSerial.available() > 0) {
    String response = picoSerial.readStringUntil('\n');
    response.trim();
    return response;
  }
  return "";
}

void acquireAPD(float acquisitionTime) {
  digitalWrite(counterClear, HIGH);
  digitalWrite(countEnable, HIGH);

  unsigned long startTime = micros();
  while (micros() - startTime < (unsigned long)(acquisitionTime * 1e6)) {
    // Busy-wait for acquisition
  }

  digitalWrite(countEnable, LOW);
  unsigned long elapsedTime = micros() - startTime;

  Serial.print("Elapsed Time (us): ");
  Serial.println(elapsedTime);
}

void sendI2C(String message, int address) {
  Wire.beginTransmission(address);
  Wire.write(message.c_str());
  Wire.endTransmission();

  delay(100); // Allow slave to process

  Wire.requestFrom(address, 32);
  String response = "";
  while (Wire.available()) {
    char c = Wire.read();
    if (c == '\n') {
      break;
    }
    response += c;
  }

  if (address == SLAVE1_ADDRESS) {
    Serial.println("<A:" + response);
  } else if (address == SLAVE2_ADDRESS) {
    Serial.println("<B:" + response);
  } else if (address == SLAVE3_ADDRESS) {
    Serial.println("<C:" + response);
  }
}
