#include <Wire.h>
#include <SoftwareSerial.h>

const int countEnable = 13;     // Pin for resetting latch to LOW. Note Active-LOW
const int counterClear = 12;  // Pin clearing the counter IC
const int loadRegisterPin = 9; // Pin for loading counter values into the storage register
const int lastDigit = 10;    // Pin for reading the last digit of the counters

const int picoRX = 2;  // Connect to TX of Pico
const int picoTX = 3;  // Connect to RX of Pico

SoftwareSerial picoSerial(picoRX, picoTX);

void setup() {
  Serial.begin(9600);
  picoSerial.begin(9600);
  // pinMode(ledPin, OUTPUT);
  pinMode(counterClear, OUTPUT);
  pinMode(lastDigit, INPUT);
  pinMode(countEnable, OUTPUT);

  digitalWrite(countEnable, LOW); // disable the toggle flip flop, initial state of output is 0V when countEnable is LOW.
  digitalWrite(counterClear, LOW); // clear the counter initially. Active-LOW
  digitalWrite(counterClear, HIGH); // HIGH keeps counter from clearing. 

  digitalWrite(loadRegisterPin, LOW);
  Serial.println("Ready to receive commands:");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim(); // Remove any leading/trailing whitespace
    parseInput(input);
  }
}

void sendToPico(String command) {
    picoSerial.print("UART-UNO-APD_pico:#");
    picoSerial.println(command);
}

String readFromPico() {
  String response = ""; // Initialize the response variable

  if (picoSerial.available() > 0) {
    // Read the response from the Pico until a newline character is encountered
    // Serial.println("Reading from PICO - BUG");
    String response = picoSerial.readStringUntil('\n');
    response.trim();  // Removes any leading/trailing whitespace or newline characters
    // if (response.length() == 0) {  // Check if the string is empty
    //   // If an empty string is received, skip the rest of the loop
    //   return response;  // Skip the rest of this iteration of loop()
    // }

    // Echo the message from the Pico
    // Serial.print("Message from Pico: ");
  }
  return response;
  }

void parseInput(String input) {
  int spaceIndex = input.indexOf(' ');

  if (spaceIndex == -1) {
    Serial.println("Error: Invalid input format. Use <command> <value>.");
    return;
  }

  String command = input.substring(0, spaceIndex);
  String valueStr = input.substring(spaceIndex + 1);
  // float value = valueStr.toFloat();

  performCommand(command, valueStr);
}

String acquireData(float acquisitionTime) {
  digitalWrite(counterClear, LOW); // clear counter, active-low
  digitalWrite(counterClear, HIGH);

  digitalWrite(countEnable, HIGH); // flip flip is now active, counting can begin at CLKA/B
  
  unsigned long startTime = micros();
  unsigned long waitTime = startTime + (unsigned long)(acquisitionTime * 1000000);
  
  while (micros() < waitTime) {
    // Busy-waiting for the acquisition time to elapse
  }

  digitalWrite(countEnable, LOW); // flip flop inactive, Q = LOW // Ends counting signal, holds counts
  unsigned long endTime = micros(); // timestamp end of counting
  digitalWrite(loadRegisterPin, HIGH); // LOAD The values into the register...
  delay(1);
  digitalWrite(loadRegisterPin, LOW); 

  sendToPico("read");
  int finalBit = digitalRead(lastDigit); // grabs the final bit from the flip flop
  Serial.print("finalBit: ");
  Serial.println(finalBit);

  while (picoSerial.available() > 0) {
    String response = readFromPico();
    Serial.println(response);
  }
  String response = readFromPico();
  // Serial.print("")
  // Serial.println(response);

  // process the pico response and bits here

  unsigned long elapsedTime = endTime - startTime;
  Serial.print("Elapsed time: ");
  Serial.print(elapsedTime);
  Serial.println(" us");

  // return a response of counts and time

  return response;
}

void performCommand(String command, String value) {
  if (command == "t") {
    float floatValue = value.toFloat();
    String readResponse = acquireData(floatValue);
    Serial.print("Final data from pico: ");
    Serial.println(readResponse);
    // Serial.print("Counts: ");
    // Serial.println(counts);
  } 
  else if (command == "e") {
    if (value == "1") {
      digitalWrite(countEnable, HIGH);
      Serial.println("Enable set to HIGH");
      // Serial.println(SD);
    }
    else if (value == "0") {
      digitalWrite(countEnable, LOW);
      Serial.println("Enable set to LOW");
    }
  }
  else {
    Serial.println("Error: Unknown command.");
  }
}
