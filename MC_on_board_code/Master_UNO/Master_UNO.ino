#include <SoftwareSerial.h>

const int picoRX = 12;  // Connect to TX of Pico
const int picoTX = 13;  // Connect to RX of Pico
bool passFlag = false;


SoftwareSerial picoSerial(picoRX, picoTX);

void setup() {
  Serial.begin(9600);
  picoSerial.begin(9600);
  Serial.println("Arduino is ready to receive commands.");
}

void loop() {
  if (Serial.available() > 0) {
    // Read the command until a newline character is encountered
    String command = Serial.readStringUntil('\n');

    
    command.trim(); // Removes any leading/trailing whitespace or newline characters
    if (command.length() == 0) {  // Check if the string is empty
      // If an empty string is received, skip the rest of the loop
      return;  // Skip the rest of this iteration of loop()
    }

    // Send the command to the Raspberry Pi Pico
    picoSerial.print("UART-UNO-APD_pico:#");
    picoSerial.println(command);

    // Echo the command back to the Serial Monitor
    // Serial.print("Command sent to Pico: ");
    // Serial.println(command);
  }

  if (picoSerial.available() > 0) {
    // Read the response from the Pico until a newline character is encountered
    String response = picoSerial.readStringUntil('\n');
    response.trim(); // Removes any leading/trailing whitespace or newline characters
    if (response.length() == 0) {  // Check if the string is empty
      // If an empty string is received, skip the rest of the loop
      return;  // Skip the rest of this iteration of loop()
    }

    // Echo the message from the Pico
    // Serial.print("Message from Pico: ");
    Serial.println(response);
  }
}