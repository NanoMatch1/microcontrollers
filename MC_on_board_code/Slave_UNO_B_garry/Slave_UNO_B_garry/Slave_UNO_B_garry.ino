#include <Wire.h>

#include <AccelStepper.h>

// Define stepper motor connections (adjust pin numbers based on CNC Shield wiring)
AccelStepper stepperX(AccelStepper::DRIVER, 2, 5);  // Pin 2 = step, Pin 5 = direction for X Axis
AccelStepper stepperY(AccelStepper::DRIVER, 3, 6);  // Pin 3 = step, Pin 6 = direction for Y Axis
AccelStepper stepperZ(AccelStepper::DRIVER, 4, 7);  // Pin 4 = step, Pin 7 = direction for Z Axis
AccelStepper stepperA(AccelStepper::DRIVER, 10, 11); // Pin 10 = step, Pin 11 = direction for A Axis

const int stepPin = 3;
const int enablePinA = 8;  // Enable pin for Stepper A
const int enablePinB = 9;  // Enable pin for Stepper B
const int enablePinC = 12; // Enable pin for Stepper C (Z Axis)
const int enablePinD = 13; // Enable pin for Stepper D (A Axis)

const int SLAVE_ADDRESS = 9;  // I2C address of this slave Arduino
int testFlag = 0;

void setup() {
  Wire.begin(SLAVE_ADDRESS);  // Initialize I2C as slave
  Wire.onReceive(receiveEvent);  // Register event handler for received data
  Wire.onRequest(requestEvent);  // Register event handler for data requests
  Serial.begin(9600);

  pinMode(stepPin, OUTPUT);
  pinMode(enablePinA, OUTPUT);
  pinMode(enablePinB, OUTPUT);
  pinMode(enablePinC, OUTPUT);
  pinMode(enablePinD, OUTPUT);

  stepperX.setMaxSpeed(1000);
  stepperX.setAcceleration(1000);
  stepperY.setMaxSpeed(1000);
  stepperY.setAcceleration(1000);
  stepperZ.setMaxSpeed(1000);
  stepperZ.setAcceleration(1000);
  stepperA.setMaxSpeed(1000);
  stepperA.setAcceleration(1000);
}

void loop() {
  stepperX.run();
  stepperY.run();
  stepperZ.run();
  stepperA.run();
  // Main loop does nothing, all work done in event handlers
}



void receiveEvent(int howMany) {
  String command = "";
  while (Wire.available()) {
    char c = Wire.read();
    command += c;
  }

  // Serial.print("Received command: ");
  // Serial.println(command);

  // Process the command here
  // (You can add more complex command processing logic if needed)
  
  if (command == "test") {
    testFlag = 2;
    }
  else {
    testFlag = 0;
  }

  else if (command.startsWith("X")) {
    // Extract number from command and move X-axis
    int pos = command.substring(1).toInt();
    stepperX.moveTo(pos);
    Serial.print("Moving X: ");
    Serial.println(pos);
  } else if (command.startsWith("Y")) {
    // Extract number from command and move Y-axis
    int pos = command.substring(1).toInt();
    stepperY.moveTo(pos);
    Serial.print("Moving Y: ");
    Serial.println(pos);
  } else if (command.startsWith("Z")) {
    // Extract number from command and move Z-axis
    int pos = command.substring(1).toInt();
    stepperZ.moveTo(pos);
    Serial.print("Moving Z: ");
    Serial.println(pos);
  } else if (command.startsWith("A")) {
    // Extract number from command and move A-axis
    int pos = command.substring(1).toInt();
    stepperA.moveTo(pos);
    Serial.print("Moving A: ");
    Serial.println(pos);
  }
  }



  // For this example, we just print the received command
  // You can set a flag or take some action based on the command
}

void requestEvent() {
  // Send back a completion message
  String response = "ccB"+String(testFlag)+"\n";
  Wire.write(response.c_str());
}
