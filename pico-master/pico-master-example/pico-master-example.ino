#include <SPI.h>

const byte ssPin = 10; // Slave Select pin

void setup() {
  // Set the Slave Select Pin as output
  pinMode(ssPin, OUTPUT);
  
  // Initialize SPI:
  SPI.begin();
  
  // Set SPI clock speed and format
  SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE0));
  
  Serial.begin(9600); // Start serial communication at 9600 baud rate
}

void loop() {
  digitalWrite(ssPin, LOW); // Select the slave device
  
  // Send a command to the slave device
  byte command = 0x01; // Example command
  SPI.transfer(command);
  
  // Deselect the slave device
  digitalWrite(ssPin, HIGH);
  
  // Small delay to allow the slave to process the command
  delay(1000); // Wait for 1 second
  
  // Send and receive more commands as needed
}

void endSPI() {
  SPI.endTransaction(); // End the SPI transaction
}
