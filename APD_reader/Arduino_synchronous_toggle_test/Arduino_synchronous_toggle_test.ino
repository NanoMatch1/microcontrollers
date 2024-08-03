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
  pinMode(counterClear, OUTPUT);
  pinMode(lastDigit, INPUT);
  pinMode(countEnable, OUTPUT);

  digitalWrite(countEnable, LOW); // disable the toggle flip flop, initial state of output is 0V when countEnable is LOW.
  digitalWrite(counterClear, LOW); // clear the counter initially. Active-LOW
  // digitalWrite(counterClear, HIGH); // HIGH keeps counter from clearing. 

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

void flushSerialBuffer(SoftwareSerial &serial) {
  while (serial.available() > 0) {
    serial.read();
  }
}

void sendToPico(String command) {
    picoSerial.print("UART-UNO-APD_pico:#");
    picoSerial.println(command);
    // flushSerialBuffer(picoSerial);
}

String readFromPico() {
  String response = ""; // Initialize the response variable outside the if block
  unsigned long time_start = millis();


  if (picoSerial.available() > 0) {
    // Read the response from the Pico until a newline character is encountered
    response = picoSerial.readStringUntil('\n');
    response.trim();  // Removes any leading/trailing whitespace or newline characters
    if (response.length() == 0) {  // Check if the string is empty
      // If an empty string is received, return immediately
      return response;
    }

    // Echo the message from the Pico
    // Serial.println(response);
    return response;
  }

}

void parseInput(String input) {
  int spaceIndex = input.indexOf(' ');

  if (spaceIndex == -1) {
    Serial.println("Error: Invalid input format. Use <command> <value>.");
    return;
  }

  String command = input.substring(0, spaceIndex);
  String valueStr = input.substring(spaceIndex + 1);

  performCommand(command, valueStr);
}

String acquireData(float acquisitionTime) {
  // digitalWrite(counterClear, LOW); // clear counter, active-low
  digitalWrite(counterClear, HIGH); // Also triggers the flip flop to be active. LOW forces flip flop reset

  digitalWrite(countEnable, HIGH); // One side of AND gate. Signal passes to flip flop
  
  unsigned long startTime = micros();
  unsigned long waitTime = startTime + (unsigned long)(acquisitionTime * 1000000);
  
  while (micros() < waitTime) {
    // Busy-waiting for the acquisition time to elapse
  }
  
  digitalWrite(countEnable, LOW); // AND gate LOW // Ends counting signal, holds counts and FLIP FLOP
  unsigned long endTime = micros(); // timestamp end of counting
  
  bool finalBit = digitalRead(lastDigit);

  digitalWrite(loadRegisterPin, HIGH); // LOAD The values into the register...
  delay(1);
  digitalWrite(loadRegisterPin, LOW); 

  finalBit = digitalRead(lastDigit);

  sendToPico("read");
  Serial.print("finalBit: ");
  Serial.println(finalBit);

  // delay(1000);
  unsigned long wait_time = millis();
  
  while (millis() < (wait_time + 5*1000)) {
    while (picoSerial.available() == 0) {
      delay(1);
      // do nothing and wait
    }
  
    String response = readFromPico();
    Serial.println(response);
    unsigned long elapsedTime = endTime - startTime;
    int data_index = response.indexOf('+');
    String data = response.substring(data_index+1);
    // int counts = data.toInt();
    // float corrected_counts = round(counts*0.999969);

    Serial.print("COUNTS: ");
    Serial.println(data);
    Serial.print("Elapsed time: ");
    Serial.print(elapsedTime);
    Serial.println(" us");
    delay(500);
    digitalWrite(counterClear, LOW); // reset counter, active-low

    return response;
  }
  Serial.println("TIMEOUT waiting for PICO response.");
}

void performCommand(String command, String value) {
  if (command == "t") {
    float floatValue = value.toFloat();
    String response = acquireData(floatValue);
    // Serial.print("Final:");
    // Serial.println(response);
  } 
  else if (command == "r") {
    sendToPico("echo");
    delay(100);
    String response = readFromPico();
    if (response.length() > 0) {
      Serial.print("Message from Pico: ");
      Serial.println(response);
    }
  }
  else if (command == "e") {
    if (value == "1") {
      digitalWrite(countEnable, HIGH);
      Serial.println("Enable set to HIGH");
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
