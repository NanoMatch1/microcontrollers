#include <Wire.h>

const int SLAVE_ADDRESS = 9;  // I2C address of this slave Arduino
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


  // For this example, we just print the received command
  // You can set a flag or take some action based on the command
}

void requestEvent() {
  // Send back a completion message
  String response = "ccB"+String(testFlag)+"\n";
  Wire.write(response.c_str());
}
