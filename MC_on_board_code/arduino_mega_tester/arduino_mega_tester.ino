/*
  Multi-Module Stepper Motor Control using AccelStepper Library

  This code controls four modules, each containing four stepper motors (A, X, Y, Z), using the AccelStepper library.
  The stepper motors are driven in DRIVER mode, where each motor is controlled by a step and direction pin.

  - Each module follows the naming pattern: A (first), X, Y, Z.
  - Commands are received over Serial communication in the format:
    "<module><motor><position>"
    e.g., "1A1000" moves module 1's A motor to position 1000.
  - The motors are updated dynamically in the loop to allow smooth movement.
  - Acceleration and speed are set uniformly across all motors.
*/

#include <AccelStepper.h>

AccelStepper stepperA1(AccelStepper::DRIVER, 24, 25);
AccelStepper stepperX1(AccelStepper::DRIVER, 26, 27);
AccelStepper stepperY1(AccelStepper::DRIVER, 28, 29);
AccelStepper stepperZ1(AccelStepper::DRIVER, 22, 23);

AccelStepper stepperA2(AccelStepper::DRIVER, 30, 31);
AccelStepper stepperX2(AccelStepper::DRIVER, 32, 33);
AccelStepper stepperY2(AccelStepper::DRIVER, 34, 35);
AccelStepper stepperZ2(AccelStepper::DRIVER, 36, 37);

AccelStepper stepperA3(AccelStepper::DRIVER, 38, 39);
AccelStepper stepperX3(AccelStepper::DRIVER, 40, 41);
AccelStepper stepperY3(AccelStepper::DRIVER, 42, 43);
AccelStepper stepperZ3(AccelStepper::DRIVER, 44, 45);

AccelStepper stepperA4(AccelStepper::DRIVER, 46, 47);
AccelStepper stepperX4(AccelStepper::DRIVER, 48, 49);
AccelStepper stepperY4(AccelStepper::DRIVER, 50, 51);
AccelStepper stepperZ4(AccelStepper::DRIVER, 52, 53);

const int ldr0pin = A0;      // LDR input pin
const int gShutPin = 9;      // Grating shutter pin


// Variables
int ldr0value = 0;
volatile unsigned long counter = 0;

void setup() {
    Serial.begin(9600);
    AccelStepper* steppers[] = {&stepperA1, &stepperX1, &stepperY1, &stepperZ1,
                                &stepperA2, &stepperX2, &stepperY2, &stepperZ2,
                                &stepperA3, &stepperX3, &stepperY3, &stepperZ3,
                                &stepperA4, &stepperX4, &stepperY4, &stepperZ4};
    
    for (int i = 0; i < 16; i++) {
        steppers[i]->setMaxSpeed(5000);
        steppers[i]->setAcceleration(5000);
    }

  pinMode(gShutPin, OUTPUT);
  digitalWrite(gShutPin, LOW);

}

void loop() {
    stepperA1.run(); stepperX1.run(); stepperY1.run(); stepperZ1.run();
    stepperA2.run(); stepperX2.run(); stepperY2.run(); stepperZ2.run();
    stepperA3.run(); stepperX3.run(); stepperY3.run(); stepperZ3.run();
    stepperA4.run(); stepperX4.run(); stepperY4.run(); stepperZ4.run();

    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        parseCommand(command);
        Serial.println("#CF");
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

void parseMotionCommand(String command) {
    AccelStepper* steppers[] = {&stepperA1, &stepperX1, &stepperY1, &stepperZ1,
                                &stepperA2, &stepperX2, &stepperY2, &stepperZ2,
                                &stepperA3, &stepperX3, &stepperY3, &stepperZ3,
                                &stepperA4, &stepperX4, &stepperY4, &stepperZ4};


    char module = command.charAt(0);
    int motorIndex = (module - '1') * 4; 
    char motor = command.charAt(1);
    int pos = command.substring(2).toInt();
      
    switch (motor) {
        case 'A': steppers[motorIndex]->move(pos); break;
        case 'X': steppers[motorIndex + 1]->move(pos); break;
        case 'Y': steppers[motorIndex + 2]->move(pos); break;
        case 'Z': steppers[motorIndex + 3]->move(pos); break;
    }
  Serial.print("Moving motor ");
  Serial.print(module);
  Serial.print(motor);
  Serial.println(pos);
}


void parseCommand(String command) {
    if (command.startsWith("o") && command.endsWith("o")) {
      parseMotionCommand(command.substring(1, command.length() - 1));
    }

    else if (command.startsWith("m") && command.endsWith("m")) {
      String content = command.substring(1, command.length() - 1);
      String com = content.substring(0, 3);
      String comvalstring = content.substring(4); //Assumes space in message
    

      if (com == "gsh") {
        monoShutter(comvalstring);
      } else if (com == "ld0") {
        readLDR();
      } else {
        Serial.println("Unknown command.");
      }
    }
}
