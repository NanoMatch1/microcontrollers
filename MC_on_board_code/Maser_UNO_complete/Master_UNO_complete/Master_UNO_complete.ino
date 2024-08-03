#include <Wire.h>
#include <SoftwareSerial.h>

// COM10 = Master
// COM9 = Slave A
// COM11 = Slave B
// COM14 = Slave APD pico
// When adding I2C - take code from A,B, or C, and remember to add lines in "processCommand" and "sendI2C" functions

const int picoRX = 12;  // Connect to TX of Pico
const int picoTX = 13;  // Connect to RX of Pico
const int SLAVE1_ADDRESS = 8;  // I2C address of the first slave Arduino
const int SLAVE2_ADDRESS = 9;  // I2C address of the second slave Arduino (example)
const int SLAVE3_ADDRESS = 7; // I2C address of pico APD reader slave
bool passFlag = false;

// ADP acquisition
const int checkPin = 2; // Pin to receive the interrupt signal
const int resetPin = 3;     // Pin to send the reset high signal

// Variables
volatile unsigned long counter = 0; // Counter to increment
volatile unsigned long runCounter = 0; // runtime counter to increment
float runTime = 0.0;                // Time for the interrupt loop to run
unsigned long startTime = 0;        // Start time for the interrupt loop

SoftwareSerial picoSerial(picoRX, picoTX);

void setup() {
  // Initialize pins
  pinMode(checkPin, INPUT); // Set interrupt pin as input
  pinMode(resetPin, OUTPUT);    // Set reset pin as output
  digitalWrite(resetPin, LOW);  // Ensure reset pin is initially LOW

  Serial.begin(9600);
  picoSerial.begin(9600);
  Wire.begin();  // Initialize I2C as master
  Serial.println("Arduino is ready to receive commands.");
}

void loop() {
  if (Serial.available() > 0) {
    // Read the command until a newline character is encountered
    String command = Serial.readStringUntil('\n');
    command.trim();  // Removes any leading/trailing whitespace or newline characters
    if (command.length() == 0) {  // Check if the string is empty
      // If an empty string is received, skip the rest of the loop
      return;  // Skip the rest of this iteration of loop()
    }

    // Process command
    // Serial.print("Received command: UI>UNO:");
    // Serial.println(command);
    processCommand(command);

    // Send the command to the Raspberry Pi Pico
    // picoSerial.print("UART-UNO-APD_pico:#");
    // picoSerial.println(command);
  }

  if (picoSerial.available() > 0) {
    // Read the response from the Pico until a newline character is encountered
    Serial.println("Reading from PICO - BUG");
    String response = picoSerial.readStringUntil('\n');
    response.trim();  // Removes any leading/trailing whitespace or newline characters
    if (response.length() == 0) {  // Check if the string is empty
      // If an empty string is received, skip the rest of the loop
      return;  // Skip the rest of this iteration of loop()
    }

    // Echo the message from the Pico
    // Serial.print("Message from Pico: ");
    Serial.println(response);
  }
}

void acquireAPD(float acqtime) {
  // Reset counter and start time
  counter = 0;
  digitalWrite(resetPin, HIGH);
  // delay(0.001);  // Keep the reset high for a short period
  startTime = millis();
  digitalWrite(resetPin, LOW);
  
  // Run the acquisition loop for the specified time
  while (millis() - startTime < acqtime * 1000) {
    // Check the state of the check pin
    if (digitalRead(checkPin) == HIGH) {
      // Send the reset high signal
      digitalWrite(resetPin, HIGH);
      // delay(0.001);  // Keep the reset high for a short period
      digitalWrite(resetPin, LOW);
      // Increment the counter
      counter++;
    }
  // Report the counter value to the serial monitor

  }
  Serial.print("#DAT");
  Serial.println(counter);
}

void APDcoms(String message) {
  if (message.startsWith("acq")) {
    String acqtimeStr = message.substring(3, message.length()); // get time component
    float acqtime = acqtimeStr.toFloat(); // turn into a float
    // Serial.print("Acquiring for ");
    // Serial.print(acqtime);
    // Serial.print(" seconds...\n");
    acquireAPD(acqtime);
  }
  else if (message.startsWith("run")) {
    String acqtimeStr = message.substring(3, message.length());
    float acqtime = acqtimeStr.toFloat(); // turn into a float
    Serial.println("Running for 30 loops...");
    while (runCounter < 30) {
      acquireAPD(acqtime);
      runCounter++;
    }
    runCounter = 0;
  }
  Serial.println("#CF");
}

void processCommand(String command) {
  // Example command structure: "<A:1234>"
  // Serial.println(command);
  if (command.startsWith("o") && command.endsWith("o")) {
    String content = command.substring(1, command.length() - 1);  // Remove '<' and '>'
    char device = content.charAt(0);  // First character is the device identifier
    String message = content.substring(1);  // The rest is the message
    // Serial.print("Device: ");
    // Serial.print("UNO>A:");
    // Serial.println(message);
    // Serial.println(device);
    // Serial.println("Returning for testing");
    // Serial.println("#CF");
    // return;

    switch (device) {
      case 'A':
        Serial.print("UNO>A:");
        Serial.println(message);
        sendI2C(message, SLAVE1_ADDRESS);
        break;
      case 'B':
        Serial.print("UNO>B:");
        Serial.println(message);
        sendI2C(message, SLAVE2_ADDRESS);
        break;
      case 'C':
        Serial.print("UNO>C:");
        Serial.println(message);
        sendI2C(message, SLAVE3_ADDRESS);
        break;
      case 'D':
        // Serial.print("Acquiring for ");
        // Serial.print(message);
        // Serial.println("seconds...");
        APDcoms(message);
        break;
      default:
        Serial.println("Unknown device identifier - failed to send command");
        break;
    }
  } else {
    Serial.println("Invalid command format#CF");
  }
}

void sendI2C(String message, int address) {
  Wire.beginTransmission(address);  // Start I2C transmission to the given address
  Wire.write(message.c_str());  // Send the string as bytes
  Wire.endTransmission();  // Stop I2C transmission

  delay(100); // Allow time for the slave to process the command

  // Serial.println("Receiving coms from A");
  Wire.requestFrom(address, 32);  // Request up to 32 bytes from the slave
  String response = "";
  while (Wire.available()) {
    char c = Wire.read();
    Serial.print(c);  // Print the response from the slave
    if (c == '\n') {
      break;
    }
    response += c;
  }
  // clear buffer
  while (Wire.available()) {
    Wire.read();
  }

  if (address == 8) {
    Serial.println("UI<UNO<A:" + response);
  }
  else if (address == 9) {
    Serial.println("UI<UNO<B:" + response);
  }
  else if (address == 7) {
    Serial.println("UI<UNO<C:" + response);
  }
  Serial.println("#CF");
}
