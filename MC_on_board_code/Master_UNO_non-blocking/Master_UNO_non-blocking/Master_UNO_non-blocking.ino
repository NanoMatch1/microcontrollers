#include <NeoSWSerial.h>

// NeoSWSerial picoSerial(12, 13);  // Pins 12 and 13 for RX, TX

// volatile bool newData = false;
// String dataBuffer = "";

// // ISR to handle incoming data
// void serialEvent() {
//   while (picoSerial.available()) {
//     char c = picoSerial.read();
//     dataBuffer += c;  // Buffer data
//     newData = true;
//   }
// }

// void setup() {
//   picoSerial.begin(9600);
//   picoSerial.attachInterrupt(serialEvent);
//   Serial.begin(9600);
//   Serial.println("Arduino ready to receive commands.");
// }

// void loop() {
//   if (Serial.available() > 0) {
//     // Read the command until a newline character is encountered
//     String command = Serial.readStringUntil('\n');
//     command.trim(); // Removes any leading/trailing whitespace or newline characters

//     // Send the command to the Raspberry Pi Pico
//     picoSerial.println(command);

//     // Echo the command back to the Serial Monitor
//     Serial.print("Command sent to Pico: ");
//     Serial.println(command);
//   }

//   if (newData) {
//     Serial.println("Starting transmission");
//     Serial.print("Coms from pico: ");
//     Serial.println(dataBuffer);  // Send the complete string to the serial port
//     dataBuffer = "";  // Clear buffer after processing
//     newData = false;  // Reset flag
//   }
//   // Other non-blocking or less time-sensitive code
//   // Serial.println("Other code executed");
//   delay(1); // Adding a delay to reduce the frequency of loop execution and easy monitoring
// }

NeoSWSerial picoSerial(12, 13); // Pins 12 and 13 for RX, TX

volatile bool newData = false;
volatile String dataBuffer = "";

void serialEvent() {
  while (picoSerial.available()) {
    char c = picoSerial.read();
    dataBuffer += c;
    newData = true;
  }
}

void setup() {
  picoSerial.begin(9600);
  picoSerial.attachInterrupt(serialEvent);
  Serial.begin(9600);
  Serial.println("Setup complete. Waiting for data...");
}

void loop() {
  if (newData) {
    Serial.print("Received from Pico: ");
    Serial.println(dataBuffer);
    dataBuffer = "";
    newData = false;
  }
}