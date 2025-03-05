#include <Wire.h>
#include <AccelStepper.h>

// COM9 = Slave B

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
  stepperA.setMaxSpeed(5000);
  stepperA.setAcceleration(5000);
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
    else {
      processCommand(command);
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
  else {
    processCommand(command);
  }
  // else if (command.startsWith("scang1")) {
  //   String steps = command.substring(6);
  // }

  // else if (command == "calscan") {

  // }

}

int findNextAxisIndex(const String &command, int startIndex, const char *axes) {
  int nextIndex = command.length(); // Default to the end of the string
  for (int i = 0; axes[i] != '\0'; i++) {
    int tempIndex = command.indexOf(axes[i], startIndex);
    if (tempIndex != -1 && tempIndex < nextIndex) {
      nextIndex = tempIndex;
    }
  }
  return nextIndex;
}

String processStepCommand(String command) {
  // Initialize response string
  String response = "";

  // Parse commands for each axis
  int xPos = 0, yPos = 0, zPos = 0, aPos = 0;
  bool xMove = false, yMove = false, zMove = false, aMove = false;

  // List of valid axis identifiers
  const char *axes = "XYZA";

  // Find and process X-axis command
  int xIndex = command.indexOf('X');
  if (xIndex != -1) {
    int nextIndex = findNextAxisIndex(command, xIndex + 1, axes);
    xPos = command.substring(xIndex + 1, nextIndex).toInt();
    if (xPos != 0) {
      xMove = true;
    }
    response += "X" + String(xPos) + " ";
  }

  // Find and process Y-axis command
  int yIndex = command.indexOf('Y');
  if (yIndex != -1) {
    int nextIndex = findNextAxisIndex(command, yIndex + 1, axes);
    yPos = command.substring(yIndex + 1, nextIndex).toInt();
    if (yPos != 0) {
      yMove = true;
    }
    response += "Y" + String(yPos) + " ";
  }

  // Find and process Z-axis command
  int zIndex = command.indexOf('Z');
  if (zIndex != -1) {
    int nextIndex = findNextAxisIndex(command, zIndex + 1, axes);
    zPos = command.substring(zIndex + 1, nextIndex).toInt();
    if (zPos != 0) {
      zMove = true;
    }
    response += "Z" + String(zPos) + " ";
  }

  // Find and process A-axis command
  int aIndex = command.indexOf('A');
  if (aIndex != -1) {
    int nextIndex = findNextAxisIndex(command, aIndex + 1, axes);
    aPos = command.substring(aIndex + 1, nextIndex).toInt();
    if (aPos != 0) {
      aMove = true;
    }
    response += "A" + String(aPos) + " ";
  }

  // Move the stepper motors based on the parsed commands
  if (xMove) stepperX.move(xPos);
  if (yMove) stepperY.move(yPos);
  if (zMove) stepperZ.move(zPos);
  if (aMove) stepperA.move(aPos);

  // Print the response
  if (response == "") {
    response = "Unknown command UNO-B";
  }
  return response;
}

// void backlashCorrection() {
//   waitForMotorsInternal();
//   // remove backlash back
//   if (xMove) stepperX.move(-20);
//   if (yMove) stepperY.move(-20);
//   if (zMove) stepperZ.move(-20);
//   if (aMove) stepperA.move(-20);

//   waitForMotorsInternal();
//   // remove backlash forwards
//   if (xMove) stepperX.move(20);
//   if (yMove) stepperY.move(20);
//   if (zMove) stepperZ.move(20);
//   if (aMove) stepperA.move(20);
// }

void waitForMotorsInternal() {
  while (true) {
    if (stepperX.isRunning() == true) {
      continue;
    }
    else if (stepperY.isRunning() == true) {
      continue;
    }
    else if (stepperZ.isRunning() == true) {
      continue;
    }
    else if (stepperA.isRunning() == true) {
      continue;
    }
    return;
  }
}


void processCommand(String command) {
  
  if (command == "isrun") {
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
  else {
    response = processStepCommand(command);
  }
  Serial.println(response);
  // For this example, we just print the received command
  // You can set a flag or take some action based on the command
}

void requestEvent() {
  // Send the response set in receiveEvent
  String tosend = response+"\n";
  Wire.write(tosend.c_str());
}
