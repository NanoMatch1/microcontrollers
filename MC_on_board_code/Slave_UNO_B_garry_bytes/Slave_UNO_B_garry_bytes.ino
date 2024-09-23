#include <Wire.h>
#include <AccelStepper.h>

// Define stepper motor connections
AccelStepper stepperX(AccelStepper::DRIVER, 2, 5);  // Pin 2 = step, Pin 5 = direction for X Axis
AccelStepper stepperY(AccelStepper::DRIVER, 3, 6);  // Pin 3 = step, Pin 6 = direction for Y Axis
AccelStepper stepperZ(AccelStepper::DRIVER, 4, 7);  // Pin 4 = step, Pin 7 = direction for Z Axis
AccelStepper stepperA(AccelStepper::DRIVER, 12, 13); // Pin 12 = step, Pin 13 = direction for A Axis

const int SLAVE_ADDRESS = 9;  // I2C address of this slave Arduino
byte responseCode = 0x00;  // Byte response code

// Function prototypes
void receiveEvent(int howMany);
void requestEvent();

void setup() {
  Wire.begin(SLAVE_ADDRESS);  // Initialize I2C as slave
  Wire.onReceive(receiveEvent);  // Register event handler for received data
  Wire.onRequest(requestEvent);  // Register event handler for data requests
  Serial.begin(9600);

  // Set max speed and acceleration for stepper motors
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
  // Run the steppers
  stepperX.run();
  stepperY.run();
  stepperZ.run();
  stepperA.run();
}

// Event handler for received data
void receiveEvent(int howMany) {
  if (howMany < 1) return;  // No data received
  
  byte command = Wire.read();  // First byte is the command

  switch (command) {
    case 0x01:  // "status" command
      responseCode = 0x01;  // Set response to "status OK"
      break;
      
    case 0x02:  // "isrun" command: Check if any motor is running
      if (stepperX.isRunning() || stepperY.isRunning() || stepperZ.isRunning() || stepperA.isRunning()) {
        responseCode = 0x01;  // Motors running
      } else {
        responseCode = 0x00;  // Motors stopped
      }
      break;

    case 0x03:  // "setpos" command: Set new positions for steppers
      if (howMany == 9) {  // Expecting 8 bytes for 4 positions (2 bytes per motor)
        int posX = (Wire.read() << 8) | Wire.read();  // Read 2 bytes for X position
        int posY = (Wire.read() << 8) | Wire.read();  // Read 2 bytes for Y position
        int posZ = (Wire.read() << 8) | Wire.read();  // Read 2 bytes for Z position
        int posA = (Wire.read() << 8) | Wire.read();  // Read 2 bytes for A position

        stepperX.setCurrentPosition(posX);
        stepperY.setCurrentPosition(posY);
        stepperZ.setCurrentPosition(posZ);
        stepperA.setCurrentPosition(posA);

        responseCode = 0x02;  // Acknowledge position set
      }
      break;

    case 0x04:  // "getpos" command: Get current positions of the motors
      responseCode = 0x03;  // Ready to send positions
      break;

    default:
      responseCode = 0xFF;  // Unknown command
      break;
  }
}

// Event handler for data requests (Master asks for data)
void requestEvent() {
  if (responseCode == 0x03) {
    // Send current motor positions as 8 bytes (2 bytes per motor)
    Wire.write(stepperX.currentPosition() >> 8);  // High byte for X
    Wire.write(stepperX.currentPosition() & 0xFF);  // Low byte for X
    Wire.write(stepperY.currentPosition() >> 8);  // High byte for Y
    Wire.write(stepperY.currentPosition() & 0xFF);  // Low byte for Y
    Wire.write(stepperZ.currentPosition() >> 8);  // High byte for Z
    Wire.write(stepperZ.currentPosition() & 0xFF);  // Low byte for Z
    Wire.write(stepperA.currentPosition() >> 8);  // High byte for A
    Wire.write(stepperA.currentPosition() & 0xFF);  // Low byte for A
  } else {
    // Send the 1-byte response code for simple commands
    Wire.write(responseCode);
  }
}
