#include <Wire.h>
#include <SoftwareSerial.h>

// COM10 = Master
// COM9 = Slave A
// COM11 = Slave B
// COM14 = Slave APD pico
// When adding I2C - take code from A,B, or C, and remember to add lines in "processCommand" and "sendI2C" functions

// Communication variables
const int picoRX = 19;  // Connect to TX of Pico
const int picoTX = 18;  // Connect to RX of Pico
const int SLAVE1_ADDRESS = 8;  // I2C address of the first slave Arduino
const int SLAVE2_ADDRESS = 9;  // I2C address of the second slave Arduino (example)
const int SLAVE3_ADDRESS = 7; // I2C address of pico APD reader slave
bool passFlag = false;

// APD detector variables
const int countEnable = 13;     // Pin for resetting latch to LOW. Note Active-LOW
const int counterClear = 12;  // Pin clearing the counter IC
const int lastDigit = 11;    // Pin for reading the last digit of the counters

const int gShutPin = 9; // Pin for controlling the stepper motor pinhole shutter/LDR shutter
int ldr0pin = A0; // select the input pin for LDR
int ldr0value = 0; // variable to store the value coming from the sensor

// // ADP acquisition
// const int checkPin = 2; // Pin to receive the interrupt signal
// const int resetPin = 3;     // Pin to send the reset high signal

// Timing ariables
volatile unsigned long counter = 0; // Counter to increment
volatile unsigned long runCounter = 0; // runtime counter to increment
float runTime = 0.0;                // Time for the interrupt loop to run
unsigned long startTime = 0;        // Start time for the interrupt loop

// SoftwareSerial picoSerial(picoRX, picoTX);

void setup() {
  // Initialise pins
  pinMode(counterClear, OUTPUT);
  pinMode(lastDigit, INPUT);
  pinMode(countEnable, OUTPUT);
  pinMode(gShutPin, OUTPUT); // set up grating shutter pin

  digitalWrite(countEnable, LOW); // disable the toggle flip flop, initial state of output is 0V when countEnable is LOW.
  digitalWrite(counterClear, LOW); // clear the counter initially. Active-LOW
  // digitalWrite(loadRegisterPin, LOW);
  digitalWrite(gShutPin, LOW);

  Serial.begin(9600);
  // picoSerial.begin(9600);
  Serial1.begin(9600);
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
    processCommand(command);
    Serial.println("#CF");

  }

  // if (Serial1.available() > 0) {
  //   // Read the response from the Pico until a newline character is encountered
  //   // Serial.println("Reading from PICO - BUG");
  //   String response = picoSerial.readStringUntil('\n');
  //   response.trim();  // Removes any leading/trailing whitespace or newline characters
  //   if (response.length() == 0) {  // Check if the string is empty
  //     // If an empty string is received, skip the rest of the loop
  //     return;  // Skip the rest of this iteration of loop()
  //   }

  //   // Echo the message from the Pico
  //   // Serial.print("Message from Pico: ");
  //   Serial.println(response);
  // }
}

// void flushSerialBuffer(Serial1 &serial) {
//   while (serial.available() > 0) {
//     serial.read();
//   }
// }

void gShutter(String state) {
  if (state == "on") {
    digitalWrite(gShutPin, HIGH);
    Serial.println("Shutter closed, LDR ready");
  }
  else if (state == "off") {
    digitalWrite(gShutPin, LOW);
    Serial.println("Shutter open");
  }
}

void stepScanX(int numberOfSteps) {
  int counts = 0;
  while (counts <= numberOfSteps) {
    break;
  }
}

int sendToPico(String command) {
    String response = "";
    int count = 0;
    Serial1.print("UART-UNO-APD_pico:#");
    Serial1.println(command);

    while (Serial1.available() == 0 && count < 1000) {
      count ++;
      delay(1);
      // wait for a command from the pico (~120 ms)
    }

    response = readFromPico();
    // Serial.println(response);
    if (response == "1") {
      return 1;
    } 
    else {
      Serial.println("Code 0: coms error with PICO");
      return 0;
    }
}
    // flushSerialBuffer(picoSerial);


String readFromPico() {
  String response = ""; // Initialize the response variable outside the if block

  if (Serial1.available() > 0) {
    // Read the response from the Pico until a newline character is encountered
    response = Serial1.readStringUntil('\n');
    response.trim();  // Removes any leading/trailing whitespace or newline characters
    if (response.length() == 0) {  // Check if the string is empty
      // If an empty string is received, return immediately
      return response;
    }
    return response;
  }
}

// void acquireAPD(float acqtime) {
//   // Reset counter and start time
//   counter = 0;
//   digitalWrite(resetPin, HIGH);
//   // delay(0.001);  // Keep the reset high for a short period
//   startTime = millis();
//   digitalWrite(resetPin, LOW);
  
//   // Run the acquisition loop for the specified time
//   while (millis() - startTime < acqtime * 1000) {
//     // Check the state of the check pin
//     if (digitalRead(checkPin) == HIGH) {
//       // Send the reset high signal
//       digitalWrite(resetPin, HIGH);
//       // delay(0.001);  // Keep the reset high for a short period
//       digitalWrite(resetPin, LOW);
//       // Increment the counter
//       counter++;
//     }
//   // Report the counter value to the serial monitor

//   }
//   Serial.print("#DAT");
//   Serial.println(counter);
// }

// void APDcoms(String message) {
//   if (message.startsWith("acq")) {
//     String acqtimeStr = message.substring(3, message.length()); // get time component
//     float acqtime = acqtimeStr.toFloat(); // turn into a float
//     // Serial.print("Acquiring for ");
//     // Serial.print(acqtime);
//     // Serial.print(" seconds...\n");
//     acquireAPD(acqtime);
//   }
//   else if (message.startsWith("run")) {
//     String acqtimeStr = message.substring(3, message.length());
//     float acqtime = acqtimeStr.toFloat(); // turn into a float
//     Serial.println("Running for 30 loops...");
//     while (runCounter < 30) {
//       acquireAPD(acqtime);
//       runCounter++;
//     }
//     runCounter = 0;
//   }
//   Serial.println("#CF");
// }

String acquireAPD(float acquisitionTime) {
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

  // digitalWrite(loadRegisterPin, HIGH); // LOAD The values into the register...
  // delay(1);
  // digitalWrite(loadRegisterPin, LOW); 

  finalBit = digitalRead(lastDigit);

  int code = sendToPico("read");
  if (code == 0) {
    return;
  }
  Serial.print("finalBit: ");
  Serial.println(finalBit);

  // delay(1000);
  unsigned long wait_time = millis();
  
  while (millis() < (wait_time + 5*1000)) {
    while (Serial1.available() == 0) {
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
    Serial.print(data+"/");
    Serial.println(elapsedTime);
    // Serial.print("Elapsed time: ");
    // Serial.print(elapsedTime);
    // Serial.println(" us");
    // delay(500);
    digitalWrite(counterClear, LOW); // reset counter, active-low

    return response;
  }
  Serial.println("TIMEOUT waiting for PICO response.");
}

void processCommand(String command) {
  // Example command structure: "<A:1234>"
  // Serial.println(command);
  if (command.startsWith("p") && command.endsWith("p")) {
    String content = command.substring(1, command.length() - 1);  // Remove '<' and '>'
    String message = content.substring(0);  // The rest is the message
    Serial.println("Sending to pico");

    int code = sendToPico(message);
    if (code == 0) {
      // Serial.println("Code 0: coms error with PICO");
    return;
    }

    delay(500);
    String response = readFromPico();
    Serial.print("Response from Pico:");
    Serial.println(response);
    // Serial.println("#CF");
  }

  else if (command.startsWith("m") && command.endsWith("m")) { // process simple three-character commands followed by a float or int
    String response = "";
    String content = command.substring(1, command.length() - 1);  // Remove '<' and '>'
    String com = content.substring(0, 3);  // The 3 character command
    String comvalstring = content.substring(3, content.length()); 

    if (com == "acq") {
      float comVal = comvalstring.toFloat();
      response = acquireAPD(comVal);
      // Serial.println("#CF");
      return;
    }
    else if (com == "gsh") {
      gShutter(comvalstring);
      return;
    }
    else if (com == "ld0") {
      int count = 0;
      while (count < 5) {
        ldr0value += analogRead(ldr0pin);
        count ++;
      }
      Serial.print('t');
      Serial.println(ldr0value);
      ldr0value = 0;
      return;
    }
    else if (com == "run") {
      float comVal = comvalstring.toFloat();
      int count = 0;
      while (count < 30) {
        response = acquireAPD(comVal);
        count ++;
      }
    // Serial.println("#CF");
    return;
    }
    else {
      Serial.print("Command not recognised: ");
      Serial.println(content);
    }
  }

  else if (command.startsWith("o") && command.endsWith("o")) {
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
      // case 'D':
      //   // Serial.print("Acquiring for ");
      //   // Serial.print(message);
      //   // Serial.println("seconds...");
      //   APDcoms(message);
      //   break;
      default:
        Serial.println("Unknown device identifier - failed to send command");
        break;
    }
  } else {
    Serial.print("Invalid command format");
    // Serial.println("#CF");
  }
  // String response = readFromPico();
  // Serial.println(response);
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
