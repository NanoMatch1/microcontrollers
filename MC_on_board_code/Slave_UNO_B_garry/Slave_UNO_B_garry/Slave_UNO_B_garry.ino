#include <Wire.h>
#include <AccelStepper.h>

// TODO: Add case separators for relative and asbolute positioning

// Define stepper motor connections (adjust pin numbers based on CNC Shield wiring)
AccelStepper stepperX(AccelStepper::DRIVER, 2, 5);  // Pin 2 = step, Pin 5 = direction for X Axis
AccelStepper stepperY(AccelStepper::DRIVER, 3, 6);  // Pin 3 = step, Pin 6 = direction for Y Axis
AccelStepper stepperZ(AccelStepper::DRIVER, 4, 7);  // Pin 4 = step, Pin 7 = direction for Z Axis
AccelStepper stepperA(AccelStepper::DRIVER, 12, 13); // Pin 10 = step, Pin 11 = direction for A Axis

// const int stepPin = 3;
// const int enablePinA = 8;  // Enable pin for Stepper A
// const int enablePinB = 9;  // Enable pin for Stepper B
// const int enablePinC = 12; // Enable pin for Stepper C (Z Axis)
// const int enablePinD = 13; // Enable pin for Stepper D (A Axis)


const int SLAVE_ADDRESS = 9;  // I2C address of this slave Arduino
String testFlag = "0";

String identifier = "Uno-B Garry";
String response = "";

// Function prototypes
void receiveEvent(int howMany);
void requestEvent();

void setup() {
  Wire.begin(SLAVE_ADDRESS);  // Initialize I2C as slave
  Wire.onReceive(receiveEvent);  // Register event handler for received data
  Wire.onRequest(requestEvent);  // Register event handler for data requests
  Serial.begin(9600);

  // pinMode(stepPin, OUTPUT);
  // pinMode(enablePinA, OUTPUT);
  // pinMode(enablePinB, OUTPUT);
  // pinMode(enablePinC, OUTPUT);
  // pinMode(enablePinD, OUTPUT);

  stepperX.setMaxSpeed(5000);
  stepperX.setAcceleration(5000);
  stepperY.setMaxSpeed(5000);
  stepperY.setAcceleration(5000);
  stepperZ.setMaxSpeed(5000);
  stepperZ.setAcceleration(5000);
  stepperA.setMaxSpeed(1000);
  stepperA.setAcceleration(1000);
}

void loop() {
  stepperX.run();
  stepperY.run();
  stepperZ.run();
  stepperA.run();
  if (Serial.available() > 0) {
    // Read the command until a newline character is encountered
    String command = Serial.readStringUntil('\n');
    command.trim();  // Removes any leading/trailing whitespace or newline characters
    if (command.length() == 0) {  // Check if the string is empty
      // If an empty string is received, skip the rest of the loop
      return;  // Skip the rest of this iteration of loop()
    } else if (command == "status") {
      Serial.println(identifier);
    }
    // Main loop does nothing, all work done in event handlers
  }
}

// void scanAndRead() {
//       int index = 0;
//       int totalSteps = 20;
//       int stepIncrement = 2;
//       int pos = 0;
    
//     // Loop through each step position
//     // for (int pos = 0; pos <= totalSteps; pos += stepIncrement) {
//     while (index <= totalSteps) {
//         stepperX.move(stepIncrement); // Move motor
//         delay(1); // Wait for motor to stabilize
        
//         int analogValue = analogRead(ANALOG_PIN); // Read analog input
        
//         // Store the data
//         stepPosition[index] = pos;
//         analogValues[index] = analogValue;
//         index++;
//         pos++;
//     }
// }

void receiveEvent(int howMany) {
  String command = "";
  while (Wire.available()) {
    char c = Wire.read();
    command += c;
  }

  // Process the command here
  // (You can add more complex command processing logic if needed)
  if (command == "test") {
    testFlag = "2";
    response = "Test mode activated";
  } 
  // else if (command.startsWith("scang1")) {
  //   String steps = command.substring(6);
  // }

  // else if (command == "calscan") {

  // }



  else if (command == "isrun") {
    if (stepperX.isRunning() == true) {
      response = "R1";
    }
    else if (stepperY.isRunning() == true) {
      response = "R1";
    }
    else if (stepperZ.isRunning() == true) {
      response = "R1";
    }
    else if (stepperA.isRunning() == true) {
      response = "R1";
    }

    else {
      response = "S0";
    }
  }
  else if (command.startsWith("setpos")) {
    String newPositions = command.substring(6);
    char str[newPositions.length() + 1];
    newPositions.toCharArray(str, newPositions.length() + 1);

    int pos1, pos2, pos3, pos4;

    // Pointer to hold each part after splitting
    char *token;

    // Split the string by ',' and process each token
    // Split the string by ',' and process each token
    token = strtok(str, ",");
    if (token != NULL) pos1 = atoi(token); // Assign first value to pos1
    token = strtok(NULL, ",");
    if (token != NULL) pos2 = atoi(token); // Assign second value to pos2
    token = strtok(NULL, ",");
    if (token != NULL) pos3 = atoi(token); // Assign third value to pos3
    token = strtok(NULL, ",");
    if (token != NULL) pos4 = atoi(token); // Assign fourth value to pos4
    // response = token;
    //Serial.println("newPosition");

    stepperX.setCurrentPosition(pos1);
    stepperY.setCurrentPosition(pos2);
    stepperZ.setCurrentPosition(pos3);
    stepperA.setCurrentPosition(pos4);
    
    response = "S0";
  }
  else if (command == "status") {
    response = identifier;
  } 
  else if (command == "pos") {
    String currentPosition = ("<PX"+String(stepperX.currentPosition())+",Y"+String(stepperY.currentPosition())+",Z"+String(stepperZ.currentPosition())+",A"+String(stepperA.currentPosition())+"P>");
    response = currentPosition;
  }
    else if (command.startsWith("X")) {
    // Extract number from command and move X-axis
    int pos = command.substring(1).toInt();
    stepperX.move(pos);
    response = "X" + String(pos);
  } else if (command.startsWith("Y")) {
    // Extract number from command and move Y-axis
    int pos = command.substring(1).toInt();
    stepperY.move(pos);
    response = "Y" + String(pos);
  } else if (command.startsWith("Z")) {
    // Extract number from command and move Z-axis
    int pos = command.substring(1).toInt();
    stepperZ.move(pos);
    response = "Z" + String(pos);
  } else if (command.startsWith("A")) {
    // Extract number from command and move A-axis
    int pos = command.substring(1).toInt();
    stepperA.move(pos);
    response = "A" + String(pos);
  } else {
    testFlag = "0";
    response = "Unknown command";
  }

  // For this example, we just print the received command
  // You can set a flag or take some action based on the command
}

void requestEvent() {
  // Send the response set in receiveEvent
  String tosend = response+"\n";
  Wire.write(tosend.c_str());
}
