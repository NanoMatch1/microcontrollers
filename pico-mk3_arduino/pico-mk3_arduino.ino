#include <Arduino.h>

const int lightPin = 17;

void setup() {
  Serial.begin(115200);   // USB serial
  Serial1.begin(115200);  // UART
  pinMode(lightPin, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command.startsWith("*")) {
      // Strip the asterisk and process the Pico-level command
      command = command.substring(1);
      processPicoCommand(command);
    } else {
      // It's a GCode command, send it directly
      Serial1.println(command);  // Sending GCode to MKS Gen V1.4 via UART
      Serial.print("Sent GCode: ");
      Serial.println(command);
    }
  }

  // Reading from 3D printer and forwarding to USB (optional)
  if (Serial1.available() > 0) {
    String printerResponse = Serial1.readStringUntil('\n');
    Serial.println(printerResponse);
  }
}

void processPicoCommand(String command) {
  // Implement your Pico-specific command processing logic here
  int spaceIndex = command.indexOf(' '); // Find the space
  String commandType = command.substring(0, spaceIndex); // Extract the command type
  String commandValue = command.substring(spaceIndex + 1); 
  if (commandType == "light") {
    int duty = commandValue.toInt();
    analogWrite(lightPin, duty);
  }
  Serial.print("Processed Pico Command: ");
  Serial.println(command);
  // For example, parsing and executing different functions based on the command
}
