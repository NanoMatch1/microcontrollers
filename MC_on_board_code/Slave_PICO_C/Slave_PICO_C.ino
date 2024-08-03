// // Define pins
// #include <Wire.h>

// const int slaveAddress = 0x07; // I2C address of the slave device
// const int interruptPin = 2; // GPIO pin for the interrupt from the TC pin
// const int resetPin = 3; // GPIO pin to output the TTL high pulse to reset the counter
// volatile unsigned long interruptCounter = 0;
// int testFlag = 0;

// void setup() {
//   Wire.begin(slaveAddress); // Join I2C bus as a slave with address 0x08
//   Wire.onReceive(receiveEvent); // Register event handler for receiving data
//   Wire.onRequest(requestEvent); // Register event handler for sending data

//   // Set pin modes
//   pinMode(interruptPin, INPUT);
//   pinMode(resetPin, OUTPUT);
//   digitalWrite(resetPin, LOW); // Ensure the reset pin starts low

//   // Attach interrupt to the interrupt pin
//   attachInterrupt(digitalPinToInterrupt(interruptPin), TC_ISR, RISING);
//   // Serial.begin(115200);

// }

// void loop() {
//   // Output the interrupt counter value to the serial monitor
//   // Serial.print("Interrupt Counter: ");
//   // Serial.println(interruptCounter);

//   // Optional: Add any other code that needs to run continuously
//   // delay(1000); // Adjust delay as needed for your application
// }

// // Function to handle data received from the master
// void receiveEvent(int howMany) {
//   String command = "";
//   while (Wire.available()) {
//     char c = Wire.read();
//     command += c;
//   }

//   Serial.println(command);

//   if (command == "test") {
//     testFlag = 3;
//     // Serial.println("sending test flag");
//     }
//   else if (command == "report") {
//     testFlag = interruptCounter;
//     interruptCounter = 0;
//   }
//   else {
//     testFlag = 0;
//   }
//   // For this example, we just print the received command
//   // You can set a flag or take some action based on the command

// }

// // Function to handle data requested by the master
// void requestEvent() {
//   // Send back a completion message
//   // Serial.print("sending back test flag:");
//   // Serial.println("ccC"+String(testFlag)+"\n");
//   String response = "ccC"+String(testFlag)+"\n";
//   Wire.write(response.c_str());
// }

// // ISR to handle the interrupt
// void TC_ISR() {
//   interruptCounter++; // Increment the counter on each interrupt
//   digitalWrite(resetPin, HIGH); // Output TTL high pulse to reset counter
//   delayMicroseconds(0.1); // Ensure the signal is high long enough to be registered
//   digitalWrite(resetPin, LOW); // Set the reset pin back to low
// }

#include <Wire.h>

const int SLAVE_ADDRESS = 7;  // I2C address of this slave Arduino
int testFlag = 0;

void setup() {
  Wire.begin(SLAVE_ADDRESS);  // Initialize I2C as slave
  Wire.onReceive(receiveEvent);  // Register event handler for received data
  Wire.onRequest(requestEvent);  // Register event handler for data requests
  Serial.begin(9600);
}

void loop() {
  // Main loop does nothing, all work done in event handlers
}



void receiveEvent(int howMany) {
  String command = "";
  while (Wire.available()) {
    char c = Wire.read();
    command += c;
  }

  while (Wire.available()) {
    Wire.read();
  }

  // Serial.print("Received command: ");
  // Serial.println(command);

  // Process the command here
  // (You can add more complex command processing logic if needed)
  
  if (command == "test") {
    testFlag = 3;
    }
  else {
    testFlag = 0;
  }


  // For this example, we just print the received command
  // You can set a flag or take some action based on the command
}

void requestEvent() {
  // Send back a completion message
  String response = "ccC"+String(testFlag)+"\n";
  Wire.write(response.c_str());
}


